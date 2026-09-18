# CLI reference

## sc config

Show or set scaffold configuration. With no options, prints the current config.

```
sc config [OPTIONS]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `--root` | PATH | unset | Set a default projects root |
| `--clear` | FLAG | off | Clear the configured root |

Set a root so the tree-searching commands (`check -r`, `run -r`, `status`) work from anywhere without cd-ing into your code directory:

```bash
sc config --root ~/code
sc status            # now scans ~/code from anywhere
```

Single-project commands (`check`, `upgrade`, `adopt` without `-r`) still default to the current directory. Config lives at `~/.scaffold/config.json`; override the location with the `SCAFFOLD_CONFIG` environment variable.

## sc init

Create a new Python project.

```
sc init PROJECT_NAME [OPTIONS]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `--author, -a` | TEXT | git user.name | Author name |
| `--email, -e` | TEXT | git user.email | Author email |
| `--description, -d` | TEXT | auto | Project description |
| `--python, -p` | TEXT | `3.12` | Python version |
| `--no-git` | FLAG | off | Skip git init |
| `--llms` | FLAG | off | Include an llms.txt file |
| `--mcp` | FLAG | off | Include an MCP server |
| `--skill` | FLAG | off | Include a Claude Code Agent Skill |
| `--auto-update` | FLAG | off | Include a scheduled workflow that PRs scaffold updates |
| `--dry-run` | FLAG | off | Preview only |

## sc check

Check project structure and configuration.

```
sc check [OPTIONS]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `--path` | PATH | cwd | Project path |
| `--recursive, -r` | FLAG | off | Check all projects in tree |
| `--max-depth` | INT | 3 | Directory depth limit |

## sc upgrade

Upgrade infrastructure files to latest templates.

```
sc upgrade [OPTIONS]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `--path` | PATH | cwd | Project path |
| `--dry-run` | FLAG | off | Preview which files change |
| `--recursive, -r` | FLAG | off | Upgrade all projects in tree |
| `--max-depth` | INT | 3 | Directory depth limit |

Review the applied changes with `git diff`.

## sc adopt

Bring an existing repository up to scaffold standards. Adds missing files without overwriting anything that already exists, even if the repo was not created by scaffold.

```
sc adopt [OPTIONS]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `--path` | PATH | cwd | Repository path |
| `--dry-run` | FLAG | off | Preview without writing |

## sc status

Run pytest and prek across your projects (cached) and show their status in a per-project table.

```
sc status [OPTIONS]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `--command` | TEXT | both | Only `pytest` or `prek` |
| `--force, -f` | FLAG | off | Re-run, ignore cache |
| `--detailed, -d` | FLAG | off | Show full output |
| `--path` | PATH | config root or cwd | Repos directory to search |
| `--max-depth` | INT | 3 | Directory depth limit |

Results are cached by file mtime, so unchanged projects are instant; `--force` re-runs everything. The search root defaults to the configured root (see `sc config`) or the current directory.
