"""Unit tests for scaffold configuration."""

from pathlib import Path

import pytest

from scaffold.config import ScaffoldConfig, load_config, resolve_root, save_config

pytestmark = pytest.mark.unit


def test_load_config_missing_returns_default(tmp_path: Path) -> None:
    """Load returns an empty config when the file is absent."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    cfg = load_config(tmp_path / "config.json")

    assert cfg is not None, "Must return a config"
    assert cfg.root is None, "Missing config must have no root"


def test_save_and_load_config_round_trips(tmp_path: Path) -> None:
    """A saved root is read back on the next load."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    config_file = tmp_path / "config.json"
    root = tmp_path / "code"
    root.mkdir()
    save_config(ScaffoldConfig(root=root), config_file)

    assert load_config(config_file).root == root, "Root must survive a round trip"


def test_resolve_root_prefers_explicit_path(tmp_path: Path) -> None:
    """An explicit path wins over any configured root."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    assert resolve_root(tmp_path, use_config=False) == tmp_path, "Explicit path returned as-is"


def test_resolve_root_uses_config_when_enabled(tmp_path: Path) -> None:
    """resolve_root falls back to the configured root when enabled."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    config_file = tmp_path / "config.json"
    root = tmp_path / "code"
    root.mkdir()
    save_config(ScaffoldConfig(root=root), config_file)

    resolved = resolve_root(None, use_config=True, config_file=config_file)

    assert resolved == root, "Must use the configured root when use_config is set"


def test_resolve_root_ignores_config_when_disabled(tmp_path: Path) -> None:
    """resolve_root falls back to cwd, not config, when disabled."""
    assert tmp_path is not None, "Temp path must not be None"
    assert tmp_path.exists(), "Temp path must exist"

    config_file = tmp_path / "config.json"
    save_config(ScaffoldConfig(root=tmp_path / "code"), config_file)

    resolved = resolve_root(None, use_config=False, config_file=config_file)

    assert resolved == Path.cwd(), "Single-repo ops must default to cwd"
