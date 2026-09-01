#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as Et
from pathlib import Path
from typing import Final, Literal, Never

# ---------------------------------------------------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------------------------------------------------
VERSION_PATTERN: Final[re.Pattern[str]] = re.compile(r"^\d+\.\d+\.\d+(-preview\.\d+)?$")
BumpPart = Literal["major", "minor", "patch", "preview"]
XML_EXTENSIONS: Final[set[str]] = {".xml", ".csproj", ".props", ".targets", ".vbproj", ".fsproj"}

# ---------------------------------------------------------------------------------------------------------------------
# Code
# ---------------------------------------------------------------------------------------------------------------------
def fail(message: str) -> Never:
    print(message)
    raise SystemExit(1)


def validate_version(version: str) -> bool:
    """
    Validate version format: major.minor.patch or major.minor.patch-preview.number.
    """
    return VERSION_PATTERN.match(version) is not None


def bump(version: str, part: BumpPart) -> str:
    """
    Bump version according to 'major', 'minor', 'patch', or 'preview'.
    Expects a format like: 0.1.0-preview.88
    """
    core: str
    preview: str | None
    core, preview = version, None
    if "-preview." in version:
        core, preview = version.split("-preview.")
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
        new_version += f"-preview.{preview}"
    return new_version


def is_xml_file(path: Path) -> bool:
    """Check if the file is an XML file based on extension."""
    return path.suffix.lower() in XML_EXTENSIONS


def read_version_from_text(path: Path) -> str:
    """Read version from a plain text file (e.g. VERSION). Returns first line trimmed."""
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        fail(f"Error: File is empty: {path}")
    return content.splitlines()[0].strip()


def write_version_to_text(path: Path, new_version: str) -> None:
    """Write a plain text file with just the version string."""
    path.write_text(new_version + "\n", encoding="utf-8")


def read_version_from_xml(path: Path, xpath: str) -> tuple[str, Et.Element]:
    """Read version from an XML file. Returns (version, element)."""
    tree = Et.parse(path)
    root = tree.getroot()
    elem = root.find(xpath)
    if elem is None or not elem.text:
        fail(f"Error: Version element '{xpath}' not found in {path}.")
    return elem.text.strip(), (tree, elem)


def write_version_to_xml(path: Path, tree: Et.ElementTree, elem: Et.Element, new_version: str) -> None:
    """Write updated version back to XML file."""
    elem.text = new_version
    tree.write(path, encoding="utf-8", xml_declaration=True)


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


def main() -> int:
    if len(sys.argv) < 3:
        fail("Usage: bump_version.py <bump> <version_file> [version_element] [custom_version]")

    part = sys.argv[1].lower()
    version_file = Path(sys.argv[2])
    version_element = sys.argv[3] if len(sys.argv) > 3 else ".//Version"

    if not version_file.exists():
        fail(f"Error: File not found: {version_file}")

    # Read current version based on file type
    use_xml = is_xml_file(version_file)
    if use_xml:
        old_version, (xml_tree, xml_elem) = read_version_from_xml(version_file, version_element)
    else:
        old_version = read_version_from_text(version_file)
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
    if use_xml:
        write_version_to_xml(version_file, xml_tree, xml_elem, new_version)
    else:
        write_version_to_text(version_file, new_version)

    print(f"Bumped version: {old_version} -> {new_version}")
    print(new_version)  # Output for GitHub Actions to capture
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
