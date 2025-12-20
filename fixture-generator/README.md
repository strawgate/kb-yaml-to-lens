# Kibana Lens Fixture Generator

A Docker-based tool that generates test fixtures for the `kb-yaml-to-lens` Python compiler using Kibana's official LensConfigBuilder API.

## Purpose

This tool is **NOT** a replacement for the Python compiler. Instead, it generates **known-good** Kibana JSON outputs that serve as test fixtures for validating the Python compiler's output.

### Why This Tool?

1. **Test Accuracy**: Uses Kibana's official API to generate authoritative JSON structures
2. **Version Compatibility**: Easy to regenerate fixtures when Kibana versions change
3. **Regression Testing**: Ensures Python compiler output matches Kibana's expected format
4. **Documentation**: Generated JSON serves as reference for understanding Kibana structures

## Architecture

```
YAML Input → Docker Tool (LensConfigBuilder) → Kibana JSON
                                                     ↓
                                      Python Test Fixture (test_*_data.py)
                                                     ↓
                                      Python Compiler Validates Against It
```

## System Requirements

| Requirement | Value |
|-------------|-------|
| **Node.js** | 20.19.4 (from Kibana .node-version) |
| **Yarn** | ^1.22.19 (Yarn Classic v1) |
| **RAM** | 8GB+ recommended, 4GB minimum |
| **Disk** | 20-25GB (Kibana source + node_modules) |
| **OS** | Linux/macOS (Windows requires WSL) |
| **Docker** | Latest stable version |

## Quick Start

### 1. Build the Docker Image

```bash
cd fixture-generator
docker-compose build
```

**Note**: The first build takes 15-30 minutes as it bootstraps the entire Kibana codebase.

### 2. Generate a Fixture

```bash
# Create an example YAML file
docker-compose run fixture-generator example -o /tool/input/my-fixture.yaml

# Generate the Kibana JSON fixture
docker-compose run fixture-generator generate /tool/input/my-fixture.yaml -o /tool/output/my-fixture.json
```

### 3. Use in Python Tests

```python
# tests/panels/charts/metric/test_metric_data.py
import json

# Load the generated fixture
with open('fixture-generator/output/my-fixture.json') as f:
    KIBANA_GENERATED_FIXTURE = json.load(f)

TEST_CASES = [
    (LENS_CONFIG, ESQL_CONFIG, KIBANA_GENERATED_FIXTURE),
]
```

## CLI Commands

### Generate Fixture

```bash
docker-compose run fixture-generator generate <input.yaml> -o <output.json>
```

Options:
- `-o, --output <path>`: Output file path (default: `./fixture.json`)
- `--pretty`: Pretty print JSON output (default: true)
- `--validate`: Validate YAML without generating

### Validate YAML

```bash
docker-compose run fixture-generator validate <input.yaml>
```

### Generate Example

```bash
docker-compose run fixture-generator example -o /tool/input/example.yaml
```

## YAML Configuration Format

```yaml
version: "1.0"

settings:
  dataView: "logs-*"  # Default data view ID
  timeFrom: "now-24h"
  timeTo: "now"

dashboard:
  title: "My Test Dashboard"
  description: "Test fixtures for validation"

panels:
  # Metric visualization
  - type: metric
    title: "Total Count"
    layout: quarter  # full, half, third, quarter
    config:
      metric:
        operation: count
        label: "Total"
      trendLine: true
      color: "#00BFB3"

  # XY Chart
  - type: xy
    title: "Requests Over Time"
    layout: half
    config:
      seriesType: line  # line, bar, area, bar_stacked, area_stacked
      xAxis:
        field: "@timestamp"
        type: date_histogram
        interval: auto
      yAxis:
        operation: count
        label: "Requests"
      breakdown:
        field: "status_code"
        size: 5

  # Pie Chart
  - type: pie
    title: "Distribution"
    layout: quarter
    config:
      shape: donut  # pie, donut, treemap, waffle
      sliceBy:
        - field: "category"
          size: 10
      metric:
        operation: count

  # Data Table
  - type: datatable
    title: "Top Entries"
    layout: half
    config:
      columns:
        - field: "url.path"
          operation: terms
          size: 20
        - operation: count
        - field: "response_time"
          operation: average
      sorting:
        columnIndex: 1
        direction: desc

  # Gauge
  - type: gauge
    title: "Error Rate"
    layout: quarter
    config:
      shape: arc  # horizontalBullet, verticalBullet, semiCircle, arc, circle
      metric:
        operation: count
        label: "Errors"
      min: 0
      max: 100
      goal: 5

  # Heatmap
  - type: heatmap
    title: "Activity Heatmap"
    layout: half
    config:
      xAxis:
        field: "@timestamp"
        type: date_histogram
        interval: "1h"
      yAxis:
        field: "source"
        size: 10
      value:
        operation: count
```

## Supported Visualization Types

- **Metric**: Single value with optional secondary metric, breakdown, and trendline
- **XY Chart**: Line, bar, area charts with optional stacking and breakdown
- **Pie/Donut**: Pie charts with multiple slice dimensions
- **Data Table**: Tabular data with sorting
- **Gauge**: Gauge visualizations with min/max/goal values
- **Heatmap**: Two-dimensional heatmaps

## Development Workflow

### Generating Test Fixtures

1. **Create YAML test case** describing the desired visualization
2. **Run fixture generator** to create Kibana JSON
3. **Copy JSON to Python test** in appropriate `test_*_data.py` file
4. **Run Python tests** to validate compiler output matches fixture

### Example Workflow

```bash
# 1. Create test case YAML
cat > input/metric-with-breakdown.yaml <<EOF
version: "1.0"
settings:
  dataView: "logs-*"
dashboard:
  title: "Metric Test"
panels:
  - type: metric
    title: "Count by Agent"
    layout: full
    config:
      metric:
        operation: count
      breakdown:
        field: "agent.name"
        size: 5
EOF

# 2. Generate fixture
docker-compose run fixture-generator generate \
  /tool/input/metric-with-breakdown.yaml \
  -o /tool/output/metric-with-breakdown.json

# 3. Copy to Python test
cp output/metric-with-breakdown.json ../tests/fixtures/

# 4. Update test_metric_data.py to use the fixture
# 5. Run tests
cd .. && poetry run pytest tests/panels/charts/metric/
```

## Docker Image Optimization

### Using the Optimized Multi-Stage Build

For faster rebuilds, use the optimized Dockerfile:

```bash
docker-compose -f docker-compose.yml build --file Dockerfile.optimized
```

This caches the Kibana bootstrap in a separate layer.

### Volume Caching

The docker-compose.yml uses volumes to cache:
- `kibana_node_modules`: Kibana dependencies
- `yarn_cache`: Yarn package cache

These persist between runs for faster execution.

## Troubleshooting

### Build Failures

**Problem**: Kibana bootstrap fails with memory errors

**Solution**: Increase Docker memory allocation to 10GB+

```yaml
# docker-compose.yml
services:
  fixture-generator:
    mem_limit: 10g
```

### Node Version Mismatch

**Problem**: Node version incompatibility

**Solution**: Ensure Dockerfile uses Node.js 20.19.4 matching Kibana's `.node-version`

### Disk Space Issues

**Problem**: Not enough disk space for Kibana

**Solution**: Ensure 25GB+ available. Clean up Docker:

```bash
docker system prune -a
docker volume prune
```

## Integration with Python Compiler

### Current Test Structure

The Python compiler tests use this pattern:

```python
@pytest.mark.parametrize(('in_lens_config', 'in_esql_config', 'out_layer'), TEST_CASES)
async def test_compile_metric(in_lens_config: dict, in_esql_config: dict, out_layer: dict):
    lens_chart = LensMetricChart.model_validate(in_lens_config)
    layer_id, kbn_columns, kbn_state = compile_lens_metric_chart(lens_chart)

    # Compare Python compiler output to expected (fixture)
    assert DeepDiff(out_layer, kbn_state_layer.model_dump(), ...) == {}
```

### Adding Fixture-Generated Tests

```python
# Load fixture generated by this tool
KIBANA_FIXTURE = json.loads(Path('fixtures/metric-breakdown.json').read_text())

TEST_CASES.append((
    IN_LENS_CONFIG,
    IN_ESQL_CONFIG,
    KIBANA_FIXTURE['state']['datasourceStates']['formBased']['layers']['layer_id']
))
```

## Multi-Version Support

To support multiple Kibana versions, build separate images:

```bash
# Kibana 8.x
docker build --build-arg KIBANA_VERSION=8.15.0 -t fixture-gen:8.15 .

# Kibana 9.x
docker build --build-arg KIBANA_VERSION=9.0.0 -t fixture-gen:9.0 .
```

Then specify version in docker-compose:

```yaml
services:
  fixture-generator-8:
    image: fixture-gen:8.15
  fixture-generator-9:
    image: fixture-gen:9.0
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Regenerate Fixtures

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
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

      - name: Regenerate all fixtures
        run: |
          for yaml in fixture-generator/input/*.yaml; do
            docker-compose run fixture-generator generate \
              "/tool/input/$(basename $yaml)" \
              -o "/tool/output/$(basename $yaml .yaml).json"
          done

      - name: Create PR with updated fixtures
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: "chore: regenerate test fixtures"
          title: "Update Kibana test fixtures"
```

## Contributing

When adding new visualization types:

1. Create builder in `src/visualizations/`
2. Add type to `src/parser/attribute-builder.ts`
3. Update YAML schema documentation
4. Add example configuration
5. Generate test fixture
6. Update Python compiler to match

## License

Same as parent project (kb-yaml-to-lens)

## Support

For issues with the fixture generator, please file an issue in the main repository with the `fixture-generator` label.
