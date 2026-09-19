"""Unit tests for the status command helpers."""

from datetime import datetime
from pathlib import Path

import pytest

from scaffold.storage import CommandResult, ResultStorage

pytestmark = pytest.mark.unit


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
