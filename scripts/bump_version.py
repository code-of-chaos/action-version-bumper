#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Protocol

from scripts.versioning import BumpPart, bump, fail, validate_version

# ---------------------------------------------------------------------------------------------------------------------
# Handler interface
# ---------------------------------------------------------------------------------------------------------------------
class Handler(Protocol):
    EXTENSIONS: set[str]

    def read_version(self, path: Path, element: str) -> tuple[str, Any]: ...
    def write_version(self, path: Path, data: Any, element: str, new_version: str) -> None: ...

# ---------------------------------------------------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------------------------------------------------
from scripts import text_handler, xml_handler, json_handler

HANDLERS: list[Handler] = [xml_handler, json_handler, text_handler]

# ---------------------------------------------------------------------------------------------------------------------
# Code
# ---------------------------------------------------------------------------------------------------------------------
def find_handler(version_file: Path) -> Handler:
    """Find the matching handler by file extension. Text handler is the fallback."""
    suffix = version_file.suffix.lower()
    for handler in HANDLERS:
        if suffix in handler.EXTENSIONS:
            return handler
    return text_handler


def main() -> int:
    if len(sys.argv) < 3:
        fail("Usage: bump_version.py <bump> <version_file> [version_element] [custom_version]")

    part = sys.argv[1].lower()
    version_file = Path(sys.argv[2])
    version_element = sys.argv[3] if len(sys.argv) > 3 else ".//Version"

    if not version_file.exists():
        fail(f"Error: File not found: {version_file}")

    handler = find_handler(version_file)

    # Read current version
    old_version, data = handler.read_version(version_file, version_element)
    if not validate_version(old_version):
        fail(f"Error: Invalid version format '{old_version}' in {version_file}. Expected X.Y.Z or X.Y.Z-preview.N")

    # Calculate new version
    if part == "custom":
        if len(sys.argv) < 5:
            fail("Error: custom version must be provided as the 4th argument")

        new_version = sys.argv[4]
        if not validate_version(new_version):
            fail(
                f"Error: Invalid version format '{new_version}'. "
                "Expected format: X.Y.Z or X.Y.Z-preview.N"
            )
    else:
        if part not in ("major", "minor", "patch", "preview"):
            fail(f"Error: Unknown bump part '{part}'")
        new_version = bump(old_version, part)

    # Write new version
    handler.write_version(version_file, data, version_element, new_version)

    print(f"Bumped version: {old_version} -> {new_version}")
    print(new_version)  # Output for GitHub Actions to capture
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
