# Docker and Binary Publishing Workflow Specification

This document specifies the GitHub Actions workflow needed to build and publish Docker images and standalone binaries for the kb-dashboard compiler.

## Workflow File Location

`.github/workflows/publish-compiler.yml`

## Workflow Specification

```yaml
---
name: Publish Compiler Artifacts
on:
  push:
    tags:
      - 'v*.*.*'
  workflow_dispatch:

permissions:
  contents: write
  packages: write

jobs:
  docker:
    name: Build and Publish Docker Image
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata for Docker
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}/kb-dashboard-compiler
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=semver,pattern={{major}}
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  binaries:
    name: Build Standalone Binaries
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            platform: linux
          - os: macos-latest
            platform: darwin
          - os: windows-latest
            platform: windows
    runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Install PyInstaller
        run: uv pip install pyinstaller

      - name: Build binary
        run: uv run python build_binaries.py

      - name: Upload binary artifact
        uses: actions/upload-artifact@v4
        with:
          name: kb-dashboard-${{ matrix.platform }}
          path: dist/kb-dashboard-*
          if-no-files-found: error

  release:
    name: Create GitHub Release
    needs: [docker, binaries]
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/')
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Download all artifacts
        uses: actions/download-artifact@v4
        with:
          path: artifacts

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: artifacts/**/*
          generate_release_notes: true
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Usage Instructions

### For Manual Creation

1. Create the file `.github/workflows/publish-compiler.yml`
2. Copy the workflow specification above into the file
3. Commit and push

### For Copilot Creation

Use the following prompt with @copilot:

```text
@copilot Create a new GitHub Actions workflow file at `.github/workflows/publish-compiler.yml`
with the EXACT contents from the file `DOCKER_BINARY_WORKFLOW_SPEC.md` in this repository.
Copy the YAML content from the "Workflow Specification" section between the triple backticks.
Do not modify the content - use it exactly as written.
```

## Triggering the Workflow

### Automatic Triggers

- Push a Git tag matching `v*.*.*` pattern (e.g., `v1.0.0`)

  ```bash
  git tag v1.0.0
  git push origin v1.0.0
  ```

### Manual Trigger

- Go to Actions → Publish Compiler Artifacts → Run workflow

## What Gets Published

### Docker Images

Published to GitHub Container Registry at:

- `ghcr.io/<owner>/kb-yaml-to-lens/kb-dashboard-compiler:latest`
- `ghcr.io/<owner>/kb-yaml-to-lens/kb-dashboard-compiler:v1.0.0`
- `ghcr.io/<owner>/kb-yaml-to-lens/kb-dashboard-compiler:1.0`
- `ghcr.io/<owner>/kb-yaml-to-lens/kb-dashboard-compiler:1`

Multi-architecture support: `linux/amd64`, `linux/arm64`

### Standalone Binaries

Attached to GitHub Releases:

- `kb-dashboard-linux-x64` (Linux x86_64)
- `kb-dashboard-darwin-x64` (macOS Intel)
- `kb-dashboard-darwin-arm64` (macOS Apple Silicon)
- `kb-dashboard-windows-x64.exe` (Windows x86_64)

## Testing Before Publishing

### Test Docker Build Locally

```bash
make docker-build
make docker-test
```

### Test Binary Build Locally

```bash
make build-binary
./dist/kb-dashboard-* --help
```
