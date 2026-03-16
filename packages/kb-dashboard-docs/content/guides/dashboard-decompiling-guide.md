# Dashboard Decompiling Guide: Converting Kibana JSON to YAML

This guide covers converting existing Kibana dashboards into kb-yaml-to-lens YAML. It is designed to be consumed by both humans and LLMs performing conversions.

## Quick Reference

**Complete Documentation**: For full schema reference and examples, use [llms-full.txt](https://strawgate.com/kb-yaml-to-lens/llms-full.txt) which contains all project documentation.

**Workflow**:

1. **Fetch** the dashboard NDJSON (`kb-dashboard fetch`) or download it from a repository.
2. **Decompile** into a YAML skeleton: `kb-dashboard decompile dashboard.ndjson -o dashboard.yaml`. This gives you panel stubs with layout, titles, and panel types pre-filled. Each stub includes `TODO(decompile)` comments containing the original Kibana panel JSON.
3. **Fill in panel configs** using the TODO comments as reference. Translate the original Kibana JSON into the YAML schema using the current panel-specific keys (`type`, `data_view`, `metrics`, `dimension`, `breakdown`, `breakdowns`, etc.). Use the [Component Mapping](#component-mapping) section below and the panel type documentation as guides.
4. **Compile** to verify the YAML is valid: `kb-dashboard compile`.
5. **Round-trip validate**: disassemble both the original and compiled NDJSON, then compare them.

## What Decompile Produces

The `decompile` command generates a YAML skeleton, not a complete dashboard. Specifically:

- Dashboard-level metadata (name, id, description) is extracted.
- Every panel gets a stub with the correct `size` and `position` from the grid layout.
- Panel titles are preserved where present.
- Panel types are detected (lens, markdown, links, etc.), but for lens panels the inner configuration is left empty (`lens: {}`). This means the decompiled YAML will **not** compile as-is.
- Each panel stub includes `TODO(decompile)` comments containing the original Kibana panel JSON. These comments are your primary reference for filling in the lens configuration.

You (or an LLM) need to translate the Kibana JSON from the TODO comments into the YAML schema. The [Component Mapping](#component-mapping) section below shows how each Kibana construct maps to YAML.

## JSON-to-YAML Conversion Prompt Scaffold

Use this prompt pattern when asking an LLM to complete a decompiled dashboard. Keep the request scoped to one dashboard at a time.

```text
Complete the decompiled YAML stubs in <yaml_file>. Each panel has TODO comments
containing the original Kibana panel JSON — use these to fill in the lens
configuration (type, data_view, metrics, `dimension`, `breakdown`, `breakdowns`, and related panel-specific fields).

Requirements:
1. Preserve panel layout (size and position are already set).
2. Translate every panel's original JSON into the correct YAML schema.
3. Use the panel type reference and component mapping from the decompiling guide.
4. Omit fields that match default values.
5. After conversion, validate:
   - kb-dashboard compile --input-dir <yaml_dir> --output-dir <compiled_dir>
   - kb-dashboard disassemble <compiled_dir>/output.ndjson -o <compiled_disassembled_dir>
   - kb-dashboard disassemble original.ndjson -o <original_disassembled_dir>
   - kb-dashboard compare <original_disassembled_dir> <compiled_disassembled_dir>
6. Summarize any mismatches found during validation.
```

## Fetching Dashboard from Kibana

Retrieve a dashboard directly from Kibana using a URL or ID:

```bash
# Using dashboard URL
kb-dashboard fetch "https://kibana.example.com/app/dashboards#/view/my-id" \
    --output dashboard.ndjson

# Using dashboard ID
kb-dashboard fetch my-dashboard-id --output dashboard.ndjson
```

**Input Types:**

The `fetch` command accepts two types of input:

1. **Dashboard URL** - Full Kibana dashboard URL (e.g., `https://kibana.example.com/app/dashboards#/view/my-id`)
2. **Dashboard ID** - Plain dashboard ID (e.g., `my-dashboard-id`)

**How it works:**

- If the input looks like a URL, the dashboard ID is extracted from the URL
- Otherwise, the input is treated as a plain dashboard ID

**Authentication Options:**

```bash
# API Key authentication (recommended)
kb-dashboard fetch my-dashboard-id --output dashboard.ndjson \
    --kibana-api-key "your-api-key"

# Username/password authentication
kb-dashboard fetch my-dashboard-id --output dashboard.ndjson \
    --kibana-username user --kibana-password pass

# Specific Kibana space
kb-dashboard fetch my-dashboard-id --output dashboard.ndjson \
    --kibana-space-id "my-space"
```

**Input Formats Supported:**

- **URL (standard):** `https://kibana.example.com/app/dashboards#/view/{id}`
- **URL (with space):** `https://kibana.example.com/s/{space}/app/dashboards#/view/{id}`
- **URL (with query params):** `https://kibana.example.com/app/dashboards#/view/{id}?_g=...`
- **Plain dashboard ID:** `my-dashboard-id` or `dashboard-123`

## Decompilation

Generate a YAML skeleton directly from NDJSON:

```bash
kb-dashboard decompile dashboard.ndjson -o dashboard.yaml
```

The output is a starting point, not a finished dashboard. See [What Decompile Produces](#what-decompile-produces) above for details on what you get and what still needs to be filled in.

## Disassembly

The `disassemble` command breaks dashboard NDJSON into individual JSON files. It serves two purposes:

1. **Inspecting individual panels** — When you need to read the raw Kibana JSON for a specific panel in isolation (e.g., to understand a complex configuration).
2. **Round-trip validation** — Disassemble both the original and compiled NDJSON, then use `compare` to check they match.

Disassembly is **not** the primary conversion path. Use `decompile` to get your YAML skeleton, then fill in the stubs.

```bash
kb-dashboard disassemble dashboard.ndjson -o output_dir/
```

**Output Structure:**

```text
output_dir/
├── metadata.json       # Dashboard title, description, id
├── options.json        # Display options (margins, colors, etc.)
├── controls.json       # Dashboard controls (if present)
├── filters.json        # Dashboard-level filters (if present)
├── references.json     # Data view references
└── panels/             # Individual panel JSON files
    ├── 000_panel-1_lens.json
    ├── 001_panel-2_markdown.json
    └── ...
```

## Conversion Strategy

### Recommended Approach

With `decompile`, you get all panels at once as stubs. The recommended workflow is:

1. Run `kb-dashboard decompile` to get the full YAML skeleton with all panel stubs.
2. Fill in one panel at a time, starting with the simplest (markdown panels, metric panels).
3. Compile incrementally to catch errors early: finish required fields in remaining stubs, or temporarily comment/remove unfinished panel entries before running `kb-dashboard compile`.
4. Move on to more complex panels (XY charts, datatables) once simpler ones validate.
5. Run the full round-trip validation when all panels are complete.

### Minimal YAML

Omit fields that match defaults. Common defaults:

**Dashboard Level:**

- `settings.margins: true`
- `settings.sync.colors: false`
- `settings.sync.cursor: true`
- `settings.sync.tooltips: false`
- `settings.titles: true`

**Panel Level:**

- Legend: `show: true`, `position: right`
- Values: `show_values: false`
- Breakdown: `size: 5`

Reference the documentation in llms-full.txt for component-specific defaults.

## Component Mapping

### Dashboard Metadata

**Input (metadata.json):**

```json
{
  "id": "my-dashboard-id",
  "title": "System Metrics Overview",
  "description": "Dashboard showing system performance metrics"
}
```

**Output (YAML):**

```yaml
---
dashboards:
  - name: System Metrics Overview
    description: Dashboard showing system performance metrics
    panels: []  # Panels will be added incrementally
```

### Markdown Panels

**Input:**

```json
{
  "type": "markdown",
  "gridData": {"x": 0, "y": 0, "w": 48, "h": 3},
  "panelConfig": {
    "markdown": "# Title\n\nContent here"
  }
}
```

**Output:**

```yaml
- markdown:
    content: |
      # Title

      Content here
  size: {w: 48, h: 3}
```

### Lens Metric Panels

**Input:**

```json
{
  "type": "lens",
  "gridData": {"x": 0, "y": 3, "w": 24, "h": 15},
  "embeddableConfig": {
    "attributes": {
      "title": "Total Documents",
      "visualizationType": "lnsMetric",
      "state": {
        "datasourceStates": {
          "formBased": {
            "layers": {
              "layer1": {
                "columns": {
                  "col1": {
                    "operationType": "count",
                    "label": "Count"
                  }
                }
              }
            }
          }
        }
      },
      "references": [
        {
          "type": "index-pattern",
          "id": "logs-*",
          "name": "indexpattern-datasource-layer-layer1"
        }
      ]
    }
  }
}
```

**Output:**

```yaml
- title: Total Documents
  size: {w: 24, h: 15}
  position: {x: 0, y: 3}
  lens:
    type: metric
    data_view: logs-*
    primary:
      aggregation: count
```

### Lens Pie Charts

**Input:**

```json
{
  "type": "lens",
  "visualizationType": "lnsPie",
  "state": {
    "datasourceStates": {
      "formBased": {
        "layers": {
          "layer1": {
            "columns": {
              "col1": {
                "operationType": "terms",
                "sourceField": "status",
                "params": {"size": 5, "orderBy": {"type": "column", "columnId": "col2"}, "orderDirection": "desc"}
              },
              "col2": {
                "operationType": "count"
              }
            }
          }
        }
      }
    }
  }
}
```

**Output:**

```yaml
- title: Status Breakdown
  size: {w: 24, h: 15}
  position: {x: 24, y: 3}
  lens:
    type: pie
    data_view: logs-*
    breakdowns:
      - field: status
        type: values
        size: 5
    metrics:
      - aggregation: count
```

### Dashboard Controls

**Input (controls.json):**

```json
{
  "panelsJSON": "[{\"type\":\"optionsListControl\",\"order\":0,\"width\":\"medium\",\"fieldName\":\"namespace\"}]",
  "controlStyle": "oneLine"
}
```

**Output:**

```yaml
controls:
  - type: options
    label: Namespace
    data_view: metrics-*
    field: namespace
```

Reference [Dashboard Controls](../controls/config.md) for complete options.

### Dashboard Filters

**Input (filters.json):**

```json
[
  {
    "meta": {
      "type": "phrase",
      "key": "service.name",
      "params": {"query": "web-server"}
    }
  }
]
```

**Output:**
Reference [Filters & Queries](../filters/config.md) for filter conversion.

## Panel Type Reference

| Kibana Type | YAML Type | Documentation |
| ----------- | -------------------------- | ---------------------------------------- |
| `lnsMetric` | `lens.type: metric` | [Metric Charts](../panels/metric.md) |
| `lnsPie` | `lens.type: pie` | [Pie Charts](../panels/pie.md) |
| `lnsXY` | `lens.type: line/bar/area` | [XY Charts](../panels/xy.md) |
| `lnsGauge` | `lens.type: gauge` | [Gauge Charts](../panels/gauge.md) |
| `lnsDatatable` | `lens.type: datatable` | [Datatable Charts](../panels/datatable.md) |
| `markdown` | `markdown` | [Markdown Panels](../panels/markdown.md) |
| `links` | `links` | [Links Panels](../panels/links.md) |

For ES|QL-based panels, see [ES|QL Panels](../panels/esql.md).

## Validation

### Compile

```bash
kb-dashboard compile --input-dir my-yaml/ --output-dir compiled/
```

### Compare Structure

Use the compare command to quickly check panel counts and types:

```bash
kb-dashboard compare original_disassembled/ compiled_disassembled/
```

### Verification Workflow (Round-Trip Testing)

For thorough validation, use this round-trip workflow to verify the compiled output matches the original:

1. **Compile YAML to JSON:**

   ```bash
   kb-dashboard compile --input-dir my-yaml/ --output-dir /tmp/compiled/
   ```

   **IMPORTANT:** Fix any compilation errors before proceeding. The YAML must compile successfully.

2. **Disassemble both original and compiled dashboards:**

   ```bash
   # Disassemble original
   kb-dashboard disassemble original.ndjson -o /tmp/original_disassembled/

   # Disassemble compiled
   kb-dashboard disassemble /tmp/compiled/output.ndjson -o /tmp/compiled_disassembled/
   ```

3. **Compare panel structures:**

   Use the compare command to analyze differences:

   ```bash
   kb-dashboard compare /tmp/original_disassembled /tmp/compiled_disassembled
   ```

   This will show panel counts, types, and identify any mismatches.

4. **Verify panel structure and configuration:**

   Use `jq` to compare specific panel configurations between original and compiled:

   ```bash
   # Compare specific panel JSON structures
   diff -u \
     <(jq '.embeddableConfig.attributes.state' /tmp/original_disassembled/panels/003_panel-4_lens.json) \
     <(jq '.embeddableConfig.attributes.state' /tmp/compiled_disassembled/panels/003_panel-4_lens.json)
   ```

   **What to verify for each panel type:**

   **XY Charts (line, bar, area):**
   - Chart type matches (`seriesType` in original -> `type` in YAML)
   - Stacking mode preserved (if `yConfig[].axisMode: stacked` exists)
   - Legend configuration matches (`legend.isVisible`, `legend.position`)
   - Dimensions properly mapped (count columns by `isBucketed: true`)
   - Breakdown configurations match (field names, size parameters)

   **Datatables:**
   - All bucketed columns appear as row dimensions
   - Size parameters match for each dimension
   - Metric columns preserve aggregation functions

   **All Lens panels:**
   - Aggregation functions match (median, average, sum, etc.)
   - Field names are exact (including namespace prefixes)
   - Format settings preserved (percent, bytes, number, etc.)

**Understanding discrepancies:**

When comparing original and compiled dashboards, some differences are expected:

- **Expected (safe):** Panel IDs differ, minor query formatting, panel order variations
- **Needs investigation:** Panel count mismatch, visualization type changes, missing dimensions/metrics, field name differences

**Verification checklist:**

Before considering a conversion complete:

- [ ] YAML compiles without errors
- [ ] Panel counts match (or differences are documented)
- [ ] Panel types match (lens, esql, links, markdown, image, search, vega, section for Kibana 9.1+)
- [ ] Chart configurations preserved (type, stacking, legends)
- [ ] All dimensions and breakdowns accounted for
- [ ] Size parameters match original values
- [ ] Field names and aggregations verified

Note: Section is only available in Kibana 9.1+

## Common Patterns

### Lens Operation Mapping

| Kibana Operation | YAML Aggregation | Notes |
| ---------------- | ------------------------ | --------------------------- |
| `count` | `aggregation: count` | Document count |
| `sum` | `aggregation: sum` | Sum of field values |
| `avg` | `aggregation: average` | Average of field values |
| `min` | `aggregation: min` | Minimum value |
| `max` | `aggregation: max` | Maximum value |
| `median` | `aggregation: median` | Median value |
| `percentile` | `aggregation: percentile` | Requires `percentile` param |
| `terms` | `type: values` | Used in breakdowns/slices |
| `date_histogram` | `type: date_histogram` | Time-based dimension |
| `range` | `type: range` | Range-based dimension |

### XY Chart Dimensions

**Input (Kibana lens state):**

```json
{
  "columns": {
    "col1": {
      "operationType": "date_histogram",
      "sourceField": "@timestamp",
      "params": {"interval": "auto"}
    },
    "col2": {
      "operationType": "avg",
      "sourceField": "system.cpu.total.norm.pct"
    }
  }
}
```

**Output:**

```yaml
lens:
  type: line
  data_view: metrics-*
  dimension:
    field: '@timestamp'
    type: date_histogram
  metrics:
    - field: system.cpu.total.norm.pct
      aggregation: average
```

### Multi-Dimension Breakdowns

**Input:**

```json
{
  "columns": {
    "col1": {"operationType": "date_histogram", "sourceField": "@timestamp"},
    "col2": {"operationType": "terms", "sourceField": "host.name"},
    "col3": {"operationType": "avg", "sourceField": "cpu.usage"}
  }
}
```

**Output:**

```yaml
lens:
  type: line
  data_view: metrics-*
  dimension:
    field: '@timestamp'
    type: date_histogram
  breakdown:
    field: host.name
    type: values
  metrics:
    - field: cpu.usage
      aggregation: average
```

## Error Resolution

### Schema Validation Errors

```text
ValidationError: 'type' is a required property
```

**Solution:** Check required fields in panel type documentation. Each panel type has specific required fields.

### Type Errors

```text
TypeError: Expected string, got int
```

**Solution:** Verify field types match schema. Common issues:

- Numbers as strings: use `100` not `"100"`
- Booleans as strings: use `true` not `"true"`

### Unsupported Panel Types

```text
Error: Panel type 'map' is not supported
```

**Solution:** See [supported panel types](../panels/base.md). For unsupported panels, either:

- Create placeholder markdown panel
- Skip the panel and document it

### Reference Resolution

```text
Error: Data view reference 'logs-*' not found
```

**Solution:** Ensure data views exist in target Kibana instance or are defined in YAML.

## Complete Example

**Decompiled YAML stub (before filling in):**

```yaml skip
---
dashboards:
  - name: Application Monitoring
    description: Real-time application metrics
    panels:
      - title: Total Documents
        size: {w: 24, h: 15}
        position: {x: 0, y: 3}
        lens: {}
        # TODO(decompile): {"type":"lens","embeddableConfig":{"attributes":{"title":"Total Documents","visualizationType":"lnsMetric","state":{"datasourceStates":{"formBased":{"layers":{"layer1":{"columns":{"col1":{"operationType":"count","label":"Count"}}}}}}}},"references":[{"type":"index-pattern","id":"logs-*"}]}}
```

**Completed YAML (after translating the TODO comment):**

```yaml
---
dashboards:
  - name: Application Monitoring
    description: Real-time application metrics
    panels:
      - title: Total Documents
        size: {w: 24, h: 15}
        position: {x: 0, y: 3}
        lens:
          type: metric
          data_view: logs-*
          primary:
            aggregation: count
```

**Validation:**

```bash
kb-dashboard compile
# Success! 1 panel
```

## Additional Resources

- **Complete Documentation**: [llms-full.txt](https://strawgate.com/kb-yaml-to-lens/llms-full.txt)
- **Examples**: [Complete Examples](../examples/index.md)
- **Aerospike Examples**: [Complex real-world dashboards](../examples/aerospike/overview.yaml)
- **Panel Type Docs**: [Panel Types Overview](../panels/base.md)
- **Controls**: [Dashboard Controls](../controls/config.md)
- **Filters**: [Filters & Queries](../filters/config.md)
- **Advanced Topics**: [ES|QL Views](esql-views.md), [Color Assignments](color-assignments.md)
