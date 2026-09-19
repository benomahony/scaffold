import os
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def test_scaffold_python_project(tmp_path: Path) -> None:
    """Init builds a complete project, installs it, and reports success."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    project_name = "test-integration-python-full"
    original_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)

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
                "Integration test Python project",
            ],
            input="n\n",
            text=True,
            capture_output=True,
        )

        assert result.returncode == 0, f"Scaffold command must succeed. Error:\n{result.stderr}"

        # Verify scaffold init did everything
        assert "Dependencies installed" in result.stdout, "Must install dependencies"
        assert "Pre-commit hooks configured" in result.stdout, "Must configure hooks"
        assert "Tests passing" in result.stdout, "Must run tests"
        assert "Project ready!" in result.stdout, "Must show success message"

        project_path = tmp_path / project_name
        assert project_path.exists(), "Project directory must be created"
        assert (project_path / "pyproject.toml").exists(), "pyproject.toml must exist"
        assert (project_path / ".pre-commit-config.yaml").exists(), "pre-commit config must exist"
        assert (project_path / ".github" / "workflows" / "ci.yml").exists(), (
            "GitHub Actions workflow must exist"
        )
        assert (project_path / "zensical.toml").exists(), "zensical.toml must exist"
        assert (project_path / "src").exists(), "src directory must exist"
        assert (project_path / "tests").exists(), "tests directory must exist"
        assert (project_path / ".venv").exists(), "Virtual environment must exist"
        assert (project_path / ".git").exists(), "Git repository must exist"
        assert (project_path / ".git" / "hooks" / "pre-commit").exists(), (
            "Pre-commit hooks must be installed"
        )

        package_name = project_name.replace("-", "_")
        assert not (project_path / "llms.txt").exists(), "llms.txt must be opt-in"
        assert not (project_path / "src" / package_name / "mcp_server.py").exists(), (
            "MCP server must be opt-in"
        )
        assert not (project_path / ".skills" / package_name / "SKILL.md").exists(), (
            "Agent Skill must be opt-in"
        )

    finally:
        os.chdir(original_cwd)


def test_scaffold_python_project_with_docs(tmp_path: Path) -> None:
    """Init wires up the environment, git, and pre-commit hooks."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    project_name = "test-integration-python"
    original_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)

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
                "Integration test Python project",
            ],
            input="n\n",
            text=True,
            capture_output=True,
        )

        assert result.returncode == 0, f"Scaffold command must succeed. Error:\n{result.stderr}"

        # Verify scaffold init did everything
        assert "Dependencies installed" in result.stdout, "Must install dependencies"
        assert "Pre-commit hooks configured" in result.stdout, "Must configure hooks"
        assert "Tests passing" in result.stdout, "Must run tests"

        project_path = tmp_path / project_name
        assert project_path.exists(), "Project directory must be created"
        assert (project_path / ".venv").exists(), "Virtual environment must exist"
        assert (project_path / ".git" / "hooks" / "pre-commit").exists(), (
            "Pre-commit hooks must be installed"
        )

    finally:
        os.chdir(original_cwd)


def test_scaffold_upgrade_command(tmp_path: Path) -> None:
    """Upgrade rewrites a stale managed file back to the template."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    project_name = "test-upgrade-command"
    original_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)

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
                "Test upgrade command",
            ],
            input="n\n",
            text=True,
            capture_output=True,
        )

        assert result.returncode == 0, f"Scaffold command must succeed. Error:\n{result.stderr}"

        project_path = tmp_path / project_name

        precommit_file = project_path / ".pre-commit-config.yaml"
        precommit_file.write_text("# old version\n")

        upgrade_result = subprocess.run(
            ["uv", "run", "scaffold", "upgrade", "--path", str(project_path)],
            capture_output=True,
            text=True,
        )

        assert upgrade_result.returncode == 0, "Upgrade command must succeed"
        assert "Upgrade complete" in upgrade_result.stdout
        assert ".pre-commit-config.yaml" in upgrade_result.stdout

        content = precommit_file.read_text()
        assert "default_language_version" in content
        assert "# old version" not in content

    finally:
        os.chdir(original_cwd)


def test_scaffold_adopt_command(tmp_path: Path) -> None:
    """Test adopt onboards an existing repo without clobbering files."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    repo = tmp_path / "legacy"
    repo.mkdir()
    (repo / "main.py").write_text("print('hi')\n")

    result = subprocess.run(
        ["uv", "run", "scaffold", "adopt", "--path", str(repo)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Adopt command must succeed: {result.stderr}"
    assert "Adopt complete" in result.stdout, "Must confirm completion"
    assert (repo / "pyproject.toml").exists(), "Must create pyproject.toml"
    assert (repo / ".pre-commit-config.yaml").exists(), "Must create pre-commit config"
    assert (repo / "main.py").read_text() == "print('hi')\n", "Must not touch existing files"


def test_scaffold_upgrade_dry_run(tmp_path: Path) -> None:
    """Test upgrade --dry-run lists files without writing them."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    repo = tmp_path / "dryrepo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text(
        '[project]\nname = "dryrepo"\nrequires-python = ">=3.12"\n'
        'authors = [{name = "Test"}]\ndescription = "Test"\n'
    )

    result = subprocess.run(
        ["uv", "run", "scaffold", "upgrade", "--path", str(repo), "--dry-run"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Upgrade dry-run must succeed: {result.stderr}"
    assert "Would update" in result.stdout, "Must indicate dry-run summary"
    assert ".pre-commit-config.yaml" in result.stdout, "Must list the files that would change"
    assert not (repo / ".pre-commit-config.yaml").exists(), "Dry-run must not write files"


def test_upgrade_recursive(tmp_path: Path) -> None:
    """Test recursive upgrade updates multiple projects."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    original_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)

        project_names = ["proj-a", "proj-b"]

        for project_name in project_names:
            subprocess.run(
                [
                    "uv",
                    "run",
                    "scaffold",
                    "init",
                    project_name,
                    "--author",
                    "Test Author",
                    "--description",
                    "Test recursive upgrade",
                ],
                input="n\n",
                text=True,
                capture_output=True,
                check=True,
            )

            precommit_file = tmp_path / project_name / ".pre-commit-config.yaml"
            precommit_file.write_text("# old config\n")

        upgrade_result = subprocess.run(
            ["uv", "run", "scaffold", "upgrade", "--path", str(tmp_path), "-r"],
            capture_output=True,
            text=True,
        )

        assert upgrade_result.returncode == 0, (
            f"Recursive upgrade must succeed: {upgrade_result.stderr}"
        )
        assert "proj-a" in upgrade_result.stdout or "proj_a" in upgrade_result.stdout, (
            "Must upgrade proj-a"
        )
        assert "proj-b" in upgrade_result.stdout or "proj_b" in upgrade_result.stdout, (
            "Must upgrade proj-b"
        )
        assert "2 project(s)" in upgrade_result.stdout, "Must report 2 projects"

        for project_name in project_names:
            precommit_file = tmp_path / project_name / ".pre-commit-config.yaml"
            content = precommit_file.read_text()
            assert "# old config" not in content, f"{project_name} must be upgraded"
            assert "default_language_version" in content, f"{project_name} must have new config"

    finally:
        os.chdir(original_cwd)


def test_upgrade_recursive_dry_run(tmp_path: Path) -> None:
    """Test recursive upgrade dry-run doesn't modify files."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    original_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)

        project_name = "dry-run-test"
        subprocess.run(
            [
                "uv",
                "run",
                "scaffold",
                "init",
                project_name,
                "--author",
                "Test Author",
                "--description",
                "Test dry run",
            ],
            input="n\n",
            text=True,
            capture_output=True,
            check=True,
        )

        precommit_file = tmp_path / project_name / ".pre-commit-config.yaml"
        old_content = "# old config\n"
        precommit_file.write_text(old_content)

        upgrade_result = subprocess.run(
            ["uv", "run", "scaffold", "upgrade", "--path", str(tmp_path), "-r", "--dry-run"],
            capture_output=True,
            text=True,
        )

        assert upgrade_result.returncode == 0, "Dry-run must succeed"
        assert "Dry run" in upgrade_result.stdout, "Must indicate dry-run mode"
        assert (
            project_name.replace("-", "_") in upgrade_result.stdout
            or project_name in upgrade_result.stdout
        ), "Dry-run output must mention the project"

        current_content = precommit_file.read_text()
        assert current_content == old_content, "Dry-run must not modify files"

    finally:
        os.chdir(original_cwd)


def test_ai_extras_opt_in(tmp_path: Path) -> None:
    """Test llms/mcp/skill extras are off by default and enabled by flags."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    base = ["uv", "run", "scaffold", "init", "extras-demo", "-a", "Test", "-d", "Demo", "--dry-run"]
    original_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)

        default = subprocess.run(base, capture_output=True, text=True)
        assert default.returncode == 0, f"Default dry-run must succeed: {default.stderr}"
        assert "llms.txt" not in default.stdout, "llms.txt must be off by default"
        assert "mcp_server.py" not in default.stdout, "MCP server must be off by default"
        assert "SKILL.md" not in default.stdout, "Agent Skill must be off by default"
        assert "scaffold-update.yml" not in default.stdout, "Auto-update must be off by default"

        enabled = subprocess.run(
            [*base, "--llms", "--mcp", "--skill", "--auto-update"], capture_output=True, text=True
        )
        assert enabled.returncode == 0, f"Flagged dry-run must succeed: {enabled.stderr}"
        assert "llms.txt" in enabled.stdout, "--llms must add llms.txt"
        assert "mcp_server.py" in enabled.stdout, "--mcp must add the MCP server"
        assert "SKILL.md" in enabled.stdout, "--skill must add the Agent Skill"
        assert "scaffold-update.yml" in enabled.stdout, "--auto-update must add the update workflow"

    finally:
        os.chdir(original_cwd)


def test_status_runs_pytest_and_prek(tmp_path: Path) -> None:
    """Status runs both pytest and prek across all projects and shows a table."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    original_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)

        for i in range(2):
            subprocess.run(
                [
                    "uv",
                    "run",
                    "scaffold",
                    "init",
                    f"status-{i}",
                    "--author",
                    "Test Author",
                    "--description",
                    "Test status",
                ],
                input="n\n",
                text=True,
                capture_output=True,
                check=True,
            )

        result = subprocess.run(
            ["uv", "run", "scaffold", "status", "--no-cache", "--path", str(tmp_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Status must succeed: {result.stderr}"
        assert "Running pytest" in result.stdout, "Must run pytest"
        assert "Running prek" in result.stdout, "Must run prek"
        assert "pytest:" in result.stdout, "Table must have a pytest column"
        assert "prek:" in result.stdout, "Table must have a prek column"
        assert "Results saved to" in result.stdout, "Must show where results are saved"

        from scaffold.storage import ResultStorage

        storage = ResultStorage()
        pytest_results = [
            r for r in storage.load_results(command="pytest") if "status-" in r.repo_name
        ]
        prek_results = [r for r in storage.load_results(command="prek") if "status-" in r.repo_name]
        assert len(pytest_results) >= 2, "Must have pytest results for both projects"
        assert len(prek_results) >= 2, "Must have prek results for both projects"

    finally:
        os.chdir(original_cwd)


def test_status_detailed_shows_output(tmp_path: Path) -> None:
    """Status --detailed prints per-project output."""
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
                "detailed",
                "--author",
                "Test Author",
                "--description",
                "Test detailed",
            ],
            input="n\n",
            text=True,
            capture_output=True,
            check=True,
        )

        result = subprocess.run(
            [
                "uv",
                "run",
                "scaffold",
                "status",
                "--no-cache",
                "--detailed",
                "--path",
                str(tmp_path),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Detailed status must succeed: {result.stderr}"
        assert "Detailed Output:" in result.stdout, "Must show detailed output section"
        assert "Commit:" in result.stdout or "stdout:" in result.stdout, "Must show output details"

    finally:
        os.chdir(original_cwd)


def test_status_reads_stored_state_without_running(tmp_path: Path) -> None:
    """status reads remembered results and does not re-run when no run flag is given."""
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
                "state-test",
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

        subprocess.run(
            ["uv", "run", "scaffold", "status", "--no-cache", "--path", str(tmp_path)],
            capture_output=True,
            text=True,
            check=True,
        )

        result = subprocess.run(
            ["uv", "run", "scaffold", "status", "--path", str(tmp_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Read status must succeed: {result.stderr}"
        assert "Running pytest" not in result.stdout, "Read mode must not run anything"
        assert "state-test" in result.stdout or "state_test" in result.stdout, (
            "Must show stored repo"
        )

    finally:
        os.chdir(original_cwd)


def test_config_roots_used_by_status(tmp_path: Path) -> None:
    """Multiple configured roots (a folder and a single project) all get scanned."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    from scaffold.config import ScaffoldConfig, save_config

    code = tmp_path / "code"
    (code / "proj-a").mkdir(parents=True)
    (code / "proj-a" / "pyproject.toml").write_text('[project]\nname = "proj-a"\n')
    solo = tmp_path / "solo"
    solo.mkdir()
    (solo / "pyproject.toml").write_text('[project]\nname = "solo"\n')
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    config_file = tmp_path / "config.json"
    save_config(ScaffoldConfig(roots=[code, solo]), config_file)
    env = {**os.environ, "SCAFFOLD_CONFIG": str(config_file)}

    result = subprocess.run(
        ["uv", "run", "scaffold", "status"],
        cwd=elsewhere,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"status must succeed: {result.stderr}"
    assert str(code) in result.stdout, "status must scan the folder root"
    assert str(solo) in result.stdout, "status must scan the individual project root"
