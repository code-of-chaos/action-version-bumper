#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import re
from typing import Final, Literal, Never

# ---------------------------------------------------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------------------------------------------------
VERSION_PATTERN: Final[re.Pattern[str]] = re.compile(r"^\d+\.\d+\.\d+(-[\w]+[.\-]\d+)?$")
BumpPart = Literal["major", "minor", "patch", "preview"]

# ---------------------------------------------------------------------------------------------------------------------
# Code
# ---------------------------------------------------------------------------------------------------------------------
def fail(message: str) -> Never:
    print(message)
    raise SystemExit(1)


def validate_version(version: str, preview_label: str = "preview", preview_separator: str = ".") -> bool:
    """
    Validate version format: major.minor.patch or major.minor.patch-label{separator}number.
    """
    return VERSION_PATTERN.match(version) is not None


def bump(version: str, part: BumpPart, preview_label: str = "preview", preview_separator: str = ".") -> str:
    """
    Bump version according to 'major', 'minor', 'patch', or 'preview'.
    Expects a format like: 0.1.0-preview.88 or 0.1.0-BETA-1
    """
    core: str
    preview: str | None
    core, preview = version, None
    suffix = f"-{preview_label}{preview_separator}"
    if suffix in version:
        core, preview = version.split(suffix, 1)
    had_preview = preview is not None

    major, minor, patch = map(int, core.split("."))

    if part == "major":
        major += 1
        minor = 0
        patch = 0
        preview = "0" if had_preview else None
    elif part == "minor":
        minor += 1
        patch = 0
        preview = "0" if had_preview else None
    elif part == "patch":
        patch += 1
        preview = "0" if had_preview else None
    elif part == "preview":
        if preview is None:
            preview = "1"
        else:
            preview = str(int(preview) + 1)
    else:
        raise ValueError(f"Unknown bump part: {part}")

    new_version = f"{major}.{minor}.{patch}"
    if preview is not None:
        new_version += f"-{preview_label}{preview_separator}{preview}"
    return new_version


def get_major_tag(tag: str, prefix: str = "v") -> str:
    """Extract the floating major version tag from a full version tag.

    Args:
        tag: The full version tag (e.g. 'v1.2.3' or 'v1.2.3-preview.1')
        prefix: The tag prefix (default: 'v')

    Returns:
        The floating major version tag (e.g. 'v1')
    """
    version = tag[len(prefix):]
    major = version.split(".")[0]
    return f"{prefix}{major}"
