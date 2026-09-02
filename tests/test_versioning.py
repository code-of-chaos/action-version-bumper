#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import pytest

from scripts.versioning import bump, validate_version, get_major_tag

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


@pytest.mark.parametrize(
    ("version", "part", "label", "expected"),
    [
        ("1.2.3", "preview", "BETA", "1.2.3-BETA.1"),
        ("1.2.3-BETA.5", "patch", "BETA", "1.2.4-BETA.0"),
        ("1.2.3-BETA.5", "minor", "BETA", "1.3.0-BETA.0"),
        ("1.2.3-BETA.5", "major", "BETA", "2.0.0-BETA.0"),
        ("1.2.3-BETA.5", "preview", "BETA", "1.2.3-BETA.6"),
        ("1.2.3", "preview", "RC", "1.2.3-RC.1"),
        ("1.2.3-RC.2", "preview", "RC", "1.2.3-RC.3"),
    ],
)
def test_bump_with_custom_preview_label(version: str, part: str, label: str, expected: str) -> None:
    # noinspection PyTypeChecker
    assert bump(version, part, label) == expected


@pytest.mark.parametrize(
    ("version", "part", "label", "separator", "expected"),
    [
        ("1.2.3", "preview", "BETA", "-", "1.2.3-BETA-1"),
        ("1.2.3-BETA-5", "patch", "BETA", "-", "1.2.4-BETA-0"),
        ("1.2.3-BETA-5", "minor", "BETA", "-", "1.3.0-BETA-0"),
        ("1.2.3-BETA-5", "major", "BETA", "-", "2.0.0-BETA-0"),
        ("1.2.3-BETA-5", "preview", "BETA", "-", "1.2.3-BETA-6"),
        ("1.2.3", "preview", "beta", "-", "1.2.3-beta-1"),
        ("1.2.3-beta-2", "preview", "beta", "-", "1.2.3-beta-3"),
    ],
)
def test_bump_with_custom_separator(version: str, part: str, label: str, separator: str, expected: str) -> None:
    # noinspection PyTypeChecker
    assert bump(version, part, label, separator) == expected


@pytest.mark.parametrize(
    ("version", "expected"),
    [
        ("1.2.3", True),
        ("1.2.3-BETA.1", True),
        ("1.2.3-RC.1", True),
        ("1.2.3-preview.1", True),
        ("1.2.3-BETA-1", True),
        ("1.2.3-beta-1", True),
    ],
)
def test_validate_version_with_custom_label(version: str, expected: bool) -> None:
    assert validate_version(version) is expected


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
