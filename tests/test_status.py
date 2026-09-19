"""Unit tests for the status command helpers."""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from scaffold.storage import CommandResult, ResultStorage

pytestmark = pytest.mark.unit


def _save(storage: ResultStorage, repo: Path, timestamp: datetime, exit_code: int = 0) -> None:
    storage.save_result(
        CommandResult(
            repo_path=str(repo),
            repo_name=repo.name,
            command="pytest",
            timestamp=timestamp,
            exit_code=exit_code,
            duration_seconds=0.0,
            stdout="",
            stderr="",
        )
    )


def test_partition_by_freshness_reruns_only_changed_repos(tmp_path: Path) -> None:
    """A repo is fresh only if its result is newer than its newest file."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    from scaffold import cli

    storage = ResultStorage(tmp_path / "storage")
    fresh_repo = tmp_path / "fresh"
    stale_repo = tmp_path / "stale"
    fresh_repo.mkdir()
    stale_repo.mkdir()
    (fresh_repo / "a.py").write_text("x = 1")
    (stale_repo / "a.py").write_text("x = 1")

    _save(storage, fresh_repo, datetime.now() + timedelta(minutes=5))
    _save(storage, stale_repo, datetime.now() - timedelta(minutes=5))

    fresh, stale = cli._partition_by_freshness([fresh_repo, stale_repo], "pytest", storage)

    assert [r.repo_path for r in fresh] == [str(fresh_repo)], "Unchanged repo must be reused"
    assert stale == [stale_repo], "Changed repo must be re-run"


def test_rerun_failed_selects_only_failed_repos(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """--rerun-failed reruns only the repos whose last result failed."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    from scaffold import cli

    storage = ResultStorage(tmp_path)
    passing = tmp_path / "good"
    failing = tmp_path / "bad"
    passing.mkdir()
    failing.mkdir()
    for repo, exit_code in ((passing, 0), (failing, 1)):
        storage.save_result(
            CommandResult(
                repo_path=str(repo),
                repo_name=repo.name,
                command="pytest",
                timestamp=datetime.now(),
                exit_code=exit_code,
                duration_seconds=0.0,
                stdout="",
                stderr="",
            )
        )

    captured: dict = {}

    def fake_execute_bulk(command, projects, store):  # type: ignore[no-untyped-def]
        captured["projects"] = projects
        return []

    monkeypatch.setattr(cli, "_execute_bulk", fake_execute_bulk)

    cli._rerun_failed([passing, failing], storage)

    assert captured["projects"] == [failing], "Must rerun only the failed repo"
