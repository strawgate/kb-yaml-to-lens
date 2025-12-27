# Agent Instructions for Fixture Generator

This document provides instructions for AI agents working with the Kibana fixture generator.

## Critical Rules

1. **ALWAYS test fixture generation before committing code**
2. **NEVER commit untested generator changes**
3. **Use Docker for all fixture generation** (required for Kibana packages)
4. **Verify output files are created** before claiming success

## How to Run Fixture Generation

### Prerequisites Check

Before running fixture generation, verify Docker is available:

```bash
docker --version
make --version
```

### Running Fixture Generation

The fixture generator **MUST** run inside Docker because it requires Kibana's `@kbn/lens-embeddable-utils` package.

#### Generate All Fixtures

```bash
cd fixture-generator
make run
```

This will:

1. Build the Docker image if needed (takes ~6 minutes on first run)
2. Run all generator scripts in `examples/`
3. Write JSON output to `fixture-generator/output/`

#### Generate a Single Fixture

```bash
cd fixture-generator
make run-example EXAMPLE=metric-basic.js
```

Replace `metric-basic.js` with any file from `examples/`.

#### Verify Output

After running generators, check that output files were created:

```bash
ls -lh fixture-generator/output/
```

You should see JSON files corresponding to each generator that ran.

### Testing Individual Generators

To test a specific generator file:

```bash
cd fixture-generator
make run-example EXAMPLE=gauge.js
cat output/gauge.json | head -20
cat output/gauge-dataview.json | head -20  # Dual generators create both files
```

This verifies:

- The generator script runs without errors
- Output JSON files are created (dual generators create 2 files)
- JSON structure looks valid

**Note**: Most generators now use the dual-generation pattern, creating both ES|QL and Data View variants from a single script.

## Development Workflow

When creating or modifying fixture generators:

### 1. Make Your Changes

Edit generator files in `fixture-generator/examples/`.

### 2. Test Your Changes

**REQUIRED** - Run the generator to verify it works:

```bash
cd fixture-generator
make run-example EXAMPLE=your-new-generator.js
```

### 3. Verify Output

Check that the JSON output is created and valid:

```bash
cat output/your-new-generator.json | jq . | head -50
```

If `jq` is not available, use:

```bash
python -m json.tool output/your-new-generator.json | head -50
```

### 4. Run Full Test Suite

Before committing, run the project's test suite:

```bash
make check
```

This runs linting and tests for the Python compiler.

### 5. Commit Only After Testing

Only commit after:

- ✅ Generator runs successfully in Docker
- ✅ Output JSON is created
- ✅ Output JSON is valid
- ✅ `make check` passes

## Common Issues

### "Cannot find module '@kbn/lens-embeddable-utils'"

**Cause**: Trying to run generators outside Docker

**Solution**: Always use `make run` or `make run-example` - these run inside Docker where Kibana packages are available.

### "Docker image not found"

**Cause**: Docker image hasn't been built yet

**Solution**: Build the image first:

```bash
cd fixture-generator
make build
```

### "Generator runs but no output file"

**Cause**: Generator script has an error or wrong output path

**Solution**: Check the generator's console output for errors. Use `make shell` to debug:

```bash
cd fixture-generator
make shell
# Inside container:
node examples/your-generator.js
```

### "Output JSON is invalid"

**Cause**: LensConfigBuilder received invalid configuration

**Solution**: Check the generator's config against [Kibana's Lens Config API docs](https://github.com/elastic/kibana/blob/main/dev_docs/lens/config_api.mdx).

## Creating New Dual Generators

Most new generators should use the dual-generation pattern to create both ES|QL and Data View variants:

```javascript
#!/usr/bin/env node
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateMyChart() {
  // Shared configuration
  const sharedConfig = {
    chartType: 'xy',
    // ... shared properties
  };

  // ES|QL variant
  const esqlConfig = {
    ...sharedConfig,
    title: 'My Chart',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp'
    },
    // ... ES|QL-specific properties (use column names from query)
  };

  // Data View variant
  const dataviewConfig = {
    ...sharedConfig,
    title: 'My Chart (Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'  // for time-series
    },
    // ... Data View-specific properties (use aggregation functions)
  };

  await generateDualFixture(
    'my-chart',  // base filename (creates my-chart.json + my-chart-dataview.json)
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMyChart, import.meta.url);
```

**Key differences between ES|QL and Data View:**
- **Dataset**: `{ esql: 'query' }` vs `{ index: 'pattern' }`
- **Metrics**: Column names from query vs aggregation functions (e.g., `count()`, `average(field)`)
- **XY Charts**: String xAxis vs object `{ type: 'dateHistogram', field: '@timestamp' }`

## File Locations

- **Generator scripts**: `fixture-generator/examples/*.js`
- **Shared utilities**: `fixture-generator/generator-utils.js`
- **Output files**: `fixture-generator/output/*.json`
- **Test fixtures**: `tests/fixtures/*.json` (Python test suite)

## Quick Reference

```bash
# Build Docker image
cd fixture-generator && make build

# Generate all fixtures
cd fixture-generator && make run

# Generate one fixture
cd fixture-generator && make run-example EXAMPLE=gauge.js

# Verify output exists
ls -lh fixture-generator/output/

# Validate JSON
cat fixture-generator/output/gauge.json | python -m json.tool

# Run Python tests
make check

# Debug in container
cd fixture-generator && make shell
```

## Example: Adding a New Generator

```bash
# 1. Create new generator file
cat > fixture-generator/examples/my-chart.js << 'EOF'
#!/usr/bin/env node
import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateMyChart() {
  const config = {
    chartType: 'metric',
    title: 'My Custom Chart',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT()'
    },
    value: 'count'
  };

  await generateFixture(
    'my-chart.json',
    config,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMyChart, import.meta.url);
EOF

# 2. Test it runs
cd fixture-generator
make run-example EXAMPLE=my-chart.js

# 3. Verify output
cat output/my-chart.json | head -20

# 4. Add to generate-all.js if needed
# Edit generate-all.js to import and register your generator

# 5. Test full generation
make run

# 6. Run project tests
cd ..
make check

# 7. Only now commit
git add fixture-generator/examples/my-chart.js
git commit -m "feat: add my-chart fixture generator"
```

## Summary for Agents

**Before you commit any generator code:**

1. ✅ Run `cd fixture-generator && make run-example EXAMPLE=your-file.js`
2. ✅ Verify `fixture-generator/output/your-file.json` exists
3. ✅ Check JSON is valid with `python -m json.tool`
4. ✅ Run `make check` from project root
5. ✅ Only then git add/commit/push

**If you cannot run Docker**, clearly state this in your response and ask the user to test before merging.
