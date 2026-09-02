#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from scripts.versioning import fail

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
    version = data.get(key)
    if version is None:
        fail(f"Error: Key '{key}' not found in {path}.")
    return str(version).strip(), data


def write_version(path: Path, data: dict, key: str, new_version: str) -> None:
    """Write updated version back to JSON file."""
    data[key] = new_version
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
