# Version Bumper

A reusable GitHub Action for bumping semantic versions in project files. Supports both XML files (`.csproj`, `Directory.Build.props`, etc.) and plain text files (`VERSION`, `.version`, etc.).

## How It Works

1. Reads the current version from the specified file
2. Bumps the version according to the selected bump type
3. Writes the updated version back to the file
4. Optionally commits, tags, and pushes the change

The action auto-detects file type based on extension:
- **XML files** (`.xml`, `.csproj`, `.props`, `.targets`, `.vbproj`, `.fsproj`): Reads/writes using XPath
- **Everything else** (`.version`, `.txt`, no extension): Reads/writes as plain text

## Inputs

### Required

| Input          | Description                                                                                                            |
|----------------|------------------------------------------------------------------------------------------------------------------------|
| `version_file` | Path to the file containing the version, relative to the repository root (e.g. `src/Directory.Build.props`, `VERSION`) |
| `bump`         | Version bump type. One of: `major`, `minor`, `patch`, `preview`, or `custom`                                           |

### Optional

| Input                    | Description                                                                                                    | Default               |
|--------------------------|----------------------------------------------------------------------------------------------------------------|-----------------------|
| `custom_version`         | Exact version string to set. Only used when `bump` is `custom`. Must match format `X.Y.Z` or `X.Y.Z-preview.N` | `''`                  |
| `version_element`        | XPath expression to locate the version element in XML files. Ignored for plain text files                      | `.//Version`          |
| `commit`                 | Whether to commit the version change to the current branch                                                     | `false`               |
| `tag`                    | Whether to create a git tag in the format `{tag_prefix}{version}`                                              | `false`               |
| `tag_prefix`             | Prefix for the git tag. The tag will be `{tag_prefix}{version}`                                                | `v`                   |
| `commit_message`         | Template for the commit message. Supports `{version}` and `{tag}` placeholders                                 | `VersionBump : {tag}` |
| `push`                   | Whether to push the commit and tag to the remote origin                                                        | `false`               |
| `floating_major_version` | Create/update a floating major version tag (e.g. `v1` for `v1.2.0`). Requires `tag` to be `true`.              | `false`               |

## Outputs

| Output         | Description                                                                  | Example  |
|----------------|------------------------------------------------------------------------------|----------|
| `version`      | The new version string after bumping                                         | `1.2.0`  |
| `old_version`  | The previous version string before bumping                                   | `1.1.3`  |
| `tag`          | The full git tag name (prefix + version)                                     | `v1.2.0` |
| `floating_tag` | The floating major version tag name (if `floating_major_version` is enabled) | `v1`     |

## Version Format

The action supports semantic versioning with an optional preview suffix:

- **Stable**: `X.Y.Z` (e.g. `1.2.3`)
- **Preview**: `X.Y.Z-preview.N` (e.g. `1.2.3-preview.1`)

## Bump Rules

| Bump Type | From    | To                | Description                                            |
|-----------|---------|-------------------|--------------------------------------------------------|
| `major`   | `1.2.3` | `2.0.0`           | Increments major, resets minor and patch to 0          |
| `minor`   | `1.2.3` | `1.3.0`           | Increments minor, resets patch to 0                    |
| `patch`   | `1.2.3` | `1.2.4`           | Increments patch by 1                                  |
| `preview` | `1.2.3` | `1.2.3-preview.1` | Adds preview suffix (or increments if already preview) |
| `custom`  | `1.2.3` | (user-specified)  | Sets to the exact version provided in `custom_version` |

### Preview Bump Behavior

When bumping a version that already has a preview suffix:

| Bump Type | From              | To                | Description                      |
|-----------|-------------------|-------------------|----------------------------------|
| `major`   | `1.2.3-preview.5` | `2.0.0-preview.0` | Bumps major, resets preview to 0 |
| `minor`   | `1.2.3-preview.5` | `1.3.0-preview.0` | Bumps minor, resets preview to 0 |
| `patch`   | `1.2.3-preview.5` | `1.2.4-preview.0` | Bumps patch, resets preview to 0 |
| `preview` | `1.2.3-preview.5` | `1.2.3-preview.6` | Increments preview number by 1   |

## Examples

### VERSION file (plain text)

```yaml
- uses: Code-Of-Chaos/action-version-bumper@v1
  with:
    version_file: VERSION
    bump: minor
```

Given a `VERSION` file containing `1.0.0`, this produces `1.1.0`.

### Directory.Build.props (XML)

```yaml
- uses: Code-Of-Chaos/action-version-bumper@v1
  with:
    version_file: src/Directory.Build.props
    bump: minor
```

### Bump, commit, tag, and push

```yaml
- uses: Code-Of-Chaos/action-version-bumper@v1
  with:
    version_file: VERSION
    bump: minor
    commit: 'true'
    tag: 'true'
    push: 'true'
```

### Set a custom version

```yaml
- uses: Code-Of-Chaos/action-version-bumper@v1
  with:
    version_file: VERSION
    bump: custom
    custom_version: 2.0.0-preview.1
    commit: 'true'
    tag: 'true'
```

### Custom XML element

If your version is stored in a non-standard element:

```yaml
- uses: Code-Of-Chaos/action-version-bumper@v1
  with:
    version_file: src/MyProject.csproj
    bump: patch
    version_element: './/PackageVersion'
```

### Custom tag prefix

```yaml
- uses: Code-Of-Chaos/action-version-bumper@v1
  with:
    version_file: VERSION
    bump: patch
    tag: 'true'
    tag_prefix: 'release-'
```

This creates tags like `release-1.2.3` instead of `v1.2.3`.

### Custom commit message

```yaml
- uses: Code-Of-Chaos/action-version-bumper@v1
  with:
    version_file: VERSION
    bump: patch
    commit: 'true'
    commit_message: 'chore: bump version to {version}'
```

### Floating major version tag

Automatically maintain a floating major version tag (e.g. `v1`) that always points to the latest `v1.x.x` release:

```yaml
- uses: Code-Of-Chaos/action-version-bumper@v1
  with:
    version_file: VERSION
    bump: minor
    commit: 'true'
    tag: 'true'
    push: 'true'
    floating_major_version: 'true'
```

When releasing `v1.2.0`, this also updates `v1` to point to the same commit. Users can then reference `@v1` in their workflows to always get the latest `v1.x.x` release.

### Use outputs in downstream steps

```yaml
- name: Bump version
  id: version
  uses: Code-Of-Chaos/action-version-bumper@v1
  with:
    version_file: VERSION
    bump: minor
    commit: 'true'
    tag: 'true'
    push: 'true'

- name: Create GitHub Release
  uses: softprops/action-gh-release@v2
  with:
    tag_name: ${{ steps.version.outputs.tag }}
    name: Release ${{ steps.version.outputs.version }}
```

### Full release workflow

```yaml
name: Release
on:
  workflow_dispatch:
    inputs:
      bump:
        description: 'Version bump type'
        required: true
        type: choice
        options:
          - major
          - minor
          - patch
          - preview

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.RELEASE_TOKEN }}

      - name: Bump version
        id: version
        uses: Code-Of-Chaos/action-version-bumper@v1
        with:
          version_file: VERSION
          bump: ${{ inputs.bump }}
          commit: 'true'
          tag: 'true'
          push: 'true'
          floating_major_version: 'true'

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ steps.version.outputs.tag }}
          name: Release ${{ steps.version.outputs.version }}
          generate_release_notes: true
```

## Standalone Usage

The Python script can be used directly without the GitHub Action:

```bash
# Bump patch in a VERSION file
python scripts/bump_version.py patch VERSION

# Bump minor in an XML file
python scripts/bump_version.py minor src/Directory.Build.props

# Set a custom version with custom xpath
python scripts/bump_version.py custom src/Directory.Build.props .//Version 2.0.0-preview.1

# Bump using a custom xpath element
python scripts/bump_version.py patch src/MyProject.csproj .//PackageVersion
```

### CLI Arguments

```
bump_version.py <bump> <version_file> [version_element] [custom_version]
```

| Argument          | Description                                                          |
|-------------------|----------------------------------------------------------------------|
| `bump`            | Bump type: `major`, `minor`, `patch`, `preview`, or `custom`         |
| `version_file`    | Path to the file containing the version                              |
| `version_element` | XPath to the version element (XML files only, default: `.//Version`) |
| `custom_version`  | Version string when bump type is `custom`                            |

## File Type Detection

The action uses file extension to determine how to read/write the version:

| Extension                                                     | Mode        | Example Files                               |
|---------------------------------------------------------------|-------------|---------------------------------------------|
| `.xml`, `.csproj`, `.props`, `.targets`, `.vbproj`, `.fsproj` | XML (XPath) | `Directory.Build.props`, `MyProject.csproj` |
| Anything else                                                 | Plain text  | `VERSION`, `.version`, `version.txt`        |

For plain text files, the file must contain only the version string (with optional trailing newline).

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## License

MIT
