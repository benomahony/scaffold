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
| `--dry-run` | FLAG | off | Preview changes |
| `--recursive, -r` | FLAG | off | Upgrade all projects in tree |
| `--max-depth` | INT | 3 | Directory depth limit |

## sc test

Run pytest on current project or all projects.

```
sc test [OPTIONS]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `--recursive, -r` | FLAG | off | Run on all projects |
| `--force, -f` | FLAG | off | Ignore cache |
| `--path` | PATH | cwd | Root directory |
| `--max-depth` | INT | 3 | Directory depth limit |

## sc prek

Run prek on current project or all projects.

```
sc prek [OPTIONS]
```

Same options as `sc test`.

## sc list

List all Python projects in directory tree.

```
sc list [OPTIONS]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `--path` | PATH | cwd | Root directory |
| `--max-depth` | INT | 3 | Directory depth limit |

## sc status

Display cached test/prek results.

```
sc status [OPTIONS]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `--command` | TEXT | all | Filter by `pytest` or `prek` |
| `--path` | PATH | cwd | Filter by repos in directory |
| `--detailed, -d` | FLAG | off | Show full output |
