# Upgrade infrastructure files

`sc upgrade` rewrites infrastructure files to the latest scaffold templates.

## Files upgraded

- `.pre-commit-config.yaml`
- `llms.txt`
- `zensical.toml`
- `.github/workflows/ci.yml`
- `src/<package>/mcp_server.py`
- `.skills/<package>/SKILL.md`

## Single project

```bash
sc upgrade
sc upgrade --dry-run   # preview changes without writing
```

## All projects in a tree

```bash
sc upgrade --recursive
sc upgrade -r --dry-run
```
