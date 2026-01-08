# Creating Kibana Dashboard Fixtures

Technical guide for developing fixture generators using Kibana's LensConfigBuilder API.

---

## Understanding LensConfigBuilder API Limitations

**IMPORTANT:** The LensConfigBuilder API does NOT expose all Kibana Lens features.

**When a feature is not available via LensConfigBuilder:**

- ❌ **WRONG**: Conclude the feature doesn't exist in Kibana
- ✅ **CORRECT**: Investigate the Kibana codebase to find the underlying JSON structure

**Why this matters:**

The fixture generator uses Kibana's `LensConfigBuilder` API to create test fixtures. This is a **convenience API** for common use cases, but Kibana's underlying Lens visualization engine supports many more options than the builder exposes.

**Example:** ES|QL per-metric color and axis assignment options don't exist in `LensConfigBuilder`, but they DO exist in Kibana's Lens JSON schema. To implement these in our compiler, we need to:

1. Search the Kibana codebase for relevant type definitions (e.g., `YConfig`, `VisualizeEditorFormState`)
2. Examine actual Kibana dashboard exports to see the JSON structure
3. Create view models matching the discovered schema
4. Skip fixture generation (since we can't use LensConfigBuilder)
5. Test by compiling YAML and importing into Kibana

**Always investigate before concluding a feature is unsupported.**

---

## TypeScript Type Checking

Generators use TypeScript with strict type checking to catch invalid LensConfigBuilder properties at development time.

**Benefits:** Catch errors early, IDE autocomplete, no runtime overhead, future-proof when Kibana updates

**Usage:**

- Import types: `import type { LensMetricConfig } from '@kbn/lens-embeddable-utils/config_builder';`
- Annotate configs: `const esqlConfig: LensMetricConfig = { ... };`
- Run checks: `make typecheck` or `make ci`

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

## Development Workflow

1. Edit `examples/` generator (TypeScript `.ts` files)
2. Test: `make run-example EXAMPLE=your-generator.ts`
3. Verify: `cat output/your-generator.json | python -m json.tool | head`
4. Full test: `cd .. && make ci`
5. Commit only after: Type check ✅ Generator runs in Docker ✅ Output created ✅ Valid JSON ✅ `make ci` passes ✅

---

## Verification Checklist

Created/modified `examples/` generator → `make typecheck` → `make pull` (if needed) → `make run-example EXAMPLE=<file>.ts` → verify output files exist → inspect JSON (`python -m json.tool | head`) → `make ci` from root → commit

---

## Common Issues

**"Cannot find module '@kbn/lens-embeddable-utils'"**: Trying to run outside Docker. Use `make run`.

**"Docker image not found"**: Run `make pull`.

**"Generator runs but no output"**: Check console output. Debug with `make shell` then `node examples/your-generator.ts`.

**"Output JSON invalid"**: Check against [Kibana Lens Config API docs](https://github.com/elastic/kibana/blob/main/dev_docs/lens/config_api.mdx).

---

## File Locations

- **Generator scripts**: `fixture-generator/examples/*.ts`
- **Utilities**: `fixture-generator/generator-utils.js`
- **Output**: `fixture-generator/output/*.json`
