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
sc upgrade --dry-run   # preview which files change without writing
```

Because the upgraded files are tracked in git, review the applied changes with
`git diff` and revert any you want to keep with `git checkout`.

## All projects in a tree

```bash
sc upgrade --recursive
sc upgrade -r --dry-run
```
