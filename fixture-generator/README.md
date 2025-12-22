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
|-------------|-------|
| **Docker** | Latest stable |
| **Disk** | 25GB+ (Kibana source + node_modules) |
| **RAM** | 8GB+ recommended |

## Quick Start

### Option A: Use Pre-Built GHCR Image (Recommended)

**Fast path** - Uses pre-built images from GitHub Container Registry, no build required:

```bash
cd fixture-generator
docker-compose -f docker-compose.ghcr.yml run generator

# Generate specific fixture
docker-compose -f docker-compose.ghcr.yml run generator node examples/metric-basic.js
```

See [GHCR.md](GHCR.md) for complete GHCR documentation.

### Option B: Build Locally

**Build from source** - Takes 15-30 minutes but works offline:

```bash
cd fixture-generator
docker-compose build
```

**Note**: First build takes 15-30 minutes to bootstrap Kibana and make the `@kbn/lens-embeddable-utils` package available.

### 2. Generate Fixtures

```bash
# Generate all fixtures
docker-compose run generator

# Generate specific fixture
docker-compose run generator node examples/metric-basic.js
docker-compose run generator node examples/xy-chart.js
```

### 3. Copy to Python Tests

```bash
# Fixtures are written to ./output/
cp output/metric-basic.json ../tests/fixtures/
```

## Project Structure

```
fixture-generator/
├── examples/                    # Example generator scripts
│   ├── metric-basic.js         # Basic metric visualization
│   ├── metric-with-breakdown.js # Metric with breakdown
│   ├── xy-chart.js             # Line/area/bar charts
│   └── pie-chart.js            # Pie/donut charts
├── generate-all.js             # Runs all examples
├── output/                     # Generated JSON files
├── Dockerfile
├── docker-compose.yml
└── package.json
```

## How It Works

Each example script:

1. Imports `LensConfigBuilder` from Kibana's package
2. Creates a config object defining the visualization
3. Calls `builder.build(config, options)` to generate the Lens attributes
4. Writes the result as JSON to the output directory

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
3. **Run the script** via Docker
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
docker-compose run generator node examples/my-custom-metric.js

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
docker build --build-arg KIBANA_VERSION=v8.15.0 -t fixture-gen:8.15 .

# Generate with specific version
docker run -v $(pwd)/output:/tool/output fixture-gen:8.15 node examples/metric-basic.js
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

**Solution**: Increase Docker memory limit

```yaml
# docker-compose.yml
services:
  generator:
    mem_limit: 10g
```

### LensConfigBuilder Not Found

**Problem**: Cannot find `@kbn/lens-embeddable-utils`

**Solution**: Ensure Kibana bootstrap completed successfully. Check build logs for errors during the `yarn kbn bootstrap` step.

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
          docker-compose build

      - name: Generate all fixtures
        run: |
          cd fixture-generator
          docker-compose run generator

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
