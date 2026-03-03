# Scaffold

Scaffold new Python projects with opinionated defaults via the `sc` CLI.

```bash
sc init my-project
```

## What you get

Every project created by `sc` includes:

- `uv` for dependency management
- `ruff` for linting and formatting
- `basedpyright` for type checking
- `prek` pre-commit hooks (configured and installed)
- `pytest` with unit/integration markers
- `src/` layout with proper package structure
- GitHub Actions CI

## Documentation

| Section | Purpose |
|---|---|
| [Tutorials](tutorials/index.md) | Step-by-step guides to learn scaffold |
| [How-to](how-to/index.md) | Task-focused guides for common workflows |
| [Reference](reference/index.md) | CLI commands and API reference |
| [Explanation](explanation/index.md) | Design decisions and concepts |
