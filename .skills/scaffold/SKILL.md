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

- Creates Python projects with modern tooling (uv, ruff, basedpyright, pytest, prek)
- Automatically runs: uv sync, prek install, prek run (2x for formatting)
- Generates .pre-commit-config.yaml (runs with prek for 10x speed)
- Includes GitHub Actions for CI/CD and PyPI publishing
- Generates llms.txt, zensical.toml, MCP server, and Agent Skills

## Resources

- Check docs/index.md for comprehensive documentation
- Check llms.txt for LLM-friendly documentation summary
- Check src/scaffold/ for implementation details
- Check CLEANUP.md for current cleanup checklist