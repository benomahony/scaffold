import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from scaffold.models import ProjectConfig
from scaffold.storage import CommandResult, ResultStorage
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


def create_project(config: ProjectConfig, output_path: Path, run_setup: bool = True) -> None:
    assert config is not None, "Config must not be None"
    assert output_path.is_absolute(), "Output path must be absolute"

    output_path.mkdir(parents=True, exist_ok=False)
    assert output_path.exists(), "Project directory must be created"

    engine = TemplateEngine()
    render_and_write_templates(engine, config, output_path)

    if config.git_init:
        initialize_git(output_path)

    if run_setup:
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
        output_file_path = output_path / output_file.replace(
            "__package_name__", config.package_name
        )
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
    assert project_path is not None, "Project path must not be None"
    assert not (project_path / ".git").exists(), "Git repository already initialized"

    subprocess.run(["git", "init"], cwd=project_path, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=project_path, check=True, capture_output=True)


def setup_project_environment(project_path: Path) -> None:
    """Setup project environment: sync deps, install hooks, run tests."""
    _validate_project_path(project_path)
    assert project_path is not None, "Project path must not be None"
    assert (project_path / "pyproject.toml").exists(), "pyproject.toml must exist"

    import sys

    print("\n📦 Installing dependencies...", flush=True)
    sys.stdout.flush()
    subprocess.run(["uv", "sync", "--all-extras"], cwd=project_path, check=True)

    print("\n🪝 Installing pre-commit hooks...", flush=True)
    sys.stdout.flush()
    subprocess.run(["uv", "run", "prek", "install"], cwd=project_path, check=True)

    print("\n🔍 Running pre-commit on all files...", flush=True)
    sys.stdout.flush()
    subprocess.run(["uv", "run", "prek", "run", "--all-files"], cwd=project_path, check=True)

    print("\n🧪 Running tests...", flush=True)
    sys.stdout.flush()
    result = subprocess.run(["uv", "run", "pytest", "-v"], cwd=project_path, check=False)
    if result.returncode != 0:
        print(f"\n⚠️  Tests had issues (exit {result.returncode}), but continuing...")


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
        issues.append("Prek hooks not installed (run: uv run prek install)")

    return issues


def _load_project_metadata(project_path: Path) -> dict[str, str]:
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

    return {
        "project_name": project_name,
        "package_name": package_name,
        "author": author,
        "description": description,
        "python_version": python_version,
    }


def upgrade_project(project_path: Path, dry_run: bool = False) -> list[str]:
    assert project_path is not None, "Project path must not be None"
    assert project_path.exists(), "Project path must exist"

    metadata = _load_project_metadata(project_path)

    engine = TemplateEngine()
    context = {
        **metadata,
        "email": None,
        "license": "MIT",
        "year": datetime.now().year,
        "project_type": "python",
    }

    package_name = metadata["package_name"]
    files_to_upgrade = [
        ("base/.pre-commit-config.yaml.j2", ".pre-commit-config.yaml"),
        ("base/llms.txt.j2", "llms.txt"),
        ("base/zensical.toml.j2", "zensical.toml"),
        ("base/.github_workflows_ci.yml.j2", ".github/workflows/ci.yml"),
        ("python/mcp_server.py.j2", f"src/{package_name}/mcp_server.py"),
        ("python/SKILL.md.j2", f".skills/{package_name}/SKILL.md"),
    ]

    updated_files = []

    for template_path, output_file in files_to_upgrade:
        output_path = project_path / output_file

        if not dry_run:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            content = engine.render_template(template_path, context)
            output_path.write_text(content)

        updated_files.append(output_file)

    if not dry_run:
        precommit_hook = project_path / ".git" / "hooks" / "pre-commit"
        if not precommit_hook.exists():
            subprocess.run(
                ["uv", "run", "prek", "install"],
                cwd=project_path,
                check=True,
                capture_output=True,
            )

    return updated_files


def find_python_projects(root_path: Path, max_depth: int = 3) -> list[Path]:
    assert root_path is not None, "Root path must not be None"
    assert max_depth > 0, "Max depth must be positive"

    projects = []
    for pyproject in root_path.rglob("pyproject.toml"):
        project_path = pyproject.parent
        depth = len(project_path.relative_to(root_path).parts)

        if depth <= max_depth:
            projects.append(project_path)

    return sorted(projects)


def bulk_maintenance(
    root_path: Path, action: str, dry_run: bool = False, max_depth: int = 3
) -> list[dict]:
    assert root_path is not None, "Root path must not be None"
    assert action in ["check", "upgrade"], "Action must be 'check' or 'upgrade'"

    projects = find_python_projects(root_path, max_depth)
    results = []

    for project_path in projects:
        result = {"project": project_path, "status": "unknown", "details": []}

        try:
            if action == "check":
                issues = check_project(project_path)
                result["status"] = "success"
                result["details"] = issues
            elif action == "upgrade":
                changes = upgrade_project(project_path, dry_run=dry_run)
                result["status"] = "success"
                result["details"] = changes
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        results.append(result)

    return results


def _get_git_commit(repo_path: Path) -> str | None:
    assert repo_path is not None, "Repo path must not be None"
    assert repo_path.exists(), "Repo path must exist"

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout.strip()
    except Exception:  # noqa: S110
        return None
    return None


def _run_command_on_repo(repo_path: Path, command: str) -> CommandResult:
    assert repo_path is not None, "Repo path must not be None"
    assert command in ["pytest", "prek"], "Command must be 'pytest' or 'prek'"

    repo_name = repo_path.name
    git_commit = _get_git_commit(repo_path)

    cmd = ["uv", "run", command]
    if command == "prek":
        cmd.extend(["run", "--all-files"])

    start_time = time.time()
    result = subprocess.run(
        cmd,
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    duration = time.time() - start_time

    return CommandResult(
        repo_path=str(repo_path),
        repo_name=repo_name,
        command=command,
        timestamp=datetime.now(),
        exit_code=result.returncode,
        duration_seconds=duration,
        stdout=result.stdout,
        stderr=result.stderr,
        git_commit=git_commit,
    )


def run_bulk_command(
    root_path: Path,
    command: str,
    max_depth: int = 3,
    storage: ResultStorage | None = None,
) -> list[CommandResult]:
    assert root_path is not None, "Root path must not be None"
    assert command in ["pytest", "prek"], "Command must be 'pytest' or 'prek'"

    if storage is None:
        storage = ResultStorage()

    projects = find_python_projects(root_path, max_depth)
    results = []

    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(_run_command_on_repo, project, command): project for project in projects
        }

        for future in as_completed(futures):
            try:
                result = future.result()
                storage.save_result(result)
                results.append(result)
            except Exception as e:
                project = futures[future]
                error_result = CommandResult(
                    repo_path=str(project),
                    repo_name=project.name,
                    command=command,
                    timestamp=datetime.now(),
                    exit_code=-1,
                    duration_seconds=0.0,
                    stdout="",
                    stderr=f"Exception: {e}",
                )
                storage.save_result(error_result)
                results.append(error_result)

    return results
