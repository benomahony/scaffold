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
sc config --root ~/code   # set a default root so -r and status work anywhere
sc check -r          # audit every repo in a directory tree
sc upgrade           # refresh scaffold managed infrastructure files
sc upgrade --dry-run # preview which files change first
sc upgrade -r        # upgrade every repo in a tree
sc adopt             # bring a repo up to standard without clobbering files
sc run pytest -r     # run pytest across all repos (cached)
sc run prek -r       # run prek across all repos (cached)
sc status            # show the latest cached results
```

`sc config --root ~/code` stores a default projects root so the tree-searching
commands (`check -r`, `run -r`, `status`) work from anywhere, without cd-ing into
your code directory. Single-project commands still default to the current
directory. Config lives at `~/.scaffold/config.json`.

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
sc init my-project --auto-update          # PR scaffold updates on a schedule
```

Every project scaffold manages ships with uv, ruff, basedpyright, pytest with
unit and integration markers, prek hooks, a `src/` layout, GitHub Actions CI,
and docs. An `llms.txt`, an MCP server, a Claude Code Agent Skill, and a
scheduled `scaffold-update` workflow are opt-in via `--llms`, `--mcp`,
`--skill`, and `--auto-update`.

With `--auto-update`, a weekly GitHub Action runs `scaffold upgrade` against the
latest scaffold and opens a PR when your infrastructure files have drifted, so
your projects stay current as scaffold evolves.

## Development

```bash
uv sync --all-extras
uv run prek run --all-files
uv run pytest
```

## Documentation

See [docs/index.md](docs/index.md) or run `sc --help`.
