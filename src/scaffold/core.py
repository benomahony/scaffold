import subprocess
from datetime import datetime
from pathlib import Path

from scaffold.models import ProjectConfig
from scaffold.template_engine import TemplateEngine


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

        if template_path.endswith(".j2"):
            content = engine.render_template(template_path, context)
            output_file_path.write_text(content)
        else:
            template_source = engine.env.loader.get_source(engine.env, template_path)
            output_file_path.write_text(template_source[0])


def initialize_git(project_path: Path) -> None:
    assert project_path.exists(), "Project path must exist"
    assert project_path.is_dir(), "Project path must be a directory"

    subprocess.run(["git", "init"], cwd=project_path, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=project_path, check=True, capture_output=True)


def setup_project_environment(project_path: Path) -> None:
    assert project_path.exists(), "Project path must exist"
    assert project_path.is_dir(), "Project path must be a directory"

    subprocess.run(["uv", "sync"], cwd=project_path, check=True, capture_output=True)
    subprocess.run(
        ["uv", "run", "pre-commit", "install"],
        cwd=project_path,
        check=True,
        capture_output=True,
    )
