# Kibana Fixture Generator: Complete Practical Guide

This document provides a complete, tested guide for using the Kibana fixture generator to create test data for the kb-yaml-to-lens Python compiler.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Understanding the Process](#understanding-the-process)
4. [Step-by-Step Guide](#step-by-step-guide)
5. [Creating New Fixtures](#creating-new-fixtures)
6. [Troubleshooting](#troubleshooting)
7. [Real-World Example: Heatmaps](#real-world-example-heatmaps)

## Overview

### What This Tool Does

The fixture generator uses Docker to bootstrap Kibana from source, giving you access to the real `LensConfigBuilder` API. You write simple JavaScript files that call this API and export JSON fixtures for testing.

**Key Benefits:**
- Generates *real* Kibana JSON (not AI-generated approximations)
- Uses Kibana's actual `LensConfigBuilder` API
- Provides known-good test data for validating the Python compiler
- Supports multiple Kibana versions for compatibility testing

### What You'll Get

Running this tool produces:
- JSON files containing complete Lens visualization configurations
- Exact output that Kibana would generate if you created the same panel in the UI
- Test fixtures you can use for snapshot testing and validation

## Prerequisites

| Requirement | Minimum | Recommended | Notes |
|-------------|---------|-------------|-------|
| **Docker** | Latest stable | Latest stable | Required for containerized build |
| **Disk Space** | 25GB | 30GB+ | Kibana source + node_modules are large |
| **RAM** | 8GB | 16GB+ | Bootstrap process is memory-intensive |
| **Time** | 15-30 min | N/A | First build only; cached thereafter |

## Understanding the Process

### How It Works

The fixture generator follows this workflow:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Docker Build (one-time, 15-30 minutes)                  │
│    ├── Install Node.js 22.x                                 │
│    ├── Clone Kibana from GitHub                             │
│    ├── Run yarn kbn bootstrap                               │
│    └── Make @kbn/lens-embeddable-utils available            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Write Generator Script (your work)                      │
│    ├── Import LensConfigBuilder                             │
│    ├── Define visualization config                          │
│    └── Export JSON                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Run Generator                                            │
│    ├── docker compose run generator                         │
│    └── Outputs JSON to ./output/                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Use in Tests                                             │
│    ├── Copy to tests/fixtures/                              │
│    └── Compare compiler output against known-good JSON      │
└─────────────────────────────────────────────────────────────┘
```

### What's in the Docker Container

The Dockerfile creates an environment with:

1. **Ubuntu 22.04** base image
2. **Node.js 22.21.1** (matches Kibana's current requirement)
3. **Yarn 1.22.19** (Kibana's package manager)
4. **Kibana source code** (cloned from GitHub)
5. **Bootstrapped Kibana packages** (via `yarn kbn bootstrap --allow-root`)
6. **Your generator scripts** (mounted as volumes)

The key insight: By bootstrapping Kibana, all `@kbn/*` packages become available to your Node.js scripts via `NODE_PATH=/kibana/node_modules`.

## Step-by-Step Guide

### Step 1: Research the Panel Type

Before writing a generator, understand how the panel works in Kibana's API.

**Where to Find Information:**

1. **Main API Documentation:**
   - URL: `https://github.com/elastic/kibana/blob/main/dev_docs/lens/config_api.mdx`
   - Contains: Constructor requirements, build method, general configuration options

2. **Chart-Specific Documentation:**
   - URL: `https://github.com/elastic/kibana/blob/main/dev_docs/lens/{chart-type}.mdx`
   - Examples: `metric.mdx`, `xy.mdx`, `pie.mdx`, `heatmap.mdx`
   - Contains: Required vs optional parameters, example configurations

3. **TypeScript Interfaces (Advanced):**
   - Location: `x-pack/plugins/lens/` in Kibana source
   - Use case: When docs are unclear about exact field names or types

**Example: Researching Heatmaps**

For heatmaps, you'd find:

**Required Parameters:**
- `chartType: 'heatmap'` - Identifies the visualization type
- `title: string` - Visualization name
- `breakdown: string | LensBreakdownConfig` - Y-axis dimension
- `xAxis: string | LensBreakdownConfig` - X-axis dimension
- `value: string` - The metric to visualize
- `dataset: { esql: string }` - The data query

**Optional Parameters:**
- `legend: { show: boolean, position: 'top'|'left'|'bottom'|'right' }` - Legend configuration

### Step 2: Build the Docker Container

This step only needs to be done once (or when you want to update the Kibana version).

**Commands:**

```bash
cd fixture-generator
docker compose build
```

**What Happens:**

```
Time: ~15-30 minutes (first build only)

1. Downloads Ubuntu 22.04 image                    (~1 min)
2. Installs system dependencies                    (~2 min)
3. Downloads and installs Node.js 22.21.1          (~1 min)
4. Installs Yarn package manager                   (~30 sec)
5. Clones Kibana from GitHub                       (~1-2 min)
6. Runs yarn kbn bootstrap --allow-root            (~10-20 min)
   - Installs all npm dependencies
   - Builds Kibana packages
   - Makes @kbn/* packages available
7. Sets up tool workspace                          (~10 sec)
```

**Important Notes:**

- The build uses Docker volumes to cache `node_modules` and yarn cache
- Subsequent builds are much faster (minutes instead of 15-30 minutes)
- If you see "Kibana should not be run as root", ensure `--allow-root` flag is present
- If you see Node version mismatch, check that `NODE_VERSION` matches Kibana's requirements

**Verifying the Build:**

```bash
# Check that the image was created
docker images | grep fixture-generator

# Expected output:
# fixture-generator-generator  latest  <image-id>  <timestamp>  <size>
```

### Step 3: Write Your Generator Script

Create a new file in `examples/{panel-type}.js` following this template:

**Template:**

```javascript
#!/usr/bin/env node
/**
 * Example: Generate a {PANEL_TYPE} visualization
 *
 * Description of what this generator creates
 */

const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generate{PanelType}() {
  // 1. Initialize the builder
  const builder = new LensConfigBuilder();

  // 2. Define your configuration
  const config = {
    chartType: '{panel-type}',     // e.g., 'metric', 'heatmap', 'xy'
    title: 'Your Panel Title',
    dataset: {
      esql: 'FROM your-index | STATS your_metric = SUM(field) BY dimension'
    },
    // ... other required fields based on chart type
    // (see Kibana docs for your specific chart type)
  };

  // 3. Build the Lens attributes
  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-7d', to: 'now', type: 'relative' }
  });

  // 4. Write to output directory
  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, '{panel-type}.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: {panel-type}.json');
}

// Run if executed directly
if (require.main === module) {
  generate{PanelType}()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}

module.exports = { generate{PanelType} };
```

**Key Points:**

1. **Imports:** Always import from `@kbn/lens-embeddable-utils/config_builder`
2. **Async Function:** Builder.build() is async, so use async/await
3. **Config Object:** Match the structure from Kibana docs exactly
4. **Time Range:** Optional but recommended for reproducible output
5. **Export:** Export the function for use in `generate-all.js`
6. **Error Handling:** Always catch and log errors for debugging

### Step 4: Run the Generator

**Generate a Single Fixture:**

```bash
cd fixture-generator
docker compose run generator node examples/your-script.js
```

**Generate All Fixtures:**

```bash
cd fixture-generator
docker compose run generator
# This runs generate-all.js which executes all registered generators
```

**What You'll See:**

```
Generating all test fixtures...

✓ Generated: metric-basic.json
✓ Generated: metric-with-breakdown.json
✓ Generated: xy-chart.json
✓ Generated: pie-chart.json
✓ Generated: your-panel.json

✓ All fixtures generated successfully
  Output directory: ./output/
```

**Troubleshooting Generation:**

If generation fails:

1. **Check the error message** - LensConfigBuilder provides clear errors
2. **Verify config structure** - Compare against Kibana docs
3. **Validate ES|QL syntax** - Test your query separately if needed
4. **Check field types** - Ensure numeric fields for metrics, keyword for breakdowns

### Step 5: Examine the Output

**View the Generated JSON:**

```bash
ls -la fixture-generator/output/
cat fixture-generator/output/your-panel.json | jq '.' | head -50
```

**What's in the JSON:**

The output is a complete Lens visualization configuration containing:

- `title`: Visualization title
- `visualizationType`: Always 'lnsXY', 'lnsMetric', 'lnsPie', 'lnsHeatmap', etc.
- `references`: Data view references (if applicable)
- `state`:
  - `datasourceStates`: Query and field configuration
  - `visualization`: Chart-specific display settings
  - `query`: KQL/Lucene query (if provided)
  - `filters`: Applied filters (if provided)

**Important:** This is **real Kibana JSON** - exactly what Kibana would generate if you created the same panel in the UI.

### Step 6: Use Fixtures in Tests

**Copy to Test Fixtures:**

```bash
# Copy specific fixture
cp fixture-generator/output/heatmap.json tests/fixtures/

# Copy all fixtures
cp fixture-generator/output/*.json tests/scenarios/
```

**How to Use in Tests:**

1. **Snapshot Testing:**
   - Place in `tests/__snapshots__/`
   - Use with `syrupy` in pytest
   - Compare compiler output against known-good fixture

2. **Validation Testing:**
   - Load fixture as expected output
   - Run Python compiler on equivalent YAML config
   - Deep-compare the results

3. **Regression Testing:**
   - Regenerate fixtures after Kibana updates
   - Ensure compiler output still matches

## Creating New Fixtures

### Workflow for New Panel Types

When adding support for a new panel type (e.g., gauge, table, treemap):

```
1. Research → 2. Write Script → 3. Test → 4. Integrate
```

**Step 1: Research**

```bash
# Open Kibana docs for your panel type
# Example: https://github.com/elastic/kibana/blob/main/dev_docs/lens/gauge.mdx

# Take notes on:
# - Required fields (chartType, title, etc.)
# - Optional fields (legend, colors, etc.)
# - Dataset requirements (ES|QL vs standard query)
# - Field type requirements (numeric, keyword, etc.)
```

**Step 2: Write Script**

```bash
# Create new example script
cat > fixture-generator/examples/gauge.js << 'EOF'
#!/usr/bin/env node
const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generateGauge() {
  const builder = new LensConfigBuilder();

  const config = {
    chartType: 'gauge',
    title: 'Performance Gauge',
    dataset: {
      esql: 'FROM metrics-* | STATS avg_cpu = AVG(cpu_percent)'
    },
    value: 'avg_cpu',
    // Add other gauge-specific config based on docs
  };

  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-24h', to: 'now', type: 'relative' }
  });

  const outputPath = path.join(__dirname, '..', 'output', 'gauge.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));
  console.log('✓ Generated: gauge.json');
}

if (require.main === module) {
  generateGauge().catch((err) => {
    console.error('Failed to generate fixture:', err);
    process.exit(1);
  });
}

module.exports = { generateGauge };
EOF
```

**Step 3: Test**

```bash
# Run your script
cd fixture-generator
docker compose run generator node examples/gauge.js

# Verify output
cat output/gauge.json | jq '.visualizationType'
# Should output: "lnsGauge" (or similar)
```

**Step 4: Integrate**

```bash
# Add to generate-all.js
# Edit fixture-generator/generate-all.js and add:
const { generateGauge } = require('./examples/gauge');

// Add to generators array:
{ name: 'Gauge', fn: generateGauge },
```

### Testing with Different Kibana Versions

To generate fixtures for a specific Kibana version:

```bash
# Build for specific version
docker build \
  --build-arg KIBANA_VERSION=v9.3.0 \
  --build-arg NODE_VERSION=22.21.1 \
  -t fixture-gen:9.3 \
  .

# Generate with that version
docker run -v $(pwd)/output:/tool/output fixture-gen:9.3 node examples/heatmap.js

# Output goes to ./output/heatmap.json
```

**Common Kibana Versions:**

- `main` - Latest development version
- `v9.4.0` - Specific release tag
- `v9.3.0` - Previous release
- `8.15` - Branch for 8.15.x releases

## Troubleshooting

### Build Issues

**Problem: Node version mismatch**

```
Error: The engine "node" is incompatible with this module.
Expected version "22.21.1". Got "20.19.4"
```

**Solution:**

1. Check Kibana's `.node-version` file in the cloned repo
2. Update `NODE_VERSION` in Dockerfile and docker-compose.yml
3. Rebuild: `docker compose build --no-cache`

---

**Problem: "Kibana should not be run as root"**

```
Error: Kibana should not be run as root. Use --allow-root to continue.
```

**Solution:**

Ensure the Dockerfile includes `--allow-root` flag:

```dockerfile
RUN yarn kbn bootstrap --allow-root
```

---

**Problem: Out of memory during bootstrap**

```
FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory
```

**Solution:**

Increase Docker memory limit in `docker-compose.yml`:

```yaml
services:
  generator:
    mem_limit: 16g  # Increase from 10g
    environment:
      - NODE_OPTIONS=--max_old_space_size=16384  # Increase from 8192
```

---

### Generation Issues

**Problem: LensConfigBuilder not found**

```
Error: Cannot find module '@kbn/lens-embeddable-utils/config_builder'
```

**Solution:**

1. Ensure bootstrap completed successfully
2. Check `NODE_PATH` is set correctly: `ENV NODE_PATH=/kibana/node_modules`
3. Rebuild container if necessary

---

**Problem: Invalid configuration error**

```
Error: Invalid configuration for heatmap: missing required field 'breakdown'
```

**Solution:**

1. Review the chart-specific Kibana documentation
2. Ensure all required fields are present
3. Check field types match expectations (string vs object)

---

**Problem: ES|QL query syntax error**

```
Error: Failed to parse ES|QL query: unexpected token 'by'
```

**Solution:**

1. ES|QL syntax is case-sensitive: use uppercase `BY`, `STATS`, `FROM`
2. Test your query in Kibana Dev Tools first
3. Check ES|QL documentation for correct syntax

---

### Runtime Issues

**Problem: Permission denied writing to output**

```
Error: EACCES: permission denied, open '/tool/output/metric.json'
```

**Solution:**

The output directory should be mounted with write permissions. Check `docker-compose.yml`:

```yaml
volumes:
  - ./output:/tool/output  # Should allow writes
```

If needed, create output directory first:

```bash
mkdir -p fixture-generator/output
chmod 777 fixture-generator/output  # Or appropriate permissions
```

## Real-World Example: Heatmaps

This section walks through creating a heatmap fixture from start to finish.

### Step 1: Research Heatmap Configuration

**From Kibana Documentation (`dev_docs/lens/heatmap.mdx`):**

**Required:**
- `chartType: 'heatmap'`
- `title: string`
- `breakdown: string | LensBreakdownConfig` (Y-axis)
- `xAxis: string | LensBreakdownConfig` (X-axis)
- `value: string` (metric)
- `dataset: { esql: string }`

**Optional:**
- `legend: { show: boolean, position: 'top'|'left'|'bottom'|'right' }`

### Step 2: Create the Generator Script

**File: `fixture-generator/examples/heatmap.js`**

```javascript
#!/usr/bin/env node
/**
 * Generate a heatmap visualization showing geographic traffic patterns
 */

const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generateHeatmap() {
  // Initialize the builder
  const builder = new LensConfigBuilder();

  // Define heatmap configuration
  const config = {
    chartType: 'heatmap',
    title: 'Traffic Heatmap by Geographic Location',
    dataset: {
      esql: 'FROM kibana_sample_data_logs | STATS bytes = SUM(bytes) BY geo.dest, geo.src'
    },
    breakdown: 'geo.dest',  // Y-axis: destination country
    xAxis: 'geo.src',       // X-axis: source country
    value: 'bytes',         // Metric: total bytes transferred
    legend: {
      show: true,
      position: 'right'
    }
  };

  // Build the Lens attributes
  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-7d', to: 'now', type: 'relative' }
  });

  // Write to output directory
  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'heatmap.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: heatmap.json');
}

// Run if executed directly
if (require.main === module) {
  generateHeatmap()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}

module.exports = { generateHeatmap };
```

### Step 3: Add to generate-all.js

**File: `fixture-generator/generate-all.js`**

```javascript
const { generateHeatmap } = require('./examples/heatmap');

const generators = [
  { name: 'Metric (Basic)', fn: generateMetricBasic },
  { name: 'Metric (Breakdown)', fn: generateMetricWithBreakdown },
  { name: 'XY Chart', fn: generateXYChart },
  { name: 'Pie Chart', fn: generatePieChart },
  { name: 'Heatmap', fn: generateHeatmap },  // ← Add this line
];
```

### Step 4: Build and Run

```bash
# Navigate to fixture-generator directory
cd fixture-generator

# Build container (if not already built)
docker compose build

# Run heatmap generator specifically
docker compose run generator node examples/heatmap.js

# Or generate all fixtures including heatmap
docker compose run generator
```

### Step 5: Verify Output

```bash
# Check file was created
ls -lh output/heatmap.json

# View the structure
cat output/heatmap.json | jq '{
  title,
  visualizationType,
  state: {
    datasourceStates: .state.datasourceStates | keys,
    visualization: .state.visualization | keys
  }
}'

# Expected output:
# {
#   "title": "Traffic Heatmap by Geographic Location",
#   "visualizationType": "lnsHeatmap",
#   "state": {
#     "datasourceStates": ["textBased"],
#     "visualization": ["layerId", "shape", "legend", ...]
#   }
# }
```

### Step 6: Use in Python Tests

```bash
# Copy to test fixtures
cp output/heatmap.json ../tests/fixtures/kibana-heatmap-expected.json

# Now you can use it in tests
```

**Example Test (Python):**

```python
import json
from dashboard_compiler import render

def test_heatmap_compilation():
    # Load YAML config
    yaml_config = """
    dashboard:
      title: "Test Dashboard"
      panels:
        - type: heatmap
          title: "Traffic Heatmap by Geographic Location"
          query:
            esql: "FROM kibana_sample_data_logs | STATS bytes = SUM(bytes) BY geo.dest, geo.src"
          breakdown: geo.dest
          x_axis: geo.src
          value: bytes
    """

    # Compile to JSON
    result = render(yaml_config)
    panel_json = result['panels'][0]

    # Load expected fixture
    with open('tests/fixtures/kibana-heatmap-expected.json') as f:
        expected = json.load(f)

    # Compare
    assert panel_json == expected
```

## Summary

The fixture generator workflow:

1. **Research** panel configuration in Kibana docs
2. **Build** Docker container (one-time setup)
3. **Write** generator script using `LensConfigBuilder`
4. **Run** generator to produce JSON
5. **Verify** output structure
6. **Use** in Python test suite

This approach ensures:
- Test data is authoritative (from Kibana itself)
- Tests validate real-world compatibility
- Fixtures can be regenerated for new Kibana versions
- No guesswork about JSON structure

## Next Steps

- Create generators for other panel types (gauge, table, treemap)
- Generate fixtures for multiple Kibana versions
- Integrate fixtures into CI/CD pipeline
- Document any edge cases discovered
