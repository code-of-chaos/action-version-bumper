#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

from src.versioning import fail

# ---------------------------------------------------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------------------------------------------------
EXTENSIONS: Final[set[str]] = {".json"}

# ---------------------------------------------------------------------------------------------------------------------
# Code
# ---------------------------------------------------------------------------------------------------------------------
def read_version(path: Path, key: str) -> tuple[str, dict]:
    """Read version from a JSON file. Returns (version, parsed_data)."""
    content = path.read_text(encoding="utf-8")
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        fail(f"Error: Invalid JSON in {path}: {e}")
    if not isinstance(data, dict):
        fail(f"Error: JSON root in {path} must be an object.")
    version = _get_value(data, key)
    if version is None:
        fail(f"Error: Key path '{key}' not found in {path}.")
    return str(version).strip(), data


def write_version(path: Path, data: dict, key: str, new_version: str) -> None:
    """Write updated version back to JSON file."""
    parts = key.split(".")
    target: dict[str, Any] = data
    for part in parts[:-1]:
        value = target.get(part)
        if not isinstance(value, dict):
            fail(f"Error: Key path '{key}' not found in {path}.")
        target = value
    target[parts[-1]] = new_version
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _get_value(data: Any, key: str) -> Any:
    value = data
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value
