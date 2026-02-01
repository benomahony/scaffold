"""Fast unit tests for template engine without subprocess calls."""

import pytest

from scaffold.models import ProjectType
from scaffold.template_engine import TemplateEngine

pytestmark = pytest.mark.unit


def test_template_engine_get_template_files_returns_tuples() -> None:
    """Test get_template_files returns list of tuples."""
    engine = TemplateEngine()
    assert engine is not None, "Engine must not be None"

    templates = engine.get_template_files(ProjectType.PYTHON)

    assert templates is not None, "Templates must not be None"
    assert len(templates) > 0, "Must have at least one template"
    assert all(isinstance(t, tuple) for t in templates), "All items must be tuples"
    assert all(len(t) == 2 for t in templates), "All tuples must have 2 elements"


def test_template_engine_get_template_files_includes_base() -> None:
    """Test get_template_files includes base templates."""
    engine = TemplateEngine()
    assert engine is not None, "Engine must not be None"

    templates = engine.get_template_files(ProjectType.PYTHON)

    output_files = [output for _, output in templates]

    assert "pyproject.toml" in output_files, "Must include pyproject.toml"
    assert ".pre-commit-config.yaml" in output_files, "Must include pre-commit config"
    assert ".gitignore" in output_files, "Must include gitignore"


def test_template_engine_get_template_files_includes_python_specific() -> None:
    """Test get_template_files includes Python-specific templates."""
    engine = TemplateEngine()
    assert engine is not None, "Engine must not be None"

    templates = engine.get_template_files(ProjectType.PYTHON)

    output_files = [output for _, output in templates]

    assert any("__init__.py" in f for f in output_files), "Must include __init__.py"
    assert any("cli.py" in f for f in output_files), "Must include cli.py"
    assert "README.md" in output_files, "Must include README.md"


def test_template_engine_get_empty_files_returns_list() -> None:
    """Test get_empty_files returns list of file paths."""
    engine = TemplateEngine()
    assert engine is not None, "Engine must not be None"

    empty_files = engine.get_empty_files()

    assert empty_files is not None, "Empty files list must not be None"
    assert len(empty_files) > 0, "Must have at least one empty file"
    assert all(isinstance(f, str) for f in empty_files), "All items must be strings"


def test_template_engine_get_empty_files_includes_py_typed() -> None:
    """Test get_empty_files includes py.typed."""
    engine = TemplateEngine()
    assert engine is not None, "Engine must not be None"

    empty_files = engine.get_empty_files()

    assert any("py.typed" in f for f in empty_files), "Must include py.typed"


def test_template_engine_render_template_replaces_variables() -> None:
    """Test render_template replaces template variables."""
    engine = TemplateEngine()
    assert engine is not None, "Engine must not be None"

    context = {
        "project_name": "test-project",
        "package_name": "test_project",
        "author": "Test Author",
        "email": "test@example.com",
        "description": "A test project",
        "python_version": "3.12",
        "license": "MIT",
        "year": 2024,
        "project_type": "python",
    }

    content = engine.render_template("base/pyproject.toml.j2", context)

    assert content is not None, "Content must not be None"
    assert len(content) > 0, "Content must not be empty"
    assert "test-project" in content, "Must include project name"
    assert "Test Author" in content, "Must include author"
    assert "test@example.com" in content, "Must include email"
    assert "A test project" in content, "Must include description"


def test_template_engine_render_template_handles_no_email() -> None:
    """Test render_template handles missing email."""
    engine = TemplateEngine()
    assert engine is not None, "Engine must not be None"

    context = {
        "project_name": "test-project",
        "package_name": "test_project",
        "author": "Test Author",
        "email": None,
        "description": "A test project",
        "python_version": "3.12",
        "license": "MIT",
        "year": 2024,
        "project_type": "python",
    }

    content = engine.render_template("base/pyproject.toml.j2", context)

    assert content is not None, "Content must not be None"
    assert len(content) > 0, "Content must not be empty"
    assert "Test Author" in content, "Must include author"
