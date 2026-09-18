# CLI reference

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

## sc run

Run pytest or prek on the current project, or all projects with `-r`.

```
sc run {pytest|prek} [OPTIONS]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `--recursive, -r` | FLAG | off | Run on all projects |
| `--force, -f` | FLAG | off | Ignore cache |
| `--path` | PATH | cwd | Root directory |
| `--max-depth` | INT | 3 | Directory depth limit |

Results are cached; view them with `sc status`.

## sc status

Show cached pytest/prek results for projects in a directory.

```
sc status [OPTIONS]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `--command` | TEXT | all | Filter by `pytest` or `prek` |
| `--path` | PATH | cwd | Filter by repos in directory |
| `--detailed, -d` | FLAG | off | Show full output |
