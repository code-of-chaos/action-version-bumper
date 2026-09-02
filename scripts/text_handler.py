#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import Final

from scripts.versioning import fail

# ---------------------------------------------------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------------------------------------------------
EXTENSIONS: Final[set[str]] = set()

# ---------------------------------------------------------------------------------------------------------------------
# Code
# ---------------------------------------------------------------------------------------------------------------------
def read_version(path: Path, element: str) -> tuple[str, None]:
    """Read version from a plain text file (e.g. VERSION). Returns first line trimmed."""
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        fail(f"Error: File is empty: {path}")
    return content.splitlines()[0].strip(), None


def write_version(path: Path, data: None, element: str, new_version: str) -> None:
    """Write a plain text file with just the version string."""
    path.write_text(new_version + "\n", encoding="utf-8")
