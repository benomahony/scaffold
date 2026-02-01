"""Test caching functionality for bulk commands."""

import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from scaffold.core import _get_latest_file_mtime, _run_command_on_repo
from scaffold.storage import CommandResult, ResultStorage


def test_get_latest_file_mtime(tmp_path: Path) -> None:
    """Test getting latest file modification time."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    # Create some files
    (tmp_path / "file1.py").write_text("content1")
    time.sleep(0.1)
    (tmp_path / "file2.py").write_text("content2")

    mtime = _get_latest_file_mtime(tmp_path)

    assert mtime is not None, "Must return a datetime"
    assert isinstance(mtime, datetime), "Must be datetime type"
    # Should be recent (within last minute)
    assert datetime.now() - mtime < timedelta(minutes=1), "Must be recent timestamp"


def test_get_latest_file_mtime_skips_cache_dirs(tmp_path: Path) -> None:
    """Test that cache directories are skipped."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    # Create regular file
    (tmp_path / "important.py").write_text("content")
    time.sleep(0.1)

    # Create files in cache directories (should be ignored)
    cache_dir = tmp_path / "__pycache__"
    cache_dir.mkdir()
    time.sleep(0.1)
    (cache_dir / "cached.pyc").write_text("cached content")

    mtime = _get_latest_file_mtime(tmp_path)

    # The mtime should be from important.py, not the cached file
    important_mtime = datetime.fromtimestamp((tmp_path / "important.py").stat().st_mtime)
    assert abs((mtime - important_mtime).total_seconds()) < 1, "Must use non-cache file time"


def test_cache_hit_skips_command_execution(tmp_path: Path) -> None:
    """Test that cached results are used when files haven't changed."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    # Create a test repo
    test_repo = tmp_path / "test-repo"
    test_repo.mkdir()
    (test_repo / "pyproject.toml").write_text('[project]\nname = "test-repo"\n')
    (test_repo / "test.py").write_text("def test_foo(): pass")

    storage = ResultStorage(tmp_path / "storage")

    # Create a cached result that's newer than all files
    future_time = datetime.now() + timedelta(seconds=5)
    cached_result = CommandResult(
        repo_path=str(test_repo),
        repo_name="test-repo",
        command="pytest",
        timestamp=future_time,
        exit_code=0,
        duration_seconds=1.0,
        stdout="cached output",
        stderr="",
    )
    storage.save_result(cached_result)

    # Run command without force - should use cache
    result = _run_command_on_repo(test_repo, "pytest", storage=storage, force=False)

    assert result.stdout == "cached output", "Must use cached result"
    assert result.timestamp == future_time, "Must return cached timestamp"


def test_cache_miss_runs_command_when_files_changed(tmp_path: Path) -> None:
    """Test that commands run when files are newer than cache."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    # Create a test repo
    test_repo = tmp_path / "test-repo"
    test_repo.mkdir()
    (test_repo / "pyproject.toml").write_text('[project]\nname = "test-repo"\n')

    storage = ResultStorage(tmp_path / "storage")

    # Create a cached result that's older than files
    old_time = datetime.now() - timedelta(hours=1)
    cached_result = CommandResult(
        repo_path=str(test_repo),
        repo_name="test-repo",
        command="pytest",
        timestamp=old_time,
        exit_code=0,
        duration_seconds=1.0,
        stdout="old cached output",
        stderr="",
    )
    storage.save_result(cached_result)

    # Modify a file (making it newer than cache)
    (test_repo / "test.py").write_text("def test_bar(): pass")

    # Run command - should NOT use cache
    result = _run_command_on_repo(test_repo, "pytest", storage=storage, force=False, timeout=1)

    # The result should be different from cached (new execution)
    assert result.timestamp > old_time, "Must have new timestamp"
    # Command will fail but that's OK - we're testing cache logic
    assert result.exit_code != 0 or result.stdout != "old cached output", "Must run new command"


def test_force_flag_bypasses_cache(tmp_path: Path) -> None:
    """Test that force=True always runs command."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    # Create a test repo
    test_repo = tmp_path / "test-repo"
    test_repo.mkdir()
    (test_repo / "pyproject.toml").write_text('[project]\nname = "test-repo"\n')
    (test_repo / "test.py").write_text("def test_foo(): pass")

    storage = ResultStorage(tmp_path / "storage")

    # Create a cached result that's newer than all files
    future_time = datetime.now() + timedelta(seconds=5)
    cached_result = CommandResult(
        repo_path=str(test_repo),
        repo_name="test-repo",
        command="pytest",
        timestamp=future_time,
        exit_code=0,
        duration_seconds=1.0,
        stdout="cached output",
        stderr="",
    )
    storage.save_result(cached_result)

    # Run with force=True - should NOT use cache
    result = _run_command_on_repo(test_repo, "pytest", storage=storage, force=True, timeout=1)

    # Should have new timestamp (cache bypassed)
    assert result.timestamp > future_time or result.stdout != "cached output", "Must bypass cache"
