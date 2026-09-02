#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from scripts.bump_version import bump, validate_version, get_major_tag
import scripts.bump_version as bv

# ---------------------------------------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("version", "expected"),
    [
        ("1.2.3", True),
        ("1.2.3-preview.1", True),
        ("1.2", False),
        ("1.2.3-preview", False),
        ("v1.2.3", False),
    ],
)
def test_validate_version(version: str, expected: bool) -> None:
    assert validate_version(version) is expected


@pytest.mark.parametrize(
    ("version", "part", "expected"),
    [
        ("1.2.3", "patch", "1.2.4"),
        ("1.2.3", "minor", "1.3.0"),
        ("1.2.3", "major", "2.0.0"),
        ("1.2.3", "preview", "1.2.3-preview.1"),
        ("1.2.3-preview.5", "patch", "1.2.4-preview.0"),
        ("1.2.3-preview.5", "minor", "1.3.0-preview.0"),
        ("1.2.3-preview.5", "major", "2.0.0-preview.0"),
        ("1.2.3-preview.5", "preview", "1.2.3-preview.6"),
    ],
)
def test_bump(version: str, part: str, expected: str) -> None:
    # noinspection PyTypeChecker
    assert bump(version, part) == expected


def test_bump_unknown_part_raises_value_error() -> None:
    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        bump("1.2.3", "banana")


# ---------------------------------------------------------------------------------------------------------------------
# XML tests
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


def test_main_no_args_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["bump_version.py"])
    with pytest.raises(SystemExit):
        bv.main()


def test_main_missing_version_file_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", "/nonexistent/file.xml"])
    with pytest.raises(SystemExit):
        bv.main()


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


# ---------------------------------------------------------------------------------------------------------------------
# VERSION (plain text) tests
# ---------------------------------------------------------------------------------------------------------------------
def _write_text_version_file(tmp_path: Path, version: str = "1.0.0", name: str = "VERSION") -> Path:
    f = tmp_path / name
    f.write_text(version + "\n", encoding="utf-8")
    return f


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


# ---------------------------------------------------------------------------------------------------------------------
# JSON (package.json) tests
# ---------------------------------------------------------------------------------------------------------------------
DIRS_JSON = '{"name": "my-package", "version": "1.0.0", "description": "A test package"}'


def _write_json_version_file(tmp_path: Path, content: str = DIRS_JSON, name: str = "package.json") -> Path:
    f = tmp_path / name
    f.write_text(content, encoding="utf-8")
    return f


def test_main_patch_bump_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_json_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(vf), "version"])

    assert bv.main() == 0

    import json
    data = json.loads(vf.read_text(encoding="utf-8"))
    assert data["version"] == "1.0.1"


def test_main_minor_bump_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_json_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "minor", str(vf), "version"])

    assert bv.main() == 0

    import json
    data = json.loads(vf.read_text(encoding="utf-8"))
    assert data["version"] == "1.1.0"


def test_main_major_bump_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_json_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "major", str(vf), "version"])

    assert bv.main() == 0

    import json
    data = json.loads(vf.read_text(encoding="utf-8"))
    assert data["version"] == "2.0.0"


def test_main_preview_bump_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_json_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "preview", str(vf), "version"])

    assert bv.main() == 0

    import json
    data = json.loads(vf.read_text(encoding="utf-8"))
    assert data["version"] == "1.0.0-preview.1"


def test_main_custom_version_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_json_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "custom", str(vf), "version", "5.0.0-preview.1"])

    assert bv.main() == 0

    import json
    data = json.loads(vf.read_text(encoding="utf-8"))
    assert data["version"] == "5.0.0-preview.1"


def test_main_custom_key_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    content = '{"name": "my-package", "appVersion": "2.5.0", "description": "test"}'
    vf = _write_json_version_file(tmp_path, content)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(vf), "appVersion"])

    assert bv.main() == 0

    import json
    data = json.loads(vf.read_text(encoding="utf-8"))
    assert data["appVersion"] == "2.5.1"


def test_main_json_preserves_other_fields(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vf = _write_json_version_file(tmp_path)
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", str(vf), "version"])

    assert bv.main() == 0

    import json
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


# ---------------------------------------------------------------------------------------------------------------------
# Floating version tests
# ---------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("tag", "prefix", "expected"),
    [
        ("v1.2.3", "v", "v1"),
        ("v2.0.0", "v", "v2"),
        ("v10.20.30", "v", "v10"),
        ("v1.2.3-preview.1", "v", "v1"),
        ("v0.1.0", "v", "v0"),
        ("release-1.2.3", "release-", "release-1"),
        ("1.2.3", "", "1"),
    ],
)
def test_get_major_tag(tag: str, prefix: str, expected: str) -> None:
    assert get_major_tag(tag, prefix) == expected
