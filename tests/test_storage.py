import json
from datetime import datetime, timedelta
from pathlib import Path

from scaffold.storage import CommandResult, ResultStorage


def test_save_result_creates_directory(tmp_path: Path) -> None:
    """Test that save_result creates storage directory if it doesn't exist."""
    storage_dir = tmp_path / "test_scaffold"
    assert not storage_dir.exists(), "Storage directory should not exist initially"

    storage = ResultStorage(storage_dir)
    result = CommandResult(
        repo_path=str(tmp_path / "test-repo"),
        repo_name="test-repo",
        command="pytest",
        timestamp=datetime.now(),
        exit_code=0,
        duration_seconds=1.5,
        stdout="All tests passed",
        stderr="",
        git_commit="abc123",
    )

    storage.save_result(result)

    assert storage_dir.exists(), "Storage directory must be created"
    assert storage.status_file.exists(), "Status file must be created"


def test_save_result_appends_to_file(tmp_path: Path) -> None:
    """Test that save_result appends results as JSON lines."""
    storage = ResultStorage(tmp_path)

    result1 = CommandResult(
        repo_path=str(tmp_path / "repo1"),
        repo_name="repo1",
        command="pytest",
        timestamp=datetime.now(),
        exit_code=0,
        duration_seconds=1.0,
        stdout="passed",
        stderr="",
    )

    result2 = CommandResult(
        repo_path=str(tmp_path / "repo2"),
        repo_name="repo2",
        command="prek",
        timestamp=datetime.now(),
        exit_code=1,
        duration_seconds=2.0,
        stdout="",
        stderr="error",
    )

    storage.save_result(result1)
    storage.save_result(result2)

    lines = storage.status_file.read_text().strip().split("\n")
    assert len(lines) == 2, "Must have two JSON lines"

    parsed1 = json.loads(lines[0])
    assert parsed1["repo_name"] == "repo1", "First result must be repo1"

    parsed2 = json.loads(lines[1])
    assert parsed2["repo_name"] == "repo2", "Second result must be repo2"


def test_load_results_all(tmp_path: Path) -> None:
    """Test loading all results without filters."""
    storage = ResultStorage(tmp_path)

    results = [
        CommandResult(
            repo_path=str(tmp_path / "repo1"),
            repo_name="repo1",
            command="pytest",
            timestamp=datetime.now(),
            exit_code=0,
            duration_seconds=1.0,
            stdout="passed",
            stderr="",
        ),
        CommandResult(
            repo_path=str(tmp_path / "repo2"),
            repo_name="repo2",
            command="prek",
            timestamp=datetime.now(),
            exit_code=0,
            duration_seconds=2.0,
            stdout="passed",
            stderr="",
        ),
    ]

    for result in results:
        storage.save_result(result)

    loaded = storage.load_results()
    assert len(loaded) == 2, "Must load all results"
    assert loaded[0].repo_name == "repo1", "First result must be repo1"
    assert loaded[1].repo_name == "repo2", "Second result must be repo2"


def test_load_results_filter_by_command(tmp_path: Path) -> None:
    """Test filtering results by command."""
    storage = ResultStorage(tmp_path)

    pytest_result = CommandResult(
        repo_path=str(tmp_path / "repo1"),
        repo_name="repo1",
        command="pytest",
        timestamp=datetime.now(),
        exit_code=0,
        duration_seconds=1.0,
        stdout="passed",
        stderr="",
    )

    prek_result = CommandResult(
        repo_path=str(tmp_path / "repo2"),
        repo_name="repo2",
        command="prek",
        timestamp=datetime.now(),
        exit_code=0,
        duration_seconds=2.0,
        stdout="passed",
        stderr="",
    )

    storage.save_result(pytest_result)
    storage.save_result(prek_result)

    pytest_results = storage.load_results(command="pytest")
    assert len(pytest_results) == 1, "Must load only pytest results"
    assert pytest_results[0].command == "pytest", "Result must be pytest command"


def test_load_results_filter_by_repo(tmp_path: Path) -> None:
    """Test filtering results by repo_path."""
    storage = ResultStorage(tmp_path)
    repo1_path = str(tmp_path / "repo1")

    result1 = CommandResult(
        repo_path=repo1_path,
        repo_name="repo1",
        command="pytest",
        timestamp=datetime.now(),
        exit_code=0,
        duration_seconds=1.0,
        stdout="passed",
        stderr="",
    )

    result2 = CommandResult(
        repo_path=str(tmp_path / "repo2"),
        repo_name="repo2",
        command="pytest",
        timestamp=datetime.now(),
        exit_code=0,
        duration_seconds=1.0,
        stdout="passed",
        stderr="",
    )

    storage.save_result(result1)
    storage.save_result(result2)

    repo1_results = storage.load_results(repo_path=repo1_path)
    assert len(repo1_results) == 1, "Must load only repo1 results"
    assert repo1_results[0].repo_path == repo1_path, "Result must be for repo1"


def test_load_results_with_limit(tmp_path: Path) -> None:
    """Test limiting number of results returned."""
    storage = ResultStorage(tmp_path)

    for i in range(5):
        result = CommandResult(
            repo_path=str(tmp_path / f"repo{i}"),
            repo_name=f"repo{i}",
            command="pytest",
            timestamp=datetime.now(),
            exit_code=0,
            duration_seconds=1.0,
            stdout="passed",
            stderr="",
        )
        storage.save_result(result)

    limited = storage.load_results(limit=3)
    assert len(limited) == 3, "Must respect limit parameter"


def test_load_results_empty_file(tmp_path: Path) -> None:
    """Test loading results when file doesn't exist."""
    storage = ResultStorage(tmp_path)

    results = storage.load_results()
    assert len(results) == 0, "Must return empty list for nonexistent file"
    assert isinstance(results, list), "Must return list type"


def test_get_latest_by_repo(tmp_path: Path) -> None:
    """Test getting latest result per repo."""
    storage = ResultStorage(tmp_path)

    now = datetime.now()
    older = now - timedelta(hours=1)

    old_result = CommandResult(
        repo_path=str(tmp_path / "repo1"),
        repo_name="repo1",
        command="pytest",
        timestamp=older,
        exit_code=1,
        duration_seconds=1.0,
        stdout="",
        stderr="failed",
    )

    new_result = CommandResult(
        repo_path=str(tmp_path / "repo1"),
        repo_name="repo1",
        command="pytest",
        timestamp=now,
        exit_code=0,
        duration_seconds=1.5,
        stdout="passed",
        stderr="",
    )

    storage.save_result(old_result)
    storage.save_result(new_result)

    latest = storage.get_latest_by_repo("pytest")
    assert len(latest) == 1, "Must return one result per repo"
    assert str(tmp_path / "repo1") in latest, "Must have repo1 key"
    assert latest[str(tmp_path / "repo1")].exit_code == 0, "Must return latest result"
    assert latest[str(tmp_path / "repo1")].timestamp == now, "Must return newest timestamp"


def test_get_latest_by_repo_multiple_repos(tmp_path: Path) -> None:
    """Test getting latest result for multiple repos."""
    storage = ResultStorage(tmp_path)

    repo1_result = CommandResult(
        repo_path=str(tmp_path / "repo1"),
        repo_name="repo1",
        command="pytest",
        timestamp=datetime.now(),
        exit_code=0,
        duration_seconds=1.0,
        stdout="passed",
        stderr="",
    )

    repo2_result = CommandResult(
        repo_path=str(tmp_path / "repo2"),
        repo_name="repo2",
        command="pytest",
        timestamp=datetime.now(),
        exit_code=1,
        duration_seconds=2.0,
        stdout="",
        stderr="failed",
    )

    storage.save_result(repo1_result)
    storage.save_result(repo2_result)

    latest = storage.get_latest_by_repo("pytest")
    assert len(latest) == 2, "Must return results for both repos"
    assert str(tmp_path / "repo1") in latest, "Must have repo1"
    assert str(tmp_path / "repo2") in latest, "Must have repo2"


def test_get_latest_by_repo_filters_by_command(tmp_path: Path) -> None:
    """Test that get_latest_by_repo only returns results for specified command."""
    storage = ResultStorage(tmp_path)

    pytest_result = CommandResult(
        repo_path=str(tmp_path / "repo1"),
        repo_name="repo1",
        command="pytest",
        timestamp=datetime.now(),
        exit_code=0,
        duration_seconds=1.0,
        stdout="passed",
        stderr="",
    )

    prek_result = CommandResult(
        repo_path=str(tmp_path / "repo1"),
        repo_name="repo1",
        command="prek",
        timestamp=datetime.now(),
        exit_code=0,
        duration_seconds=2.0,
        stdout="passed",
        stderr="",
    )

    storage.save_result(pytest_result)
    storage.save_result(prek_result)

    pytest_latest = storage.get_latest_by_repo("pytest")
    assert len(pytest_latest) == 1, "Must return one result"
    assert pytest_latest[str(tmp_path / "repo1")].command == "pytest", "Must filter by command"
