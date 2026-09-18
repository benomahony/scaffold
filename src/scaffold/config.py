import os
from pathlib import Path

from pydantic import BaseModel

_DEFAULT_CONFIG = Path.home() / ".scaffold" / "config.json"
_CONFIG_FILE = Path(os.environ.get("SCAFFOLD_CONFIG", _DEFAULT_CONFIG))


class ScaffoldConfig(BaseModel):
    root: Path | None = None


def load_config(config_file: Path | None = None) -> ScaffoldConfig:
    target = config_file or _CONFIG_FILE
    assert target is not None, "Config target must be set"
    assert target.suffix == ".json", "Config must be a json file"

    if not target.exists():
        return ScaffoldConfig()
    return ScaffoldConfig.model_validate_json(target.read_text())


def save_config(config: ScaffoldConfig, config_file: Path | None = None) -> None:
    target = config_file or _CONFIG_FILE
    assert config is not None, "Config must not be None"
    assert target.suffix == ".json", "Config must be a json file"

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(config.model_dump_json(indent=2))


def resolve_root(path: Path | None, use_config: bool, config_file: Path | None = None) -> Path:
    assert use_config in (True, False), "use_config must be a boolean"

    if path is not None:
        assert path.exists(), f"Path {path} does not exist"
        return path

    root = load_config(config_file).root if use_config else None
    if root is not None:
        assert root.exists(), f"Configured root {root} does not exist"
        return root
    return Path.cwd()
