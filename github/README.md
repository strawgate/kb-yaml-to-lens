# Workflow Files for Maintainers

This directory contains GitHub Actions workflow files that need to be moved to `.github/workflows/` by a maintainer or Copilot.

## Files

- `docker-build-publish.yml` - Builds and publishes multi-arch Docker images to GHCR
- `build-binaries.yml` - Builds platform-specific binaries and creates GitHub releases

## Why are they here?

Claude cannot modify workflow files in `.github/workflows/` due to GitHub App permissions. The GitHub API rejects pushes that create or update workflow files without the `workflows` permission.

## How to Install

### Option 1: Manual Move

```bash
# Move workflow files to the correct location
mv github/docker-build-publish.yml .github/workflows/
mv github/build-binaries.yml .github/workflows/

# Remove this directory
rm -rf github/

# Commit the changes
git add .github/workflows/
git commit -m "Add Docker and binary build workflows"
git push
```

### Option 2: Ask Copilot

Tag @copilot in a PR comment:

```text
@copilot please move the workflow files from github/ to .github/workflows/ and delete the github/ directory
```

## Workflow Details

### docker-build-publish.yml

- **Triggers**: On version tags (`v*`) or manual workflow dispatch
- **Platforms**: linux/amd64, linux/arm64
- **Registry**: GitHub Container Registry (ghcr.io)
- **Testing**: Runs smoke tests after publishing
- **Tags**: Semantic versioning (e.g., v1.0.0, 1.0, 1, latest)

### build-binaries.yml

- **Triggers**: On version tags (`v*`) or manual workflow dispatch
- **Platforms**:
  - Linux x64 (ubuntu-latest)
  - macOS Intel (macos-13)
  - macOS ARM (macos-latest)
  - Windows x64 (windows-latest)
- **Testing**: Runs smoke tests on each platform before upload
- **Release**: Creates GitHub release with all binaries on version tags

## Testing

Both workflows include smoke tests to ensure the artifacts work correctly before publishing.

Local testing:

```bash
# Test Docker image
make docker-build
make test-docker-smoke

# Test binary
make build-binary
make test-binary-smoke
```
