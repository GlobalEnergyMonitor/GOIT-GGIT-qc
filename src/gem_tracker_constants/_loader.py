"""YAML loaders. Run once at import time; callers see plain Python objects."""

from __future__ import annotations

from importlib import resources
from typing import Any

import yaml


def _load(filename: str) -> Any:
    pkg = resources.files(__package__) / "data" / filename
    with pkg.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


FUELS: dict[str, list[str]] = _load("fuels.yaml")
STATUSES: dict[str, Any] = _load("statuses.yaml")
