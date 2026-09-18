# Run tests across all projects

`sc run pytest -r` and `sc run prek -r` run pytest or prek on every Python project found in a directory tree, in parallel.

## Run pytest on all projects

```bash
sc run pytest --recursive
sc run pytest -r --path ~/Code
```

## Run prek on all projects

```bash
sc run prek --recursive
sc run prek -r --path ~/Code
```

## Force re-run (skip cache)

Results are cached by file modification time. Use `--force` to bypass the cache:

```bash
sc run pytest -r --force
```

## View cached results

```bash
sc status
sc status --command pytest
sc status --detailed
```
