# CLI reference

## Configuration

Set one or more default project roots so `sc status` (and `sc upgrade -r`) search
them from anywhere, without cd-ing into your code directory. There is no config
command; create `~/.scaffold/config.json`. Each root can be a folder full of
projects, or an individual project folder:

```json
{
  "roots": [
    "/home/you/code",
    "/home/you/work/important-service",
    "/home/you/experiments/spike"
  ]
}
```

```bash
sc status            # scans every configured root from anywhere
```

Missing roots are skipped. An explicit `--path` overrides the configured roots, and `adopt` (and single-project `upgrade`) still default to the current directory. Override the config file location with the `SCAFFOLD_CONFIG` environment variable.

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

Show the last pytest/prek result for each of your projects, in a per-project table. Reads the remembered state without running anything, so you can see when tests last passed.

```
sc status [OPTIONS]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `--run` | FLAG | off | Run pytest + prek to refresh the state |
| `--force, -f` | FLAG | off | With `--run`, ignore the cache |
| `--command` | TEXT | both | Only `pytest` or `prek` |
| `--detailed, -d` | FLAG | off | Show full output |
| `--path` | PATH | config root or cwd | Repos directory to search |
| `--max-depth` | INT | 3 | Directory depth limit |

By default `sc status` reads stored results (instant). `--run` runs pytest and prek and records the results (cached by file mtime, so unchanged projects are skipped; `--force` re-runs everything). It searches the configured roots (see [Configuration](#configuration)) or the current directory.
