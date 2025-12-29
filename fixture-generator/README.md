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

### 1. Build the Docker Image

```bash
cd fixture-generator
make build
```

**Note**: First build takes ~6 minutes to bootstrap Kibana and make the `@kbn/lens-embeddable-utils` package available.

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
| `make build` | Build the Docker image |
| `make build-no-cache` | Full rebuild without cache |
| `make run` | Generate all fixtures |
| `make run-example EXAMPLE=<file>` | Run a specific example script |
| `make shell` | Open a shell in the container for debugging |
| `make test-import` | Test that @kbn/lens-embeddable-utils can be imported |
| `make clean` | Remove generated output files |
| `make clean-image` | Remove the Docker image |

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

The Dockerfile:

1. Installs Node.js 22.x (matches Kibana requirement)
2. Clones and bootstraps Kibana (making `@kbn/*` packages available)
3. Provides access to `LensConfigBuilder` from `@kbn/lens-embeddable-utils`
4. Runs your generator scripts and exports JSON to `./output/`

## Troubleshooting

### Docker Build Fails

**Problem**: Out of memory during Kibana bootstrap

**Solution**: Increase Docker memory limit in Docker Desktop settings (recommend 10GB+)

### LensConfigBuilder Not Found

**Problem**: Cannot find `@kbn/lens-embeddable-utils`

**Solution**:

1. Ensure Kibana bootstrap completed successfully
2. Check build logs for errors during `yarn kbn bootstrap`
3. Try `make test-import` to verify the module is available
4. Use `make shell` to debug interactively

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

      - name: Build fixture generator
        run: |
          cd fixture-generator
          make build

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
