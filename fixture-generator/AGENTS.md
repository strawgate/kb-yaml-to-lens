# Agent Guidelines: Fixture Generator

> Docker-based TypeScript fixture generator using Kibana's LensConfigBuilder API

---

## Code Conventions

See root CODE_STYLE.md and CODERABBIT.md for detailed conventions.

---

## Critical Rules

### Fixture Generation is Required

We're building a compiler targeting Kibana's JSON format. The fixture generator produces valid Kibana JSON using official APIs—much faster than manual creation.

**When creating/modifying fixtures:**

1. Run `cd fixture-generator && make build` (if Docker image doesn't exist)
2. Run `cd fixture-generator && make run-example EXAMPLE=<your-file>.ts`
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
| `make ci` | Run CI checks (typecheck + build) |
| `make typecheck` | Run TypeScript type checking |
| `make build` | Build Docker image (~6 min) |
| `make run` | Generate all fixtures |
| `make run-example EXAMPLE=file.ts` | Generate single fixture |
| `make shell` | Debug in container |
| `make test-import` | Test LensConfigBuilder import |
| `make clean` | Clean output directory |

### Workflow

```bash
cd fixture-generator && make build                          # First time
make run                                                     # All fixtures
make run-example EXAMPLE=metric-basic.ts                    # Single fixture
cat output/metric-basic.json | python -m json.tool | head   # Verify
```

---

## TypeScript Type Checking

Generators use TypeScript with strict type checking to catch invalid LensConfigBuilder properties at development time.

**Benefits:** Catch errors early, IDE autocomplete, no runtime overhead, future-proof when Kibana updates

**Usage:**

- Import types: `import type { LensMetricConfig } from '@kbn/lens-embeddable-utils/config_builder';`
- Annotate configs: `const esqlConfig: LensMetricConfig = { ... };`
- Run checks: `make typecheck` or `make ci`

---

## Verification

Created/modified `examples/` generator → `make typecheck` → `make build` (if needed) → `make run-example EXAMPLE=<file>.ts` → verify output files exist → inspect JSON (`python -m json.tool | head`) → `make ci` from root → commit

---

## Development Workflow

1. Edit `examples/` generator (TypeScript `.ts` files)
2. Test: `make run-example EXAMPLE=your-generator.ts`
3. Verify: `cat output/your-generator.json | python -m json.tool | head`
4. Full test: `cd .. && make ci`
5. Commit only after: Type check ✅ Generator runs in Docker ✅ Output created ✅ Valid JSON ✅ `make ci` passes ✅

---

## Creating Dual Generators

Most new generators should create both ES|QL and Data View variants:

```typescript
#!/usr/bin/env node
import type { LensXYConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateMyChart(): Promise<void> {
  const sharedConfig: Partial<LensXYConfig> = {
    chartType: 'xy',
    // ... shared properties
  };

  // ES|QL variant
  const esqlConfig: LensXYConfig = {
    ...sharedConfig,
    chartType: 'xy',
    title: 'My Chart',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp'
    },
    // ... ES|QL-specific (use column names from query)
  };

  // Data View variant
  const dataviewConfig: LensXYConfig = {
    ...sharedConfig,
    chartType: 'xy',
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

**"Generator runs but no output"**: Check console output. Debug with `make shell` then `node examples/your-generator.ts`.

**"Output JSON invalid"**: Check against [Kibana Lens Config API docs](https://github.com/elastic/kibana/blob/main/dev_docs/lens/config_api.mdx).

---

## File Locations

- **Generator scripts**: `fixture-generator/examples/*.ts`
- **Utilities**: `fixture-generator/generator-utils.js`
- **Output**: `fixture-generator/output/*.json`

---

## Summary

**Before commit:** `make typecheck` → `make run-example EXAMPLE=your-file.ts` → verify output exists → validate JSON (`python -m json.tool`) → `make ci` from root → commit

**No Docker?** State clearly, request user testing.
