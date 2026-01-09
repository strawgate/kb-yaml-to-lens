# Release Process

This document describes how to create and publish releases for kb-yaml-to-lens.

## Overview

The release process is **tag-based and fully automated**. When you push a version tag (`v*`), GitHub Actions workflows automatically:

1. Create a GitHub release with changelog
2. Build and upload CLI and LSP binaries (8 platforms total)
3. Build and publish Docker images (multi-arch)
4. Publish Python package to PyPI
5. Publish VS Code extension to marketplace

## Quick Start

To create a release:

```bash
# 1. Update version in compiler/pyproject.toml and vscode-extension/package.json
# 2. Commit and push changes
git add compiler/pyproject.toml vscode-extension/package.json
git commit -m "chore: Bump version to 1.0.0"
git push origin main

# 3. Create and push a version tag
git tag v1.0.0
git push origin v1.0.0

# 4. Wait for automated workflows to complete
# 5. Verify the release at https://github.com/strawgate/kb-yaml-to-lens/releases
```

That's it! The automation handles everything else.

## Prerequisites

Before creating a release, ensure:

- [ ] All PRs for the release are merged to `main`
- [ ] CI checks pass on `main` branch
- [ ] Version numbers are updated in:
  - `compiler/pyproject.toml` (Python package version)
  - `vscode-extension/package.json` (VS Code extension version)
- [ ] You have write access to push tags to the repository

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **Major** (v1.0.0): Breaking changes
- **Minor** (v0.1.0): New features, backward compatible
- **Patch** (v0.0.1): Bug fixes, backward compatible

### Pre-release Tags

For testing releases before official publication:

- **Release Candidate**: `v1.0.0-rc1`, `v1.0.0-rc2`
- **Alpha**: `v1.0.0-alpha1`
- **Beta**: `v1.0.0-beta1`
- **Development**: `v1.0.0-dev1`

Pre-releases are automatically detected and marked appropriately in GitHub releases.

## What Gets Released

Each release includes:

### 1. GitHub Release

**Workflow**: `.github/workflows/create-release.yml`

**Triggered by**: Version tags (`v*`)

**Contains**:

- Release notes with auto-generated changelog
- Installation instructions for all distribution methods
- Links to PyPI package and VS Code extension

### 2. Binaries (CLI + LSP)

**Workflow**: `.github/workflows/build-binaries.yml`

**Triggered by**: Version tags (`v*`)

**Platforms**:

- **CLI binaries** (4 platforms):
  - `kb-dashboard-linux-x64`
  - `kb-dashboard-darwin-x64` (macOS Intel)
  - `kb-dashboard-darwin-arm64` (macOS Apple Silicon)
  - `kb-dashboard-windows-x64.exe`

- **LSP binaries** (4 platforms):
  - `kb-dashboard-compiler-lsp-linux-x64`
  - `kb-dashboard-compiler-lsp-darwin-x64`
  - `kb-dashboard-compiler-lsp-darwin-arm64`
  - `kb-dashboard-compiler-lsp-windows-x64.exe`

All binaries are automatically attached to the GitHub release.

### 3. Docker Image

**Workflow**: `.github/workflows/docker-build-publish.yml`

**Triggered by**: Version tags (`v*`)

**Location**: `ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler`

**Architectures**: `linux/amd64`, `linux/arm64`

**Tags created**:

- `v1.0.0` (exact version)
- `v1.0` (minor version)
- `v1` (major version)
- `latest` (if released from default branch)

### 4. Python Package

**Workflow**: `.github/workflows/publish-to-pypi.yml`

**Triggered by**: GitHub release publication

**Location**: [pypi.org/project/dashboard-compiler](https://pypi.org/project/dashboard-compiler/)

**Note**: Uses PyPI Trusted Publishing (no tokens required)

### 5. VS Code Extension

**Workflow**: `.github/workflows/publish-vscode-extension.yml`

**Triggered by**: GitHub release publication

**Published to**:

- [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=strawgate.kb-dashboard-compiler)
- [Open VSX Registry](https://open-vsx.org/)

**Includes**: Platform-specific LSP binaries for all supported platforms

## Step-by-Step Release Process

### 1. Prepare the Release

```bash
# Ensure you're on the latest main branch
git checkout main
git pull origin main

# Verify all checks pass locally
make ci

# Update version numbers
# Edit compiler/pyproject.toml: version = "1.0.0"
# Edit vscode-extension/package.json: "version": "1.0.0"

# Commit version changes
git add compiler/pyproject.toml vscode-extension/package.json
git commit -m "chore: Bump version to 1.0.0"
git push origin main
```

### 2. Create and Push Tag

```bash
# Create an annotated tag
git tag -a v1.0.0 -m "Release v1.0.0"

# Or create a lightweight tag
git tag v1.0.0

# Push the tag to trigger release workflows
git push origin v1.0.0
```

**Important**: Tag names must start with `v` (e.g., `v1.0.0`, not `1.0.0`)

### 3. Monitor Workflows

Navigate to [Actions](https://github.com/strawgate/kb-yaml-to-lens/actions) and monitor:

1. **Create GitHub Release** - Should complete first (~30 seconds)
2. **Build and Publish Binaries** - Builds all 8 binaries (~5-10 minutes)
3. **Build and Publish Docker Image** - Multi-arch Docker build (~5-10 minutes)
4. **Publish to PyPI** - Waits for release, then publishes (~2 minutes)
5. **Publish VS Code Extension** - Builds LSP binaries and publishes (~10-15 minutes)

All workflows run in parallel where possible.

### 4. Verify the Release

After workflows complete, verify:

- [ ] GitHub release exists with all binaries attached: `https://github.com/strawgate/kb-yaml-to-lens/releases/tag/v1.0.0`
- [ ] Docker image is available: `docker pull ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:1.0.0`
- [ ] PyPI package is published: `https://pypi.org/project/dashboard-compiler/1.0.0/`
- [ ] VS Code extension is updated: Check marketplace version

### 5. Verify Installation

Test each distribution method:

```bash
# Test Python package
pip install dashboard-compiler==1.0.0
kb-dashboard --version

# Test Docker image
docker run ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:1.0.0 --version

# Test standalone binary (download from GitHub release)
./kb-dashboard-linux-x64 --version
```

VS Code extension will auto-update for users within 24 hours.

## Testing Pre-releases

Before cutting an official release, test with a pre-release tag:

```bash
# Create and push a release candidate
git tag v1.0.0-rc1
git push origin v1.0.0-rc1

# Verify workflows complete successfully
# Test the pre-release artifacts
# If issues found, fix and create v1.0.0-rc2

# Once satisfied, create the final release
git tag v1.0.0
git push origin v1.0.0
```

Pre-release tags are automatically marked as "Pre-release" in GitHub.

## Troubleshooting

### Workflow Failures

**If a workflow fails:**

1. Check the workflow logs in GitHub Actions
2. Fix the issue in a new commit
3. Delete and recreate the tag:

   ```bash
   git tag -d v1.0.0
   git push origin :refs/tags/v1.0.0
   git tag v1.0.0
   git push origin v1.0.0
   ```

**Common issues:**

- **Binary build failures**: Usually environment issues; check Python/UV setup

- **PyPI publish failures**: Version may already exist; increment version
- **VS Code publish failures**: Check secrets are configured correctly
- **Docker build failures**: Check Dockerfile syntax and base images

### Manual Recovery

If automated publishing fails, you can manually publish:

**Python package:**

```bash
cd compiler
uv build
uv publish  # Requires PyPI token
```

**Docker image:**

```bash
cd compiler
docker build -t ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:1.0.0 .
docker push ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:1.0.0
```

**VS Code extension:**

```bash
cd vscode-extension
make package
npx vsce publish  # Requires marketplace token
```

### Rolling Back a Release

If you need to roll back:

1. **Mark release as pre-release** in GitHub UI
2. **Publish a patch release** with the fix (preferred approach)
3. **Yank from PyPI** (last resort): `uv publish --yanked`

**Do not delete tags or releases** - this breaks user installations.

## Release Checklist

Use this checklist for each release:

- [ ] All PRs merged to `main`
- [ ] CI checks pass on `main`
- [ ] Version updated in `compiler/pyproject.toml`
- [ ] Version updated in `vscode-extension/package.json`
- [ ] Version changes committed and pushed
- [ ] Tag created and pushed (`v*` format)
- [ ] GitHub release created (automatic)
- [ ] All 8 binaries attached to release (automatic)
- [ ] Docker image published (automatic)
- [ ] PyPI package published (automatic)
- [ ] VS Code extension published (automatic)
- [ ] Release artifacts verified (manual)
- [ ] Installation tested (manual)
- [ ] Release announcement posted (optional)

## Related Documentation

- [PyPI Publishing Guide](docs/pypi-publishing.md) - Detailed PyPI setup
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development workflow
- [AGENTS.md](AGENTS.md) - CI/CD and workflow modification guidelines
