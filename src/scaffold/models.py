from enum import Enum

from pydantic import BaseModel, field_validator


class ProjectType(str, Enum):
    PACKAGE = "package"
    CLI = "cli"
    WEBAPP = "webapp"


class ProjectConfig(BaseModel):
    name: str
    type: ProjectType
    author: str
    email: str | None = None
    description: str
    python_version: str = "3.12"
    license: str = "MIT"
    git_init: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        assert v is not None and len(v) > 0, "Name must not be empty"
        normalized = v.lower().replace(" ", "-")
        package_name = normalized.replace("-", "_")
        assert package_name.isidentifier(), "Name must be convertible to valid Python identifier"
        return normalized

    @field_validator("python_version")
    @classmethod
    def validate_python_version(cls, v: str) -> str:
        assert v is not None, "Python version must not be None"
        parts = v.split(".")
        assert len(parts) >= 2, "Python version must be in format X.Y"
        assert all(p.isdigit() for p in parts), "Python version parts must be numeric"
        return v

    @property
    def package_name(self) -> str:
        return self.name.replace("-", "_")
