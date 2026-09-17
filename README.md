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
sc upgrade --dry-run # preview which files change first
sc upgrade -r        # upgrade every repo in a tree
sc adopt             # bring a repo up to standard without clobbering files
sc test -r           # run pytest across all repos (cached)
sc prek -r           # run prek across all repos (cached)
sc status            # show the latest test and prek results
```

`sc upgrade` rewrites the files scaffold owns (`.pre-commit-config.yaml`,
`zensical.toml`, CI workflow). Use `--dry-run` to preview which files change;
since they are tracked in git, review the applied changes with `git diff`.

`sc adopt` onboards a repository that was not created by scaffold. It adds any
missing standard files (including `pyproject.toml`) and never overwrites
anything that already exists. Follow it with `uv sync` and `sc upgrade`.

## Create a new project

```bash
sc init my-project
sc init my-project --dry-run
sc init my-project --llms --mcp --skill   # opt into the AI extras
```

Every project scaffold manages ships with uv, ruff, basedpyright, pytest with
unit and integration markers, prek hooks, a `src/` layout, GitHub Actions CI,
and docs. An `llms.txt`, an MCP server, and a Claude Code Agent Skill are opt-in
via `--llms`, `--mcp`, and `--skill`.

## Development

```bash
uv sync --all-extras
uv run prek run --all-files
uv run pytest
```

## Documentation

See [docs/index.md](docs/index.md) or run `sc --help`.
