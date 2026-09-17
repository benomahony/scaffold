# Upgrade infrastructure files

`sc upgrade` rewrites infrastructure files to the latest scaffold templates.

## Files upgraded

Always refreshed:

- `.pre-commit-config.yaml`
- `zensical.toml`
- `.github/workflows/ci.yml`

Created if missing, never overwritten (you own its contents):

- `dddlint.yaml`

Refreshed only if the project already has them (the opt-in extras from
`sc init --llms/--mcp/--skill`), never added to a project that opted out:

- `llms.txt`
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
