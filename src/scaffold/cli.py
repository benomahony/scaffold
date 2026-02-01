import os
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

from scaffold.core import create_project, preview_project
from scaffold.models import ProjectConfig, ProjectType
from scaffold.storage import ResultStorage

__version__ = "0.1.0"

app = typer.Typer(
    help="""Scaffold new Python projects with opinionated defaults.

Examples:
  sc init my-project                    Create new project
  sc init my-project --dry-run          Preview before creating
  sc check                              Check project health
  sc upgrade                            Update infrastructure files
  sc list                               List all Python projects
  sc test -r                            Run pytest on all repos
  sc prek -r                            Run prek on all repos
  sc status                             Show test results for current dir
""",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()


def version_callback(value: bool) -> None:
    assert isinstance(value, bool), "Value must be boolean"
    assert __version__ is not None, "Version must be defined"

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


@app.callback()
def main(
    _version: bool = typer.Option(
        False, "--version", "-v", callback=version_callback, is_eager=True, help="Show version"
    ),
) -> None:
    """Scaffold CLI - Create Python projects with opinionated defaults."""
    assert app is not None, "Typer app must be initialized"
    assert _version is None or isinstance(_version, bool), "Version must be None or boolean"


@app.command()
def init(
    project_name: str = typer.Argument(..., help="Project name"),
    author: str | None = typer.Option(None, "--author", "-a", help="Author name"),
    email: str | None = typer.Option(None, "--email", "-e", help="Author email"),
    description: str | None = typer.Option(None, "--description", "-d", help="Project description"),
    python_version: str = typer.Option("3.12", "--python", "-p", help="Python version"),
    no_git_init: bool = typer.Option(False, "--no-git", help="Skip git initialization"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without creating"),
) -> None:
    """Create a new Python project with everything configured.

    Automatically sets up dependencies, pre-commit hooks, tests, and git.
    Opens your editor when ready - no manual setup required!
    """
    assert project_name is not None, "Project name must be provided"

    # Validate project name
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

    project_type = ProjectType.PYTHON

    if author is None:
        author = _get_git_config("user.name") or "Unknown"

    if email is None:
        email = _get_git_config("user.email")

    if description is None:
        description = f"Python project: {project_name}"

    assert author is not None, "Author must be provided"
    assert description is not None, "Description must be provided"

    config = ProjectConfig(
        name=project_name,
        type=project_type,
        author=author,
        email=email,
        description=description,
        python_version=python_version,
        git_init=not no_git_init,
    )

    output_path = Path.cwd() / project_name

    if dry_run:
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
        return

    assert not output_path.exists(), f"Directory {output_path} already exists"

    # Create project structure (without running setup yet)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating project structure...", total=None)

        try:
            create_project(config, output_path.resolve(), run_setup=False)
            progress.update(task, description="[green]✓[/green] Project structure created!")
        except Exception as e:
            progress.update(task, description=f"[red]✗[/red] Failed: {e}")
            raise

    # cd into project directory IMMEDIATELY after creating files
    os.chdir(output_path)

    # Now run setup from within the project directory
    from scaffold.core import setup_project_environment

    setup_project_environment(output_path)

    console.print("\n[green]✨ Project ready![/green]")
    console.print(f"[dim]{output_path.resolve()}[/dim]\n")
    console.print("[green]✓[/green] Dependencies installed")
    console.print("[green]✓[/green] Pre-commit hooks configured")
    console.print("[green]✓[/green] Tests passing")

    # Start shell in project dir, open nvim, keep shell open after nvim exits
    if sys.stdout.isatty():
        shell = os.environ.get("SHELL", "/bin/zsh")
        console.print(f"\n[dim]Starting shell in {output_path.name}/ and opening editor...[/dim]")
        # Run nvim, then exec a shell so user stays in project directory
        os.execvp(shell, [shell, "-c", f"nvim . && exec {shell}"])


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

    from scaffold.core import bulk_maintenance, check_project

    if recursive:
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
            project_name = result["project"].name
            status = result["status"]
            details = result.get("details", [])

            if status == "success":
                if details:
                    console.print(f"[yellow]![/yellow] {project_name}: {len(details)} issue(s)")
                    for issue in details:
                        console.print(f"    • {issue}")
                else:
                    console.print(f"[green]✓[/green] {project_name}")
            elif status == "error":
                console.print(
                    f"[red]✗[/red] {project_name}: {result.get('error', 'Unknown error')}"
                )

        if issues_count > 0:
            console.print("\n[dim]Run 'sc upgrade -r' to fix infrastructure files[/dim]")
    else:
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
    """Upgrade project infrastructure files to latest standards."""
    assert path is not None, "Path must not be None"
    assert path.exists(), f"Path {path} does not exist"

    from scaffold.core import bulk_maintenance, upgrade_project

    if recursive:
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
            project_name = result["project"].name
            status = result["status"]
            details = result.get("details", [])

            if status == "success":
                if details:
                    icon = "[yellow]~[/yellow]" if dry_run else "[green]✓[/green]"
                    console.print(f"{icon} {project_name}: {len(details)} file(s)")
                else:
                    console.print(f"[green]✓[/green] {project_name}: up to date")
            elif status == "error":
                console.print(
                    f"[red]✗[/red] {project_name}: {result.get('error', 'Unknown error')}"
                )

        if dry_run:
            console.print("\n[dim]Run without --dry-run to apply changes[/dim]")
        else:
            console.print("\n[green]Upgrade complete![/green]")
    else:
        console.print(f"[bold]Upgrading project at:[/bold] {path}\n")

        if dry_run:
            console.print("[yellow]Dry run mode - no files will be modified[/yellow]\n")

        try:
            changes = upgrade_project(path, dry_run=dry_run)

            if not changes:
                console.print("[green]✓ Project is already up to date![/green]")
                return

            if dry_run:
                console.print(f"[yellow]Would update {len(changes)} file(s):[/yellow]\n")
            else:
                console.print(f"[green]Updated {len(changes)} file(s):[/green]\n")

            for file in changes:
                console.print(f"  {'[yellow]~[/yellow]' if dry_run else '[green]✓[/green]'} {file}")

            if dry_run:
                console.print("\n[dim]Run without --dry-run to apply changes[/dim]")
            else:
                console.print("\n[green]Upgrade complete![/green]")

        except Exception as e:
            console.print(f"[red]✗ Upgrade failed: {e}[/red]")
            raise


@app.command()
def test(
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Run on all projects in tree"),
    path: Path = typer.Option(Path.cwd(), help="Root directory to search for projects"),
    max_depth: int = typer.Option(
        3, "--max-depth", help="Maximum directory depth for recursive search"
    ),
) -> None:
    """Run pytest on current project or all projects with -r."""
    assert path is not None, "Path must not be None"
    assert path.exists(), f"Path {path} does not exist"

    from concurrent.futures import ProcessPoolExecutor, as_completed

    from scaffold.core import _run_command_on_repo, find_python_projects

    if not recursive:
        console.print("[bold]Running pytest on current project...[/bold]\n")
        result = subprocess.run(["uv", "run", "pytest"], check=False)
        raise typer.Exit(result.returncode)

    console.print(f"[bold]Running pytest on all projects in:[/bold] {path}\n")
    console.print(f"[dim]Max depth: {max_depth}[/dim]\n")

    projects = find_python_projects(path, max_depth)

    if not projects:
        console.print("[yellow]No Python projects found[/yellow]")
        return

    storage = ResultStorage()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("Running pytest...", total=len(projects))

        results = []
        with ProcessPoolExecutor() as executor:
            futures = {
                executor.submit(_run_command_on_repo, project, "pytest"): project
                for project in projects
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    storage.save_result(result)
                    results.append(result)
                    status = "✓" if result.exit_code == 0 else "✗"
                    progress.update(task, advance=1, description=f"Running pytest... {status}")
                except Exception as e:
                    project = futures[future]
                    console.print(f"[red]Error in {project.name}: {e}[/red]")
                    progress.advance(task)

    total = len(results)
    passed = sum(1 for r in results if r.exit_code == 0)
    failed = sum(1 for r in results if r.exit_code != 0)

    console.print("\n[bold]Test Results:[/bold]")
    console.print(f"  Total tested: {total}")
    console.print(f"  [green]✓[/green] Passed: {passed}")
    if failed > 0:
        console.print(f"  [red]✗[/red] Failed: {failed}\n")

        console.print("[bold]Failed repositories:[/bold]")
        for result in results:
            if result.exit_code != 0:
                console.print(f"  [red]✗[/red] {result.repo_name} (exit {result.exit_code})")
    else:
        console.print()

    console.print(f"[dim]Results saved to {storage.status_file}[/dim]")


@app.command()
def prek(
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Run on all projects in tree"),
    path: Path = typer.Option(Path.cwd(), help="Root directory to search for projects"),
    max_depth: int = typer.Option(
        3, "--max-depth", help="Maximum directory depth for recursive search"
    ),
) -> None:
    """Run prek on current project or all projects with -r."""
    assert path is not None, "Path must not be None"
    assert path.exists(), f"Path {path} does not exist"

    from concurrent.futures import ProcessPoolExecutor, as_completed

    from scaffold.core import _run_command_on_repo, find_python_projects

    if not recursive:
        console.print("[bold]Running prek on current project...[/bold]\n")
        result = subprocess.run(["uv", "run", "prek", "run", "--all-files"], check=False)
        raise typer.Exit(result.returncode)

    console.print(f"[bold]Running prek on all projects in:[/bold] {path}\n")
    console.print(f"[dim]Max depth: {max_depth}[/dim]\n")

    projects = find_python_projects(path, max_depth)

    if not projects:
        console.print("[yellow]No Python projects found[/yellow]")
        return

    storage = ResultStorage()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("Running prek...", total=len(projects))

        results = []
        with ProcessPoolExecutor() as executor:
            futures = {
                executor.submit(_run_command_on_repo, project, "prek"): project
                for project in projects
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    storage.save_result(result)
                    results.append(result)
                    status = "✓" if result.exit_code == 0 else "✗"
                    progress.update(task, advance=1, description=f"Running prek... {status}")
                except Exception as e:
                    project = futures[future]
                    console.print(f"[red]Error in {project.name}: {e}[/red]")
                    progress.advance(task)

    total = len(results)
    passed = sum(1 for r in results if r.exit_code == 0)
    failed = sum(1 for r in results if r.exit_code != 0)

    console.print("\n[bold]Prek Results:[/bold]")
    console.print(f"  Total checked: {total}")
    console.print(f"  [green]✓[/green] Passed: {passed}")
    if failed > 0:
        console.print(f"  [red]✗[/red] Failed: {failed}\n")

        console.print("[bold]Failed repositories:[/bold]")
        for result in results:
            if result.exit_code != 0:
                console.print(f"  [red]✗[/red] {result.repo_name} (exit {result.exit_code})")
    else:
        console.print()

    console.print(f"[dim]Results saved to {storage.status_file}[/dim]")


@app.command(name="list")
def list_projects(
    path: Path = typer.Option(Path.cwd(), help="Root directory to search for projects"),
    max_depth: int = typer.Option(
        3, "--max-depth", help="Maximum directory depth for recursive search"
    ),
) -> None:
    """List all Python projects in directory tree."""
    assert path is not None, "Path must not be None"
    assert path.exists(), f"Path {path} does not exist"

    from scaffold.core import find_python_projects

    console.print(f"[bold]Finding Python projects in:[/bold] {path}")
    console.print(f"[dim]Max depth: {max_depth}[/dim]\n")

    projects = find_python_projects(path, max_depth)

    if not projects:
        console.print("[yellow]No Python projects found[/yellow]")
        return

    console.print(f"[bold]Found {len(projects)} project(s):[/bold]\n")

    for project in projects:
        relative = project.relative_to(path) if project.is_relative_to(path) else project
        console.print(f"  • {relative}")

    console.print("\n[dim]Run 'sc test -r' or 'sc prek -r' to execute commands[/dim]")


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
                "[green]✓ PASS[/green]"
                if pytest_result.exit_code == 0
                else "[red]✗ FAIL[/red]"
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
                "[green]✓ PASS[/green]"
                if prek_result.exit_code == 0
                else "[red]✗ FAIL[/red]"
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


@app.command()
def status(
    command: str | None = typer.Option(None, help="Filter by command (pytest or prek)"),
    path: Path = typer.Option(Path.cwd(), help="Filter by repos in this directory"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed output"),
) -> None:
    """Display test/prek results for projects in current directory."""
    assert command is None or command in ["pytest", "prek"], "Command must be 'pytest' or 'prek'"
    assert isinstance(detailed, bool), "Detailed must be boolean"

    from scaffold.core import find_python_projects

    storage = ResultStorage()

    if not storage.status_file.exists():
        console.print(
            "[yellow]No results found. Run 'sc test -r' or 'sc prek -r' first.[/yellow]"
        )
        return

    projects = find_python_projects(path, max_depth=3)
    project_paths = {str(p) for p in projects}

    all_results = storage.load_results(command=command) if command else storage.load_results()

    results = [r for r in all_results if r.repo_path in project_paths]

    if not results:
        console.print(
            f"[yellow]No results found for projects in {path}[/yellow]\n"
            f"[dim]Run 'sc test -r' or 'sc prek -r' in this directory[/dim]"
        )
        return

    console.print(f"[bold]Bulk Command Results[/bold] - {path}")
    if command:
        console.print(f"[dim]Filtered by: {command}[/dim]")
    console.print(f"[dim]Total results: {len(results)}[/dim]\n")

    _print_results_by_repo(results)

    if detailed:
        _print_detailed_results(results)


if __name__ == "__main__":
    app()
