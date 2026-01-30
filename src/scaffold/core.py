import subprocess
from datetime import datetime
from pathlib import Path

from scaffold.models import ProjectConfig
from scaffold.template_engine import TemplateEngine


def _validate_project_path(project_path: Path) -> None:
    assert project_path.exists(), "Project path must exist"
    assert project_path.is_dir(), "Project path must be a directory"


def preview_project(config: ProjectConfig, output_path: Path) -> list[str]:
    assert config is not None, "Config must not be None"
    assert output_path.is_absolute(), "Output path must be absolute"

    engine = TemplateEngine()
    templates = engine.get_template_files(config.type)
    empty_files = engine.get_empty_files()

    all_files = []

    for _, output_file in templates:
        file_path = output_file.replace("__package_name__", config.package_name)
        all_files.append(file_path)

    for empty_file in empty_files:
        file_path = empty_file.replace("__package_name__", config.package_name)
        all_files.append(file_path)

    return sorted(all_files)


def create_project(config: ProjectConfig, output_path: Path) -> None:
    assert config is not None, "Config must not be None"
    assert output_path.is_absolute(), "Output path must be absolute"

    output_path.mkdir(parents=True, exist_ok=False)
    assert output_path.exists(), "Project directory must be created"

    engine = TemplateEngine()
    render_and_write_templates(engine, config, output_path)

    if config.git_init:
        initialize_git(output_path)

    setup_project_environment(output_path)


def render_and_write_templates(
    engine: TemplateEngine, config: ProjectConfig, output_path: Path
) -> None:
    assert engine is not None, "Engine must not be None"
    assert config is not None, "Config must not be None"

    context = {
        "project_name": config.name,
        "package_name": config.package_name,
        "author": config.author,
        "email": config.email,
        "description": config.description,
        "python_version": config.python_version,
        "license": config.license,
        "year": datetime.now().year,
        "project_type": config.type.value,
    }

    templates = engine.get_template_files(config.type)
    assert len(templates) > 0, "Must have templates to render"

    for template_path, output_file in templates:
        output_file_path = output_path / output_file.replace("__package_name__", config.package_name)
        output_file_path.parent.mkdir(parents=True, exist_ok=True)

        content = engine.render_template(template_path, context)
        output_file_path.write_text(content)

    empty_files = engine.get_empty_files()
    assert len(empty_files) > 0, "Must have empty files defined"

    for empty_file in empty_files:
        empty_file_path = output_path / empty_file.replace("__package_name__", config.package_name)
        empty_file_path.parent.mkdir(parents=True, exist_ok=True)
        empty_file_path.touch()


def initialize_git(project_path: Path) -> None:
    _validate_project_path(project_path)

    subprocess.run(["git", "init"], cwd=project_path, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=project_path, check=True, capture_output=True)


def setup_project_environment(project_path: Path) -> None:
    _validate_project_path(project_path)

    subprocess.run(["uv", "sync"], cwd=project_path, check=True, capture_output=True)
    subprocess.run(
        ["uv", "run", "pre-commit", "install"],
        cwd=project_path,
        check=True,
        capture_output=True,
    )


def check_project(project_path: Path) -> list[str]:
    assert project_path is not None, "Project path must not be None"
    assert project_path.exists(), "Project path must exist"

    issues = []

    pyproject_file = project_path / "pyproject.toml"
    if not pyproject_file.exists():
        issues.append("Missing pyproject.toml")
        return issues

    precommit_file = project_path / ".pre-commit-config.yaml"
    if not precommit_file.exists():
        issues.append("Missing .pre-commit-config.yaml")

    src_dir = project_path / "src"
    if not src_dir.exists():
        issues.append("Missing src/ directory")

    tests_dir = project_path / "tests"
    if not tests_dir.exists():
        issues.append("Missing tests/ directory")

    git_dir = project_path / ".git"
    if not git_dir.exists():
        issues.append("Not a git repository (run: git init)")

    precommit_hook = project_path / ".git" / "hooks" / "pre-commit"
    if git_dir.exists() and not precommit_hook.exists():
        issues.append("Pre-commit hooks not installed (run: uv run pre-commit install)")

    return issues


def upgrade_project(project_path: Path, dry_run: bool = False) -> list[str]:
    assert project_path is not None, "Project path must not be None"
    assert project_path.exists(), "Project path must exist"

    import tomllib

    pyproject_file = project_path / "pyproject.toml"
    if not pyproject_file.exists():
        raise ValueError("Not a Python project (missing pyproject.toml)")

    with open(pyproject_file, "rb") as f:
        pyproject_data = tomllib.load(f)

    project_name = pyproject_data.get("project", {}).get("name")
    if not project_name:
        raise ValueError("pyproject.toml missing project.name")

    package_name = project_name.replace("-", "_")
    author = pyproject_data.get("project", {}).get("authors", [{}])[0].get("name", "Unknown")
    description = pyproject_data.get("project", {}).get("description", "")
    python_version = pyproject_data.get("project", {}).get("requires-python", ">=3.12")
    python_version = python_version.replace(">=", "").strip()

    engine = TemplateEngine()
    context = {
        "project_name": project_name,
        "package_name": package_name,
        "author": author,
        "email": None,
        "description": description,
        "python_version": python_version,
        "license": "MIT",
        "year": datetime.now().year,
        "project_type": "python",
    }

    files_to_upgrade = [
        ("base/.pre-commit-config.yaml.j2", ".pre-commit-config.yaml"),
    ]

    updated_files = []

    for template_path, output_file in files_to_upgrade:
        output_path = project_path / output_file

        if not dry_run:
            content = engine.render_template(template_path, context)
            output_path.write_text(content)

        updated_files.append(output_file)

    return updated_files
