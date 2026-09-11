# Scaffold

Keep Python repos current with opinionated tooling via the `sc` CLI.

`sc` maintains a fleet of repos: check their health, refresh infrastructure files to the latest standards, adopt repos that were not created by scaffold, and run tests or prek across everything at once. It also creates new projects from scratch when you need one.

```bash
sc check -r          # audit every repo in a tree
sc upgrade --diff    # review infrastructure changes before they land
sc adopt             # bring an existing repo up to standard
sc init my-project   # start a new project
```

## What you get

Every project scaffold manages includes:

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
