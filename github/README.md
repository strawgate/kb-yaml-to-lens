# Workflow Files Pending Installation

This directory contains GitHub Actions workflow files that need to be moved to `.github/workflows/` by a maintainer.

## Why are these files here?

Claude Code's GitHub App does not have permission to create or modify workflow files in `.github/workflows/`. To work around this limitation, workflow files are created in this `github/` directory and must be manually moved by a maintainer with appropriate permissions.

## Files in this directory

### `create-release.yml`
**Purpose:** Dedicated release creator workflow that triggers on version tags (e.g., `v1.0.0`)

**What it does:**
- Triggers when a tag matching `v*` is pushed
- Generates changelog from git commits since the previous tag
- Creates a GitHub Release with:
  - Version-specific title
  - Changelog and installation instructions
  - Auto-generated release notes

**Installation:** Move this file to `.github/workflows/create-release.yml`

### `build-binaries.yml`
**Purpose:** Modified version of the existing binary build workflow that uploads artifacts to an existing release

**What changed:**
- Added new `upload-to-release` job that runs after all binaries are built
- Downloads all binary artifacts
- Uploads them to the GitHub Release created by `create-release.yml`
- Uses `allowUpdates: true` to safely add artifacts without overwriting release description

**Installation:** Replace `.github/workflows/build-binaries.yml` with this file

## Installation Instructions

1. Move `create-release.yml`:
   ```bash
   mv github/create-release.yml .github/workflows/create-release.yml
   ```

2. Replace `build-binaries.yml`:
   ```bash
   mv github/build-binaries.yml .github/workflows/build-binaries.yml
   ```

3. Delete this directory:
   ```bash
   rm -rf github/
   ```

4. Commit the changes:
   ```bash
   git add .github/workflows/create-release.yml .github/workflows/build-binaries.yml
   git rm -r github/
   git commit -m "feat: add automated release creation workflow"
   ```

## How the Release Process Works (Option A)

**Option A** uses a dedicated release creator workflow with separate jobs for artifact uploads:

1. **Tag pushed** (e.g., `v1.0.0`)
2. **`create-release.yml` triggers first**
   - Creates the GitHub Release with description and notes
3. **`build-binaries.yml` triggers in parallel**
   - Builds binaries for all platforms
   - Uploads them to the existing release using `allowUpdates: true`
4. **`docker-build-publish.yml` triggers in parallel**
   - Builds and publishes Docker images (no release upload needed)
5. **`publish-to-pypi.yml` triggers after release creation**
   - Publishes package to PyPI (triggered by `release: [published]` event)

This approach avoids race conditions by having one workflow create the release and others update it with artifacts.
