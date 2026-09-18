import os
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from scaffold.core import create_project, preview_project
from scaffold.models import ProjectConfig, ProjectType
from scaffold.storage import ResultStorage

__version__ = "0.1.0"

app = typer.Typer(
    help="""Keep Python repos current with opinionated tooling.

Examples:
  sc check                              Check project health
  sc check -r                           Check every repo in a tree
  sc upgrade                            Refresh infrastructure files
  sc upgrade --dry-run                  Preview which files change
  sc adopt                              Bring an existing repo up to standard
  sc test -r                            Run pytest across all repos
  sc test --status                      Show the last cached test results
  sc prek -r                            Run prek across all repos
  sc init my-project                    Create a new project from scratch
""",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()


def version_callback(value: bool) -> None:
    assert __version__, "Version must be defined"
    assert "." in __version__, "Version must be dotted"

    if value:
        console.print(f"sc version {__version__}")
        raise typer.Exit()


def _get_git_config(key: str) -> str | None:
    assert key is not None, "Git config key must not be None"
    assert len(key) > 0, "Git config key must not be empty"

    try:
        result = subprocess.run(
            ["git", "config", key],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return None


def _build_init_config(
    project_name: str,
    author: str | None,
    email: str | None,
    description: str | None,
    python_version: str,
    no_git_init: bool,
    *,
    with_llms: bool,
    with_mcp: bool,
    with_skill: bool,
    with_auto_update: bool,
) -> ProjectConfig:
    assert project_name, "Project name must be provided"
    assert python_version, "Python version must be provided"

    package_name = project_name.replace("-", "_")
    reserved_names = {"test", "tests", "src", "lib", "data", "docs", "setup", "build", "dist"}
    if package_name in reserved_names:
        console.print(
            f"[red]✗ Cannot use '{project_name}' - conflicts with Python/common module names[/red]"
        )
        console.print(
            f"[dim]Try: {project_name}-app, my-{project_name}, {project_name}-cli, etc.[/dim]"
        )
        raise typer.Exit(1)

    return ProjectConfig(
        name=project_name,
        type=ProjectType.PYTHON,
        author=author if author is not None else (_get_git_config("user.name") or "Unknown"),
        email=email if email is not None else _get_git_config("user.email"),
        description=description if description is not None else f"Python project: {project_name}",
        python_version=python_version,
        git_init=not no_git_init,
        with_llms=with_llms,
        with_mcp=with_mcp,
        with_skill=with_skill,
        with_auto_update=with_auto_update,
    )


def _show_init_dry_run(config: ProjectConfig, output_path: Path, project_name: str) -> None:
    assert config is not None, "Config must not be None"
    assert output_path is not None, "Output path must not be None"

    console.print("[bold]Dry run - Preview mode[/bold]\n")
    console.print(f"[cyan]Project:[/cyan] {project_name}")
    console.print(f"[cyan]Type:[/cyan] {config.type.value}")
    console.print(f"[cyan]Path:[/cyan] {output_path.resolve()}")
    console.print(f"[cyan]Author:[/cyan] {config.author}")
    if config.email:
        console.print(f"[cyan]Email:[/cyan] {config.email}")
    console.print(f"[cyan]Python:[/cyan] {config.python_version}")
    console.print(f"[cyan]Git init:[/cyan] {config.git_init}\n")
    files = preview_project(config, output_path.resolve())
    console.print("[bold]Files that would be created:[/bold]")
    for file in files:
        console.print(f"  {file}")
    console.print("\n[dim]Run without --dry-run to create the project[/dim]")


def _run_init(config: ProjectConfig, output_path: Path) -> None:
    assert config is not None, "Config must not be None"
    assert output_path.is_absolute(), "Output path must be absolute"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating project structure...", total=None)
        try:
            create_project(config, output_path, run_setup=False)
            progress.update(task, description="[green]✓[/green] Project structure created!")
        except Exception as e:
            progress.update(task, description=f"[red]✗[/red] Failed: {e}")
            raise

    os.chdir(output_path)
    from scaffold.core import setup_project_environment

    setup_project_environment(output_path)
    console.print("\n[green]✨ Project ready![/green]")
    console.print(f"[dim]{output_path.resolve()}[/dim]\n")
    console.print("[green]✓[/green] Dependencies installed")
    console.print("[green]✓[/green] Pre-commit hooks configured")
    console.print("[green]✓[/green] Tests passing")
    if sys.stdout.isatty():
        shell = os.environ.get("SHELL", "/bin/zsh")
        console.print(f"\n[dim]Starting shell in {output_path.name}/ and opening editor...[/dim]")
        os.execvp(shell, [shell, "-c", f"nvim . && exec {shell}"])


def _check_recursive(path: Path, max_depth: int) -> None:
    assert path is not None, "Path must not be None"
    assert max_depth > 0, "Max depth must be positive"

    from scaffold.core import bulk_maintenance

    console.print(f"[bold]Checking projects in:[/bold] {path}\n")
    console.print(f"[dim]Max depth: {max_depth}[/dim]\n")
    results = bulk_maintenance(path, "check", max_depth=max_depth)
    total = len(results)
    if total == 0:
        console.print("[yellow]No Python projects found[/yellow]")
        return
    success_count = sum(1 for r in results if r["status"] == "success" and not r["details"])
    issues_count = sum(1 for r in results if r["status"] == "success" and r["details"])
    error_count = sum(1 for r in results if r["status"] == "error")
    console.print(f"[bold]Checked {total} project(s):[/bold]")
    console.print(f"  [green]✓[/green] Clean: {success_count}")
    if issues_count > 0:
        console.print(f"  [yellow]![/yellow] Issues: {issues_count}")
    if error_count > 0:
        console.print(f"  [red]✗[/red] Errors: {error_count}")
    console.print()
    for result in results:
        name = result["project"].name
        details = result.get("details", [])
        if result["status"] == "success":
            if details:
                console.print(f"[yellow]![/yellow] {name}: {len(details)} issue(s)")
                for issue in details:
                    console.print(f"    • {issue}")
            else:
                console.print(f"[green]✓[/green] {name}")
        elif result["status"] == "error":
            console.print(f"[red]✗[/red] {name}: {result.get('error', 'Unknown error')}")
    if issues_count > 0:
        console.print("\n[dim]Run 'sc upgrade -r' to fix infrastructure files[/dim]")


def _upgrade_recursive(path: Path, dry_run: bool, max_depth: int) -> None:
    assert path is not None, "Path must not be None"
    assert max_depth > 0, "Max depth must be positive"

    from scaffold.core import bulk_maintenance

    console.print(f"[bold]Upgrading projects in:[/bold] {path}\n")
    console.print(f"[dim]Max depth: {max_depth}{', Dry run mode' if dry_run else ''}[/dim]\n")
    if dry_run:
        console.print("[yellow]Dry run - no files will be modified[/yellow]\n")
    results = bulk_maintenance(path, "upgrade", dry_run=dry_run, max_depth=max_depth)
    total = len(results)
    if total == 0:
        console.print("[yellow]No Python projects found[/yellow]")
        return
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = sum(1 for r in results if r["status"] == "error")
    console.print(f"[bold]Processed {total} project(s):[/bold]")
    console.print(f"  [green]✓[/green] Success: {success_count}")
    if error_count > 0:
        console.print(f"  [red]✗[/red] Errors: {error_count}")
    console.print()
    for result in results:
        name = result["project"].name
        details = result.get("details", [])
        if result["status"] == "success":
            icon = "[yellow]~[/yellow]" if dry_run else "[green]✓[/green]"
            msg = (
                f"{icon} {name}: {len(details)} file(s)"
                if details
                else f"[green]✓[/green] {name}: up to date"
            )
            console.print(msg)
        elif result["status"] == "error":
            console.print(f"[red]✗[/red] {name}: {result.get('error', 'Unknown error')}")
    if dry_run:
        console.print("\n[dim]Run without --dry-run to apply changes[/dim]")
    else:
        console.print("\n[green]Upgrade complete![/green]")


def _print_file_changes(changes: list, dry_run: bool, verb: str) -> None:
    assert changes is not None, "Changes must not be None"
    assert verb in ["update", "create"], "Verb must be 'update' or 'create'"

    past = "updated" if verb == "update" else "created"
    would = "Would update" if verb == "update" else "Would create"
    header = (
        f"[yellow]{would} {len(changes)} file(s):[/yellow]\n"
        if dry_run
        else f"[green]{past.capitalize()} {len(changes)} file(s):[/green]\n"
    )
    console.print(header)
    mark = "[green]✓[/green]" if verb == "update" else "[green]+[/green]"
    for change in changes:
        icon = "[yellow]~[/yellow]" if dry_run else mark
        console.print(f"  {icon} {change.path}")


def _upgrade_single(path: Path, dry_run: bool) -> None:
    assert path is not None, "Path must not be None"
    assert path.exists(), f"Path {path} does not exist"

    from scaffold.core import apply_changes, ensure_prek_hooks, plan_upgrade

    console.print(f"[bold]Upgrading project at:[/bold] {path}\n")
    if dry_run:
        console.print("[yellow]Dry run mode - no files will be modified[/yellow]\n")
    try:
        changes = plan_upgrade(path)
    except Exception as e:
        console.print(f"[red]✗ Upgrade failed: {e}[/red]")
        raise
    if not changes:
        console.print("[green]✓ Project is already up to date![/green]")
        return
    if not dry_run:
        apply_changes(path, changes)
        ensure_prek_hooks(path)
    _print_file_changes(changes, dry_run, "update")
    console.print(
        "\n[dim]Run without --dry-run to apply changes[/dim]"
        if dry_run
        else "\n[green]Upgrade complete![/green]"
    )


def _execute_bulk(
    command: str, projects: list, storage: ResultStorage, cached_results_map: dict, force: bool
) -> tuple[list, int, int, int]:
    assert command in ["pytest", "prek"], "Command must be 'pytest' or 'prek'"
    assert projects is not None, "Projects must not be None"

    from concurrent.futures import ProcessPoolExecutor, as_completed

    from scaffold.core import _run_command_on_repo

    results: list = []
    cached_count = passed_count = failed_count = 0
    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(_run_command_on_repo, project, command, 600, storage, force): project
            for project in projects
        }
        for future in as_completed(futures):
            try:
                result = future.result()
                cached = cached_results_map.get(str(result.repo_path))
                is_cached = cached and result.timestamp == cached.timestamp and not force
                if not is_cached:
                    storage.save_result(result)
                else:
                    cached_count += 1
                results.append(result)
                if result.exit_code == 0:
                    passed_count += 1
                    status_icon = "[green]✓[/green]"
                else:
                    failed_count += 1
                    status_icon = "[red]✗[/red]"
                cached_str = " [dim](cached)[/dim]" if is_cached else ""
                console.print(f"{status_icon} {result.repo_name}{cached_str}")
            except Exception as e:
                project = futures[future]
                console.print(f"[red]Error in {project.name}: {e}[/red]")
    return results, cached_count, passed_count, failed_count


def _print_bulk_summary(
    command: str,
    results: list,
    storage: ResultStorage,
    cached_count: int,
    passed_count: int,
    failed_count: int,
) -> None:
    assert command in ["pytest", "prek"], "Command must be 'pytest' or 'prek'"
    assert results is not None, "Results must not be None"

    label = "Test" if command == "pytest" else "Prek"
    total_label = "tested" if command == "pytest" else "checked"
    console.print(f"\n[bold]{label} Results:[/bold]")
    console.print(f"  Total {total_label}: {len(results)}")
    if cached_count > 0:
        console.print(f"  [dim]📦 Cached: {cached_count} (unchanged since last run)[/dim]")
    console.print(f"  [green]✓[/green] Passed: {passed_count}")
    if failed_count > 0:
        console.print(f"  [red]✗[/red] Failed: {failed_count}\n")
        console.print("[bold]Failed repositories:[/bold]")
        for result in results:
            if result.exit_code != 0:
                console.print(f"  [red]✗[/red] {result.repo_name} (exit {result.exit_code})")
    else:
        console.print()
    console.print(f"[dim]Results saved to {storage.status_file}[/dim]")


def _run_bulk_interactive(command: str, path: Path, max_depth: int, force: bool) -> None:
    assert command in ["pytest", "prek"], "Command must be 'pytest' or 'prek'"
    assert path.exists(), "Path must exist"

    from scaffold.core import find_python_projects

    console.print(f"[bold]Running {command} on all projects in:[/bold] {path}\n")
    console.print(f"[dim]Max depth: {max_depth}[/dim]\n")
    projects = find_python_projects(path, max_depth)
    if not projects:
        console.print("[yellow]No Python projects found[/yellow]")
        return
    storage = ResultStorage()
    cached_results_map = storage.get_latest_by_repo(command) if not force else {}
    results, cached_count, passed_count, failed_count = _execute_bulk(
        command, projects, storage, cached_results_map, force
    )
    _print_bulk_summary(command, results, storage, cached_count, passed_count, failed_count)


@app.callback()
def main(
    _version: bool = typer.Option(
        False, "--version", "-v", callback=version_callback, is_eager=True, help="Show version"
    ),
) -> None:
    """Scaffold CLI - Keep Python repos current with opinionated tooling."""
    assert app is not None, "Typer app must be initialized"
    assert app.registered_commands, "App must expose commands"


@app.command()
def init(
    project_name: str = typer.Argument(..., help="Project name"),
    author: str | None = typer.Option(None, "--author", "-a", help="Author name"),
    email: str | None = typer.Option(None, "--email", "-e", help="Author email"),
    description: str | None = typer.Option(None, "--description", "-d", help="Project description"),
    python_version: str = typer.Option("3.12", "--python", "-p", help="Python version"),
    no_git_init: bool = typer.Option(False, "--no-git", help="Skip git initialization"),
    with_llms: bool = typer.Option(False, "--llms", help="Include an llms.txt file"),
    with_mcp: bool = typer.Option(False, "--mcp", help="Include an MCP server"),
    with_skill: bool = typer.Option(False, "--skill", help="Include a Claude Code Agent Skill"),
    auto_update: bool = typer.Option(
        False, "--auto-update", help="Include a workflow that PRs scaffold updates on a schedule"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without creating"),
) -> None:
    """Create a new Python project with everything configured.

    Automatically sets up dependencies, pre-commit hooks, tests, and git.
    Opens your editor when ready - no manual setup required!

    The llms.txt, MCP server, Agent Skill, and scheduled scaffold-update
    workflow are opt-in via --llms, --mcp, --skill, and --auto-update.
    """
    assert project_name, "Project name must be provided"
    assert python_version, "Python version must be provided"

    config = _build_init_config(
        project_name,
        author,
        email,
        description,
        python_version,
        no_git_init,
        with_llms=with_llms,
        with_mcp=with_mcp,
        with_skill=with_skill,
        with_auto_update=auto_update,
    )
    output_path = Path.cwd() / project_name

    if dry_run:
        _show_init_dry_run(config, output_path, project_name)
        return

    if output_path.exists():
        console.print(f"[red]✗ Directory '{project_name}' already exists[/red]")
        raise typer.Exit(1)

    _run_init(config, output_path.resolve())


@app.command()
def check(
    path: Path = typer.Option(Path.cwd(), help="Project path to check"),
    recursive: bool = typer.Option(
        False, "--recursive", "-r", help="Check all projects in directory tree"
    ),
    max_depth: int = typer.Option(
        3, "--max-depth", help="Maximum directory depth for recursive search"
    ),
) -> None:
    """Check project structure and configuration."""
    assert path is not None, "Path must not be None"
    assert path.exists(), f"Path {path} does not exist"

    from scaffold.core import check_project

    if recursive:
        _check_recursive(path, max_depth)
        return

    console.print(f"[bold]Checking project at:[/bold] {path}\n")
    issues = check_project(path)
    if not issues:
        console.print("[green]✓ Project structure looks good![/green]")
        return
    console.print(f"[yellow]Found {len(issues)} issue(s):[/yellow]\n")
    for issue in issues:
        console.print(f"  [red]✗[/red] {issue}")
    console.print("\n[dim]Run 'sc upgrade' to fix infrastructure files[/dim]")


@app.command()
def upgrade(
    path: Path = typer.Option(Path.cwd(), help="Project path to upgrade"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without applying"),
    recursive: bool = typer.Option(
        False, "--recursive", "-r", help="Upgrade all projects in directory tree"
    ),
    max_depth: int = typer.Option(
        3, "--max-depth", help="Maximum directory depth for recursive search"
    ),
) -> None:
    """Upgrade project infrastructure files to latest standards.

    Refreshes scaffold-managed files in place. Use --dry-run to preview which
    files change first; review the applied changes with 'git diff'.
    """
    assert path is not None, "Path must not be None"
    assert path.exists(), f"Path {path} does not exist"

    if recursive:
        _upgrade_recursive(path, dry_run, max_depth)
    else:
        _upgrade_single(path, dry_run)


@app.command()
def adopt(
    path: Path = typer.Option(Path.cwd(), help="Repository path to adopt"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing"),
) -> None:
    """Bring an existing repository up to scaffold standards.

    Adds missing infrastructure and standard files without overwriting
    anything that already exists. Works even if the repo was not created by
    scaffold. Run 'sc upgrade' afterwards to keep managed files current.
    """
    assert path is not None, "Path must not be None"
    assert path.exists(), f"Path {path} does not exist"

    from scaffold.core import apply_changes, ensure_prek_hooks, plan_adopt

    console.print(f"[bold]Adopting repository at:[/bold] {path}\n")
    if dry_run:
        console.print("[yellow]Dry run mode - no files will be written[/yellow]\n")
    try:
        changes = plan_adopt(path)
    except Exception as e:
        console.print(f"[red]✗ Adopt failed: {e}[/red]")
        raise
    if not changes:
        console.print("[green]✓ Repository already has all standard files![/green]")
        return
    if not dry_run:
        apply_changes(path, changes)
        ensure_prek_hooks(path)
    _print_file_changes(changes, dry_run, "create")
    if dry_run:
        console.print("\n[dim]Run without --dry-run to write files[/dim]")
    else:
        console.print("\n[green]Adopt complete![/green]")
        console.print("[dim]Run 'uv sync', then 'sc upgrade' as needed.[/dim]")


@app.command(name="sync-hook-pins", hidden=True)
def sync_hook_pins_command() -> None:
    """Copy pinned hook revisions from .pre-commit-config.yaml into the template.

    Maintenance command for the scaffold repo itself: run after 'prek update'
    so 'sc upgrade' distributes the refreshed pins. Run from the repo root.
    """
    from scaffold.core import sync_hook_pins

    config = Path(".pre-commit-config.yaml")
    template = Path("src/scaffold/templates/base/.pre-commit-config.yaml.j2")
    assert config.exists(), "Run this from a repo with a .pre-commit-config.yaml"
    assert template.exists(), "Run this from the scaffold repo root"

    if sync_hook_pins(config, template):
        console.print("[green]✓ Synced hook pins into the template[/green]")
    else:
        console.print("[green]✓ Template hook pins already current[/green]")


@app.command()
def test(
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Run on all projects in tree"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-run, ignore cache"),
    status: bool = typer.Option(False, "--status", help="Show cached results instead of running"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="With --status, show output"),
    path: Path = typer.Option(Path.cwd(), help="Root directory to search for projects"),
    max_depth: int = typer.Option(
        3, "--max-depth", help="Maximum directory depth for recursive search"
    ),
) -> None:
    """Run pytest on the current project, all projects with -r, or --status for cached results."""
    assert path is not None, "Path must not be None"
    assert path.exists(), f"Path {path} does not exist"

    if status:
        _show_status("pytest", path, detailed)
        return
    if not recursive:
        console.print("[bold]Running pytest on current project...[/bold]\n")
        result = subprocess.run(["uv", "run", "pytest"], check=False)
        raise typer.Exit(result.returncode)

    _run_bulk_interactive("pytest", path, max_depth, force)


@app.command()
def prek(
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Run on all projects in tree"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-run, ignore cache"),
    status: bool = typer.Option(False, "--status", help="Show cached results instead of running"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="With --status, show output"),
    path: Path = typer.Option(Path.cwd(), help="Root directory to search for projects"),
    max_depth: int = typer.Option(
        3, "--max-depth", help="Maximum directory depth for recursive search"
    ),
) -> None:
    """Run prek on the current project, all projects with -r, or --status for cached results."""
    assert path is not None, "Path must not be None"
    assert path.exists(), f"Path {path} does not exist"

    if status:
        _show_status("prek", path, detailed)
        return
    if not recursive:
        console.print("[bold]Running prek on current project...[/bold]\n")
        result = subprocess.run(["uv", "run", "prek", "run", "--all-files"], check=False)
        raise typer.Exit(result.returncode)

    _run_bulk_interactive("prek", path, max_depth, force)


def _print_results_by_repo(results: list) -> None:
    assert results is not None, "Results must not be None"
    assert len(results) > 0, "Results must not be empty"

    from datetime import datetime, timedelta

    now = datetime.now()
    grouped = {}
    for result in results:
        repo = result.repo_name
        if repo not in grouped:
            grouped[repo] = {"pytest": None, "prek": None, "path": result.repo_path}
        grouped[repo][result.command] = result

    for repo_name in sorted(grouped.keys()):
        repo_data = grouped[repo_name]
        pytest_result = repo_data.get("pytest")
        prek_result = repo_data.get("prek")
        pytest_status = ""
        prek_status = ""
        timestamp_str = ""

        if pytest_result:
            pytest_status = (
                "[green]✓ PASS[/green]" if pytest_result.exit_code == 0 else "[red]✗ FAIL[/red]"
            )
            age = now - pytest_result.timestamp
            if age > timedelta(days=1):
                timestamp_str = f"[dim]{age.days}d ago[/dim]"
            elif age > timedelta(hours=1):
                hours = int(age.total_seconds() / 3600)
                timestamp_str = f"[dim]{hours}h ago[/dim]"
            else:
                minutes = int(age.total_seconds() / 60)
                timestamp_str = f"[dim]{minutes}m ago[/dim]"

        if prek_result:
            prek_status = (
                "[green]✓ PASS[/green]" if prek_result.exit_code == 0 else "[red]✗ FAIL[/red]"
            )

        test_col = f"pytest: {pytest_status}" if pytest_result else ""
        prek_col = f"prek: {prek_status}" if prek_result else ""
        combined = f"{test_col}  {prek_col}".strip()
        console.print(f"{repo_name:30} {combined:40} {timestamp_str}")


def _print_detailed_results(results: list) -> None:
    assert results is not None, "Results must not be None"
    assert len(results) > 0, "Results must not be empty"

    console.print("\n[bold]Detailed Output:[/bold]\n")
    for result in results:
        status = "PASS" if result.exit_code == 0 else f"FAIL ({result.exit_code})"
        console.print(f"[bold]{result.repo_name}[/bold] - {result.command} - {status}")
        if result.git_commit:
            console.print(f"  Commit: {result.git_commit[:8]}")
        if result.stdout:
            console.print(f"  [dim]stdout:[/dim]\n{result.stdout[:500]}")
        if result.stderr:
            console.print(f"  [dim]stderr:[/dim]\n{result.stderr[:500]}")
        console.print()


def _show_status(command: str, path: Path, detailed: bool) -> None:
    assert command in ["pytest", "prek"], "Command must be pytest or prek"
    assert path.exists(), "Path must exist"

    from scaffold.core import find_python_projects

    storage = ResultStorage()
    runner = "test" if command == "pytest" else "prek"
    if not storage.status_file.exists():
        console.print(f"[yellow]No results yet. Run 'sc {runner} -r' first.[/yellow]")
        return

    project_paths = {str(p) for p in find_python_projects(path, max_depth=3)}
    results = [r for r in storage.load_results(command=command) if r.repo_path in project_paths]

    if not results:
        console.print(
            f"[yellow]No {command} results for projects in {path}[/yellow]\n"
            f"[dim]Run 'sc {runner} -r' in this directory[/dim]"
        )
        return

    console.print(f"[bold]Cached {command} results[/bold] - {path}")
    console.print(f"[dim]Total results: {len(results)}[/dim]\n")
    _print_results_by_repo(results)
    if detailed:
        _print_detailed_results(results)


if __name__ == "__main__":
    app()
