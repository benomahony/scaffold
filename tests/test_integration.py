import os
import shutil
import subprocess
from pathlib import Path

import pytest


def test_scaffold_cli_project(tmp_path: Path) -> None:
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    project_name = "test-integration-cli"
    original_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)

        result = subprocess.run(
            [
                "uv",
                "run",
                "scaffold",
                "new",
                project_name,
                "--type",
                "cli",
                "--author",
                "Test Author",
                "--description",
                "Integration test CLI",
            ],
            input="n\n",
            text=True,
            capture_output=True,
        )

        assert result.returncode == 0, f"Scaffold command must succeed. Error:\n{result.stderr}"

        project_path = tmp_path / project_name
        assert project_path.exists(), "Project directory must be created"
        assert (project_path / "pyproject.toml").exists(), "pyproject.toml must exist"
        assert (
            project_path / ".pre-commit-config.yaml"
        ).exists(), "pre-commit config must exist"
        assert (project_path / "src").exists(), "src directory must exist"
        assert (project_path / "tests").exists(), "tests directory must exist"

        subprocess.run(
            ["uv", "sync", "--extra", "dev"], cwd=project_path, check=True, capture_output=True
        )

        test_result = subprocess.run(
            ["uv", "run", "pytest", "-v"], cwd=project_path, capture_output=True, text=True
        )
        assert test_result.returncode == 0, f"Tests must pass. Output:\n{test_result.stdout}"

        subprocess.run(
            ["uv", "run", "pre-commit", "run", "--all-files"],
            cwd=project_path,
            capture_output=True,
            check=False,
        )

        precommit_result = subprocess.run(
            ["uv", "run", "pre-commit", "run", "--all-files"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert (
            precommit_result.returncode == 0
        ), f"Pre-commit hooks must pass. Output:\n{precommit_result.stdout}\n{precommit_result.stderr}"

    finally:
        os.chdir(original_cwd)


def test_scaffold_package_project(tmp_path: Path) -> None:
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    project_name = "test-integration-package"
    original_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)

        result = subprocess.run(
            [
                "uv",
                "run",
                "scaffold",
                "new",
                project_name,
                "--type",
                "package",
                "--author",
                "Test Author",
                "--description",
                "Integration test package",
            ],
            input="n\n",
            text=True,
            capture_output=True,
        )

        assert result.returncode == 0, f"Scaffold command must succeed. Error:\n{result.stderr}"

        project_path = tmp_path / project_name
        assert project_path.exists(), "Project directory must be created"

        subprocess.run(
            ["uv", "sync", "--extra", "dev"], cwd=project_path, check=True, capture_output=True
        )

        subprocess.run(
            ["uv", "run", "pre-commit", "run", "--all-files"],
            cwd=project_path,
            capture_output=True,
            check=False,
        )

        precommit_result = subprocess.run(
            ["uv", "run", "pre-commit", "run", "--all-files"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert (
            precommit_result.returncode == 0
        ), f"Pre-commit hooks must pass. Output:\n{precommit_result.stdout}\n{precommit_result.stderr}"

    finally:
        os.chdir(original_cwd)
