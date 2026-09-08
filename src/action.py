#!/usr/bin/env python3
"""GitHub Action orchestration for version bumps."""
# ---------------------------------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import os
import subprocess
from pathlib import Path

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.bump_version import bump_file, set_version
from src.versioning import fail, validate_version

# ---------------------------------------------------------------------------------------------------------------------
# Code
# ---------------------------------------------------------------------------------------------------------------------
def input_value(name: str, default: str = "") -> str:
    return os.environ.get(name.upper(), default)


def enabled(name: str) -> bool:
    return input_value(name).lower() == "true"


def git(*args: str, check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], check=check, text=True, capture_output=capture_output)


def write_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        fail("Error: GITHUB_OUTPUT is not set")
    with open(output_path, "a", encoding="utf-8", newline="") as output:
        output.write(f"{name}={value}\n")


def additional_files(value: str) -> list[Path]:
    lines = (line.rstrip("\r") for line in value.splitlines())
    return [Path(line) for line in lines if line]


def remote_tag_exists(tag: str) -> bool:
    result = git("ls-remote", "--tags", "origin", tag, check=False, capture_output=True)
    return any(line.split("\t")[-1] == f"refs/tags/{tag}" for line in result.stdout.splitlines())


def local_tag_exists(tag: str) -> bool:
    return git("rev-parse", tag, check=False, capture_output=True).returncode == 0


def main() -> int:
    bump = input_value("bump").lower()
    version_file = Path(input_value("version_file"))
    custom_version = input_value("custom_version")
    preview_label = input_value("preview_label", "preview")
    preview_separator = input_value("preview_separator", ".")
    tag_prefix = input_value("tag_prefix", "v")
    tag_enabled = enabled("tag")
    floating_major = enabled("floating_major_version")
    floating_minor = enabled("floating_minor_version")

    if bump == "custom" and not custom_version:
        fail("Error: custom_version is required when bump is 'custom'")
    if bump == "custom" and not validate_version(custom_version, preview_label, preview_separator):
        fail(f"Error: Invalid version format '{custom_version}'.")
    if (floating_major or floating_minor) and not tag_enabled:
        fail("Error: floating version tags require tag to be true")

    old_version, new_version = bump_file(
        bump,
        version_file,
        input_value("version_element"),
        custom_version,
        preview_label,
        preview_separator,
    )
    tag = f"{tag_prefix}{new_version}"
    files = [version_file, *additional_files(input_value("additional_version_files"))]

    # Apply every file before touching Git, so a bad additional file cannot leave Git state behind.
    for path in files[1:]:
        set_version(path, new_version)

    floating_major_tag = ""
    floating_minor_tag = ""
    if tag_enabled:
        version_without_prefix = tag[len(tag_prefix) :]
        if floating_major:
            floating_major_tag = f"{tag_prefix}{version_without_prefix.split('.')[0]}"
        if floating_minor:
            floating_minor_tag = f"{tag_prefix}{version_without_prefix.rsplit('.', 1)[0]}"

    write_output("version", new_version)
    write_output("old_version", old_version)
    write_output("tag", tag)
    write_output("floating_major_tag", floating_major_tag)
    write_output("floating_minor_tag", floating_minor_tag)

    if not (enabled("commit") or tag_enabled or enabled("push")):
        return 0

    git("config", "user.name", "github-actions[bot]")
    git("config", "user.email", "github-actions[bot]@users.noreply.github.com")

    if enabled("commit"):
        git("add", "--", *(str(path) for path in files))
        if git("diff", "--cached", "--quiet", check=False).returncode != 0:
            message = input_value("commit_message", "VersionBump : {tag}")
            message = message.replace("{version}", new_version).replace("{tag}", tag)
            git("commit", "-m", message)
        else:
            print("No version file changes detected; skipping commit.")

    if tag_enabled:
        if remote_tag_exists(tag):
            print(f"Tag {tag} already exists on origin; skipping tag.")
        elif not local_tag_exists(tag):
            git("tag", tag)
        for floating_tag in (floating_major_tag, floating_minor_tag):
            if floating_tag:
                git("tag", "-f", floating_tag)

    if enabled("push"):
        ref_name = os.environ.get("GITHUB_REF_NAME", "")
        git("push", "origin", f"HEAD:refs/heads/{ref_name}")
        if tag_enabled and local_tag_exists(tag):
            git("push", "origin", tag)
        for floating_tag in (floating_major_tag, floating_minor_tag):
            if floating_tag:
                git("push", "origin", floating_tag, "--force")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
