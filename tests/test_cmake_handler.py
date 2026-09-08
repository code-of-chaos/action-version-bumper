from __future__ import annotations

import sys
from pathlib import Path

import pytest

import scripts.bump_version as bv


def _write_cmake_file(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "CMakeLists.txt"
    path.write_bytes(content.encode("utf-8"))
    return path


@pytest.mark.parametrize(
    "content",
    [
        "project(InfiniFrame.Native VERSION 1.1.1 LANGUAGES CXX)\n",
        "project ( InfiniFrame.Native\n    VERSION\t1.1.1\n    LANGUAGES CXX )\n",
        "cmake_minimum_required(VERSION 3.20)\nproject(InfiniFrame.Native VERSION 1.1.1)\n",
    ],
)
def test_main_patch_bump_cmake_preserves_formatting(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, content: str) -> None:
    path = _write_cmake_file(tmp_path, content)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(path)])

    assert bv.main() == 0

    updated = path.read_bytes().decode("utf-8")
    assert updated.count("1.1.2") == 1
    assert "project(InfiniFrame.Native VERSION 1.1.1" not in updated
    if "\t" in content:
        assert "\t1.1.2" in updated


def test_main_preview_bump_cmake(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = _write_cmake_file(tmp_path, "project(InfiniFrame.Native VERSION 1.1.1)\n")
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "preview", str(path)])

    assert bv.main() == 0
    assert "VERSION 1.1.1-preview.1" in path.read_text(encoding="utf-8")


def test_main_missing_cmake_project_version_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = _write_cmake_file(tmp_path, "project(InfiniFrame.Native LANGUAGES CXX)\n")
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(path)])

    with pytest.raises(SystemExit):
        bv.main()


def test_main_ambiguous_cmake_project_versions_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    content = "project(One VERSION 1.0.0)\nproject(Two VERSION 2.0.0)\n"
    path = _write_cmake_file(tmp_path, content)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(path)])

    with pytest.raises(SystemExit):
        bv.main()


def test_cmake_preserves_crlf_line_endings(tmp_path: Path) -> None:
    path = _write_cmake_file(tmp_path, "project(One VERSION 1.0.0)\r\nset(NAME One)\r\n")

    bv.set_version(path, "1.0.1")

    assert path.read_bytes() == b"project(One VERSION 1.0.1)\r\nset(NAME One)\r\n"
