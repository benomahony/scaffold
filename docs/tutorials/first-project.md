# Your first project

This tutorial walks through creating a Python project with scaffold end-to-end.

## Prerequisites

- Python 3.12+
- `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- `git` configured with your name and email

## Install scaffold

```bash
uv tool install scaffold
```

## Create a project

```bash
sc init hello-world
```

Scaffold will:

1. Generate the project structure under `hello-world/`
2. Run `uv sync` to install dependencies
3. Install pre-commit hooks via `prek install`
4. Run `prek run --all-files` to verify everything is clean
5. Run `pytest` to confirm tests pass
6. Open your editor in the project directory

## Explore what was created

```
hello-world/
├── src/
│   └── hello_world/
│       └── __init__.py
├── tests/
│   └── __init__.py
├── pyproject.toml
├── .pre-commit-config.yaml
└── llms.txt
```

## Check project health

```bash
sc check
```

If everything is configured correctly you'll see:

```
✓ Project structure looks good!
```

## Next steps

- Read [how to upgrade infrastructure files](../how-to/upgrade-project.md)
- See the full [CLI reference](../reference/cli.md)
