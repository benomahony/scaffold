# Run tests across all projects

`sc test -r` and `sc prek -r` run pytest or prek on every Python project found in a directory tree, in parallel.

## Run pytest on all projects

```bash
sc test --recursive
sc test -r --path ~/Code
```

## Run prek on all projects

```bash
sc prek --recursive
sc prek -r --path ~/Code
```

## Force re-run (skip cache)

Results are cached by file modification time. Use `--force` to bypass the cache:

```bash
sc test -r --force
```

## View results

```bash
sc status
sc status --detailed
```
