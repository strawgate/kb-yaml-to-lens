# Kibana Dashboard Fixture Generator

A Docker-based tool for generating Kibana dashboard JSON fixtures using TypeScript and Kibana's official APIs. These fixtures are used as test data for the `kb-yaml-to-lens` Python compiler.

## Purpose

Generate **known-good** Kibana dashboard JSON by:
1. Writing dashboard definitions in **TypeScript code**
2. Using Kibana's **LensConfigBuilder API** to generate proper JSON
3. Exporting JSON fixtures for Python test suite validation
4. Supporting multiple Kibana versions for compatibility testing

## Why This Approach?

- **Authoritative**: Uses Kibana's actual API, not reverse-engineering
- **Version Flexibility**: Easy to regenerate fixtures for different Kibana versions
- **Type Safety**: TypeScript provides autocomplete and type checking
- **Test Accuracy**: Ensures Python compiler output matches Kibana's format exactly

## System Requirements

| Requirement | Value |
|-------------|-------|
| **Docker** | Latest stable |
| **Disk** | 25GB+ (Kibana source + node_modules) |
| **RAM** | 8GB+ recommended |

## Quick Start

### 1. Build the Docker Image

```bash
cd fixture-generator
docker-compose build
```

**Note**: First build takes 15-30 minutes to bootstrap Kibana.

### 2. Generate Fixtures

```bash
# Generate all fixtures
docker-compose run generator

# Generate specific dashboard
docker-compose run generator node dist/dashboards/metric-examples.js
```

### 3. Copy to Python Tests

```bash
# Fixtures are written to ./output/
cp output/metric-basic.json ../tests/fixtures/
```

## Project Structure

```
fixture-generator/
├── src/
│   ├── dashboards/          # Dashboard definitions (you edit these)
│   │   ├── metric-examples.ts
│   │   ├── xy-examples.ts
│   │   └── pie-examples.ts
│   ├── lib/
│   │   └── generator.ts     # Helper to run Kibana API and export JSON
│   └── cli.ts               # Main entry point
├── output/                  # Generated JSON files
├── Dockerfile
├── docker-compose.yml
└── package.json
```

## Creating Dashboard Definitions

Dashboard definitions are TypeScript files in `src/dashboards/` that use Kibana's LensConfigBuilder:

```typescript
// src/dashboards/metric-examples.ts
import { generateFixture } from '../lib/generator';

// Define your dashboard using Kibana's API
export async function generateMetricBasic() {
  const { LensConfigBuilder } = await import('@kbn/lens-embeddable-utils/config_builder');

  const builder = new LensConfigBuilder();

  // Use Kibana's API to build the visualization
  const lensConfig = builder
    .metric()
    .addMetric('count')
    .build();

  // Export as JSON fixture
  await generateFixture('metric-basic.json', {
    title: 'Basic Metric',
    visualizationType: 'lnsMetric',
    ...lensConfig
  });
}

// Export multiple variations
export async function generateMetricWithBreakdown() {
  // ... define another dashboard variant
}

// Run all generators in this file
if (require.main === module) {
  Promise.all([
    generateMetricBasic(),
    generateMetricWithBreakdown(),
  ]).then(() => console.log('✓ Metric fixtures generated'));
}
```

## Workflow for Adding Test Fixtures

1. **Create dashboard definition** in `src/dashboards/my-test.ts`
2. **Use Kibana's LensConfigBuilder** to programmatically build the dashboard
3. **Run fixture generator** via Docker
4. **Copy JSON to Python tests** in appropriate location
5. **Use in test cases** to validate compiler output

### Example Workflow

```bash
# 1. Create new dashboard definition
cat > src/dashboards/my-test.ts << 'EOF'
import { generateFixture } from '../lib/generator';

export async function generateMyTest() {
  const { LensConfigBuilder } = await import('@kbn/lens-embeddable-utils/config_builder');
  const builder = new LensConfigBuilder();

  const config = builder
    .metric()
    .addMetric('count', { label: 'Total Events' })
    .build();

  await generateFixture('my-test.json', config);
}

if (require.main === module) {
  generateMyTest();
}
EOF

# 2. Rebuild and generate
docker-compose build
docker-compose run generator node dist/dashboards/my-test.js

# 3. Copy to Python tests
cp output/my-test.json ../tests/fixtures/

# 4. Use in Python test
# In tests/panels/charts/metric/test_metric_data.py:
# import json
# MY_FIXTURE = json.loads(Path('../fixtures/my-test.json').read_text())
# TEST_CASES.append((IN_CONFIG, ESQL_CONFIG, MY_FIXTURE))
```

## Multi-Version Support

To generate fixtures for different Kibana versions:

```bash
# Build for Kibana 8.15
docker build --build-arg KIBANA_VERSION=8.15 -t fixture-gen:8.15 .

# Build for Kibana 9.0
docker build --build-arg KIBANA_VERSION=9.0 -t fixture-gen:9.0 .

# Generate with specific version
docker run -v $(pwd)/output:/tool/output fixture-gen:8.15 node dist/dashboards/metric-examples.js
```

## Docker Setup Details

The Dockerfile:
1. Installs Node.js 20.x (matches Kibana requirement)
2. Clones and bootstraps Kibana (making `@kbn/*` packages available)
3. Installs TypeScript and builds your dashboard definitions
4. Runs generators and exports JSON to `./output/`

## Example Dashboard Definitions

See `src/dashboards/` for examples:
- `metric-examples.ts` - Metric visualizations (basic, with breakdown, with secondary)
- `xy-examples.ts` - XY charts (line, bar, area, stacked)
- `pie-examples.ts` - Pie/donut charts
- `table-examples.ts` - Data tables
- `gauge-examples.ts` - Gauge visualizations
- `heatmap-examples.ts` - Heatmap visualizations

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

### Kibana Packages Not Found

**Problem**: Cannot find `@kbn/lens-embeddable-utils`

**Solution**: Ensure Kibana bootstrap completed successfully. Check build logs.

### Generated JSON Looks Wrong

**Problem**: Fixture doesn't match expected format

**Solution**: Compare with actual Kibana export. The LensConfigBuilder API should produce correct output, but you may need to adjust your TypeScript code.

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
      - uses: actions/checkout@v3

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

1. Create `src/dashboards/new-viz-examples.ts`
2. Use Kibana's LensConfigBuilder to define examples
3. Run generator and verify output
4. Copy fixtures to Python tests
5. Update Python compiler to match (if needed)

## License

Same as parent project

## Support

File issues in main repository with `fixture-generator` label
