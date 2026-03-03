# Design decisions

## Why `uv`?

`uv` is the fastest Python package manager available and has a clean, reproducible lockfile format. Scaffold uses `uv` exclusively — no pip, no poetry, no pipenv.

## Why `src/` layout?

The `src/` layout prevents accidental imports from the project root during development and ensures installed packages behave identically to the source. It is now the recommended layout for Python packaging.

## Why `prek` over `pre-commit`?

`prek` is a `pre-commit` wrapper that integrates cleanly with `uv run`. It surfaces the same hooks but with a simpler interface and better error messages.

## Why atomic commits?

Scaffold enforces a 100-line commit limit via `atomic-commit-guard.sh`. Small, focused commits:

- Are easier to review
- Are easier to revert
- Make `git bisect` effective
- Produce a meaningful project history

## Why NASA05 assertions?

Every function must have at least two non-redundant assertions. This follows NASA's safety-critical coding standard and catches bugs at the earliest possible point with clear, descriptive failure messages.

## Why no mocks?

Tests use real implementations and dependency injection instead of `unittest.mock`. Mocks couple tests to implementation details and often pass when the real code would fail. `pydantic-ai`'s `TestModel` provides structured fake LLM responses without mocking.
