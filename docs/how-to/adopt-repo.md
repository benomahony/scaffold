# Adopt an existing repository

`sc adopt` brings a repository that was not created by scaffold up to standard. It adds the missing infrastructure and standard files without overwriting anything that already exists.

## What it adds

Any of these files that are missing:

- `pyproject.toml` (name derived from the directory when absent)
- `.pre-commit-config.yaml`, `.gitignore`, `.python-version`
- `README.md`, `llms.txt`, `zensical.toml`
- `.github/workflows/ci.yml`
- `src/<package>/__init__.py`, `src/<package>/py.typed`, `tests/__init__.py`
- `src/<package>/mcp_server.py`, `.skills/<package>/SKILL.md`

Existing files are never touched.

## Usage

```bash
sc adopt
sc adopt --dry-run   # preview without writing
sc adopt --diff      # show the contents of each new file as a diff
```

After adopting, install dependencies and keep the managed files current:

```bash
uv sync
sc upgrade
```
