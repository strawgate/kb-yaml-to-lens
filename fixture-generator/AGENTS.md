# Agent Guidelines: Fixture Generator

> Docker-based JavaScript fixture generator using Kibana's official LensConfigBuilder API

---

## Critical Rules — READ THIS FIRST

### Fixture Generation is Required

We're building a compiler that targets Kibana's JSON format. The fixture generator reliably produces valid Kibana JSON by using Kibana's official APIs. This takes a couple of minutes to run, which is much faster than creating fixtures manually.

**When creating or modifying fixture generator files:**

1. Run `cd fixture-generator && make build` (if Docker image doesn't exist)
2. Run `cd fixture-generator && make run-example EXAMPLE=<your-file>.js`
3. Verify output file exists in `fixture-generator/output/`
4. Inspect the output JSON to ensure it's valid
5. Commit BOTH the generator script AND the output JSON files

**Why this matters:**

- Ensures the compiler produces JSON that actually works in Kibana
- Provides accurate reference for what Kibana expects
- Catches schema changes when Kibana updates
- Faster than creating fixtures manually

**If you can't run Docker:**

State this clearly in your response and request that the user run `cd fixture-generator && make run-example EXAMPLE=<file>.js` to verify the output before merging. Don't commit untested generator code.

---

## Quick Reference

### Essential Commands

| Command | Purpose |
| ------- | ------- |
| `make ci` | Run CI checks (build + test-import) |
| `make fix` | No linting (placeholder for consistency) |
| `make build` | Build Docker image (first time only, ~6 minutes) |
| `make run` | Generate all fixtures |
| `make run-example EXAMPLE=file.js` | Generate single fixture |
| `make shell` | Debug in Docker container |
| `make test-import` | Test that LensConfigBuilder imports |
| `make clean` | Clean output directory |

### Common Workflow

```bash
# First time setup
cd fixture-generator
make build

# Generate all fixtures
make run

# Generate one fixture
make run-example EXAMPLE=metric-basic.js

# Verify output
ls -lh output/
cat output/metric-basic.json | python -m json.tool | head -50
```

---

## Fixture Generation Verification Checklist

When creating or modifying fixture generators, complete this checklist:

- [ ] Created/modified generator script in `examples/`
- [ ] Ran `make build` (if Docker image doesn't exist)
- [ ] Ran `make run-example EXAMPLE=<your-file>.js`
- [ ] Verified `output/<your-file>.json` exists
- [ ] Verified `output/<your-file>-dataview.json` exists (for dual generators)
- [ ] Inspected JSON structure with `cat output/<your-file>.json | python -m json.tool | head -100`
- [ ] Compared fixture to compiler output (if applicable)
- [ ] Ran `make ci` from project root - all tests pass
- [ ] Committed changes

Copy this checklist into your response and check off each item as you complete it.

---

## How to Run Fixture Generation

### Prerequisites Check

```bash
docker --version
make --version
```

### Running Generators

The fixture generator runs inside Docker because it requires Kibana's `@kbn/lens-embeddable-utils` package.

**Generate all fixtures:**

```bash
cd fixture-generator
make run
```

**Generate single fixture:**

```bash
cd fixture-generator
make run-example EXAMPLE=metric-basic.js
```

**Verify output:**

```bash
ls -lh fixture-generator/output/
cat fixture-generator/output/metric-basic.json | head -20
```

---

## Development Workflow

### 1. Make Your Changes

Edit generator files in `fixture-generator/examples/`.

### 2. Test Your Changes

```bash
cd fixture-generator
make run-example EXAMPLE=your-new-generator.js
```

### 3. Verify Output

```bash
cat output/your-new-generator.json | python -m json.tool | head -50
```

### 4. Run Full Test Suite

```bash
cd ..
make ci  # Or: make check (alias)
```

### 5. Commit Only After Testing

Only commit after:

- ✅ Generator runs successfully in Docker
- ✅ Output JSON is created
- ✅ Output JSON is valid
- ✅ `make ci` passes

---

## Creating New Dual Generators

Most new generators should use the dual-generation pattern to create both ES|QL and Data View variants:

```javascript
#!/usr/bin/env node
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateMyChart() {
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
      timeFieldName: '@timestamp'
    },
    // ... Data View-specific properties (use aggregation functions)
  };

  await generateDualFixture(
    'my-chart',
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
- **Metrics**: Column names from query vs aggregation functions
- **XY Charts**: String xAxis vs object `{ type: 'dateHistogram', field: '@timestamp' }`

---

## Common Issues

### "Cannot find module '@kbn/lens-embeddable-utils'"

**Cause**: Trying to run generators outside Docker

**Solution**: Always use `make run` or `make run-example`

### "Docker image not found"

**Cause**: Docker image hasn't been built yet

**Solution**: Run `make build`

### "Generator runs but no output file"

**Cause**: Generator script has an error

**Solution**: Check console output. Use `make shell` to debug:

```bash
cd fixture-generator
make shell
# Inside container:
node examples/your-generator.js
```

### "Output JSON is invalid"

**Cause**: LensConfigBuilder received invalid configuration

**Solution**: Check against [Kibana's Lens Config API docs](https://github.com/elastic/kibana/blob/main/dev_docs/lens/config_api.mdx)

---

## File Locations

- **Generator scripts**: `fixture-generator/examples/*.js`
- **Shared utilities**: `fixture-generator/generator-utils.js`
- **Output files**: `fixture-generator/output/*.json`
- **Test fixtures**: Generated fixtures are compared against Python compiler output in test scenarios

---

## Summary for Agents

**Before you commit any generator code:**

1. Run `cd fixture-generator && make run-example EXAMPLE=your-file.js`
2. Verify `fixture-generator/output/your-file.json` exists
3. Check JSON is valid with `python -m json.tool`
4. Run `make ci` from project root
5. Only then git add/commit/push

**If you cannot run Docker**, clearly state this in your response and ask the user to test before merging.
