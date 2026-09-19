import os
from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_scaffold_config(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    config_file = tmp_path_factory.mktemp("scaffold-config") / "config.json"
    previous = os.environ.get("SCAFFOLD_CONFIG")
    os.environ["SCAFFOLD_CONFIG"] = str(config_file)
    try:
        yield config_file
    finally:
        if previous is None:
            os.environ.pop("SCAFFOLD_CONFIG", None)
        else:
            os.environ["SCAFFOLD_CONFIG"] = previous
