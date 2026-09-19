# Check status across all projects

`sc status` runs pytest and prek on every Python project found under your root (the configured root, or the current directory), in parallel, and prints a per-project pass/fail table.

## Run across all projects

```bash
sc status
sc status --path ~/Code
```

Set a default root once so `sc status` works from anywhere (see [Configuration](../reference/cli.md#configuration)) by creating `~/.scaffold/config.json`:

```json
{ "root": "/home/you/Code" }
```

## Only one tool

```bash
sc status --command pytest
sc status --command prek
```

## Force re-run (skip cache)

Results are cached by file modification time, so unchanged projects are instant. Use `--force` to re-run everything:

```bash
sc status --force
sc status --detailed   # full output per project
```
