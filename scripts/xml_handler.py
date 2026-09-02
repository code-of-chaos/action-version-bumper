#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import xml.etree.ElementTree as Et
from pathlib import Path
from typing import Final

from scripts.versioning import fail

# ---------------------------------------------------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------------------------------------------------
EXTENSIONS: Final[set[str]] = {".xml", ".csproj", ".props", ".targets", ".vbproj", ".fsproj"}

# ---------------------------------------------------------------------------------------------------------------------
# Code
# ---------------------------------------------------------------------------------------------------------------------
def read_version(path: Path, xpath: str) -> tuple[str, tuple[Et.ElementTree, Et.Element]]:
    """Read version from an XML file. Returns (version, (tree, element))."""
    tree = Et.parse(path)
    root = tree.getroot()
    elem = root.find(xpath)
    if elem is None or not elem.text:
        fail(f"Error: Version element '{xpath}' not found in {path}.")
    return elem.text.strip(), (tree, elem)


def write_version(path: Path, data: tuple[Et.ElementTree, Et.Element], xpath: str, new_version: str) -> None:
    """Write updated version back to XML file."""
    tree, elem = data
    elem.text = new_version
    tree.write(path, encoding="utf-8", xml_declaration=True)
