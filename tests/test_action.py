from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import src.action as action


def set_inputs(monkeypatch: pytest.MonkeyPatch, output: Path, **values: str) -> None:
    defaults = {
        "version_file": "VERSION",
        "bump": "patch",
        "custom_version": "",
        "version_element": "",
        "additional_version_files": "",
        "commit": "false",
        "tag": "false",
        "tag_prefix": "v",
        "commit_message": "VersionBump : {tag}",
        "push": "false",
        "floating_major_version": "false",
        "floating_minor_version": "false",
        "preview_label": "preview",
        "preview_separator": ".",
    }
    defaults.update(values)
    for name, value in defaults.items():
        monkeypatch.setenv(name.upper(), value)
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setenv("GITHUB_REF_NAME", "release")


def test_commit_tags_floating_tags_and_push(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    version_file = tmp_path / "VERSION"
    version_file.write_text("1.2.3\n", encoding="utf-8")
    output = tmp_path / "output"
    set_inputs(
        monkeypatch,
        output,
        version_file=str(version_file),
        commit="true",
        tag="true",
        push="true",
        floating_major_version="true",
        floating_minor_version="true",
    )
    calls: list[list[str]] = []
    tag_created = False
    bump_calls = 0
    original_bump_file = action.bump_file

    def bump_once(*args: object, **kwargs: object) -> tuple[str, str]:
        nonlocal bump_calls
        bump_calls += 1
        return original_bump_file(*args, **kwargs)

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal tag_created
        calls.append(command)
        if command[:3] == ["git", "ls-remote", "--tags"]:
            return subprocess.CompletedProcess(command, 0, "", "")
        if command[:2] == ["git", "rev-parse"]:
            result = 0 if tag_created else 1
            return subprocess.CompletedProcess(command, result, "", "")
        if command[:3] == ["git", "diff", "--cached"]:
            return subprocess.CompletedProcess(command, 1, "", "")
        if command[:2] == ["git", "tag"] and len(command) == 3:
            tag_created = True
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(action.subprocess, "run", fake_run)
    monkeypatch.setattr(action, "bump_file", bump_once)
    assert action.main() == 0

    assert bump_calls == 1
    assert version_file.read_text(encoding="utf-8").strip() == "1.2.4"
    assert output.read_text(encoding="utf-8").splitlines() == [
        "version=1.2.4",
        "old_version=1.2.3",
        "tag=v1.2.4",
        "floating_major_tag=v1",
        "floating_minor_tag=v1.2",
    ]
    assert ["git", "commit", "-m", "VersionBump : v1.2.4"] in calls
    assert ["git", "tag", "v1.2.4"] in calls
    assert ["git", "tag", "-f", "v1"] in calls
    assert ["git", "tag", "-f", "v1.2"] in calls
    assert ["git", "push", "origin", "HEAD:refs/heads/release"] in calls
    assert ["git", "push", "origin", "v1.2.4"] in calls
    assert ["git", "push", "origin", "v1", "--force"] in calls
    assert ["git", "push", "origin", "v1.2", "--force"] in calls


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ({"bump": "custom", "custom_version": ""}, "custom_version"),
        ({"bump": "custom", "custom_version": "not-a-version"}, "Invalid version"),
        ({"tag": "false", "floating_major_version": "true"}, "require tag"),
    ],
)
def test_validation_failures_happen_before_git(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, values: dict[str, str], message: str
) -> None:
    version_file = tmp_path / "VERSION"
    version_file.write_text("1.0.0\n", encoding="utf-8")
    set_inputs(monkeypatch, tmp_path / "output", version_file=str(version_file), **values)
    monkeypatch.setattr(action.subprocess, "run", lambda *args, **kwargs: pytest.fail("Git ran"))

    with pytest.raises(SystemExit, match="1"):
        action.main()


def test_additional_file_failure_stops_before_git(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    version_file = tmp_path / "VERSION"
    additional_file = tmp_path / "additional.VERSION"
    version_file.write_text("1.0.0\n", encoding="utf-8")
    additional_file.write_text("2.0.0\n", encoding="utf-8")
    set_inputs(
        monkeypatch,
        tmp_path / "output",
        version_file=str(version_file),
        commit="true",
        tag="true",
        push="true",
        additional_version_files="additional.VERSION\nmissing.VERSION",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(action.subprocess, "run", lambda *args, **kwargs: pytest.fail("Git ran"))

    with pytest.raises(SystemExit, match="1"):
        action.main()
    assert version_file.read_text(encoding="utf-8").strip() == "1.0.1"
    assert additional_file.read_text(encoding="utf-8").strip() == "1.0.1"
