# Kibana Lens Playwright Automation Guide

Validated against Kibana 9.3.0 with bootstrap data from `scripts/bootstrap-explore-kibana.sh`.

**Prerequisites:** Kibana at `http://localhost:443` (no auth), Elasticsearch at `http://localhost:9200`, seeded indices `logs-default-generic` / `metrics-default-generic`, data views `logs-*` / `metrics-*`.

## Essential Patterns

- **Prefer `browser_run_code` for known workflows.** Batch multiple Kibana interactions in a single call using Playwright role selectors (e.g., `page.getByRole('button', { name: 'Save' })`). This is far more efficient than individual snapshot→click→snapshot chains. See the recipes below.
- **Use snapshots only for discovery.** When you don't know what's on the page, save a snapshot to disk and grep it:

  ```text
  browser_snapshot(filename="/tmp/gh-aw/agent/page.md")
  ```

  ```bash
  grep 'button.*Legend\|button.*Save' /tmp/gh-aw/agent/page.md
  ```

- **`browser_click` and `browser_wait_for` return inline diffs.** Don't take an extra `browser_snapshot` after every click — the response already contains changed elements with fresh refs. Only save a new snapshot when you need to search a full page.
- **Wait after navigation.** `browser_navigate` then `browser_wait_for` with `textGone: "Loading Elastic"`.
- **Close dialogs** using a scoped locator in `browser_run_code`, for example `await page.getByRole('dialog').getByRole('button', { name: 'Close', exact: true }).click()`, or use `browser_press_key` with `Escape`.
- **Exit editors deliberately.** Opening panel editors may trigger "Unsaved changes" prompts. Use `browser_handle_dialog(accept: true)` or exit via "Exit without saving".
- **Keep `browser_run_code` return values small.** Return a short status string, not full API responses.

## `browser_run_code` Recipes

### Navigate to Lens and wait for load

```js
async (page) => {
  await page.goto('http://localhost:443/app/lens');
  await page.getByText('Loading Elastic').first().waitFor({ state: 'hidden' });
  const tip = page.getByRole('button', { name: "Don't show again" });
  if (await tip.isVisible({ timeout: 1000 }).catch(() => false)) await tip.click();
  return 'Lens ready';
}
```

### Switch chart type

```js
async (page) => {
  await page.locator('[data-test-subj="lnsChartSwitchPopover"]').click();
  await page.getByRole('option', { name: 'Pie' }).click(); // or Line, Bar, Area, Metric, Gauge, Table, etc.
  return 'Switched to Pie';
}
```

### Add a dimension or metric to a slot

```js
async (page) => {
  await page.getByRole('button', { name: 'Add or drag-and-drop a field to Slice by' }).click();
  await page.getByRole('button', { name: 'Top values' }).waitFor({ state: 'visible' });
  await page.getByRole('button', { name: 'Top values' }).click();
  await page.getByRole('combobox', { name: 'Field' }).waitFor({ state: 'visible' });
  await page.getByRole('combobox', { name: 'Field' }).fill('log.level');
  await page.getByRole('option', { name: /log\.level/ }).waitFor({ state: 'visible' });
  await page.getByRole('option', { name: /log\.level/ }).click();
  await page.getByRole('button', { name: 'Close', exact: true }).click();
  return 'Added Top 5 values of log.level to Slice by';
}
```

### Set legend width

```js
async (page) => {
  await page.getByRole('button', { name: 'Legend' }).click();
  await page.getByRole('button', { name: /Width/ }).waitFor({ state: 'visible' });
  await page.getByRole('button', { name: /Width/ }).click();
  await page.getByRole('option', { name: 'Extra large' }).waitFor({ state: 'visible' });
  await page.getByRole('option', { name: 'Extra large' }).click();
  return 'Legend set to Extra large';
}
```

### Set time range

```js
async (page) => {
  await page.getByRole('button', { name: 'Date quick select' }).click();
  await page.getByRole('spinbutton', { name: 'Time value' }).clear();
  await page.getByRole('spinbutton', { name: 'Time value' }).fill('1');
  // Time unit is a native <select>, so use selectOption (not fill + click)
  await page.getByRole('combobox', { name: 'Time unit' }).selectOption('y');
  await page.getByRole('button', { name: 'Apply', exact: true }).waitFor({ state: 'visible' });
  await page.getByRole('button', { name: 'Apply', exact: true }).click();
  return 'Time range set to last 1 year';
}
```

### Edit ES|QL in Monaco editor

```js
async (page) => {
  const editor = page.locator('.monaco-editor').first();
  await editor.click({ force: true });
  await page.keyboard.press('ControlOrMeta+A');
  await page.keyboard.press('Backspace');
  await page.keyboard.type('FROM logs-* | STATS count=COUNT(*) BY log.level', { delay: 20 });
  await page.keyboard.press('Escape');
  return 'ES|QL query entered';
}
```

### Check dashboard panels for errors

After navigating to a dashboard, check whether panels rendered or show errors.
Panels with errors display messages like "Counter rate requires a date histogram"
or "No results found" inside a `<figure>` element.

```js
async (page) => {
  const figures = await page.locator('figure').allTextContents();
  const errors = figures.filter(t => /error|requires|failed|invalid|No results/i.test(t));
  return errors.length === 0
    ? `All ${figures.length} panels rendered OK`
    : `ERRORS: ${JSON.stringify(errors)}`;
}
```

### Open a panel's Lens editor from a dashboard

Panel action buttons are hidden until you hover. Use `data-test-subj` selectors,
not role-based names like `"Panel options for ..."` (those don't exist).

```js
async (page) => {
  // Hover the panel to reveal action buttons
  await page.locator('[data-test-subj="embeddablePanel"]').first().hover();
  await page.waitForTimeout(500);
  // Click the edit button (pencil icon, only visible on hover)
  await page.locator('[data-test-subj="embeddablePanelAction-editPanel"]').click({ force: true });
  await page.waitForTimeout(3000);
  return 'Lens editor opened';
}
```

For a specific panel when multiple exist, scope by title:

```js
async (page) => {
  const panel = page.locator('[data-test-subj="embeddablePanel"]', { has: page.getByText('My Panel Title') });
  await panel.hover();
  await page.waitForTimeout(500);
  await panel.locator('[data-test-subj="embeddablePanelAction-editPanel"]').click({ force: true });
  await page.waitForTimeout(3000);
  return 'Opened editor for My Panel Title';
}
```

### Import a compiled dashboard

```js
async (page) => {
  await page.goto('http://localhost:443/app/management/kibana/objects');
  await page.getByText('Loading Elastic').first().waitFor({ state: 'hidden' });
  await page.getByRole('button', { name: 'Import' }).click();
  const fileInput = page.locator('input[type="file"]');
  await fileInput.waitFor({ state: 'attached' });
  await fileInput.setInputFiles('/tmp/gh-aw/agent/compiled/compiled_dashboards.ndjson');
  await page.getByRole('dialog').getByRole('button', { name: 'Import', exact: true }).click();
  await page.getByText('Successfully imported').waitFor({ state: 'visible', timeout: 10000 }).catch(() => {});
  const success = await page.getByText('Successfully imported').isVisible().catch(() => false);
  return success ? 'Import succeeded' : 'Import may have failed — check page';
}
```

### Open Style or Legend toolbar popover

```js
async (page) => {
  await page.getByRole('button', { name: 'Style' }).click();
  return 'Style popover opened';
}
```

### Full example: create a pie chart with extra_large legend

```js
async (page) => {
  await page.locator('[data-test-subj="lnsChartSwitchPopover"]').click();
  await page.getByRole('option', { name: 'Pie' }).waitFor({ state: 'visible' });
  await page.getByRole('option', { name: 'Pie' }).click();

  await page.getByRole('button', { name: 'Add or drag-and-drop a field to Slice by' }).waitFor({ state: 'visible' });
  await page.getByRole('button', { name: 'Add or drag-and-drop a field to Slice by' }).click();
  await page.getByRole('button', { name: 'Top values' }).waitFor({ state: 'visible' });
  await page.getByRole('button', { name: 'Top values' }).click();
  await page.getByRole('combobox', { name: 'Field' }).waitFor({ state: 'visible' });
  await page.getByRole('combobox', { name: 'Field' }).fill('log.level');
  await page.getByRole('option', { name: /log\.level/ }).waitFor({ state: 'visible' });
  await page.getByRole('option', { name: /log\.level/ }).click();
  await page.getByRole('button', { name: 'Close', exact: true }).click();

  await page.getByRole('button', { name: 'Add or drag-and-drop a field to Metric' }).waitFor({ state: 'visible' });
  await page.getByRole('button', { name: 'Add or drag-and-drop a field to Metric' }).click();
  await page.getByRole('button', { name: 'Count', exact: true }).waitFor({ state: 'visible' });
  await page.getByRole('button', { name: 'Count', exact: true }).click();
  await page.getByRole('button', { name: 'Close', exact: true }).click();

  await page.getByRole('button', { name: 'Legend' }).click();
  await page.getByRole('button', { name: /Width/ }).waitFor({ state: 'visible' });
  await page.getByRole('button', { name: /Width/ }).click();
  await page.getByRole('option', { name: 'Extra large' }).waitFor({ state: 'visible' });
  await page.getByRole('option', { name: 'Extra large' }).click();

  return 'Pie chart created with log.level, count, extra_large legend';
}
```

## Create a Lens Visualization

1. **Navigate:** `browser_navigate` to `http://localhost:443/app/lens`, wait for load.
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

### Gauge Color Range Editor Notes

- Kibana's range editor may normalize row display (for example, final row shown as `<= max`) instead of mirroring raw stop arrays one-to-one.
- For number ranges, UI labels like "Suggested value" can refer to gauge bounds and are easy to confuse with palette stop rows; verify both controls explicitly.
- Open bounds (`range_min: null` / `range_max: null`) can appear as disabled/auto edge rows with only interior boundaries shown as explicit stop inputs.

## ES|QL Visualizations

ES|QL panels are added from a **Dashboard** (not Lens directly): Dashboard → Add → New panel → ES|QL. The Monaco editor requires `browser_run_code` — see the ES|QL recipe above. After entering the query: Escape (dismiss autocomplete) → click "Run query". The config panel then works identically to Lens. Click "Apply and close" to add to dashboard.

## Exporting Saved Objects

```bash
mkdir -p artifacts/kibana-saved-objects
SAVED_OBJECT_ID="<id-from-url>"
curl -fsS -X POST "http://localhost:443/api/saved_objects/_export" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d "{\"objects\":[{\"type\":\"lens\",\"id\":\"${SAVED_OBJECT_ID}\"}],\"includeReferencesDeep\":true}" \
  -o "artifacts/kibana-saved-objects/<name>.ndjson"
```
Returns NDJSON: index-pattern, lens object, export summary.

## Validation Rule: Do Not Re-Export Imports

Re-exporting a saved object that was just imported is **not** a valid correctness test. That only proves round-trip persistence for the same JSON payload, not whether Kibana's editor interprets and displays settings as expected.

Use this validation sequence instead:
1. Import compiled artifact.
2. Open panel in **Edit visualization**.
3. Verify visible editor controls (shape, range type, min/max, stops, etc.) match expectations.
4. Confirm rendered panel appearance on dashboard.

Only treat export diffs as supplemental evidence after UI editor checks pass.

Some palette parameters (for example `continuity`) may not be exposed in the current Kibana editor for certain chart types. In those cases:
- do not fail UI-parity solely because the control is absent,
- verify all visible editor controls and rendered behavior,
- then use export checks only as supplemental evidence for the non-exposed field.

## Common Pitfalls

1. **Monaco editor** — standard click/type times out. Must use `browser_run_code` with `force: true` (see ES|QL recipe above).
2. **Comboboxes** — Kibana uses EUI comboboxes, not `<select>`. In `browser_run_code`: `.fill()` to filter, then `.getByRole('option', ...)` to select. With individual tool calls: `browser_type` to filter, save snapshot to disk, `grep 'option.*value'` to find the ref, then `browser_click`. Never use `browser_fill_form` with `combobox` type. **Exception:** the time range "Time unit" IS a native `<select>` — use `selectOption()` for that one.
3. **Multiple "Close" buttons** — use `{ name: 'Close', exact: true }` or scope to a dialog inside `browser_run_code`: `await page.getByRole('dialog').getByRole('button', { name: 'Close', exact: true }).click()`.
4. **Color picker popovers** — close with Escape before interacting behind them.
5. **Unsaved work dialog** — handle `beforeunload` with `browser_handle_dialog` (accept: true).
6. **Chart type switching** — Gauge/Legacy Metric warn "modifies configuration"; Region map warns "clears configuration".
7. **Chart type button name changes** — after switching chart type, the button text changes (e.g., "Bar" → "Pie"). Use `[data-test-subj="lnsChartSwitchPopover"]` instead of matching by name.
8. **Metric Method toggle** — dialog has Quick function / Formula toggle; pipeline aggregations may be disabled.
9. **False-positive export checks** — exporting an object you just imported does not validate UI/editor parity.

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
