# Agent Guidelines: Fixture Generator

> Docker-based JavaScript fixture generator using Kibana's official LensConfigBuilder API

---

## Critical Rules — READ THIS FIRST

### ⚠️ MANDATORY FIXTURE GENERATION REQUIREMENT ⚠️

**When creating or modifying ANY fixture generator file, you MUST:**

1. ✅ Run `cd fixture-generator && make build` (if Docker image doesn't exist)
2. ✅ Run `cd fixture-generator && make run-example EXAMPLE=<your-file>.js`
3. ✅ Verify output file exists in `fixture-generator/output/`
4. ✅ Inspect the output JSON to ensure it's valid
5. ✅ Commit BOTH the generator script AND the output JSON files

**This is NOT optional. This is NOT negotiable. There are ZERO exceptions.**

### What "MUST" Means

- **MUST** = You are REQUIRED to do this before committing
- **NEVER** = You are FORBIDDEN from doing this under any circumstances
- If you skip fixture generation, your work will be REJECTED and you will be asked to redo it

### Forbidden Excuses

The following are **EXPLICITLY FORBIDDEN** and will result in your PR being rejected:

❌ "The Docker build takes too long for CI" — The 6-minute build is **cached** after first run
❌ "Not practical in this CI environment" — Docker **IS** available in CI
❌ "This follows existing patterns so testing isn't needed" — **ALL** generators must be tested
❌ "I'll defer to manual validation when needed" — Testing must happen **NOW**, not later
❌ "I can't run Docker" — Then **DO NOT** commit code (see exception below)

### The Only Valid Exception

**IF AND ONLY IF** you genuinely cannot run Docker (e.g., in a truly restricted environment):

1. ✅ Explicitly state: "I cannot run Docker in this environment"
2. ✅ Request: "Please run `cd fixture-generator && make run-example EXAMPLE=<file>.js` and verify the output"
3. ❌ DO NOT commit the generator script until the user confirms it works
4. ❌ DO NOT proceed to the next step until validation is complete

**If you commit untested generator code, it will be rejected regardless of your excuse.**

### Why This Matters

Fixture generators create test data from **real Kibana APIs**. This ensures:

- The compiler produces output that **actually works** in Kibana
- Schema changes in Kibana are **caught immediately**
- We have **verified examples** for every chart type

Skipping fixture generation means shipping **unvalidated code** that may produce invalid Kibana JSON.

---

## Quick Reference

### Essential Commands

| Command | Purpose |
| ------- | ------- |
| `make build` | Build Docker image (first time only, ~6 minutes) |
| `make run` | Generate all fixtures |
| `make run-example EXAMPLE=file.js` | Generate single fixture |
| `make shell` | Debug in Docker container |
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

When creating or modifying fixture generators, you MUST complete this checklist:

- [ ] Created/modified generator script in `examples/`
- [ ] Ran `make build` (if Docker image doesn't exist)
- [ ] Ran `make run-example EXAMPLE=<your-file>.js`
- [ ] Verified `output/<your-file>.json` exists
- [ ] Verified `output/<your-file>-dataview.json` exists (for dual generators)
- [ ] Inspected JSON structure with `cat output/<your-file>.json | python -m json.tool | head -100`
- [ ] Compared fixture to compiler output (if applicable)
- [ ] Ran `make check` from project root - all tests pass
- [ ] Committed changes

**Copy this checklist into your response and check off each item as you complete it.**

---

## How to Run Fixture Generation

### Prerequisites Check

```bash
docker --version
make --version
```

### Running Generators

The fixture generator **MUST** run inside Docker because it requires Kibana's `@kbn/lens-embeddable-utils` package.

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

### 2. Test Your Changes (REQUIRED)

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
make check
```

### 5. Commit Only After Testing

Only commit after:

- ✅ Generator runs successfully in Docker
- ✅ Output JSON is created
- ✅ Output JSON is valid
- ✅ `make check` passes

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

1. ✅ Run `cd fixture-generator && make run-example EXAMPLE=your-file.js`
2. ✅ Verify `fixture-generator/output/your-file.json` exists
3. ✅ Check JSON is valid with `python -m json.tool`
4. ✅ Run `make check` from project root
5. ✅ Only then git add/commit/push

**If you cannot run Docker**, clearly state this in your response and ask the user to test before merging.
