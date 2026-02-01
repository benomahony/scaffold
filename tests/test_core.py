"""Fast unit tests for core functions without subprocess calls."""

from pathlib import Path

import pytest

from scaffold.core import check_project, preview_project
from scaffold.models import ProjectConfig, ProjectType

pytestmark = pytest.mark.unit


def test_preview_project_returns_sorted_files(tmp_path: Path) -> None:
    """Test preview_project returns sorted list of files."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    config = ProjectConfig(
        name="test-project",
        type=ProjectType.PYTHON,
        author="Test Author",
        email="test@example.com",
        description="Test description",
        python_version="3.12",
        git_init=True,
    )

    files = preview_project(config, tmp_path)

    assert files is not None, "Files list must not be None"
    assert len(files) > 0, "Must have at least one file"
    assert files == sorted(files), "Files must be sorted"
    assert "pyproject.toml" in files, "Must include pyproject.toml"
    assert ".pre-commit-config.yaml" in files, "Must include pre-commit config"


def test_preview_project_replaces_package_name(tmp_path: Path) -> None:
    """Test preview_project replaces __package_name__ placeholder."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    config = ProjectConfig(
        name="my-awesome-project",
        type=ProjectType.PYTHON,
        author="Test",
        email=None,
        description="Test",
        python_version="3.12",
        git_init=True,
    )

    files = preview_project(config, tmp_path)

    assert files is not None, "Files list must not be None"
    assert any("my_awesome_project" in f for f in files), (
        "Must replace package name placeholder"
    )
    assert not any("__package_name__" in f for f in files), (
        "Must not contain placeholder in output"
    )


def test_check_project_detects_missing_pyproject(tmp_path: Path) -> None:
    """Test check_project detects missing pyproject.toml."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    issues = check_project(tmp_path)

    assert issues is not None, "Issues list must not be None"
    assert len(issues) > 0, "Must detect missing pyproject.toml"
    assert "Missing pyproject.toml" in issues, "Must report missing pyproject.toml"


def test_check_project_detects_missing_precommit(tmp_path: Path) -> None:
    """Test check_project detects missing .pre-commit-config.yaml."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\nname = 'test'\n")

    issues = check_project(tmp_path)

    assert issues is not None, "Issues list must not be None"
    assert len(issues) > 0, "Must detect missing pre-commit config"
    assert any("pre-commit" in issue for issue in issues), "Must report missing pre-commit config"


def test_check_project_detects_missing_directories(tmp_path: Path) -> None:
    """Test check_project detects missing src/ and tests/ directories."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\nname = 'test'\n")

    precommit = tmp_path / ".pre-commit-config.yaml"
    precommit.write_text("repos: []\n")

    issues = check_project(tmp_path)

    assert issues is not None, "Issues list must not be None"
    assert len(issues) >= 2, "Must detect missing src/ and tests/"
    assert any("src/" in issue for issue in issues), "Must report missing src/"
    assert any("tests/" in issue for issue in issues), "Must report missing tests/"


def test_check_project_detects_missing_git(tmp_path: Path) -> None:
    """Test check_project detects missing git repository."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\nname = 'test'\n")

    precommit = tmp_path / ".pre-commit-config.yaml"
    precommit.write_text("repos: []\n")

    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()

    issues = check_project(tmp_path)

    assert issues is not None, "Issues list must not be None"
    assert len(issues) > 0, "Must detect missing git repo"
    assert any("git" in issue.lower() for issue in issues), "Must report missing git repo"


def test_check_project_clean_project_has_no_issues(tmp_path: Path) -> None:
    """Test check_project returns empty list for valid project."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\nname = 'test'\n")

    precommit = tmp_path / ".pre-commit-config.yaml"
    precommit.write_text("repos: []\n")

    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "hooks").mkdir()
    (tmp_path / ".git" / "hooks" / "pre-commit").touch()

    issues = check_project(tmp_path)

    assert issues is not None, "Issues list must not be None"
    assert len(issues) == 0, "Clean project must have no issues"
