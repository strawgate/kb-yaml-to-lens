# Kibana Lens Playwright Automation Guide

Validated against Kibana 9.3.0 with bootstrap data from `scripts/bootstrap-explore-kibana.sh`.

**Prerequisites:** Kibana at `http://localhost:5601` (no auth), Elasticsearch at `http://localhost:9200`, seeded indices `logs-default-generic` / `metrics-default-generic`, data views `logs-*` / `metrics-*`.

## Essential Patterns

- **Snapshot before every click.** Use `browser_snapshot` for the accessibility tree with `ref` values. Refs invalidate after every interaction. Use `browser_take_screenshot` only for visual verification.
- **Wait after navigation.** `browser_navigate` then `browser_wait_for` with `textGone: "Loading Elastic"`.
- **Comboboxes are NOT `<select>`.** Kibana uses EUI comboboxes. Use `browser_type` into the ref, `browser_snapshot`, then `browser_click` the matching option. Never use `browser_fill_form` with type `combobox`.
- **Close dialogs** with the "Close"/"Back" button ref, or `browser_press_key` with `Escape`.

## Create a Lens Visualization

1. **Navigate:** `browser_navigate` to `http://localhost:5601/app/lens`, wait for load.
2. **Verify data:** Field list should show available fields. Bootstrap seeds relative timestamps within "Last 15 minutes". If empty, re-run `scripts/bootstrap-explore-kibana.sh`.
3. **Choose chart type:** Click the chart type button, select from dropdown (Bar, Line, Area, Metric, Table, Pie, Gauge, Heat map, Waffle, Treemap, Tag cloud, Mosaic).
4. **Configure slots:** Click "Add or drag-and-drop a field" for each slot. Select a function, then a field via the combobox pattern. Click "Close" when done.
5. **Customize appearance:** Use Legend and Style toolbar buttons for chart-specific options.
6. **Save:** Click Save, fill title, choose destination (library recommended for export), click "Save and add to library". Note the saved object ID from the URL.

## Chart Type Slot Reference

| Chart type | Slots |
|------------|-------|
| **Bar/Line/Area** | Horizontal axis, Vertical axis, Breakdown (optional), Stacking toggle (Bar/Area) |
| **Pie** | Slice by (multi), Metric |
| **Table** | Rows, Split metrics by, Metrics (multi) |
| **Metric** | Primary metric, Secondary metric, Maximum value, Break down by |
| **Gauge** | Metric, Goal, Minimum value, Maximum value |
| **Heat map** | Horizontal axis, Vertical axis, Cell value |
| **Waffle** | Slice by, Metric, Maximum value |
| **Treemap** | Group by (multi), Metric |
| **Tag cloud/Mosaic** | Tags/Horizontal axis, Vertical axis (Mosaic), Metric |

## Dimension & Metric Settings

**Dimension functions** (Slice by, Horizontal axis, Breakdown): Date histogram, Filters, Intervals, Top values.

**Metric functions** (Metric, Vertical axis): Count, Average, Sum, Min, Max, Median, Percentile, Percentile rank, Unique Count, Last value, Standard deviation, Counter rate, Cumulative sum, Differences, Moving average.

**Dimension options:** Number of values, Rank by, Rank direction, Collapse by, Advanced (include missing, group as "Other", accuracy mode, include/exclude filters).

**Metric options:** Normalize by unit, Filter by, Reduced time range, Time shift, Hide zero values.

**Appearance (per-dimension/metric):** Name override, Value format (metrics), Color mapping (dimensions via "Edit colors").

**Table-specific:** Text alignment (L/C/R), Color by value (None/Cell/Text), Hide column, Directly filter on click, Summary Row.

**Metric chart:** Primary = main KPI, Secondary = below primary, Maximum = progress bar, Break down by = multiple tiles.

## Color Mapping

1. Click "Edit colors" in dimension config → "Assign colors to terms" dialog
2. Click "Add all unassigned terms" to populate
3. Click "Pick a color" per term → Colors/Custom/Neutral tabs
4. Press Escape to close picker, "Back" to return

## ES|QL Visualizations

ES|QL panels are added from a **Dashboard** (not Lens directly): Dashboard → Add → New panel → ES|QL.

**Monaco editor workaround** — standard `browser_click`/`browser_type` timeout on Monaco. Use `browser_run_code`:
```js
async (page) => {
  const editor = page.locator('.monaco-editor').first();
  await editor.click({ force: true });
  await page.keyboard.press('ControlOrMeta+A');
  await page.keyboard.press('Backspace');
  await page.keyboard.type('FROM logs-default-generic | STATS count=COUNT(*) BY log.level', { delay: 20 });
}
```
After typing: Escape (dismiss autocomplete) → click "Run query". The config panel then works identically to Lens. Click "Apply and close" to add to dashboard.

## Exporting Saved Objects

```bash
mkdir -p artifacts/kibana-saved-objects
SAVED_OBJECT_ID="<id-from-url>"
curl -fsS -X POST "http://localhost:5601/api/saved_objects/_export" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d "{\"objects\":[{\"type\":\"lens\",\"id\":\"${SAVED_OBJECT_ID}\"}],\"includeReferencesDeep\":true}" \
  -o "artifacts/kibana-saved-objects/<name>.ndjson"
```
Returns NDJSON: index-pattern, lens object, export summary.

## Common Pitfalls

1. **Stale refs** — always re-snapshot before clicking.
2. **Monaco editor** — must use `browser_run_code` with `force: true` (see above).
3. **Combobox errors** — `browser_fill_form` with `combobox` type fails; use type + click.
4. **Multiple "Close" buttons** — use the specific ref from the latest snapshot.
5. **Color picker popovers** — close with Escape before interacting behind them.
6. **Unsaved work dialog** — handle `beforeunload` with `browser_handle_dialog` (accept: true).
7. **Chart type switching** — Gauge/Legacy Metric warn "modifies configuration"; Region map warns "clears configuration".
8. **Metric Method toggle** — dialog has Quick function / Formula toggle; pipeline aggregations may be disabled.

## Saved Object Structure Reference (Pie/Donut)

Key fields in exported `lens` object `attributes.state`:
```yaml
visualization:
  shape: "donut" | "pie"
  layers[0]:
    categoryDisplay: "inside" | "default" | "hide"
    numberDisplay: "value" | "percent" | "hidden"
    emptySizeRatio: 0.54           # donut hole (0=pie, ~0.54=medium)
    legendDisplay: "default" | "show" | "hide"
    primaryGroups: ["<column-id>"]  # slice-by
    metrics: ["<column-id>"]
    colorMapping:
      assignments:
        - rules: [{ type: "raw", value: "error" }]
          color: { type: "categorical", paletteId: "default", colorIndex: 6 }

datasourceStates.formBased.layers.<layer-id>.columns:
  <slice-column-id>:
    operationType: "terms"
    sourceField: "log.level"
    params: { size: 5, orderDirection: "desc", otherBucket: true }
  <metric-column-id>:
    operationType: "count"
    sourceField: "___records___"
```
