# Kibana Dashboard Fixture Generator

A simple helper tool for generating Kibana dashboard JSON fixtures using Kibana's `LensConfigBuilder` API. These fixtures are used as test data for the `kb-yaml-to-lens` Python compiler.

## Purpose

Generate **known-good** Kibana dashboard JSON by:

1. Using Kibana's **LensConfigBuilder API** directly in JavaScript
2. Building visualizations programmatically with the config builder
3. Exporting JSON fixtures for Python test suite validation
4. Supporting multiple Kibana versions for compatibility testing

## Why This Approach?

- **Authoritative**: Uses Kibana's actual config builder API, not reverse-engineering
- **Simple**: Just JavaScript files that call the API and export JSON
- **Version Flexible**: Easy to regenerate fixtures for different Kibana versions
- **Direct**: No TypeScript compilation, no complex tooling—just Node.js scripts

## System Requirements

| Requirement | Value |
| ------------- | ------- |
| **Docker** | Latest stable |
| **Make** | GNU Make |
| **Disk** | 25GB+ (Kibana source + node_modules) |
| **RAM** | 8GB+ recommended |

## Quick Start

### 1. Pull the Pre-built Base Image

```bash
cd fixture-generator
make pull
```

**Note**: This pulls the pre-built Kibana base image from GitHub Container Registry. No local Docker build required!

### 2. Generate Fixtures

```bash
# Generate all fixtures
make run

# Generate specific fixture
make run-example EXAMPLE=metric-basic.js
make run-example EXAMPLE=xy-chart.js
```

### 3. Copy to Python Tests

```bash
# Fixtures are written to ./output/
cp output/metric-basic.json ../tests/fixtures/
```

## Available Commands

Run `make help` to see all commands:

| Command | Description |
| --------- | ------------- |
| `make pull` | Pull pre-built base image from GHCR (required first step) |
| `make run` | Generate all fixtures |
| `make run-example EXAMPLE=<file>` | Run a specific example script |
| `make shell` | Open a shell in the container for debugging |
| `make test-import` | Test that @kbn/lens-embeddable-utils can be imported |
| `make build-base` | Build base image locally (for testing base image changes) |
| `make clean` | Remove generated output files |

## Project Structure

```text
fixture-generator/
├── examples/                    # Example generator scripts
│   ├── metric-basic.js         # Basic metric (ES|QL only)
│   ├── metric-with-breakdown.js # Metric with breakdown (ES|QL only)
│   ├── metric-with-trend.js    # Metric with trend (dual: ES|QL + Data View)
│   ├── metric-grid.js          # Metric grid (dual: ES|QL + Data View)
│   ├── xy-chart.js             # XY chart (ES|QL only)
│   ├── xy-chart-stacked-bar.js # Stacked bar (dual: ES|QL + Data View)
│   ├── xy-chart-dual-axis.js   # Dual-axis (dual: ES|QL + Data View)
│   ├── xy-chart-multi-layer.js # Multi-layer (dual: ES|QL + Data View)
│   ├── xy-chart-advanced-legend.js # Advanced legend config (dual)
│   ├── xy-chart-custom-colors.js # Custom color palette (dual)
│   ├── pie-chart.js            # Pie chart (ES|QL only)
│   ├── pie-chart-donut.js      # Donut chart (dual: ES|QL + Data View)
│   ├── pie-chart-advanced-colors.js # Advanced colors (dual)
│   ├── datatable-advanced.js   # Advanced datatable (dual: ES|QL + Data View)
│   ├── gauge.js                # Gauge chart (dual: ES|QL + Data View)
│   ├── treemap.js              # Treemap (dual: ES|QL + Data View)
│   ├── waffle.js               # Waffle chart (dual: ES|QL + Data View)
│   └── heatmap.js              # Heatmap (ES|QL only)
├── generator-utils.js          # Shared utility functions
├── generate-all.js             # Runs all examples
├── output/                     # Generated JSON files
├── Dockerfile
├── Makefile
└── package.json
```

**Note**: Most examples now generate **both ES|QL and Data View variants** from a single file, reducing duplication and ensuring consistency.

## How It Works

Each example script:

1. Imports `LensConfigBuilder` from Kibana's package
2. Creates a config object defining the visualization
3. Calls `builder.build(config, options)` to generate the Lens attributes
4. Writes the result as JSON to the output directory

### ES|QL vs Data View Examples

The fixture generator includes two types of examples:

**ES|QL Examples** - Use Elasticsearch Query Language for data retrieval:

```javascript
dataset: {
  esql: 'FROM logs-* | STATS count = COUNT()'
}
```

**Data View Examples** - Use standard Kibana data views with index patterns:

```javascript
dataset: {
  index: 'logs-*',
  timeFieldName: '@timestamp'  // optional
}
```

Both approaches generate valid Kibana Lens visualizations, providing test coverage for different data source configurations in the Python compiler.

### Example Script

```javascript
// examples/metric-basic.js
const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generateMetricBasic() {
  // Initialize builder
  const builder = new LensConfigBuilder();

  // Define visualization config
  const config = {
    chartType: 'metric',
    title: 'Basic Count Metric',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT()'
    },
    value: 'count',
    label: 'Total Events'
  };

  // Build the Lens attributes
  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-24h', to: 'now', type: 'relative' }
  });

  // Write to output
  const outputPath = path.join(__dirname, '..', 'output', 'metric-basic.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));
  console.log('✓ Generated: metric-basic.json');
}

generateMetricBasic();
```

## Creating New Fixtures

1. **Create a new script** in `examples/` directory
2. **Use LensConfigBuilder** to define your visualization
3. **Run the script** via Make
4. **Copy the JSON** to your test suite

### Example Workflow

```bash
# 1. Create new example script
cat > examples/my-custom-metric.js << 'EOF'
const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generateCustomMetric() {
  const builder = new LensConfigBuilder();

  const config = {
    chartType: 'metric',
    title: 'Custom Metric',
    dataset: { esql: 'FROM my-index | STATS avg = AVG(my_field)' },
    value: 'avg'
  };

  const result = await builder.build(config);
  fs.writeFileSync(
    path.join(__dirname, '..', 'output', 'my-custom-metric.json'),
    JSON.stringify(result, null, 2)
  );
}

generateCustomMetric();
EOF

# 2. Run the generator
make run-example EXAMPLE=my-custom-metric.js

# 3. Copy to Python tests
cp output/my-custom-metric.json ../tests/fixtures/
```

## Chart Types

The LensConfigBuilder supports these chart types:

- **metric** - Single value metrics, with optional secondary metrics and breakdowns
- **xy** - Line, bar, area charts with time series or categorical data
- **pie** - Pie and donut charts
- **table** - Data tables
- **gauge** - Gauge visualizations
- **heatmap** - Heatmap visualizations
- **tagcloud** - Tag cloud visualizations
- **treemap** - Treemap visualizations
- **mosaic** - Mosaic visualizations
- **regionmap** - Region map visualizations

See [Kibana's Lens documentation](https://github.com/elastic/kibana/tree/main/dev_docs/lens) for configuration options.

## Multi-Version Support

To generate fixtures for different Kibana versions:

```bash
# Build for specific Kibana version
make build KIBANA_VERSION=v8.15.0

# Or directly with docker
docker build --build-arg KIBANA_VERSION=v8.15.0 -t kibana-fixture-generator:v8.15.0 .

# Generate with specific version
docker run --rm \
  -v $(pwd)/output:/kibana/output \
  kibana-fixture-generator:v8.15.0 \
  node examples/metric-basic.js
```

## Docker Setup

The project uses pre-built Kibana base images with direct volume mounting:

**Base Image (`Dockerfile.base`)**

1. Installs Node.js 22.x (matches Kibana requirement)
2. Clones and bootstraps Kibana (making `@kbn/*` packages available)
3. Published weekly to GitHub Container Registry
4. Build time: ~6 minutes (one-time, automated via GitHub Actions)

**Runtime Approach**

Instead of building a local Docker image, fixture generation uses `docker run` with volume mounts:

1. Pull the pre-built base image from GHCR (one-time operation)
2. Mount generator scripts directly into the container
3. Execute fixture generation without any local builds

This approach eliminates all local Docker builds - just pull and run!

### Base Image Updates

Base images are automatically rebuilt weekly via GitHub Actions workflow. To trigger a manual rebuild or build a custom version:

```bash
# Trigger workflow manually via GitHub UI:
# Actions → Build and Publish Kibana Base Images → Run workflow

# Or build locally for testing:
make build-base KIBANA_VERSION=v9.2.0

# Push to GHCR (requires authentication):
docker push ghcr.io/strawgate/kb-yaml-to-lens/kibana-base:v9.2.0
```

### Using Different Kibana Versions

```bash
# Pull a different pre-built version
make pull KIBANA_VERSION=v9.1.0

# Generate fixtures with that version
make run KIBANA_VERSION=v9.1.0
```

## Troubleshooting

### Docker Pull Fails

**Problem**: Cannot pull base image from GHCR

**Solution**: Ensure you have internet connectivity and Docker is running. The base images are publicly accessible and don't require authentication.

### LensConfigBuilder Not Found

**Problem**: Cannot find `@kbn/lens-embeddable-utils`

**Solution**:

1. Ensure you pulled the base image: `make pull`
2. Try `make test-import` to verify the module is available
3. Use `make shell` to debug interactively
4. If the problem persists, the base image may need to be rebuilt (check GitHub Actions workflow)

### Invalid Configuration

**Problem**: Builder throws error about invalid config

**Solution**: Check the [Kibana Lens config API docs](https://github.com/elastic/kibana/blob/main/dev_docs/lens/config_api.mdx) for valid configuration options for your chart type.

## CI/CD Integration

```yaml
# .github/workflows/regenerate-fixtures.yml
name: Regenerate Fixtures

on:
  workflow_dispatch:

jobs:
  regenerate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Pull pre-built base image
        run: |
          cd fixture-generator
          make pull

      - name: Generate all fixtures
        run: |
          cd fixture-generator
          make run

      - name: Create PR with updated fixtures
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: "chore: regenerate Kibana test fixtures"
          title: "Update test fixtures"
```

## Contributing

When adding new visualization types:

1. Create `examples/new-viz.js`
2. Use `LensConfigBuilder` API to define the visualization
3. Add to `generate-all.js` if it should be generated by default
4. Run generator and verify output
5. Copy fixtures to Python tests
6. Update Python compiler to match (if needed)

## Documentation

- [Kibana Lens Config API](https://github.com/elastic/kibana/blob/main/dev_docs/lens/config_api.mdx)
- [Metric Visualizations](https://github.com/elastic/kibana/blob/main/dev_docs/lens/metric.mdx)
- [XY Charts](https://github.com/elastic/kibana/blob/main/dev_docs/lens/xy.mdx)
- [Pie Charts](https://github.com/elastic/kibana/blob/main/dev_docs/lens/pie.mdx)

## License

Same as parent project
