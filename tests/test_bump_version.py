#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import sys

import pytest

import scripts.bump_version as bv

# ---------------------------------------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------------------------------------
def test_main_no_args_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["bump_version.py"])
    with pytest.raises(SystemExit):
        bv.main()


def test_main_missing_version_file_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["bump_version.py", "patch", "/nonexistent/file.xml"])
    with pytest.raises(SystemExit):
        bv.main()
