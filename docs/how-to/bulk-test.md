# Check status across all projects

`sc status` shows the last pytest/prek result for every Python project found under your configured roots (or the current directory), as a per-project pass/fail table. With no flags it reads the remembered state instantly; the run flags refresh it in parallel.

## Read the remembered state

```bash
sc status
sc status --path ~/Code
```

Set your project roots once so `sc status` works from anywhere (see [Configuration](../reference/cli.md#configuration)) by creating `~/.scaffold/config.json`:

```json
{ "roots": ["/home/you/Code", "/home/you/work/service"] }
```

## Run a tool

`--test`/`--prek` run that tool and skip repos unchanged since their last run:

```bash
sc status --test          # run pytest
sc status --prek          # run prek
sc status --test --prek   # run both
```

## Rerun everything (skip cache)

`--no-cache` reruns both tools on every repo, ignoring the unchanged-repo skip:

```bash
sc status --no-cache
sc status --no-cache --detailed   # full output per project
```

## Rerun only what failed

After fixing some red repos, recheck just those:

```bash
sc status --rerun-failed
```
