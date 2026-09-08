#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import re
from pathlib import Path
from typing import Final

from scripts.versioning import fail

# ---------------------------------------------------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------------------------------------------------
EXTENSIONS: Final[set[str]] = set()
PROJECT_VERSION_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\bproject\s*\([^)]*?\bVERSION\s+(?P<version>[^\s)]+)",
    re.IGNORECASE | re.DOTALL,
)

# ---------------------------------------------------------------------------------------------------------------------
# Code
# ---------------------------------------------------------------------------------------------------------------------
def is_cmake_file(path: Path) -> bool:
    return path.name.lower() == "cmakelists.txt"

def read_version(path: Path, element: str = "") -> tuple[str, tuple[str, re.Match[str]]]:
    """Read the single project VERSION value while preserving source formatting."""
    content = path.read_bytes().decode("utf-8")
    matches = list(PROJECT_VERSION_PATTERN.finditer(content))
    if not matches:
        fail(f"Error: No project(... VERSION ...) pattern found in {path}.")
    if len(matches) > 1:
        fail(f"Error: Multiple project(... VERSION ...) patterns found in {path}; unable to choose one.")
    match = matches[0]
    return match.group("version").strip(), (content, match)


def write_version(path: Path, data: tuple[str, re.Match[str]], element: str, new_version: str) -> None:
    """Replace only the matched CMake version value and preserve all other bytes."""
    content, match = data
    start, end = match.span("version")
    updated = content[:start] + new_version + content[end:]
    path.write_bytes(updated.encode("utf-8"))
