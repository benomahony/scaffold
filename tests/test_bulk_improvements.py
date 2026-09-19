"""Test improvements to bulk commands."""

import os
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def test_status_groups_results_by_repo(tmp_path: Path) -> None:
    """status shows pytest and prek grouped per repository."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    original_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)

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

        result = subprocess.run(
            ["uv", "run", "scaffold", "status", "--run", "--path", str(tmp_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, "Status must succeed"
        assert "status-group-test" in result.stdout or "status_group_test" in result.stdout, (
            "Must show repo"
        )
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
