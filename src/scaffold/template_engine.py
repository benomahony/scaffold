from pathlib import Path

from jinja2 import Environment, PackageLoader

from scaffold.models import ProjectType


class TemplateEngine:
    def __init__(self) -> None:
        self.env = Environment(
            loader=PackageLoader("scaffold", "templates"),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        assert self.env is not None, "Jinja environment must be initialized"
        assert self.env.loader is not None, "Jinja loader must be configured"

    def render_template(self, template_path: str, context: dict) -> str:
        assert template_path is not None, "Template path must not be None"
        assert isinstance(context, dict), "Context must be a dictionary"

        template = self.env.get_template(template_path)
        return template.render(**context)

    def get_template_files(self, project_type: ProjectType) -> list[tuple[str, str]]:
        assert project_type is not None, "Project type must not be None"
        assert project_type == ProjectType.PYTHON, "Only PYTHON type supported"

        templates = [
            ("base/pyproject.toml.j2", "pyproject.toml"),
            ("base/.pre-commit-config.yaml.j2", ".pre-commit-config.yaml"),
            ("base/.gitignore.j2", ".gitignore"),
            ("base/.python-version.j2", ".python-version"),
            ("base/README.md.j2", "README.md"),
            ("base/__init__.py.j2", "src/__package_name__/__init__.py"),
            ("python/cli.py.j2", "src/__package_name__/cli.py"),
            ("python/core.py.j2", "src/__package_name__/core.py"),
            ("python/test_cli.py.j2", "tests/test_cli.py"),
            ("python/test_core.py.j2", "tests/test_core.py"),
            ("python/docs_index.md.j2", "docs/index.md"),
        ]

        assert len(templates) > 0, "Must have at least one template"
        return templates

    def get_empty_files(self) -> list[str]:
        assert self.env is not None, "Environment must be initialized"

        return [
            "src/__package_name__/py.typed",
            "tests/__init__.py",
        ]
