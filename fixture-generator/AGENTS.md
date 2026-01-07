# Agent Guidelines: Fixture Generator

> Docker-based JavaScript fixture generator using Kibana's LensConfigBuilder API

---

## Code Conventions

See root CODE_STYLE.md and CODERABBIT.md for detailed conventions.

---

## Critical Rules

### Fixture Generation is Required

We're building a compiler targeting Kibana's JSON format. The fixture generator produces valid Kibana JSON using official APIs—much faster than manual creation.

**When creating/modifying fixtures:**

1. Run `cd fixture-generator && make build` (if Docker image doesn't exist)
2. Run `cd fixture-generator && make run-example EXAMPLE=<your-file>.js`
3. Verify output exists in `fixture-generator/output/`
4. Inspect JSON validity
5. Commit BOTH script AND output files

**Why:** Ensures compiler produces JSON that works in Kibana. Provides accurate reference. Catches schema changes.

**If you can't run Docker:** State this clearly and request user verification before merging.

---

## Quick Reference

### Commands

| Command | Purpose |
| ------- | ------- |
| `make ci` | Run CI checks |
| `make build` | Build Docker image (~6 min) |
| `make run` | Generate all fixtures |
| `make run-example EXAMPLE=file.js` | Generate single fixture |
| `make shell` | Debug in container |
| `make test-import` | Test LensConfigBuilder import |
| `make clean` | Clean output directory |

### Workflow

```bash
# First time
cd fixture-generator
make build

# Generate all
make run

# Generate one
make run-example EXAMPLE=metric-basic.js

# Verify
ls -lh output/
cat output/metric-basic.json | python -m json.tool | head -50
```

---

## Verification Checklist

- [ ] Created/modified generator in `examples/`
- [ ] Ran `make build` (if needed)
- [ ] Ran `make run-example EXAMPLE=<file>.js`
- [ ] Verified `output/<file>.json` exists
- [ ] Verified `output/<file>-dataview.json` exists (for dual generators)
- [ ] Inspected JSON: `cat output/<file>.json | python -m json.tool | head -100`
- [ ] Compared to compiler output (if applicable)
- [ ] Ran `make ci` from root - all pass
- [ ] Committed changes

---

## Development Workflow

### 1. Make Changes

Edit generators in `fixture-generator/examples/`.

### 2. Test

```bash
cd fixture-generator
make run-example EXAMPLE=your-generator.js
```

### 3. Verify

```bash
cat output/your-generator.json | python -m json.tool | head -50
```

### 4. Run Full Test

```bash
cd ..
make ci
```

### 5. Commit After Testing

Only after:
- ✅ Generator runs in Docker
- ✅ Output JSON created
- ✅ Output JSON valid
- ✅ `make ci` passes

---

## Creating Dual Generators

Most new generators should create both ES|QL and Data View variants:

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
    // ... ES|QL-specific (use column names from query)
  };

  // Data View variant
  const dataviewConfig = {
    ...sharedConfig,
    title: 'My Chart (Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    // ... Data View-specific (use aggregation functions)
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

**Key differences:**
- **Dataset**: `{ esql: 'query' }` vs `{ index: 'pattern' }`
- **Metrics**: Column names vs aggregation functions
- **XY Charts**: String xAxis vs object `{ type: 'dateHistogram', field: '@timestamp' }`

---

## Common Issues

**"Cannot find module '@kbn/lens-embeddable-utils'"**: Trying to run outside Docker. Use `make run`.

**"Docker image not found"**: Run `make build`.

**"Generator runs but no output"**: Check console output. Debug with `make shell` then `node examples/your-generator.js`.

**"Output JSON invalid"**: Check against [Kibana Lens Config API docs](https://github.com/elastic/kibana/blob/main/dev_docs/lens/config_api.mdx).

---

## File Locations

- **Generator scripts**: `fixture-generator/examples/*.js`
- **Utilities**: `fixture-generator/generator-utils.js`
- **Output**: `fixture-generator/output/*.json`

---

## Summary

**Before committing:**

1. Run `cd fixture-generator && make run-example EXAMPLE=your-file.js`
2. Verify `output/your-file.json` exists
3. Check JSON valid: `python -m json.tool`
4. Run `make ci` from root
5. Then commit

**If you can't run Docker**, state this clearly and ask user to test.
