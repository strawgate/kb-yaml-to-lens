# Using GHCR Images for Fixture Generation

This guide explains how to use pre-built Docker images from GitHub Container Registry (GHCR) for the Kibana fixture generator.

## Quick Start

### 1. Using Pre-Built GHCR Images (Recommended)

Pre-built images are available from GHCR and eliminate the 15-30 minute build time:

```bash
cd fixture-generator

# Use docker-compose with GHCR (no build needed)
docker-compose -f docker-compose.ghcr.yml run generator

# Generate specific fixture
docker-compose -f docker-compose.ghcr.yml run generator node examples/metric-basic.js

# Use specific Kibana version
KIBANA_VERSION=v9.3.0 docker-compose -f docker-compose.ghcr.yml run generator
```

### 2. Available Images

Images are published to: `ghcr.io/strawgate/kb-yaml-to-lens/kibana-fixture-generator`

Available tags:

- `main` - Latest development version (updated weekly)
- `latest` - Alias for `main`
- `v9.4.0`, `v9.3.0`, etc. - Specific Kibana releases

### 3. Manual Image Pull

You can also pull and use images directly:

```bash
# Pull latest image
docker pull ghcr.io/strawgate/kb-yaml-to-lens/kibana-fixture-generator:main

# Run with manual docker command
docker run -v $(pwd)/examples:/tool/examples -v $(pwd)/output:/tool/output \
  ghcr.io/strawgate/kb-yaml-to-lens/kibana-fixture-generator:main \
  node examples/metric-basic.js
```

## Building Images (For Maintainers)

### Automated Builds

Images are built automatically by GitHub Actions:

1. **Scheduled Builds**: Every Monday at 2 AM UTC, builds latest Kibana version
2. **Manual Builds**: Trigger via workflow dispatch in GitHub Actions
3. **On Changes**: When `Dockerfile.ghcr` is updated

### Manual Workflow Dispatch

To build a specific Kibana version:

1. Go to GitHub Actions → "Build Kibana Fixture Generator Image"
2. Click "Run workflow"
3. Enter Kibana version (e.g., `v9.4.0`, `main`)
4. Optionally enable "Force rebuild"
5. Click "Run workflow"

The workflow will:

- Check if image already exists (skip if found unless force rebuild enabled)
- Build Docker image with bootstrapped Kibana
- Push to GHCR
- Verify LensConfigBuilder is available
- Generate summary with usage instructions

### Local Build

If you need to build locally (e.g., for testing, custom Kibana branches):

```bash
cd fixture-generator

# Build with specific Kibana version
docker build -f Dockerfile.ghcr \
  --build-arg KIBANA_VERSION=v9.4.0 \
  --build-arg NODE_VERSION=22.21.1 \
  -t my-fixture-generator:v9.4.0 \
  .

# Run locally built image
docker run -v $(pwd)/examples:/tool/examples -v $(pwd)/output:/tool/output \
  my-fixture-generator:v9.4.0 \
  node examples/metric-basic.js
```

Or use the local-build profile in docker-compose:

```bash
# Build locally
docker-compose --profile local-build build

# Run locally built image
docker-compose --profile local-build run generator-local
```

## Architecture

### Image Contents

Each GHCR image contains:

- Ubuntu 22.04 base
- Node.js 22.21.1 (matches Kibana requirement)
- Yarn 1.22.19
- Kibana source code (specific version)
- Bootstrapped Kibana packages (~8-10GB)
- `@kbn/lens-embeddable-utils` with LensConfigBuilder API

### Benefits

1. **Fast CI/CD**: No 15-30 minute Kibana bootstrap on each run
2. **Consistent Environment**: Everyone uses the same bootstrapped Kibana
3. **Version Flexibility**: Multiple Kibana versions available as separate tags
4. **Disk Efficiency**: Image stored in GHCR, not on every developer machine
5. **Automatic Updates**: Weekly scheduled builds keep latest version fresh

### Image Size

- Full image: ~8-10GB (includes Kibana source + node_modules)
- Download time: 5-10 minutes on typical connection
- Docker caches layers, subsequent pulls much faster

## Troubleshooting

### Image Not Found

If you get "image not found" error:

1. Check available images: <https://github.com/strawgate/kb-yaml-to-lens/pkgs/container/kb-yaml-to-lens%2Fkibana-fixture-generator>
2. Ensure you're authenticated with GHCR (public read access should work)
3. Try pulling latest: `docker pull ghcr.io/strawgate/kb-yaml-to-lens/kibana-fixture-generator:latest`
4. If unavailable, trigger manual build via workflow dispatch

### Authentication Required

GHCR images are public for this repository, but if you need authentication:

```bash
# Authenticate with GitHub token
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### Specific Version Not Available

If a specific Kibana version isn't published:

1. Trigger manual workflow dispatch in GitHub Actions
2. Specify the desired Kibana version (e.g., `v8.15.3`)
3. Wait 15-30 minutes for build to complete
4. Image will be available at `ghcr.io/strawgate/kb-yaml-to-lens/kibana-fixture-generator:v8.15.3`

### Build Failures

If automated builds fail:

1. Check GitHub Actions logs for the workflow
2. Common issues:
   - Node version mismatch (update `NODE_VERSION` in workflow)
   - Kibana bootstrap failure (check Kibana compatibility)
   - Out of memory (GitHub Actions provides sufficient resources)
3. Manual workaround: Build locally and test before updating workflow

## CI/CD Integration

### Using in GitHub Actions

```yaml
jobs:
  test-fixtures:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate fixtures
        run: |
          cd fixture-generator
          docker-compose -f docker-compose.ghcr.yml run generator
      
      - name: Upload fixtures
        uses: actions/upload-artifact@v3
        with:
          name: fixtures
          path: fixture-generator/output/*.json
```

### Local Development

For development, use GHCR images to avoid long build times:

```bash
# Create alias for convenience
alias fixture-gen="docker-compose -f docker-compose.ghcr.yml run generator"

# Use it
fixture-gen node examples/metric-basic.js
```

## Maintenance

### Updating Node Version

When Kibana updates its Node requirement:

1. Update `NODE_VERSION` in `.github/workflows/build-kibana-fixture-image.yml`
2. Update `NODE_VERSION` in `fixture-generator/Dockerfile.ghcr`
3. Trigger manual workflow dispatch with `force_rebuild: true`

### Adding New Kibana Versions

New versions are added automatically via scheduled builds. To add specific version:

1. Trigger workflow dispatch
2. Specify version (e.g., `v9.5.0`)
3. Image will be available within 30 minutes

### Cleaning Up Old Images

Old images can be deleted from GHCR package settings on GitHub:

1. Go to repository → Packages → kibana-fixture-generator
2. Select versions to delete
3. Click "Delete"

Recommendation: Keep last 3-4 major versions, delete older ones.
