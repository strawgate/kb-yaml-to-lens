# Distribution Guide

This guide covers using, building, and publishing the kb-dashboard compiler as Docker images and standalone binaries.

## Using Pre-built Artifacts

### Docker Image

Pull from GitHub Container Registry:

```bash
docker pull ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest
```

Available tags: `latest`, `v1.0.0`, `1.0`, `1`

#### Basic usage

```bash
docker run --rm \
  -v $(pwd)/inputs:/inputs \
  -v $(pwd)/output:/output \
  ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest \
  compile --input-dir /inputs --output-dir /output
```

#### With Kibana upload

```bash
docker run --rm -v $(pwd)/inputs:/inputs \
  ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest \
  compile --input-dir /inputs --upload \
  --kibana-url http://host.docker.internal:5601 \
  --kibana-username elastic --kibana-password changeme
```

Supported platforms: `linux/amd64`, `linux/arm64`

### Standalone Binaries

Download from [GitHub Releases](https://github.com/strawgate/kb-yaml-to-lens/releases):

- **Linux x64**: `kb-dashboard-linux-x64`
- **macOS Intel**: `kb-dashboard-darwin-x64`
- **macOS Apple Silicon**: `kb-dashboard-darwin-arm64`
- **Windows x64**: `kb-dashboard-windows-x64.exe`

#### Installation (Linux/macOS)

```bash
curl -L -o kb-dashboard https://github.com/strawgate/kb-yaml-to-lens/releases/latest/download/kb-dashboard-linux-x64
chmod +x kb-dashboard
sudo mv kb-dashboard /usr/local/bin/  # Optional
```

#### Usage

```bash
kb-dashboard compile --input-dir inputs --output-dir output
```

## Building Locally

### Docker

```bash
make docker-build      # Build image
make docker-test       # Basic test (help command)
make test-docker-smoke # Comprehensive smoke tests
```

### Binaries

```bash
make build-binary      # Builds for current platform
make test-binary-smoke # Run smoke tests on binary
```

Output: `dist/kb-dashboard-{platform}-{arch}[.exe]`

## Publishing (Maintainers)

### Automated via GitHub Actions

**Prerequisites**: The GitHub Actions workflows must first be installed. See [github/README.md](../github/README.md) for installation instructions.

Create and push a version tag to trigger automated builds and publishing:

```bash
git tag v1.0.0
git push origin v1.0.0
```

This automatically:

1. **Docker**: Builds multi-arch images (amd64, arm64) and publishes to GHCR
2. **Binaries**: Builds for Linux, macOS (Intel/ARM), and Windows
3. **Testing**: Runs smoke tests on all artifacts before publishing
4. **Release**: Creates GitHub release with binaries attached

### Manual Workflow Trigger

You can also trigger builds manually via GitHub Actions UI:

- Go to Actions > "Build and Publish Docker Image" or "Build and Publish Binaries"
- Click "Run workflow"
- Specify the tag/version

### Manual Publishing

#### Docker

```bash
docker buildx create --use
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest \
  --push .
```

#### Binaries

Build on each platform with `make build-binary`, then:

```bash
gh release create v1.0.0 dist/* --title "v1.0.0" --notes "Release notes"
```

## Troubleshooting

### Docker: Cannot connect to Kibana

Use `host.docker.internal` instead of `localhost` to access host services.

### Docker: Permission denied on output

```bash
docker run --rm --user $(id -u):$(id -g) \
  -v $(pwd)/inputs:/inputs -v $(pwd)/output:/output \
  kb-dashboard-compiler:latest compile --input-dir /inputs --output-dir /output
```

### macOS: Security warning for binary

Allow in System Preferences > Security & Privacy.

## CI/CD Integration

### GitHub Actions

```yaml
- name: Compile dashboards
  run: |
    docker run --rm \
      -v ${{ github.workspace }}/inputs:/inputs \
      -v ${{ github.workspace }}/output:/output \
      ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest \
      compile --input-dir /inputs --output-dir /output
```

### Binary in CI

```bash
curl -L -o kb-dashboard https://github.com/strawgate/kb-yaml-to-lens/releases/latest/download/kb-dashboard-linux-x64
chmod +x kb-dashboard
./kb-dashboard compile --input-dir inputs --output-dir output
```
