import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from scaffold.core import create_project, preview_project
from scaffold.models import ProjectConfig, ProjectType

app = typer.Typer(help="Scaffold new Python projects with opinionated defaults", no_args_is_help=True)
console = Console()


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


@app.command()
def new(
    project_name: str = typer.Argument(..., help="Project name"),
    author: str | None = typer.Option(None, "--author", help="Author name"),
    email: str | None = typer.Option(None, "--email", help="Author email"),
    description: str | None = typer.Option(None, "--description", "-d", help="Project description"),
    python_version: str = typer.Option("3.12", help="Python version"),
    no_git_init: bool = typer.Option(False, help="Skip git initialization"),
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
def list_templates() -> None:
    assert console is not None, "Console must be initialized"
    assert len(list(ProjectType)) > 0, "Must have at least one project type"

    console.print("[bold]Available project templates:[/bold]\n")
    for template_type in ProjectType:
        console.print(f"  [cyan]{template_type.value:8}[/cyan] - {template_type.description}")


if __name__ == "__main__":
    app()
