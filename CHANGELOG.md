# Changelog

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
