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
        assert isinstance(project_type, ProjectType), "Must be ProjectType enum"

        base_templates = [
            ("base/pyproject.toml.j2", "pyproject.toml"),
            ("base/.pre-commit-config.yaml.j2", ".pre-commit-config.yaml"),
            ("base/.gitignore.j2", ".gitignore"),
            ("base/.python-version.j2", ".python-version"),
            ("base/README.md.j2", "README.md"),
        ]

        type_templates: dict[ProjectType, list[tuple[str, str]]] = {
            ProjectType.PACKAGE: [
                ("package/__init__.py.j2", "src/__package_name__/__init__.py"),
                ("package/py.typed", "src/__package_name__/py.typed"),
                ("package/tests_init.py", "tests/__init__.py"),
                ("package/docs_index.md.j2", "docs/index.md"),
            ],
            ProjectType.CLI: [
                ("cli/__init__.py.j2", "src/__package_name__/__init__.py"),
                ("cli/cli.py.j2", "src/__package_name__/cli.py"),
                ("cli/core.py.j2", "src/__package_name__/core.py"),
                ("cli/py.typed", "src/__package_name__/py.typed"),
                ("cli/tests_init.py", "tests/__init__.py"),
                ("cli/test_cli.py.j2", "tests/test_cli.py"),
            ],
            ProjectType.WEBAPP: [
                ("webapp/__init__.py.j2", "src/__package_name__/__init__.py"),
                ("webapp/main.py.j2", "src/__package_name__/main.py"),
                ("webapp/routes.py.j2", "src/__package_name__/routes.py"),
                ("webapp/py.typed", "src/__package_name__/py.typed"),
                ("webapp/base.html.j2", "src/__package_name__/templates/base.html"),
                ("webapp/tests_init.py", "tests/__init__.py"),
                ("webapp/test_main.py.j2", "tests/test_main.py"),
            ],
        }

        templates = base_templates + type_templates[project_type]
        assert len(templates) > 0, "Must have at least one template"
        return templates
