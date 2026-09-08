# Changelog

## [2.1.0] - Unreleased

### Added

- CMakeLists.txt version bumping through `project(... VERSION ...)` declarations.
- `additional_version_files` for applying one canonical version bump across XML, JSON, CMake, and plain-text files in a single commit.
- Python-based action orchestration through `src/action.py`; `action.yml` is now a thin composite wrapper.
- Validation for custom versions and floating-tag configuration before Git operations begin.
- Unit coverage for commit, tag, floating-tag, push, validation, and multi-file failure behavior.

### Changed

- The canonical version file is bumped exactly once. Additional files receive that calculated version.
- Canonical and additional files are staged together, and additional-file failures stop before commit, tagging, or pushing.
- Action inputs are passed to Python through environment variables, avoiding unsafe shell interpolation of input values.

## [2.0.0]

### Breaking Changes

- Removed the ambiguous `floating_tag` action output.
- Use `floating_major_tag` and/or `floating_minor_tag` instead.
- Major, minor, and patch bumps from preview versions now produce stable versions without a preview suffix. Only `preview` retains or increments the preview suffix.

### Added

- JSON version bumping for files such as `package.json`.
- JSON `version` default and dot-separated nested key paths such as `metadata.version`.
- `floating_minor_version` support, including simultaneous major and minor floating tags.
- `floating_major_tag` and `floating_minor_tag` outputs.
