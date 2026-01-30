import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from scaffold.core import create_project, preview_project
from scaffold.models import ProjectConfig, ProjectType

__version__ = "0.1.0"

app = typer.Typer(
    help="""Scaffold new Python projects with opinionated defaults.

Examples:
  sc init my-project                    Create new project
  sc init my-project --dry-run          Preview before creating
  sc check                              Check project health
  sc upgrade                            Update infrastructure files
""",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()


def version_callback(value: bool) -> None:
    assert isinstance(value, bool), "Value must be boolean"

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
    version: bool = typer.Option(
        False, "--version", "-v", callback=version_callback, is_eager=True, help="Show version"
    ),
) -> None:
    """Scaffold CLI - Create Python projects with opinionated defaults."""
    pass


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
    assert project_name is not None, "Project name must be provided"

    project_type = ProjectType.PYTHON

    if author is None:
        git_author = _get_git_config("user.name")
        if git_author:
            author = typer.prompt("Author name", default=git_author)
        else:
            author = typer.prompt("Author name")

    if email is None:
        git_email = _get_git_config("user.email")
        if git_email:
            if typer.confirm(f"Use email {git_email}?", default=True):
                email = git_email
        else:
            if typer.confirm("Add author email?", default=False):
                email = typer.prompt("Author email")

    if description is None:
        default_description = f"Python project: {project_name}"
        if typer.confirm(f"Use default description: '{default_description}'?", default=True):
            description = default_description
        else:
            description = typer.prompt("Project description")

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

        console.print(f"\n[dim]Run without --dry-run to create the project[/dim]")
        return

    assert not output_path.exists(), f"Directory {output_path} already exists"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating project structure...", total=None)

        try:
            create_project(config, output_path.resolve())
            progress.update(task, description="[green]✓[/green] Project created successfully!")
        except Exception as e:
            progress.update(task, description=f"[red]✗[/red] Failed: {e}")
            raise

    console.print(f"\n[green]✨ Project created at {output_path}[/green]")
    console.print("\nNext steps:")
    console.print(f"  cd {project_name}")
    console.print("  uv sync")
    console.print("  uv run pre-commit run --all-files")


@app.command()
def check(path: Path = typer.Option(Path.cwd(), help="Project path to check")) -> None:
    """Check project structure and configuration."""
    assert path is not None, "Path must not be None"
    assert path.exists(), f"Path {path} does not exist"

    from scaffold.core import check_project

    console.print(f"[bold]Checking project at:[/bold] {path}\n")

    issues = check_project(path)

    if not issues:
        console.print("[green]✓ Project structure looks good![/green]")
        return

    console.print(f"[yellow]Found {len(issues)} issue(s):[/yellow]\n")
    for issue in issues:
        console.print(f"  [red]✗[/red] {issue}")

    console.print("\n[dim]Run 'scaffold upgrade' to fix infrastructure files[/dim]")


@app.command()
def upgrade(
    path: Path = typer.Option(Path.cwd(), help="Project path to upgrade"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without applying"),
) -> None:
    """Upgrade project infrastructure files to latest standards."""
    assert path is not None, "Path must not be None"
    assert path.exists(), f"Path {path} does not exist"

    from scaffold.core import upgrade_project

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


if __name__ == "__main__":
    app()
