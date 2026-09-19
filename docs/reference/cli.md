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

Create a new Python project. The new project is added to your configured roots
(unless an existing root already covers it), so `sc status` includes it from
anywhere.

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

Show the pytest/prek result for each of your projects, in a per-project table. With no flags it reruns only the repos whose files changed since their last result and reuses the cache for the rest, so the status is always current while unchanged repos stay instant.

```
sc status [OPTIONS]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `--no-cache` | FLAG | off | Regenerate: rerun pytest + prek on every repo |
| `--rerun-failed` | FLAG | off | Rerun only the repos that last failed |
| `--detailed, -d` | FLAG | off | Show full output |
| `--path` | PATH | config root or cwd | Repos directory to search |
| `--max-depth` | INT | 3 | Directory depth limit |

With no flags, `sc status` reruns only the repos whose files changed since their last recorded result (unchanged repos are served from the cache, so they are instant), keeping the status current cheaply. `--no-cache` reruns pytest and prek on every repo regardless. `--rerun-failed` reruns only the `(repo, tool)` pairs whose last recorded result failed. It searches the configured roots (see [Configuration](#configuration)) or the current directory.
