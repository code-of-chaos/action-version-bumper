#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

import scripts.bump_version as bv

# ---------------------------------------------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------------------------------------------
DIRS_JSON = '{"name": "my-package", "version": "1.0.0", "description": "A test package"}'


def _write_json_version_file(tmp_path: Path, content: str = DIRS_JSON, name: str = "package.json") -> Path:
    f = tmp_path / name
    f.write_text(content, encoding="utf-8")
    return f

# ---------------------------------------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------------------------------------
def test_main_patch_bump_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_json_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(vf), "version"])

    assert bv.main() == 0

    data = json.loads(vf.read_text(encoding="utf-8"))
    assert data["version"] == "1.0.1"


def test_main_minor_bump_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_json_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "minor", str(vf), "version"])

    assert bv.main() == 0

    data = json.loads(vf.read_text(encoding="utf-8"))
    assert data["version"] == "1.1.0"


def test_main_major_bump_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_json_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "major", str(vf), "version"])

    assert bv.main() == 0

    data = json.loads(vf.read_text(encoding="utf-8"))
    assert data["version"] == "2.0.0"


def test_main_preview_bump_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_json_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "preview", str(vf), "version"])

    assert bv.main() == 0

    data = json.loads(vf.read_text(encoding="utf-8"))
    assert data["version"] == "1.0.0-preview.1"


def test_main_custom_version_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_json_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "custom", str(vf), "version", "5.0.0-preview.1"])

    assert bv.main() == 0

    data = json.loads(vf.read_text(encoding="utf-8"))
    assert data["version"] == "5.0.0-preview.1"


def test_main_custom_key_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    content = '{"name": "my-package", "appVersion": "2.5.0", "description": "test"}'
    vf = _write_json_version_file(tmp_path, content)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(vf), "appVersion"])

    assert bv.main() == 0

    data = json.loads(vf.read_text(encoding="utf-8"))
    assert data["appVersion"] == "2.5.1"


def test_main_json_preserves_other_fields(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_json_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(vf), "version"])

    assert bv.main() == 0

    data = json.loads(vf.read_text(encoding="utf-8"))
    assert data["name"] == "my-package"
    assert data["description"] == "A test package"
    assert data["version"] == "1.0.1"


def test_main_missing_json_key_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_json_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(vf), "nonexistent"])
    with pytest.raises(SystemExit):
        bv.main()


def test_main_invalid_json_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_json_version_file(tmp_path, '{"name": "broken", "version":')
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(vf), "version"])
    with pytest.raises(SystemExit):
        bv.main()
