"""Test the complete scaffold workflow from init to ready-to-code."""

import os
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def test_complete_scaffold_workflow(tmp_path: Path) -> None:
    """Test complete workflow: init creates project and opens editor.

    This test verifies that `sc init name123` does EVERYTHING:
    1. Creates project structure
    2. Installs dependencies (uv sync --all-extras)
    3. Configures pre-commit hooks (prek install)
    4. Runs tests (pytest)
    5. Initializes git and stages files
    6. Opens editor automatically (if TTY)

    User does NOTHING - just run `sc init name` and start coding!
    """
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    project_name = "test-complete-flow"
    original_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)

        # Run scaffold init
        result = subprocess.run(
            [
                "uv",
                "run",
                "scaffold",
                "init",
                project_name,
                "--author",
                "Test Author",
                "--description",
                "Test complete workflow",
            ],
            input="n\n",
            text=True,
            capture_output=True,
        )

        # Should succeed
        assert result.returncode == 0, f"Scaffold init failed:\n{result.stderr}"

        # Should show that everything is ready
        assert "Project ready!" in result.stdout, "Missing success message"
        assert "Dependencies installed" in result.stdout, "Missing deps confirmation"
        assert "Pre-commit hooks configured" in result.stdout, "Missing hooks confirmation"
        assert "Tests passing" in result.stdout, "Missing tests confirmation"

        project_path = tmp_path / project_name

        # Verify project structure exists
        assert project_path.exists(), "Project directory must exist"
        assert (project_path / "pyproject.toml").exists(), "pyproject.toml must exist"
        assert (project_path / ".venv").exists(), "Virtual environment must exist"
        assert (project_path / ".git").exists(), "Git repository must be initialized"

        # Verify prek hooks installed
        assert (project_path / ".git" / "hooks" / "pre-commit").exists(), "Prek hooks must be installed"

        # Verify tests passed (pytest was run during init)
        # The fact that init succeeded means pytest passed

        # Verify we can run pytest again
        test_result = subprocess.run(
            ["uv", "run", "pytest", "-v"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert test_result.returncode == 0, f"Tests should pass:\n{test_result.stdout}"

        # Verify prek hooks work
        prek_result = subprocess.run(
            ["uv", "run", "prek", "run", "-a"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert prek_result.returncode == 0, f"Prek should pass:\n{prek_result.stdout}"

    finally:
        os.chdir(original_cwd)


def test_workflow_creates_working_project(tmp_path: Path) -> None:
    """Verify the created project is immediately usable."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    project_name = "test-usable-project"
    original_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)

        subprocess.run(
            [
                "uv",
                "run",
                "scaffold",
                "init",
                project_name,
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

        project_path = tmp_path / project_name
        package_name = project_name.replace("-", "_")

        # Can import the package
        result = subprocess.run(
            ["uv", "run", "python", "-c", f"import {package_name}; print({package_name}.__version__)"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "Should be able to import package"
        assert "0.1.0" in result.stdout, "Version should be 0.1.0"

        # CLI works
        cli_result = subprocess.run(
            ["uv", "run", package_name, "--help"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert cli_result.returncode == 0, "CLI should work"
        assert "Usage:" in cli_result.stdout, "Should show help"

    finally:
        os.chdir(original_cwd)


def test_complete_manual_workflow(tmp_path: Path) -> None:
    """Verify project is fully usable immediately after init.

    After running `sc init project-name`, everything is ready:
    - Dependencies installed (uv sync already ran)
    - Pre-commit hooks configured (prek install already ran)
    - Tests passing (pytest already ran)
    - Git initialized and files staged

    This test verifies all these operations actually work without
    requiring any manual intervention from the user.
    """
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    project_name = "test-manual-workflow"
    original_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)

        # Step 0: Create the project
        result = subprocess.run(
            [
                "uv",
                "run",
                "scaffold",
                "init",
                project_name,
                "--author",
                "Test User",
                "--description",
                "Testing manual workflow",
            ],
            input="n\n",
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0, f"Init must succeed:\n{result.stderr}"

        project_path = tmp_path / project_name

        # Step 1: CD into project directory
        os.chdir(project_path)
        assert Path.cwd() == project_path, "Must be in project directory"

        # Step 2: Run uv sync (install dependencies)
        sync_result = subprocess.run(
            ["uv", "sync", "--extra", "dev"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert sync_result.returncode == 0, f"uv sync must succeed:\n{sync_result.stderr}"

        # Step 3: Verify venv exists and can be activated
        venv_path = project_path / ".venv"
        assert venv_path.exists(), "Virtual environment must exist"
        assert (venv_path / "bin" / "python").exists(), "Python must exist in venv"
        assert (venv_path / "bin" / "activate").exists(), "Activate script must exist"

        # Verify we can use the venv
        venv_python = venv_path / "bin" / "python"
        python_result = subprocess.run(
            [str(venv_python), "--version"],
            capture_output=True,
            text=True,
        )
        assert python_result.returncode == 0, "Venv Python must work"
        assert "Python 3" in python_result.stdout, "Must be Python 3"

        # Step 4: Run tests (using uv run to activate venv)
        test_result = subprocess.run(
            ["uv", "run", "pytest", "-v"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert test_result.returncode == 0, f"Tests must pass:\n{test_result.stdout}\n{test_result.stderr}"
        assert "passed" in test_result.stdout, "Tests must show passed status"

        # Step 5: Run pre-commit hooks (should pass on first run)
        prek_result = subprocess.run(
            ["uv", "run", "prek", "run", "--all-files"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert prek_result.returncode == 0, (
            f"Pre-commit hooks must pass on first run (scaffold should generate clean code):\n"
            f"{prek_result.stdout}\n{prek_result.stderr}"
        )

        # Verify hooks are actually installed in git
        pre_commit_hook = project_path / ".git" / "hooks" / "pre-commit"
        assert pre_commit_hook.exists(), "Pre-commit hook must be installed"

        # Step 6: Verify directory is ready for editor
        # Check that all expected files exist for a good dev experience
        package_name = project_name.replace("-", "_")

        expected_files = [
            "pyproject.toml",
            ".pre-commit-config.yaml",
            ".gitignore",
            f"src/{package_name}/__init__.py",
            f"src/{package_name}/cli.py",
            "tests/test_cli.py",
            "tests/test_core.py",
            "README.md",
            "llms.txt",
            "zensical.toml",
        ]

        for file_path in expected_files:
            full_path = project_path / file_path
            assert full_path.exists(), f"{file_path} must exist for editor readiness"

        # Verify we can import the package
        import_result = subprocess.run(
            ["uv", "run", "python", "-c", f"import {package_name}; print('Import successful')"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert import_result.returncode == 0, f"Package must be importable:\n{import_result.stderr}"
        assert "Import successful" in import_result.stdout, "Import must succeed"

        # Verify the CLI works
        cli_result = subprocess.run(
            ["uv", "run", package_name, "--help"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert cli_result.returncode == 0, "CLI must work"
        assert "Usage:" in cli_result.stdout, "CLI must show help"

        # Step 7: Verify editor (neovim) can open and close
        # Open neovim in headless mode and immediately quit
        nvim_result = subprocess.run(
            ["nvim", "--headless", "+quit"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert nvim_result.returncode == 0, "Neovim must open and close successfully"

    finally:
        os.chdir(original_cwd)
