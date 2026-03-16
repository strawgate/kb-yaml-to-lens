# Explore Agent: Verification Process

You have **two independent verification jobs**. You must complete both
and report results for each separately. Do not skip either one.

---

## Prereq: Read compiler source and examples

Before starting either job, read the relevant compiler source in
`packages/kb-dashboard-core/src/` and at least one example YAML file
for the chart type you are testing.

### YAML format reference

Every YAML file **must** start with a `dashboards:` top-level key. Panels go
under `dashboards[].panels[]` and use a discriminator key (`lens:`, `esql:`,
`vega:`, `markdown:`, `search:`, `links:`, `image:`, or `section:`).

**Base dashboard template** — copy this as your starting point:
```yaml
---
dashboards:
  - id: test-dashboard
    name: Test Dashboard
    description: Verification test
    panels:
      - title: My Metric
        lens:
          type: metric
          data_view: logs-*
          primary:
            aggregation: count
      - title: My Line Chart
        lens:
          type: line
          data_view: logs-*
          y_axis:
            - aggregation: count
```

**Common mistakes to avoid:**
- Use `aggregation: count`, NOT `type: count` — metrics use `aggregation` to
  specify the function (count, average, sum, min, max, unique_count, etc.)
- Use `data_view: logs-*` or `data_view: metrics-*` (the data view **name**),
  NOT the data view UUID
- Seeded data views are `logs-*` and `metrics-*` with ECS-compatible fields:
  - **Both:** `@timestamp`, `service.name`, `host.name`, `host.ip`, `event.dataset`, `event.module`
  - **Logs:** `message`, `log.level`, `http.response.status_code`, `http.response.bytes`,
    `http.request.method`, `url.path`, `user_agent.name`, `service.environment`
  - **Metrics:** `system.cpu.user.pct`, `system.cpu.system.pct`, `system.cpu.total.pct`,
    `system.memory.used.pct`, `system.memory.used.bytes`, `system.load.1`
- Gauge uses `metric:` not `primary:` for its metric slot

### Panel documentation by chart type

| Chart type | Example YAML | Compiler source |
|------------|-------------|-----------------|
| **XY** (line, bar, area) | `packages/kb-dashboard-docs/content/examples/multi-panel-showcase.yaml` | `packages/kb-dashboard-core/src/kb_dashboard_core/panels/charts/xy/` |
| **Metric** | `packages/kb-dashboard-docs/content/examples/metric-formatting-examples.yaml` | `packages/kb-dashboard-core/src/kb_dashboard_core/panels/charts/metric/` |
| **Pie / Donut** | `packages/kb-dashboard-docs/content/examples/multi-panel-showcase.yaml` | `packages/kb-dashboard-core/src/kb_dashboard_core/panels/charts/pie/` |
| **Heatmap** | `packages/kb-dashboard-docs/content/examples/heatmap-examples.yaml` | `packages/kb-dashboard-core/src/kb_dashboard_core/panels/charts/heatmap/` |
| **Gauge** | Real-world examples in `packages/kb-dashboard-docs/content/examples/system/` | `packages/kb-dashboard-core/src/kb_dashboard_core/panels/charts/gauge/` |
| **Treemap** | `samples/treemap.yml` | `packages/kb-dashboard-core/src/kb_dashboard_core/panels/charts/treemap/` |
| **Waffle** | Real-world examples in `packages/kb-dashboard-docs/content/examples/` | `packages/kb-dashboard-core/src/kb_dashboard_core/panels/charts/waffle/` |
| **Tag cloud** | `packages/kb-dashboard-docs/content/examples/multi-panel-showcase.yaml` | `packages/kb-dashboard-core/src/kb_dashboard_core/panels/charts/tagcloud/` |
| **Data table** | Real-world examples in `packages/kb-dashboard-docs/content/examples/` | `packages/kb-dashboard-core/src/kb_dashboard_core/panels/charts/datatable/` |
| **Mosaic** | — | `packages/kb-dashboard-core/src/kb_dashboard_core/panels/charts/mosaic/` |
| **ES\|QL** | `packages/kb-dashboard-docs/content/examples/multi-panel-showcase.yaml` | `packages/kb-dashboard-core/src/kb_dashboard_core/panels/charts/esql/` |

**Additional references:**
- Color mapping: `packages/kb-dashboard-docs/content/examples/color-palette-examples.yaml`
- Dimensions & breakdowns: `packages/kb-dashboard-docs/content/examples/dimensions-example.yaml`
- Full documentation index: `packages/kb-dashboard-docs/content/examples/index.md`

**Always read an example YAML file for the chart type you are working with
before authoring your own.** Do not guess at the YAML structure.

---

## Job 1: YAML → Compile → Kibana (does our compiler produce valid panels?)

**Goal:** Verify that the compiler's output actually works in Kibana.

For each feature you are testing:

1. **Author** a minimal YAML config exercising the feature (using the base
   template above and the example YAML for that chart type).
2. **Compile and upload:**
   ```bash
   uv run kb-dashboard compile --input-file <file> --output-dir /tmp/compiled/ \
     --upload --kibana-url http://host.docker.internal:443
   ```
3. **Navigate** to the dashboard in Playwright and **check for panel errors.**
   Use the "Check dashboard panels for errors" recipe. A successful upload
   does NOT mean the panel works — Kibana may show runtime errors like
   "Counter rate requires a date histogram" or expression failures.
   **Do not skip this step.**
4. **Open** the panel in the Lens editor (use the "Open a panel's Lens editor
   from a dashboard" recipe) and verify:
   - Every YAML setting is reflected in the editor UI controls
   - The panel renders data (not "No results" or an error)
   - Kibana does not show warnings or "invalid" states
5. **Record** the result per feature: YAML used, pass/fail, what you observed.

### Job 1 output format

In your report, use this exact heading and table:

```markdown
## Job 1: Compiler → Kibana

| Feature | YAML | Panel renders? | Editor correct? | Status |
|---------|------|---------------|-----------------|--------|
| count metric | `primary: {aggregation: count}` | Yes | Yes — shows "Count of records" | PASS |
| formula heatmap | `value: {formula: 'counter_rate(...)'}` | No — "requires date histogram" | N/A | BUG |
```

---

## Job 2: Kibana → Export → Compare (does our compiler know all the fields?)

**Goal:** Discover fields and defaults the compiler doesn't know about by
creating panels manually in Kibana and comparing the exported JSON to the
compiler's view models.

1. **Create** fresh panels in the Kibana Lens editor using a wide variety of
   settings. Try edge cases, unusual combinations, and settings you haven't
   seen in the YAML examples. Use different chart types, multiple metrics,
   breakdowns, color mappings, legend positions, etc.
2. **Save** the dashboard and **export** it:
   ```bash
   uv run kb-dashboard fetch <dashboard-id> --output /tmp/exported.ndjson \
     --kibana-url http://host.docker.internal:443
   ```
3. **Inspect** the exported JSON. For each panel, compare the
   `state.visualization` and `state.datasourceStates` against the compiler's
   view models in `packages/kb-dashboard-core/src/`. Look for:
   - Fields Kibana produces that the compiler doesn't emit
   - Default values that differ from the compiler's defaults
   - Structural patterns the compiler gets wrong
4. **Record** each discrepancy with the Kibana JSON snippet and the
   corresponding compiler view model field (or note that it's missing).

### Job 2 output format

In your report, use this exact heading and table:

```markdown
## Job 2: Kibana → Compiler comparison

| Setting created in Kibana | Kibana JSON field | Compiler emits? | Correct? | Status |
|--------------------------|-------------------|-----------------|----------|--------|
| Legend position right | `legendDisplay: "show"`, `legendPosition: "right"` | Yes | Yes | PASS |
| Custom number format | `format: {id: "number", params: {pattern: "0.0%"}}` | No | N/A | GAP |
```

---

## Fields to ignore in exported JSON

When comparing Kibana-exported JSON against the compiler's view models,
**ignore** these runtime artifacts — they are **never** bugs:

- `adHocDataViews` / `indexPatternRefs`
- `migrationVersion` / `typeMigrationVersion` / `coreMigrationVersion`
- Auto-generated `id`, `updatedAt`, `created_at`, `updated_at`, `version`, `namespaces`
- `references[].id` values
- JSON key ordering differences
- `kibanaSavedObjectMeta.searchSourceJSON` default empty filters/query

Only flag a difference as a bug if it affects a **functional setting** —
something that changes how the panel looks or behaves.

---

## Fix-and-verify workflow (when investigating known bugs)

When validating or fixing specific compiler bugs (e.g., from a triage issue):

1. **Reproduce** — Write YAML that triggers the bug, compile, upload, confirm
   the bug in Kibana.
2. **Show the diff** — Create the same panel manually in Kibana, export it,
   compare relevant fields.
3. **Fix it** — Edit the compiler source. Smallest possible change.
4. **Verify** — Recompile and re-upload. Confirm the panel works in Kibana.
5. **Run tests** — `just core test` and `just core lint`. Update snapshots
   if needed.
6. **Report** — YAML config, before/after Kibana behavior, compiler file and
   line changed, test changes.

**Do not skip the Kibana steps.** A fix that was only verified by reading
code is not a verified fix.
