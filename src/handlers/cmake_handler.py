#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import re
from pathlib import Path
from typing import Final

from src.versioning import fail

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


def _mask_comments(content: str) -> str:
    """Replace line comments with spaces while preserving offsets and line endings."""
    masked = list(content)
    in_quote = False
    escaped = False
    index = 0
    while index < len(content):
        char = content[index]
        if char == '"' and not escaped:
            in_quote = not in_quote
        if char == "#" and not in_quote:
            bracket = re.match(r"#(\[=*)\[", content[index:])
            if bracket:
                delimiter = "]" + "=" * (len(bracket.group(1)) - 1) + "]"
                end = content.find(delimiter, index + len(bracket.group(0)))
                end = len(content) if end == -1 else end + len(delimiter)
                for comment_index in range(index, end):
                    if content[comment_index] not in "\r\n":
                        masked[comment_index] = " "
                index = end
                escaped = False
                continue
            while index < len(content) and content[index] not in "\r\n":
                masked[index] = " "
                index += 1
            continue
        escaped = char == "\\" and not escaped
        if char != "\\":
            escaped = False
        index += 1
    return "".join(masked)


def read_version(path: Path, element: str = "") -> tuple[str, tuple[str, re.Match[str]]]:
    """Read the single project VERSION value while preserving source formatting."""
    content = path.read_bytes().decode("utf-8")
    matches = list(PROJECT_VERSION_PATTERN.finditer(_mask_comments(content)))
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
