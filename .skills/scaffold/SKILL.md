---
name: scaffold
description: Python project scaffolding tool that creates opinionated Python projects with modern tooling (uv, ruff, basedpyright, pytest, prek, GitHub Actions, docs, MCP servers, and Agent Skills). Use when working on the scaffold codebase, adding features, fixing bugs, or understanding how scaffold generates projects.
---

# scaffold Skill

This skill helps you work with scaffold.

## When to Use This Skill

Use this skill when:

- User asks about scaffold features or capabilities
- User wants to use scaffold in their code
- User needs help with scaffold API or CLI
- User wants examples of scaffold usage

## Project Information

- **Description**: Scaffold new Python projects with opinionated defaults
- **Author**: Ben O'Mahony
- **Documentation**: See docs/index.md for full documentation
- **Source**: src/scaffold/

## Quick Reference

### CLI Usage

```bash
scaffold --help
```

### Library Usage

```python
from scaffold.core import example_function

result = example_function("World")
```

## Key Features

- Maintains existing repos: `sc check`, `sc upgrade`, `sc adopt`
- `sc config --root <path>` sets a default root so `-r`/`status` work from anywhere
- `sc upgrade --dry-run` previews which files change; review applied changes with git
- `sc adopt` onboards repos not created by scaffold, never clobbering existing files
- `sc status` runs pytest + prek across many repos (cached) and shows a pass/fail table
- Creates new projects with modern tooling (uv, ruff, basedpyright, pytest, prek)
- Generates GitHub Actions CI and zensical.toml docs
- llms.txt, MCP server, and Agent Skill are opt-in via `sc init --llms/--mcp/--skill`

## Resources

- Check docs/index.md for comprehensive documentation
- Check src/scaffold/ for implementation details
