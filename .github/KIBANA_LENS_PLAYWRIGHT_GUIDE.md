# Kibana Lens Playwright Automation Guide

Step-by-step instructions for automating Kibana Lens visualization creation
via Playwright MCP browser tools. These steps have been validated against
Kibana 9.3.0 with the bootstrap data from `scripts/bootstrap-explore-kibana.sh`.

## Prerequisites

- Kibana running at `http://localhost:5601` (no auth, `xpack.security.enabled=false`)
- Elasticsearch at `http://localhost:9200`
- Seeded indices: `logs-default-generic`, `metrics-default-generic`
- Playwright MCP tools available (`browser_navigate`, `browser_snapshot`,
  `browser_click`, `browser_type`, `browser_fill_form`, `browser_wait_for`,
  `browser_press_key`, `browser_take_screenshot`)

## Key Patterns

### Always take snapshots, not screenshots, for interaction

Use `browser_snapshot` to get the accessibility tree with element `ref` values
for clicking. Use `browser_take_screenshot` only for visual verification.
Element refs change after every interaction — always re-snapshot before clicking.

### Wait for Kibana to load after navigation

```
browser_navigate  -> url: http://localhost:5601/app/lens
browser_wait_for  -> textGone: "Loading Elastic"
```

### Kibana comboboxes are NOT `<select>` elements

Kibana uses EUI comboboxes. Do NOT use `browser_fill_form` with type `combobox`.
Instead:

1. `browser_type` into the combobox ref with the search text
2. `browser_snapshot` to find the matching option
3. `browser_click` on the option ref

Example:

```
browser_type  -> ref: <combobox-ref>, text: "log.level"
browser_snapshot
browser_click -> ref: <option-ref>  (the matching option in the dropdown)
```

### Closing dialogs and popovers

- Click "Close" or "Back" buttons visible in the snapshot
- Or use `browser_press_key` with `Escape`

## Step-by-Step: Create a Data View

If Lens shows "How do you want to explore your data?" with a "Create data view"
button, a data view is needed.

1. **Click "Create data view"** button
2. **Fill the form** using `browser_fill_form`:
   - Name: `logs-default-generic` (or your target index)
   - Index pattern: `logs-default-generic`
3. The timestamp field (`@timestamp`) auto-populates
4. **Click "Save data view to Kibana"**

The data view is now available. If one already exists, Lens opens directly to
the editor.

## Step-by-Step: Create a Visualization in Lens

### 1. Navigate to Lens

```
browser_navigate -> url: http://localhost:5601/app/lens
browser_wait_for -> textGone: "Loading Elastic"
```

### 2. Verify data is visible

The bootstrap script seeds data with relative timestamps that fall within the
default "Last 15 minutes" range. No time picker changes should be needed.

After navigating, the field list panel should show "N available fields" (not 0).
If the field list is empty, the bootstrap may not have seeded data recently
enough — re-run `bash scripts/bootstrap-explore-kibana.sh` to refresh timestamps.

### 3. Choose chart type

1. Click the chart type button in the Config panel (e.g., "Bar")
2. A dropdown appears with all chart types:
   - **Bar**, **Line**, **Area**, **Metric**, **Table**, **Pie**, **Gauge**,
     **Heat map**, **Waffle**, **Region map**, **Treemap**, **Tag cloud**,
     **Mosaic**, Legacy Metric
3. Click the desired option (e.g., "Pie")

The Config panel axes update to match the chart type:
- Pie: "Slice by" (dimension) + "Metric"
- Bar: "Horizontal axis" + "Vertical axis" + "Breakdown"
- etc.

### 4. Configure dimensions (Slice by / Axes)

Click the "Add or drag-and-drop a field to ..." button for the desired slot.
A configuration dialog opens.

#### Choosing a function

The dialog shows available functions:

**Dimension functions** (for Slice by, Horizontal axis, Breakdown):
- **Date histogram** — bucket by time intervals
- **Filters** — custom filter buckets
- **Intervals** — numeric range buckets
- **Top values** — most common field values (most common for pie slices)

**Metric functions** (for Metric, Vertical axis):
- **Count** — document count (no field needed)
- **Average**, **Sum**, **Min**, **Max**, **Median** — field aggregations
- **Percentile**, **Percentile rank** — distribution metrics
- **Unique Count** — cardinality
- **Last value** — most recent value
- **Standard deviation**
- **Counter rate**, **Cumulative sum**, **Differences**, **Moving average** —
  pipeline aggregations (may be disabled depending on context)

Click the function name to select it.

#### Choosing a field

After selecting a function that requires a field:
1. **Type** into the Field combobox using `browser_type`
2. **Snapshot** to see matching options
3. **Click** the matching option

#### Additional dimension settings

After selecting function + field, the dialog expands to show:
- **Number of values** (for Top values): spinbutton, default 5
- **Rank by**: combobox — Alphabetical, Rarity, Significance, Custom,
  Count of records
- **Rank direction**: Ascending / Descending buttons
- **Collapse by**: None, Sum, Min, Max, Average
- **Advanced** (expandable):
  - Include documents without the selected field (switch)
  - Group remaining values as "Other" (switch, default on)
  - Enable accuracy mode (switch)
  - Include values / Exclude values (combobox filters)

#### Additional metric settings

- **Normalize by unit**: None, per second, per minute, per hour, per day
- **Filter by**: custom filter
- **Reduced time range**: combobox
- **Time shift**: combobox
- **Hide zero values**: switch (default on)

#### Appearance (per-dimension)

At the bottom of the dimension dialog:
- **Name**: textbox to override the display label
- **Value format** (metrics only): combobox — Default, Number, Percent, Bytes, etc.
- **Color mapping** (dimensions only): "Edit colors" button

Click **Close** to dismiss the configuration dialog.

### 5. Customize appearance

#### Legend (toolbar button)

- **Visibility**: Auto / Show / Hide
- **Width**: combobox (Small, Medium, Large, Extra Large)
- **Label truncation**: switch + Line limit spinbutton

#### Style (toolbar button)

**Pie/Donut specific:**
- **Donut hole**: combobox — None, Small, Medium, Large
  - Open via the "Open list of options" button next to the combobox
  - Click the desired option in the dropdown listbox

**Titles and text:**
- **Slice labels**: Hide / Inside / Auto
- **Slice values**: Hide / Integer / Percentage
- **Decimal places**: spinbutton

**Bar/Line/Area specific:**
- Axis titles, grid lines, etc. (varies by chart type)

### 6. Color mapping

1. Click "Edit colors" in the Slice config dialog
2. The "Assign colors to terms" dialog opens:
   - **Color palette**: button — Elastic (default), or other palettes
   - **Mode**: Categorical / Gradient
   - **Color assignments**: initially empty
3. Click **"Add all unassigned terms"** to auto-populate with current values
4. For each term, click **"Pick a color"** to open the color picker:
   - **Colors tab**: palette swatches (e.g., `#f6726a` for red, `#16c5c0`
     for teal, `#61a2ff` for blue, `#eaae01` for yellow)
   - **Custom tab**: hex input for arbitrary colors
   - **Neutral colors**: grayscale options
5. Click a color swatch to assign it
6. Press **Escape** to close the color picker popover
7. Click **Back** to return to the Slice dialog

### 7. Save the visualization

1. Click **Save** in the top-right toolbar
2. Fill in:
   - **Title**: descriptive name
   - **Description**: optional
3. Choose destination:
   - **Existing**: add to existing dashboard
   - **New**: create new dashboard
   - **None**: save to library only (recommended for export)
4. Click **"Save and add to library"** (or "Save and go to Dashboard")

The URL updates to include the saved object ID:
`/app/lens#/edit/<saved-object-id>`

## Exporting the Saved Object

After saving, extract the ID from the URL and export via API:

```bash
SAVED_OBJECT_ID="<id-from-url>"
curl -s -X POST "http://localhost:5601/api/saved_objects/_export" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d "{\"objects\":[{\"type\":\"lens\",\"id\":\"${SAVED_OBJECT_ID}\"}],\"includeReferencesDeep\":true}"
```

The response is NDJSON with:
1. The `index-pattern` (data view) object
2. The `lens` object with full state
3. An export summary line

Save to `artifacts/kibana-saved-objects/<name>.ndjson`.

## Common Pitfalls

1. **"Empty dataset" tip**: Appears when no data exists in the current time
   range. The bootstrap seeds relative timestamps so this should not happen.
   If it does, re-run the bootstrap script to refresh timestamps.

2. **Stale element refs**: Every UI interaction invalidates previous refs.
   Always `browser_snapshot` before clicking.

3. **Monaco editor (ES|QL)**: The ES|QL query editor uses Monaco which
   intercepts pointer events. Standard `browser_click` and `browser_type` on
   the textarea ref will timeout. Instead use `browser_run_code`:
   ```js
   async (page) => {
     const editor = page.locator('.monaco-editor').first();
     await editor.click({ force: true });
     await page.keyboard.press('ControlOrMeta+A');
     await page.keyboard.press('Backspace');
     await page.keyboard.type('FROM logs-default-generic | STATS count=COUNT(*) BY log.level', { delay: 20 });
   }
   ```
   After typing, dismiss autocomplete with `Escape`, then click "Run query".
   Prefer data view + Lens UI over ES|QL when possible.

4. **Combobox errors**: `browser_fill_form` with type `combobox` will fail
   with "Element is not a `<select>` element". Use `browser_type` + click
   approach instead.

5. **Multiple "Close" buttons**: When nested dialogs are open, the generic
   "Close" selector may match the wrong one. Use the specific ref from the
   most recent snapshot.

6. **Color picker popovers**: These are floating dialogs. Close them with
   Escape before trying to interact with elements behind them.

7. **Unsaved work dialog**: Navigating away from Lens with unsaved changes
   triggers a `beforeunload` dialog. Handle it with `browser_handle_dialog`
   (accept: true), or it may auto-dismiss.

8. **Chart type switching warnings**: Some chart types show warnings when
   switching:
   - "Changing to this visualization modifies the current configuration"
     (Gauge, Legacy Metric)
   - "Changing to this visualization clears the current configuration"
     (Region map)

9. **Metric dialog Method toggle**: The metric configuration dialog has a
   "Quick function" / "Formula" toggle. The default is "Quick function".
   Pipeline aggregations (Counter rate, Cumulative sum, Differences, Moving
   average) may be disabled depending on context.

## Chart Type Config Panel Reference

Each chart type has different slots in the Config panel:

| Chart type | Slots |
|------------|-------|
| **Bar** | Horizontal axis (Optional), Vertical axis, Breakdown (Optional), Stacking toggle |
| **Line** | Horizontal axis (Optional), Vertical axis, Breakdown (Optional) |
| **Area** | Horizontal axis (Optional), Vertical axis, Breakdown (Optional), Stacking toggle |
| **Pie** | Slice by (Optional, multi), Metric |
| **Table** | Rows (Optional), Split metrics by (Optional), Metrics (multi) |
| **Metric** | Primary metric, Secondary metric (Optional), Maximum value (Optional), Break down by (Optional) |
| **Gauge** | Metric, Goal (Optional), Minimum value (Optional), Maximum value (Optional) |
| **Heat map** | Horizontal axis, Vertical axis (Optional), Cell value |
| **Waffle** | Slice by (Optional), Metric, Maximum value (Optional) |
| **Treemap** | Group by (Optional, multi), Metric |
| **Tag cloud** | Tags, Metric |
| **Mosaic** | Horizontal axis, Vertical axis (Optional), Metric |

### Table-specific settings

In the dimension/metric config dialog for Table charts:
- **Text alignment**: Left / Center / Right buttons (metrics default to Right)
- **Color by value**: None / Cell / Text buttons
- **Hide column**: switch
- **Directly filter on click**: switch (dimensions only)
- **Summary Row**: combobox (None, Sum, Average, etc.) — metrics only

### Metric-specific settings

The Metric chart type shows big number tiles:
- **Primary metric**: the main KPI value (has color swatch for threshold coloring)
- **Secondary metric**: shown smaller below the primary
- **Maximum value**: enables a progress bar behind the metric
- **Break down by**: splits into multiple tiles

## Step-by-Step: Create an ES|QL Visualization

ES|QL visualizations are created from a **Dashboard**, not from Lens directly.

### 1. Create or open a Dashboard

```
browser_navigate -> url: http://localhost:5601/app/dashboards
browser_wait_for -> textGone: "Loading Elastic"
```

Click "Create a dashboard" or open an existing one.

### 2. Add an ES|QL panel

1. Click the **Add** button in the top toolbar
2. Click **New panel** in the dropdown
3. Click **ES|QL** in the panel type list

This opens a side panel with a Monaco code editor (default query: `FROM logs* | LIMIT 10`)
and a Lens-style visualization config panel below it.

### 3. Edit the ES|QL query

The Monaco editor intercepts pointer events — you CANNOT use `browser_click`
or `browser_type` on the textbox ref. Instead use `browser_run_code`:

```js
async (page) => {
  const editor = page.locator('.monaco-editor').first();
  await editor.click({ force: true });
  await page.keyboard.press('ControlOrMeta+A');
  await page.keyboard.press('Backspace');
  await page.keyboard.type('FROM logs-default-generic | STATS count=COUNT(*) BY log.level', { delay: 20 });
}
```

After typing:
1. Press **Escape** to dismiss autocomplete suggestions
2. Click the **Run query** button to execute

The visualization updates and the config panel populates with the query columns.

### 4. Configure the visualization

The config panel works identically to Lens — same chart types, same axis
configuration. Click the chart type button to switch (e.g., from Table to Pie).

### 5. Apply and close

Click **Apply and close** to add the panel to the dashboard.

## Saved Object Structure Reference (Pie/Donut)

Key fields in the exported `lens` saved object `attributes.state`:

```
visualization:
  shape: "donut" | "pie"
  layers[0]:
    categoryDisplay: "inside" | "default" | "hide"
    numberDisplay: "value" | "percent" | "hidden"
    emptySizeRatio: 0.54           # donut hole size (0 = pie, ~0.54 = medium)
    legendDisplay: "default" | "show" | "hide"
    primaryGroups: ["<column-id>"]  # slice-by column
    metrics: ["<column-id>"]        # metric column
    colorMapping:
      paletteId: "default"
      colorMode: { type: "categorical" }
      assignments:
        - rules: [{ type: "raw", value: "error" }]
          color: { type: "categorical", paletteId: "default", colorIndex: 6 }
          touched: true

datasourceStates.formBased.layers.<layer-id>.columns:
  <slice-column-id>:
    operationType: "terms"
    sourceField: "log.level"
    params:
      size: 5
      orderBy: { type: "column", columnId: "<metric-column-id>" }
      orderDirection: "desc"
      otherBucket: true
  <metric-column-id>:
    operationType: "count"
    sourceField: "___records___"
```
