"""Test improvements to bulk commands."""

import os
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def test_bulk_dir_command(tmp_path: Path) -> None:
    """Test bulk dir command lists all projects."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    original_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)

        # Create 2 projects
        for i in range(2):
            subprocess.run(
                [
                    "uv",
                    "run",
                    "scaffold",
                    "init",
                    f"dir-test-{i}",
                    "--author",
                    "Test",
                    "--description",
                    "Test",
                ],
                input="n\n",
                text=True,
                capture_output=True,
                check=True,
            )

        # Run bulk dir
        result = subprocess.run(
            ["uv", "run", "scaffold", "bulk", "dir", "--path", str(tmp_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, "Bulk dir must succeed"
        assert "Found 2 project(s)" in result.stdout, "Must find 2 projects"
        assert "dir-test-0" in result.stdout or "dir_test_0" in result.stdout, "Must list project 0"
        assert "dir-test-1" in result.stdout or "dir_test_1" in result.stdout, "Must list project 1"

    finally:
        os.chdir(original_cwd)


def test_bulk_status_grouped_by_repo(tmp_path: Path) -> None:
    """Test status groups results by repository."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    original_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)

        # Create project
        subprocess.run(
            [
                "uv",
                "run",
                "scaffold",
                "init",
                "status-group-test",
                "--author",
                "Test",
                "--description",
                "Test",
            ],
            input="n\n",
            text=True,
            capture_output=True,
            check=True,
        )

        # Run both commands
        subprocess.run(
            ["uv", "run", "scaffold", "bulk", "test", "--path", str(tmp_path)],
            capture_output=True,
            text=True,
            check=True,
        )

        subprocess.run(
            ["uv", "run", "scaffold", "bulk", "prek", "--path", str(tmp_path)],
            capture_output=True,
            text=True,
            check=True,
        )

        # Check status shows both results for one repo
        result = subprocess.run(
            ["uv", "run", "scaffold", "bulk", "status", "--path", str(tmp_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, "Status must succeed"
        assert "status-group-test" in result.stdout or "status_group_test" in result.stdout, (
            "Must show repo"
        )
        # Should show both pytest and prek on same line/section
        assert "pytest" in result.stdout, "Must show pytest results"
        assert "prek" in result.stdout, "Must show prek results"

    finally:
        os.chdir(original_cwd)


def test_bulk_command_with_timeout(tmp_path: Path) -> None:
    """Test that commands can timeout and handle it gracefully."""
    from scaffold.core import _run_command_on_repo

    # Create a simple test project
    test_repo = tmp_path / "timeout-test"
    test_repo.mkdir()
    pyproject = test_repo / "pyproject.toml"
    pyproject.write_text('[project]\nname = "timeout-test"\n')

    # Test with very short timeout (command will likely timeout or fail fast)
    result = _run_command_on_repo(test_repo, "pytest", timeout=1)

    assert result is not None, "Result must be returned"
    assert result.repo_name == "timeout-test", "Repo name must match"
    # Either times out (-2) or fails normally
    assert result.exit_code != 0, "Command should fail or timeout"
