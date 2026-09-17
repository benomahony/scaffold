# Adopt an existing repository

`sc adopt` brings a repository that was not created by scaffold up to standard. It adds the missing infrastructure and standard files without overwriting anything that already exists.

## What it adds

Any of these files that are missing:

- `pyproject.toml` (name derived from the directory when absent)
- `.pre-commit-config.yaml`, `.gitignore`, `.python-version`
- `README.md`, `zensical.toml`, `dddlint.yaml`
- `.github/workflows/ci.yml`
- `src/<package>/__init__.py`, `src/<package>/py.typed`, `tests/__init__.py`

Adopt stays lean: the opt-in extras (`llms.txt`, MCP server, Agent Skill) are
not added. Existing files are never touched.

## Usage

```bash
sc adopt
sc adopt --dry-run   # preview which files would be created
```

After adopting, install dependencies and keep the managed files current:

```bash
uv sync
sc upgrade
```
