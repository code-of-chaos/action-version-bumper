#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import sys
from pathlib import Path

import pytest

import scripts.bump_version as bv

# ---------------------------------------------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------------------------------------------
DIRS_XML = (
    '<?xml version="1.0" encoding="utf-8"?>'
    "<Project>"
    "  <PropertyGroup><Version>1.0.0</Version></PropertyGroup>"
    "</Project>"
)


def _write_xml_version_file(tmp_path: Path, content: str = DIRS_XML, name: str = "Directory.Build.props") -> Path:
    f = tmp_path / name
    f.write_text(content, encoding="utf-8")
    return f

# ---------------------------------------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------------------------------------
def test_main_patch_bump_xml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_xml_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(vf)])

    assert bv.main() == 0

    content = vf.read_text()
    assert "1.0.1" in content


def test_main_custom_version_xml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_xml_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "custom", str(vf), ".//Version", "5.0.0-preview.1"])

    assert bv.main() == 0

    content = vf.read_text()
    assert "5.0.0-preview.1" in content


def test_main_custom_no_version_fails_xml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_xml_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "custom", str(vf)])
    with pytest.raises(SystemExit):
        bv.main()


def test_main_custom_invalid_version_fails_xml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_xml_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "custom", str(vf), ".//Version", "not-a-version"])
    with pytest.raises(SystemExit):
        bv.main()


def test_main_unknown_part_fails_xml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_xml_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "banana", str(vf)])
    with pytest.raises(SystemExit):
        bv.main()


def test_main_no_version_element_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_xml_version_file(tmp_path, '<?xml version="1.0"?><Project><PropertyGroup></PropertyGroup></Project>')
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(vf)])
    with pytest.raises(SystemExit):
        bv.main()


def test_main_major_bump_xml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_xml_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "major", str(vf)])

    assert bv.main() == 0

    content = vf.read_text()
    assert "2.0.0" in content


def test_main_minor_bump_xml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_xml_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "minor", str(vf)])

    assert bv.main() == 0

    content = vf.read_text()
    assert "1.1.0" in content


def test_main_preview_bump_xml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_xml_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "preview", str(vf)])

    assert bv.main() == 0

    content = vf.read_text()
    assert "1.0.0-preview.1" in content


def test_main_custom_element_xpath(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    content = (
        '<?xml version="1.0" encoding="utf-8"?>'
        "<Project>"
        '  <PropertyGroup><MyVersion>2.5.0</MyVersion></PropertyGroup>'
        "</Project>"
    )
    vf = _write_xml_version_file(tmp_path, content)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(vf), ".//MyVersion"])

    assert bv.main() == 0

    result = vf.read_text()
    assert "2.5.1" in result
