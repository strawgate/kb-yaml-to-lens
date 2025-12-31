# Distribution Guide

This guide covers how to use, build, and publish the kb-dashboard compiler as Docker images and standalone binaries.

## Using Pre-built Artifacts

### Docker Image

The compiler is published as a multi-architecture Docker image to GitHub Container Registry.

#### Pulling the Image

```bash
docker pull ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest
```

Available tags:

- `latest` - Latest stable release
- `v1.0.0` - Specific version
- `1.0` - Major.minor version
- `1` - Major version

#### Running the Container

**Basic compilation:**

```bash
docker run --rm \
  -v $(pwd)/inputs:/inputs \
  -v $(pwd)/output:/output \
  ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest \
  compile --input-dir /inputs --output-dir /output
```

**With Kibana upload:**

```bash
docker run --rm \
  -v $(pwd)/inputs:/inputs \
  -e KIBANA_USERNAME=elastic \
  -e KIBANA_PASSWORD=changeme \
  ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest \
  compile --input-dir /inputs --upload \
  --kibana-url http://host.docker.internal:5601
```

**Notes:**

- Use `host.docker.internal` to access services running on the host machine
- Mount your input directory to `/inputs` in the container
- Mount your output directory to `/output` in the container
- Pass Kibana credentials via environment variables or CLI flags

#### Supported Platforms

- `linux/amd64` - Linux x86_64
- `linux/arm64` - Linux ARM64 (Apple Silicon, AWS Graviton, etc.)

### Standalone Binaries

Download platform-specific binaries from the [GitHub Releases](https://github.com/strawgate/kb-yaml-to-lens/releases) page.

#### Available Binaries

- **Linux x64**: `kb-dashboard-linux-x64`
- **macOS Intel**: `kb-dashboard-darwin-x64`
- **macOS Apple Silicon**: `kb-dashboard-darwin-arm64`
- **Windows x64**: `kb-dashboard-windows-x64.exe`

#### Installation

**Linux/macOS:**

```bash
# Download the binary
curl -L -o kb-dashboard https://github.com/strawgate/kb-yaml-to-lens/releases/latest/download/kb-dashboard-linux-x64

# Make it executable
chmod +x kb-dashboard

# Move to a directory in your PATH (optional)
sudo mv kb-dashboard /usr/local/bin/
```

**Windows:**

Download `kb-dashboard-windows-x64.exe` from the releases page and add it to your PATH.

#### Usage

Once installed, use it like any other CLI tool:

```bash
kb-dashboard compile --input-dir inputs --output-dir output
kb-dashboard --help
```

## Building Locally

### Building Docker Image

Build the Docker image locally:

```bash
make docker-build
```

Or use Docker directly:

```bash
docker build -t kb-dashboard-compiler:latest .
```

**Test the image:**

```bash
make docker-test
# Or
docker run --rm kb-dashboard-compiler:latest --help
```

### Building Standalone Binaries

Build a binary for your current platform:

```bash
make build-binary
```

This will:

1. Install PyInstaller
2. Bundle the Python interpreter and all dependencies
3. Create a single executable in `dist/`

**Output location:**

- Linux: `dist/kb-dashboard-linux-x64`
- macOS Intel: `dist/kb-dashboard-darwin-x64`
- macOS ARM: `dist/kb-dashboard-darwin-arm64`
- Windows: `dist/kb-dashboard-windows-x64.exe`

**Test the binary:**

```bash
./dist/kb-dashboard-* --help
```

## Publishing (Maintainers Only)

### Prerequisites

- Write access to the repository
- Docker Hub or GitHub Container Registry access
- GitHub personal access token with `packages:write` permission

### Automated Publishing via GitHub Actions

The repository includes a GitHub Actions workflow that automatically builds and publishes artifacts when you create a new release tag.

**Create and push a release tag:**

```bash
# Create a tag
git tag v1.0.0

# Push the tag
git push origin v1.0.0
```

The workflow will:

1. Build multi-architecture Docker images (amd64, arm64)
2. Publish to GitHub Container Registry
3. Build standalone binaries for all platforms (Linux, macOS, Windows)
4. Create a GitHub Release with all binaries attached

### Manual Publishing

#### Docker Image

Build and push multi-architecture images:

```bash
# Create and use a buildx builder
docker buildx create --use

# Build and push
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest \
  -t ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:v1.0.0 \
  --push \
  .
```

#### Binaries

Build binaries on each target platform:

**On Linux:**

```bash
make build-binary
```

**On macOS:**

```bash
make build-binary
```

**On Windows:**

```powershell
python build_binaries.py
```

Upload binaries to GitHub Release:

```bash
gh release create v1.0.0 \
  dist/kb-dashboard-linux-x64 \
  dist/kb-dashboard-darwin-x64 \
  dist/kb-dashboard-darwin-arm64 \
  dist/kb-dashboard-windows-x64.exe \
  --title "v1.0.0" \
  --notes "Release notes here"
```

## Troubleshooting

### Docker Issues

**Cannot connect to Kibana from container:**

- Use `host.docker.internal` instead of `localhost` to access host services
- Ensure Kibana is bound to `0.0.0.0`, not just `127.0.0.1`

**Permission denied when writing output:**

```bash
# Run with your user ID
docker run --rm --user $(id -u):$(id -g) \
  -v $(pwd)/inputs:/inputs \
  -v $(pwd)/output:/output \
  kb-dashboard-compiler:latest \
  compile --input-dir /inputs --output-dir /output
```

### Binary Issues

**Binary won't run on Linux:**

Make sure it's executable:

```bash
chmod +x kb-dashboard-linux-x64
```

**macOS security warning:**

macOS may block unsigned binaries. Allow it in System Preferences > Security & Privacy.

**Binary is too large:**

PyInstaller bundles the entire Python runtime. This is expected. Typical sizes:

- Linux: ~40-50 MB
- macOS: ~40-50 MB
- Windows: ~40-50 MB

## CI/CD Integration

### Using Docker in CI

**GitHub Actions example:**

```yaml
- name: Compile dashboards
  run: |
    docker run --rm \
      -v ${{ github.workspace }}/inputs:/inputs \
      -v ${{ github.workspace }}/output:/output \
      ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest \
      compile --input-dir /inputs --output-dir /output
```

**GitLab CI example:**

```yaml skip
compile_dashboards:
  image: ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:latest
  script:
    - kb-dashboard compile --input-dir inputs --output-dir output
  artifacts:
    paths:
      - output/
```

### Using Binaries in CI

Download and use binaries in CI pipelines:

```bash
# Download the binary
curl -L -o kb-dashboard \
  https://github.com/strawgate/kb-yaml-to-lens/releases/latest/download/kb-dashboard-linux-x64

# Make executable
chmod +x kb-dashboard

# Use it
./kb-dashboard compile --input-dir inputs --output-dir output
```

## Security Considerations

### Docker

- Images are built from official `python:3.12-slim` base
- No unnecessary packages installed
- Runs as non-root user by default
- Use specific version tags in production, not `latest`

### Binaries

- Built with PyInstaller using official Python distributions
- No external runtime dependencies required
- Verify checksums before use in production
- Keep binaries updated with security patches

## Support

For issues related to distribution:

- Docker: [GitHub Issues](https://github.com/strawgate/kb-yaml-to-lens/issues)
- Binaries: [GitHub Issues](https://github.com/strawgate/kb-yaml-to-lens/issues)
- Releases: [GitHub Releases](https://github.com/strawgate/kb-yaml-to-lens/releases)
