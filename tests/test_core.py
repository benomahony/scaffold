"""Fast unit tests for core functions without subprocess calls."""

from pathlib import Path

import pytest

from scaffold.core import (
    adopt_project,
    check_project,
    find_python_projects,
    plan_adopt,
    plan_upgrade,
    preview_project,
    sync_hook_pins,
    upgrade_project,
)
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
    assert any("my_awesome_project" in f for f in files), "Must replace package name placeholder"
    assert not any("__package_name__" in f for f in files), "Must not contain placeholder in output"


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


def test_upgrade_project_only_reports_changed_files(tmp_path: Path) -> None:
    """Test upgrade_project only lists files that actually changed."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname = "my-project"\nrequires-python = ">=3.12"\n'
        'authors = [{name = "Test"}]\ndescription = "Test"\n'
    )

    # Stub the pre-commit hook so upgrade_project skips prek install
    hook = tmp_path / ".git" / "hooks" / "pre-commit"
    hook.parent.mkdir(parents=True)
    hook.touch()

    first_run = upgrade_project(tmp_path)
    second_run = upgrade_project(tmp_path)

    assert first_run is not None, "First run must return a list"
    assert len(first_run) > 0, "First run must report updated files"
    assert second_run is not None, "Second run must return a list"
    assert len(second_run) == 0, "Second run must report no changes (content identical)"


def test_plan_upgrade_reports_file_changes(tmp_path: Path) -> None:
    """Test plan_upgrade returns FileChange objects with substituted paths."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname = "my-project"\nrequires-python = ">=3.12"\n'
        'authors = [{name = "Test"}]\ndescription = "Test"\n'
    )

    changes = plan_upgrade(tmp_path)

    assert changes is not None, "Changes must not be None"
    assert len(changes) > 0, "Must report changes for a fresh project"
    paths = [change.path for change in changes]
    assert ".pre-commit-config.yaml" in paths, "Must include pre-commit config"
    assert "zensical.toml" in paths, "Must include zensical config"
    assert "llms.txt" not in paths, "Must not force optional llms.txt onto a project"
    assert all(change.action == "create" for change in changes), "All files must be new"


def test_plan_upgrade_refreshes_optional_files_only_if_present(tmp_path: Path) -> None:
    """Test plan_upgrade refreshes an optional file only when it already exists."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname = "my-project"\nrequires-python = ">=3.12"\n'
        'authors = [{name = "Test"}]\ndescription = "Test"\n'
    )
    (tmp_path / "llms.txt").write_text("stale\n")

    paths = [change.path for change in plan_upgrade(tmp_path)]

    assert "llms.txt" in paths, "Must refresh an existing optional file"


def test_plan_adopt_never_clobbers_existing_files(tmp_path: Path) -> None:
    """Test plan_adopt skips files that already exist."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    repo = tmp_path / "legacy-repo"
    repo.mkdir()
    (repo / "README.md").write_text("keep me\n")

    changes = plan_adopt(repo)

    assert changes is not None, "Changes must not be None"
    paths = [change.path for change in changes]
    assert "pyproject.toml" in paths, "Must create missing pyproject.toml"
    assert "README.md" not in paths, "Must not touch existing README.md"
    assert (repo / "README.md").read_text() == "keep me\n", "Existing file must be untouched"


def test_adopt_project_creates_missing_standard_files(tmp_path: Path) -> None:
    """Test adopt_project writes missing files derived from directory name."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    repo = tmp_path / "myrepo"
    repo.mkdir()

    created = adopt_project(repo)

    assert created is not None, "Created list must not be None"
    assert "pyproject.toml" in created, "Must create pyproject.toml"
    assert (repo / "pyproject.toml").exists(), "pyproject.toml must exist on disk"
    assert (repo / ".pre-commit-config.yaml").exists(), "pre-commit config must exist"
    assert (repo / "src" / "myrepo" / "__init__.py").exists(), "Package init must exist"


def test_plan_upgrade_ensures_dddlint_config_without_clobbering(tmp_path: Path) -> None:
    """Test plan_upgrade creates dddlint.yaml when missing but never overwrites it."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname = "my-project"\nrequires-python = ">=3.12"\n'
        'authors = [{name = "Test"}]\ndescription = "Test"\n'
    )

    missing = [change.path for change in plan_upgrade(tmp_path)]
    assert "dddlint.yaml" in missing, "Must create dddlint.yaml when absent"

    (tmp_path / "dddlint.yaml").write_text("forbidden: [foo]\n")
    present = [change.path for change in plan_upgrade(tmp_path)]
    assert "dddlint.yaml" not in present, "Must never overwrite an existing dddlint.yaml"
    assert (tmp_path / "dddlint.yaml").read_text() == "forbidden: [foo]\n", "Config untouched"


def test_precommit_template_pins_and_includes_dddlint() -> None:
    """Test the pre-commit template ships current hook pins and the dddlint hook."""
    from scaffold.template_engine import TemplateEngine

    rendered = TemplateEngine().render_template(
        "base/.pre-commit-config.yaml.j2", {"package_name": "demo"}
    )

    assert "id: dddlint" in rendered, "Must include the dddlint hook"
    assert "dddlint lint src/demo" in rendered, "dddlint hook must lint the package"
    assert "rev: v0.49.1" in rendered, "markdownlint-cli must be pinned to the current release"
    assert "rev: v4.18.1" in rendered, "commitizen must be pinned to the current release"
    assert "rev: v0.1.14" in rendered, "nasa-lsp must be pinned to the current release"


def test_pyproject_template_gates_mcp_dependency() -> None:
    """Test the pyproject template only includes the mcp extra when requested."""
    from scaffold.template_engine import TemplateEngine

    engine = TemplateEngine()
    context = {
        "project_name": "demo",
        "package_name": "demo",
        "author": "Test",
        "email": None,
        "description": "Demo",
        "python_version": "3.12",
        "license": "MIT",
    }

    without_mcp = engine.render_template("base/pyproject.toml.j2", {**context, "with_mcp": False})
    with_mcp = engine.render_template("base/pyproject.toml.j2", {**context, "with_mcp": True})

    assert "mcp>=" not in without_mcp, "Default pyproject must omit the mcp dependency"
    assert "mcp>=" in with_mcp, "pyproject with --mcp must include the mcp dependency"


def test_sync_hook_pins_copies_revs_into_template(tmp_path: Path) -> None:
    """Test sync_hook_pins mirrors remote hook revs from the live config."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    config = tmp_path / ".pre-commit-config.yaml"
    config.write_text(
        "repos:\n"
        "  - repo: https://github.com/x/y\n"
        "    rev: v2.0.0\n"
        "    hooks: []\n"
        "  - repo: local\n"
        "    hooks: []\n"
    )
    template = tmp_path / "template.j2"
    template.write_text(
        "repos:\n  - repo: https://github.com/x/y\n    rev: v1.0.0\n    hooks: []\n"
    )

    changed = sync_hook_pins(config, template)

    assert changed is True, "Must report a change when a rev is stale"
    assert "rev: v2.0.0" in template.read_text(), "Template rev must be bumped"
    assert sync_hook_pins(config, template) is False, "Second run must be a no-op"


def test_find_python_projects_respects_max_depth(tmp_path: Path) -> None:
    """find_python_projects excludes projects deeper than max_depth."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    shallow = tmp_path / "shallow"
    shallow.mkdir()
    (shallow / "pyproject.toml").write_text("[project]\nname = 'shallow'\n")
    deep = tmp_path / "a" / "b" / "c" / "deep"
    deep.mkdir(parents=True)
    (deep / "pyproject.toml").write_text("[project]\nname = 'deep'\n")

    names = [p.name for p in find_python_projects(tmp_path, max_depth=2)]

    assert "shallow" in names, "Must find the shallow project"
    assert "deep" not in names, "Must exclude the project beyond max_depth"


def test_find_python_projects_excludes_venv(tmp_path: Path) -> None:
    """Test find_python_projects does not traverse .venv directories."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    real_project = tmp_path / "my-project"
    real_project.mkdir()
    (real_project / "pyproject.toml").write_text("[project]\nname = 'my-project'\n")

    venv_pkg = real_project / ".venv" / "lib" / "python3.12" / "site-packages" / "somelib"
    venv_pkg.mkdir(parents=True)
    (venv_pkg / "pyproject.toml").write_text("[project]\nname = 'somelib'\n")

    projects = find_python_projects(tmp_path)

    assert projects is not None, "Must return a list"
    assert len(projects) == 1, f"Must find exactly 1 project, found: {[p.name for p in projects]}"
    assert projects[0] == real_project, "Must find the real project, not the .venv one"
