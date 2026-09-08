from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

import src.bump_version as bv


def test_one_calculated_version_applies_to_all_supported_additional_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    canonical = tmp_path / "VERSION"
    xml = tmp_path / "Directory.Build.props"
    package = tmp_path / "package.json"
    cmake = tmp_path / "CMakeLists.txt"
    canonical.write_text("1.0.0\n", encoding="utf-8")
    xml.write_text("<Project><PropertyGroup><Version>0.8.0</Version></PropertyGroup></Project>", encoding="utf-8")
    package.write_text('{"name":"app","version":"2.0.0"}', encoding="utf-8")
    cmake.write_text("project(App VERSION 3.0.0)\n", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["bump_version.py", "minor", str(canonical)])
    assert bv.main() == 0
    new_version = "1.1.0"
    for path in (xml, package, cmake):
        bv.set_version(path, new_version)

    assert canonical.read_text(encoding="utf-8").strip() == new_version
    assert new_version in xml.read_text(encoding="utf-8")
    assert json.loads(package.read_text(encoding="utf-8"))["version"] == new_version
    assert f"VERSION {new_version}" in cmake.read_text(encoding="utf-8")


def test_additional_file_missing_fails_before_write(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        bv.set_version(tmp_path / "missing.json", "1.0.1")


def test_additional_file_invalid_fails(tmp_path: Path) -> None:
    path = tmp_path / "package.json"
    path.write_text('{"version":', encoding="utf-8")

    with pytest.raises(SystemExit):
        bv.set_version(path, "1.0.1")


@pytest.mark.parametrize("path", [Path("..") / "outside.VERSION", Path("C:/outside.VERSION")])
def test_additional_file_must_be_repository_relative(path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VERSION_BUMPER_REQUIRE_RELATIVE_PATHS", "true")
    with pytest.raises(SystemExit):
        bv.set_version(path, "1.0.1")


def test_additional_file_must_be_inside_github_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside.VERSION"
    workspace.mkdir()
    outside.write_text("1.0.0\n", encoding="utf-8")
    monkeypatch.setenv("GITHUB_WORKSPACE", str(workspace))
    monkeypatch.setenv("VERSION_BUMPER_REQUIRE_RELATIVE_PATHS", "true")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit):
        bv.set_version(Path("outside.VERSION"), "1.0.1")


def test_set_version_cli_mode_updates_one_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "CMakeLists.txt"
    path.write_text("project(App VERSION 1.0.0)\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "--set-version", str(path), "1.2.3"])

    assert bv.main() == 0
    assert "VERSION 1.2.3" in path.read_text(encoding="utf-8")


def test_additional_files_receive_preview_and_custom_versions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    canonical = tmp_path / "VERSION"
    additional = tmp_path / "CMakeLists.txt"
    canonical.write_text("1.0.0\n", encoding="utf-8")
    additional.write_text("project(App VERSION 1.0.0)\n", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["bump_version.py", "preview", str(canonical)])
    assert bv.main() == 0
    bv.set_version(additional, "1.0.0-preview.1")
    assert "VERSION 1.0.0-preview.1" in additional.read_text(encoding="utf-8")

    bv.set_version(additional, "4.0.0")
    assert "VERSION 4.0.0" in additional.read_text(encoding="utf-8")
