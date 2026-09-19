"""Unit tests for scaffold configuration."""

from pathlib import Path

import pytest

from scaffold.config import ScaffoldConfig, load_config, resolve_roots, save_config

pytestmark = pytest.mark.unit


def test_load_config_missing_returns_default(tmp_path: Path) -> None:
    """Load returns an empty config when the file is absent."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    cfg = load_config(tmp_path / "config.json")

    assert cfg is not None, "Must return a config"
    assert cfg.roots == [], "Missing config must have no roots"


def test_save_and_load_config_round_trips(tmp_path: Path) -> None:
    """Saved roots are read back on the next load."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    config_file = tmp_path / "config.json"
    one = tmp_path / "code"
    two = tmp_path / "work" / "proj"
    one.mkdir()
    two.mkdir(parents=True)
    save_config(ScaffoldConfig(roots=[one, two]), config_file)

    assert load_config(config_file).roots == [one, two], "Roots must survive a round trip"


def test_resolve_roots_prefers_explicit_path(tmp_path: Path) -> None:
    """An explicit path wins over any configured roots."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    assert resolve_roots(tmp_path, use_config=False) == [tmp_path], "Explicit path returned as-is"


def test_resolve_roots_returns_all_configured_roots(tmp_path: Path) -> None:
    """resolve_roots returns every configured root that exists."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    config_file = tmp_path / "config.json"
    one = tmp_path / "code"
    two = tmp_path / "solo-project"
    one.mkdir()
    two.mkdir()
    gone = tmp_path / "deleted"
    save_config(ScaffoldConfig(roots=[one, two, gone]), config_file)

    resolved = resolve_roots(None, use_config=True, config_file=config_file)

    assert resolved == [one, two], "Must return existing configured roots, skipping missing ones"


def test_resolve_roots_falls_back_to_cwd(tmp_path: Path) -> None:
    """resolve_roots falls back to cwd when there are no usable roots."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    config_file = tmp_path / "config.json"
    save_config(ScaffoldConfig(roots=[]), config_file)

    assert resolve_roots(None, use_config=True, config_file=config_file) == [Path.cwd()], (
        "Empty roots must fall back to cwd"
    )
    assert resolve_roots(None, use_config=False, config_file=config_file) == [Path.cwd()], (
        "Ignoring config must fall back to cwd"
    )
