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
| **Make** | GNU Make | GNU Make | For running build commands |
| **Disk Space** | 25GB | 30GB+ | Kibana source + node_modules are large |
| **RAM** | 8GB | 16GB+ | Bootstrap process is memory-intensive |
| **Time** | ~6 min | N/A | First build only; cached thereafter |

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
│    ├── make run                                             │
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

```bash
cd fixture-generator
make build
```

**Build Process:** Takes ~6 minutes first time (installs Ubuntu, Node.js 22.21.1, clones Kibana, runs `yarn kbn bootstrap --allow-root`). Subsequent builds are cached and much faster.

**Common Issues:**

- "Kibana should not be run as root" → Ensure `--allow-root` flag in Dockerfile
- Node version mismatch → Update `NODE_VERSION` to match Kibana's `.node-version`

### Step 3: Write Your Generator Script

Create a new file in `examples/{panel-type}.js` following this template:

**Template:**

```javascript
#!/usr/bin/env node
const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generate{PanelType}() {
  const builder = new LensConfigBuilder();

  const config = {
    chartType: '{panel-type}',
    title: 'Your Panel Title',
    dataset: { esql: 'FROM your-index | STATS metric = SUM(field) BY dimension' },
    // Add required fields based on chart type (see Kibana docs)
  };

  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-7d', to: 'now', type: 'relative' }
  });

  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });

  fs.writeFileSync(
    path.join(outputDir, '{panel-type}.json'),
    JSON.stringify(lensAttributes, null, 2)
  );
  console.log('✓ Generated: {panel-type}.json');
}

if (require.main === module) {
  generate{PanelType}().catch((err) => {
    console.error('Failed to generate fixture:', err);
    process.exit(1);
  });
}

module.exports = { generate{PanelType} };
```

**Key Points:** Import from `@kbn/lens-embeddable-utils/config_builder`, match config structure to Kibana docs, export function for `generate-all.js`

### Step 4: Run the Generator

**Generate a Single Fixture:**

```bash
cd fixture-generator
make run-example EXAMPLE=your-script.js
```

**Generate All Fixtures:**

```bash
cd fixture-generator
make run
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

**Quick workflow for new panel types** (gauge, table, treemap):

1. **Research:** Check `dev_docs/lens/{panel-type}.mdx` for required/optional fields
2. **Write:** Create `examples/{panel-type}.js` using template from Step 3
3. **Test:** `make run-example EXAMPLE={panel-type}.js`
4. **Integrate:** Add to `generate-all.js` generators array

### Testing with Different Kibana Versions

To generate fixtures for a specific Kibana version:

```bash
# Build for specific version
make build KIBANA_VERSION=v9.3.0

# Generate with that version
make run

# Output goes to ./output/
```

**Common Kibana Versions:**

- `v9.2.0` - Default version (recommended)
- `main` - Latest development version
- `v9.3.0` - Specific release tag
- `8.15` - Branch for 8.15.x releases

## Troubleshooting

### Build Issues

| Problem | Solution |
|---------|----------|
| **Node version mismatch**<br/>`Error: Expected version "22.21.1". Got "20.19.4"` | The Node.js version is auto-detected from Kibana's `.node-version` file during build. Rebuild with `make build-no-cache` to pick up any version changes |
| **"Kibana should not be run as root"** | Add `--allow-root` flag to `yarn kbn bootstrap` in Dockerfile |
| **Out of memory during bootstrap** | Increase Docker memory limit in Docker Desktop settings (recommend 10GB+) |

### Generation Issues

| Problem | Solution |
|---------|----------|
| **LensConfigBuilder not found** | Ensure bootstrap completed successfully. Run `make test-import` to verify |
| **Invalid configuration error**<br/>`missing required field 'breakdown'` | Review chart-specific Kibana docs, ensure all required fields present with correct types |
| **ES\|QL query syntax error** | Use uppercase keywords (`BY`, `STATS`, `FROM`), test query in Kibana Dev Tools first |
| **Permission denied writing to output** | Create output directory: `mkdir -p fixture-generator/output && chmod 777 fixture-generator/output` |

### Debugging

Use `make shell` to get an interactive shell inside the container for debugging:

```bash
make shell
# Inside container:
node -e "require('@kbn/lens-embeddable-utils/config_builder')"
ls /kibana/node_modules/@kbn/ | grep lens
```

## Real-World Example: Heatmaps

Complete example of creating a heatmap fixture. Required fields from Kibana docs: `chartType`, `title`, `breakdown` (Y-axis), `xAxis` (X-axis), `value` (metric), `dataset`.

**File: `fixture-generator/examples/heatmap.js`**

```javascript
#!/usr/bin/env node
const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generateHeatmap() {
  const builder = new LensConfigBuilder();

  const config = {
    chartType: 'heatmap',
    title: 'Traffic Heatmap by Geographic Location',
    dataset: { esql: 'FROM kibana_sample_data_logs | STATS bytes = SUM(bytes) BY geo.dest, geo.src' },
    breakdown: 'geo.dest',
    xAxis: 'geo.src',
    value: 'bytes',
    legend: { show: true, position: 'right' }
  };

  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-7d', to: 'now', type: 'relative' }
  });

  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });

  fs.writeFileSync(
    path.join(outputDir, 'heatmap.json'),
    JSON.stringify(lensAttributes, null, 2)
  );
  console.log('✓ Generated: heatmap.json');
}

if (require.main === module) {
  generateHeatmap().catch((err) => {
    console.error('Failed to generate fixture:', err);
    process.exit(1);
  });
}

module.exports = { generateHeatmap };
```

**Add to `generate-all.js`:**

```javascript
const { generateHeatmap } = require('./examples/heatmap');
generators.push({ name: 'Heatmap', fn: generateHeatmap });
```

**Run it:**

```bash
make run-example EXAMPLE=heatmap.js
# Or run all: make run
```

## Available Make Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make build` | Build the Docker image |
| `make build-no-cache` | Full rebuild without cache |
| `make run` | Generate all fixtures |
| `make run-example EXAMPLE=<file>` | Run a specific example |
| `make shell` | Open shell for debugging |
| `make test-import` | Test @kbn module import |
| `make clean` | Remove output files |
| `make clean-image` | Remove Docker image |

## Summary

**Workflow:** Research panel in Kibana docs → Build container (one-time) → Write generator script → Run to produce JSON → Use in test suite

**Benefits:** Test data is authoritative (from Kibana itself), validates real-world compatibility, regenerable for new Kibana versions
