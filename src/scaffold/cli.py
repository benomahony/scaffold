from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from scaffold.core import create_project
from scaffold.models import ProjectConfig, ProjectType

app = typer.Typer(help="Scaffold new Python projects with opinionated defaults", no_args_is_help=True)
console = Console()


@app.command()
def new(
    project_name: str = typer.Argument(..., help="Project name"),
    project_type: ProjectType | None = typer.Option(None, "--type", "-t", help="Project type"),
    author: str | None = typer.Option(None, "--author", help="Author name"),
    email: str | None = typer.Option(None, "--email", help="Author email"),
    description: str | None = typer.Option(None, "--description", "-d", help="Project description"),
    python_version: str = typer.Option("3.12", help="Python version"),
    no_git_init: bool = typer.Option(False, help="Skip git initialization"),
) -> None:
    assert project_name is not None, "Project name must be provided"

    if project_type is None:
        project_type = typer.prompt(
            "Project type",
            type=str,
            default="package",
            show_choices=True,
        )
        project_type = ProjectType(project_type)

    if author is None:
        author = typer.prompt("Author name")

    if email is None and typer.confirm("Add author email?", default=False):
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
