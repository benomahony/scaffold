# Check project health

`sc check` validates that a project has the expected files and configuration.

## Single project

```bash
sc check
# or
sc check --path /path/to/project
```

Checks for:

- `pyproject.toml`
- `.pre-commit-config.yaml`
- `src/` directory
- `tests/` directory
- `.git/` repository
- Pre-commit hook installed

## All projects in a directory tree

```bash
sc check --recursive
sc check -r --max-depth 2
```

Prints a summary of clean/issues/error counts, then details per project.
