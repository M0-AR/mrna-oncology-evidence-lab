from pathlib import Path
from typing import Any

import yaml

from .paths import CONFIG


def load_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a mapping")
    return data


def load_config(name: str) -> dict[str, Any]:
    return load_yaml(CONFIG / name)
