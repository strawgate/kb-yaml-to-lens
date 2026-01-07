# Kibana Base Image Documentation

This document explains the pre-built Kibana base image system used by the fixture generator.

## Overview

The fixture generator uses pre-built Kibana base images with direct volume mounting:

1. **Base Image** (`Dockerfile.base`) - Contains Kibana source + bootstrap (~6 minutes to build, automated weekly)
2. **Runtime Approach** - Mount generator scripts directly into pre-built base image (no local build needed)

Base images are pre-built and published to GitHub Container Registry (GHCR) weekly, eliminating the need to bootstrap Kibana or build any local Docker images.

## Published Images

Base images are available at: `ghcr.io/strawgate/kb-yaml-to-lens/kibana-base:<version>`

### Available Versions

- `v9.2.0` - Kibana 9.2.0 (default)
- `v9.1.0` - Kibana 9.1.0

Each version is also tagged with the build date (e.g., `v9.2.0-20260107`).

## Automated Workflow

The `Build and Publish Kibana Base Images` workflow:

- **Runs**: Weekly on Mondays at 3 AM UTC
- **Builds**: Multiple Kibana versions in parallel
- **Publishes**: To GHCR with automatic versioning
- **Platforms**: Multi-arch (amd64, arm64)

### Manual Trigger

To trigger a manual build:

1. Go to **Actions** → **Build and Publish Kibana Base Images**
2. Click **Run workflow**
3. Optionally specify custom Kibana versions (comma-separated)

## Local Development

### Using Pre-built Images (Default)

```bash
# Pull the latest pre-built base image
make pull

# Generate fixtures (scripts are mounted, no local build needed)
make run
```

This pulls `ghcr.io/strawgate/kb-yaml-to-lens/kibana-base:v9.2.0` and uses it directly with volume mounts.

### Building Base Image Locally

To build the base image locally (for testing base image changes):

```bash
# Build base image
make build-base KIBANA_VERSION=v9.2.0

# Use it directly with volume mounts
make run
```

## CI/CD Integration

The base image workflow is separate from the main CI/CD pipeline. This allows:

- Weekly automated base image updates without triggering full CI runs
- Manual base image rebuilds when new Kibana versions are released
- Fast local builds using cached base images
- Consistent environment across all developers and CI

## Versioning Strategy

Base images use the following tagging scheme:

- `v9.2.0` - Latest build for Kibana 9.2.0 (mutable, updated weekly)
- `v9.2.0-20260107` - Specific build from 2026-01-07 (immutable)

The `Makefile` uses the version tag (e.g., `v9.2.0`) to always pull the latest weekly build.

## Troubleshooting

### Base Image Not Found

If the base image doesn't exist yet for your version:

```bash
# Option 1: Build base image locally
make build-base KIBANA_VERSION=v9.2.0

# Option 2: Trigger workflow to build and publish it
# (via GitHub UI: Actions → Build and Publish Kibana Base Images)
```

### Authentication Issues

To pull images from GHCR, you may need to authenticate:

```bash
# Using GitHub CLI (recommended)
gh auth token | docker login ghcr.io -u USERNAME --password-stdin

# Or using a personal access token
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

Public repositories typically allow unauthenticated pulls, but rate limits may apply.

### Cache Invalidation

GitHub Actions uses GitHub's cache for faster rebuilds. If you need to force a complete rebuild:

1. Go to **Settings** → **Actions** → **Caches**
2. Delete caches starting with `kibana-`
3. Re-run the workflow

## Maintenance

### Adding New Kibana Versions

To add support for a new Kibana version:

1. Edit `.github/workflows/build-kibana-base-images.yml`
2. Add the new version to the `matrix.kibana_version` list
3. Commit and push - the workflow will build it on the next run

Example:

```yaml
strategy:
  matrix:
    kibana_version:
      - v9.2.0
      - v9.1.0
      - v9.3.0  # New version
```

### Updating Base Image Build

If you need to modify what goes into the base image:

1. Edit `fixture-generator/Dockerfile.base`
2. Build and test locally: `make build-base && make run && make test`
3. Commit and push
4. Trigger the workflow to rebuild all base images

## Size Considerations

Base images are large (~8GB) because they contain:

- Full Kibana source code
- All node_modules after bootstrap
- Compiled .peggy grammar files
- Global npm packages (tsx, typescript, etc.)

This is expected and necessary to provide `@kbn/lens-embeddable-utils` and other internal packages.

## Security

Base images are published to the **public** GitHub Container Registry. They contain:

- ✅ Public Kibana source code (Apache 2.0 license)
- ✅ Open-source dependencies
- ❌ No secrets or credentials
- ❌ No proprietary code

Images are built from the official Elastic Kibana repository with no modifications to the source.
