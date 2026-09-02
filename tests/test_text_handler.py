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
def _write_text_version_file(tmp_path: Path, version: str = "1.0.0", name: str = "VERSION") -> Path:
    f = tmp_path / name
    f.write_text(version + "\n", encoding="utf-8")
    return f

# ---------------------------------------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------------------------------------
def test_main_patch_bump_version_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_text_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(vf)])

    assert bv.main() == 0

    assert vf.read_text().strip() == "1.0.1"


def test_main_minor_bump_version_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_text_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "minor", str(vf)])

    assert bv.main() == 0

    assert vf.read_text().strip() == "1.1.0"


def test_main_major_bump_version_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_text_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "major", str(vf)])

    assert bv.main() == 0

    assert vf.read_text().strip() == "2.0.0"


def test_main_preview_bump_version_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_text_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "preview", str(vf)])

    assert bv.main() == 0

    assert vf.read_text().strip() == "1.0.0-preview.1"


def test_main_preview_increment_version_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_text_version_file(tmp_path, "1.0.0-preview.3")
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "preview", str(vf)])

    assert bv.main() == 0

    assert vf.read_text().strip() == "1.0.0-preview.4"


def test_main_custom_version_version_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_text_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "custom", str(vf), "", "2.0.0-preview.1"])

    assert bv.main() == 0

    assert vf.read_text().strip() == "2.0.0-preview.1"


def test_main_empty_version_file_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_text_version_file(tmp_path, "")
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(vf)])
    with pytest.raises(SystemExit):
        bv.main()


def test_main_invalid_version_in_text_file_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_text_version_file(tmp_path, "not-a-version")
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(vf)])
    with pytest.raises(SystemExit):
        bv.main()


def test_main_version_file_with_trailing_newline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_text_version_file(tmp_path, "1.0.0\n")
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(vf)])

    assert bv.main() == 0

    assert vf.read_text().strip() == "1.0.1"
