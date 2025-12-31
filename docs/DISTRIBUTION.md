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
make docker-build  # Build image
make docker-test   # Test image
```

### Binaries

```bash
make build-binary  # Builds for current platform
```

Output: `dist/kb-dashboard-{platform}-{arch}[.exe]`

## Publishing (Maintainers)

### Automated via GitHub Actions

Create and push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

This triggers the workflow to:

1. Build multi-arch Docker images
2. Publish to GitHub Container Registry
3. Build binaries for all platforms
4. Create GitHub Release with binaries

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
