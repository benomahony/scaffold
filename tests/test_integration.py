import os
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def test_scaffold_python_project(tmp_path: Path) -> None:
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
        assert (project_path / "llms.txt").exists(), "llms.txt must exist"
        assert (project_path / "zensical.toml").exists(), "zensical.toml must exist"
        assert (project_path / "src").exists(), "src directory must exist"
        assert (project_path / "tests").exists(), "tests directory must exist"
        assert (project_path / ".venv").exists(), "Virtual environment must exist"
        assert (project_path / ".git").exists(), "Git repository must exist"
        assert (project_path / ".git" / "hooks" / "pre-commit").exists(), (
            "Pre-commit hooks must be installed"
        )

        package_name = project_name.replace("-", "_")
        assert (project_path / "src" / package_name / "mcp_server.py").exists(), (
            "MCP server must exist"
        )
        assert (project_path / ".skills" / package_name / "SKILL.md").exists(), (
            "Agent Skill must exist"
        )

    finally:
        os.chdir(original_cwd)


def test_scaffold_python_project_with_docs(tmp_path: Path) -> None:
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


def test_scaffold_check_command(tmp_path: Path) -> None:
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    project_name = "test-check-command"
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
                "Test check command",
            ],
            input="n\n",
            text=True,
            capture_output=True,
        )

        assert result.returncode == 0, f"Scaffold command must succeed. Error:\n{result.stderr}"

        project_path = tmp_path / project_name

        check_result = subprocess.run(
            ["uv", "run", "scaffold", "check", "--path", str(project_path)],
            capture_output=True,
            text=True,
        )

        assert check_result.returncode == 0, "Check command must succeed"
        assert "Project structure looks good" in check_result.stdout

    finally:
        os.chdir(original_cwd)


def test_scaffold_upgrade_command(tmp_path: Path) -> None:
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


def test_check_recursive(tmp_path: Path) -> None:
    """Test recursive check finds and checks multiple projects."""
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
                "project1",
                "--author",
                "Test Author",
                "--description",
                "Test recursive check",
            ],
            input="n\n",
            text=True,
            capture_output=True,
            check=True,
        )

        subprocess.run(
            [
                "uv",
                "run",
                "scaffold",
                "init",
                "project2",
                "--author",
                "Test Author",
                "--description",
                "Test recursive check",
            ],
            input="n\n",
            text=True,
            capture_output=True,
            check=True,
        )

        nested_dir = tmp_path / "nested"
        nested_dir.mkdir()
        os.chdir(nested_dir)

        subprocess.run(
            [
                "uv",
                "run",
                "scaffold",
                "init",
                "project3",
                "--author",
                "Test Author",
                "--description",
                "Test recursive check",
            ],
            input="n\n",
            text=True,
            capture_output=True,
            check=True,
        )

        os.chdir(tmp_path)

        check_result = subprocess.run(
            ["uv", "run", "scaffold", "check", "--path", str(tmp_path), "-r"],
            capture_output=True,
            text=True,
        )

        assert check_result.returncode == 0, f"Recursive check must succeed: {check_result.stderr}"
        assert "project1" in check_result.stdout, "Must find project1"
        assert "project2" in check_result.stdout, "Must find project2"
        assert "project3" in check_result.stdout, "Must find project3"
        assert "3 project(s)" in check_result.stdout, "Must report 3 projects"

    finally:
        os.chdir(original_cwd)


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
        )

        current_content = precommit_file.read_text()
        assert current_content == old_content, "Dry-run must not modify files"

    finally:
        os.chdir(original_cwd)


def test_recursive_max_depth(tmp_path: Path) -> None:
    """Test max-depth limits recursive search."""
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
                "shallow",
                "--author",
                "Test Author",
                "--description",
                "Test max depth",
            ],
            input="n\n",
            text=True,
            capture_output=True,
            check=True,
        )

        deep_dir = tmp_path / "level1" / "level2" / "level3"
        deep_dir.mkdir(parents=True)
        os.chdir(deep_dir)

        subprocess.run(
            [
                "uv",
                "run",
                "scaffold",
                "init",
                "deep",
                "--author",
                "Test Author",
                "--description",
                "Test max depth",
            ],
            input="n\n",
            text=True,
            capture_output=True,
            check=True,
        )

        os.chdir(tmp_path)

        check_result = subprocess.run(
            ["uv", "run", "scaffold", "check", "--path", str(tmp_path), "-r", "--max-depth", "2"],
            capture_output=True,
            text=True,
        )

        assert check_result.returncode == 0, "Check with max-depth must succeed"
        assert "shallow" in check_result.stdout, "Must find shallow project"
        assert "deep" not in check_result.stdout, "Must not find deep project beyond max-depth"

    finally:
        os.chdir(original_cwd)


def test_ai_integration_files(tmp_path: Path) -> None:
    """Test that AI integration files (llms.txt, MCP, skills) are valid."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    project_name = "test-ai-integration"
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
                "Test AI integration",
            ],
            input="n\n",
            text=True,
            capture_output=True,
        )

        assert result.returncode == 0, f"Scaffold command must succeed. Error:\n{result.stderr}"

        project_path = tmp_path / project_name
        package_name = project_name.replace("-", "_")

        llms_txt = project_path / "llms.txt"
        assert llms_txt.exists(), "llms.txt must exist"
        llms_content = llms_txt.read_text()
        assert llms_content.startswith("# test-ai-integration"), (
            "llms.txt must start with H1 project name"
        )
        assert "> Test AI integration" in llms_content, "llms.txt must have description blockquote"
        assert "## Documentation" in llms_content, "llms.txt must have Documentation section"
        assert "## AI Integration" in llms_content, "llms.txt must have AI Integration section"

        zensical_toml = project_path / "zensical.toml"
        assert zensical_toml.exists(), "zensical.toml must exist"
        zensical_content = zensical_toml.read_text()
        assert "[project]" in zensical_content, "zensical.toml must have [project] section"
        assert 'site_name = "test-ai-integration"' in zensical_content, (
            "zensical.toml must have site_name"
        )
        assert "[project.theme]" in zensical_content, "zensical.toml must have theme section"

        mcp_server = project_path / "src" / package_name / "mcp_server.py"
        assert mcp_server.exists(), "MCP server must exist"
        mcp_content = mcp_server.read_text()
        assert "from mcp.server import Server" in mcp_content, "MCP server must import Server"
        assert "async def list_resources()" in mcp_content, "MCP server must have list_resources"
        assert "async def read_resource(" in mcp_content, "MCP server must have read_resource"

        skill_md = project_path / ".skills" / package_name / "SKILL.md"
        assert skill_md.exists(), "SKILL.md must exist"
        skill_content = skill_md.read_text()
        assert skill_content.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
        assert "name: test-ai-integration" in skill_content, (
            "SKILL.md must have name in frontmatter"
        )
        assert "description:" in skill_content, "SKILL.md must have description in frontmatter"
        assert "# test-ai-integration Skill" in skill_content, "SKILL.md must have H1 heading"

        workflow = project_path / ".github" / "workflows" / "ci.yml"
        assert workflow.exists(), "GitHub Actions workflow must exist"
        workflow_content = workflow.read_text()
        assert "name: CI and Publish" in workflow_content, "Workflow must have name"
        assert "jobs:" in workflow_content, "Workflow must have jobs"
        assert "test:" in workflow_content, "Workflow must have test job"
        assert "publish:" in workflow_content, "Workflow must have publish job"
        assert "docs:" in workflow_content, "Workflow must have docs job"
        assert "uv run zensical build" in workflow_content, "Docs job must build with zensical"

        pyproject = project_path / "pyproject.toml"
        pyproject_content = pyproject.read_text()
        assert "zensical>=" in pyproject_content, "pyproject.toml must have zensical in dev deps"
        assert "mcp>=" in pyproject_content, "pyproject.toml must have mcp optional dep"
        assert "bump-my-version>=" in pyproject_content, "pyproject.toml must have bump-my-version"

    finally:
        os.chdir(original_cwd)


def test_bulk_test_command(tmp_path: Path) -> None:
    """Test bulk test command runs pytest on all projects."""
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
                    f"bulk-test-{i}",
                    "--author",
                    "Test Author",
                    "--description",
                    "Test bulk test",
                ],
                input="n\n",
                text=True,
                capture_output=True,
                check=True,
            )

        result = subprocess.run(
            ["uv", "run", "scaffold", "bulk", "test", "--path", str(tmp_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Bulk test must succeed: {result.stderr}"
        assert "Running pytest" in result.stdout, "Must indicate pytest running"
        assert "Test Results:" in result.stdout, "Must show test results"
        assert "Total tested: 2" in result.stdout, "Must test 2 projects"
        assert "Results saved to" in result.stdout, "Must show where results are saved"

        storage_file = Path.home() / ".scaffold" / "repo_status.jsonl"
        assert storage_file.exists(), "Storage file must be created"

        from scaffold.storage import ResultStorage

        storage = ResultStorage()
        results = storage.load_results(command="pytest")
        pytest_results = [r for r in results if "bulk-test" in r.repo_name]
        assert len(pytest_results) >= 2, "Must have results for both projects"

    finally:
        os.chdir(original_cwd)


def test_bulk_prek_command(tmp_path: Path) -> None:
    """Test bulk prek command runs prek on all projects."""
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
                    f"bulk-prek-{i}",
                    "--author",
                    "Test Author",
                    "--description",
                    "Test bulk prek",
                ],
                input="n\n",
                text=True,
                capture_output=True,
                check=True,
            )

        result = subprocess.run(
            ["uv", "run", "scaffold", "bulk", "prek", "--path", str(tmp_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Bulk prek must succeed: {result.stderr}"
        assert "Running prek" in result.stdout, "Must indicate prek running"
        assert "Prek Results:" in result.stdout, "Must show prek results"
        assert "Total checked: 2" in result.stdout, "Must check 2 projects"
        assert "Results saved to" in result.stdout, "Must show where results are saved"

        from scaffold.storage import ResultStorage

        storage = ResultStorage()
        results = storage.load_results(command="prek")
        prek_results = [r for r in results if "bulk-prek" in r.repo_name]
        assert len(prek_results) >= 2, "Must have results for both projects"

    finally:
        os.chdir(original_cwd)


def test_bulk_status_command(tmp_path: Path) -> None:
    """Test bulk status command displays results."""
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
                "status-test",
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

        subprocess.run(
            ["uv", "run", "scaffold", "bulk", "test", "--path", str(tmp_path)],
            capture_output=True,
            text=True,
            check=True,
        )

        result = subprocess.run(
            ["uv", "run", "scaffold", "bulk", "status", "--command", "pytest"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Bulk status must succeed: {result.stderr}"
        assert "Bulk Command Results" in result.stdout, "Must show results header"
        assert "Command: pytest" in result.stdout, "Must filter by pytest"
        assert "status-test" in result.stdout or "status_test" in result.stdout, (
            "Must show project in results"
        )

    finally:
        os.chdir(original_cwd)


def test_bulk_status_detailed(tmp_path: Path) -> None:
    """Test bulk status detailed output."""
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
                "detailed-test",
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

        subprocess.run(
            ["uv", "run", "scaffold", "bulk", "test", "--path", str(tmp_path)],
            capture_output=True,
            text=True,
            check=True,
        )

        result = subprocess.run(
            ["uv", "run", "scaffold", "bulk", "status", "--detailed"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Detailed status must succeed: {result.stderr}"
        assert "Detailed Output:" in result.stdout, "Must show detailed output section"
        assert "Commit:" in result.stdout or "stdout:" in result.stdout, (
            "Must show commit or output details"
        )

    finally:
        os.chdir(original_cwd)
