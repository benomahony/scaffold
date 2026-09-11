# scaffold

Keep Python repos current with opinionated tooling, via the `sc` CLI.

`sc` maintains a fleet of repositories: audit their health, refresh
infrastructure files to the latest standards, adopt repos that were not
created by scaffold, and run tests or prek across everything at once. It also
creates new projects from scratch when you need one.

## Install

```bash
uv tool install git+https://github.com/benomahony/scaffold
```

## Maintain existing repos

```bash
sc check -r          # audit every repo in a directory tree
sc upgrade           # refresh scaffold managed infrastructure files
sc upgrade --diff    # review a unified diff before changes land
sc upgrade -r        # upgrade every repo in a tree
sc adopt             # bring a repo up to standard without clobbering files
sc test -r           # run pytest across all repos (cached)
sc prek -r           # run prek across all repos (cached)
sc status            # show the latest test and prek results
```

`sc upgrade` rewrites the files scaffold owns (`.pre-commit-config.yaml`,
`llms.txt`, `zensical.toml`, CI workflow, MCP server, Agent Skill). Use
`--diff` or `--dry-run` to see exactly what will change first.

`sc adopt` onboards a repository that was not created by scaffold. It adds any
missing standard files (including `pyproject.toml`) and never overwrites
anything that already exists. Follow it with `uv sync` and `sc upgrade`.

## Create a new project

```bash
sc init my-project
sc init my-project --dry-run
```

Every project scaffold manages ships with uv, ruff, basedpyright, pytest with
unit and integration markers, prek hooks, a `src/` layout, GitHub Actions CI,
docs, an MCP server, and an Agent Skill.

## Development

```bash
uv sync --all-extras
uv run prek run --all-files
uv run pytest
```

## Documentation

See [docs/index.md](docs/index.md) or run `sc --help`.
