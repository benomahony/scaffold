# Create a project

```bash
sc init <project-name> [OPTIONS]
```

## Options

| Option | Default | Description |
|---|---|---|
| `--author` | git config `user.name` | Author name |
| `--email` | git config `user.email` | Author email |
| `--description` | `"Python project: <name>"` | Project description |
| `--python` | `3.12` | Python version |
| `--no-git` | off | Skip `git init` |
| `--dry-run` | off | Preview files without creating |

## Preview before creating

```bash
sc init my-project --dry-run
```

Prints the files that would be created without touching the filesystem.

## Skip git initialisation

```bash
sc init my-project --no-git
```
