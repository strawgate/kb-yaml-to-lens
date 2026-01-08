# Kibana Dashboard Fixture Generator

Docker-based TypeScript fixture generator using Kibana's `LensConfigBuilder` API to produce known-good Kibana dashboard JSON for testing the `kb-yaml-to-lens` compiler.

## Overview

- **Authoritative**: Uses Kibana's actual config builder API, not reverse-engineering
- **Version Flexible**: Easy to regenerate fixtures for different Kibana versions
- **Zero Local Builds**: Pull pre-built base images, mount your scripts via volumes
- **Type Safe**: TypeScript with strict checking catches errors at development time

## System Requirements

| Requirement | Value |
| ------------- | ------- |
| **Docker** | Latest stable |
| **Make** | GNU Make |
| **Disk** | ~10GB (for base image) |
| **RAM** | 8GB+ recommended |

## Quick Start

```bash
cd fixture-generator

# 1. Pull pre-built base image (one time)
make pull

# 2. Generate all fixtures
make run

# 3. Copy to Python tests
cp output/v9.2.0/metric-basic-esql.json ../compiler/tests/fixtures/
```

## Available Commands

| Command | Description |
| --------- | ------------- |
| `make pull` | Pull pre-built base image from GHCR (required first step) |
| `make run` | Generate all fixtures |
| `make run-example EXAMPLE=<file>.ts` | Run a specific example script |
| `make shell` | Open a shell in the container for debugging |
| `make typecheck` | Run TypeScript type checking |
| `make test-import` | Test that @kbn/lens-embeddable-utils can be imported |
| `make build-base` | Build base image locally (for testing base image changes) |
| `make clean` | Remove generated output files |

## Project Structure

```text
fixture-generator/
├── examples/                # Example generator scripts (TypeScript)
│   ├── metric-basic.ts      # Basic metric visualization
│   ├── xy-chart.ts          # XY chart (line/bar/area)
│   ├── pie-chart.ts         # Pie/donut charts
│   ├── gauge.ts             # Gauge visualization
│   ├── heatmap.ts           # Heatmap
│   └── ...                  # Many more examples
├── generator-utils.ts       # Shared utility functions
├── generate-all.js          # Runs all examples
├── output/                  # Generated JSON files (by Kibana version)
├── Dockerfile.base          # Base image with Kibana + dependencies
└── Makefile                 # Build and run commands
```

**Note**: Most examples generate **both ES|QL and Data View variants** from a single file.

## How It Works

Each example script:

1. Imports utilities from `generator-utils.ts`
2. Creates ES|QL and Data View config objects
3. Calls `generateDualFixture()` to build both variants
4. Writes results to `output/<kibana-version>/`

### ES|QL vs Data View

**ES|QL** - Uses Elasticsearch Query Language:

```typescript
dataset: { esql: 'FROM logs-* | STATS count = COUNT()' }
```

**Data View** - Uses index patterns:

```typescript
dataset: { index: 'logs-*', timeFieldName: '@timestamp' }
```

Both generate valid Kibana Lens visualizations for testing different data source configurations.

## Creating New Fixtures

1. Create a new TypeScript file in `examples/`
2. Use the `generateDualFixture()` helper (see existing examples)
3. Run `make run-example EXAMPLE=your-file.ts`
4. Copy generated JSON to `../compiler/tests/fixtures/`

**Example**: See `examples/metric-basic.ts` for a minimal example.

**For detailed guidance**, see [FIXTURES.md](FIXTURES.md).

## Chart Types

The LensConfigBuilder supports:

- **metric** - Single value metrics with optional breakdowns
- **xy** - Line, bar, area charts
- **pie** - Pie and donut charts
- **table** - Data tables
- **gauge** - Gauge visualizations
- **heatmap** - Heatmaps
- **tagcloud** - Tag clouds
- **treemap** - Treemaps

See [Kibana's Lens documentation](https://github.com/elastic/kibana/tree/main/dev_docs/lens) for configuration options.

## Multi-Version Support

Generate fixtures for different Kibana versions:

```bash
# Pull specific version
make pull KIBANA_VERSION=v9.1.0

# Generate fixtures with that version
make run KIBANA_VERSION=v9.1.0

# Or build base image locally for a new version
make build-base KIBANA_VERSION=v9.3.0
make run KIBANA_VERSION=v9.3.0
```

Available versions: `v9.2.0` (default), `v9.1.0`

## Docker Setup

The fixture generator uses **pre-built Kibana base images** published to GitHub Container Registry:

- **Base image**: `ghcr.io/strawgate/kb-yaml-to-lens/kibana-base:v9.2.0`
- **Contents**: Kibana source + bootstrapped dependencies (~8GB)
- **Runtime**: Mount your generator scripts via Docker volumes
- **Updates**: Built weekly via GitHub Actions
- **Multi-arch**: Supports amd64 and arm64

**Using different versions**:

```bash
make pull KIBANA_VERSION=v9.1.0
make run KIBANA_VERSION=v9.1.0
```

**Building locally** (for testing base image changes):

```bash
make build-base KIBANA_VERSION=v9.2.0
```

**Adding new versions**: Edit `.github/workflows/build-kibana-base-images.yml` and add to `matrix.kibana_version`. The workflow runs weekly and can be triggered manually via GitHub Actions.

## Troubleshooting

### Docker Pull Fails

Ensure Docker is running and you have internet connectivity. Base images are publicly accessible.

### LensConfigBuilder Not Found

1. Pull the base image: `make pull`
2. Verify with `make test-import`
3. Debug with `make shell`

### Base Image Not Found for Your Version

Build locally or trigger the GitHub Actions workflow to publish it:

```bash
# Option 1: Build locally
make build-base KIBANA_VERSION=v9.2.0

# Option 2: Trigger via GitHub Actions
# Go to: Actions → Build and Publish Kibana Base Images → Run workflow
```

### Invalid Configuration

Check [Kibana's Lens config API docs](https://github.com/elastic/kibana/blob/main/dev_docs/lens/config_api.mdx) for valid options.

**For more troubleshooting and development guidance**, see [FIXTURES.md](FIXTURES.md).

## Contributing

See [FIXTURES.md](FIXTURES.md) for detailed development workflow and best practices.

## Documentation

- [Kibana Lens Config API](https://github.com/elastic/kibana/blob/main/dev_docs/lens/config_api.mdx)
- [Metric Visualizations](https://github.com/elastic/kibana/blob/main/dev_docs/lens/metric.mdx)
- [XY Charts](https://github.com/elastic/kibana/blob/main/dev_docs/lens/xy.mdx)
- [Pie Charts](https://github.com/elastic/kibana/blob/main/dev_docs/lens/pie.mdx)

## License

Same as parent project
