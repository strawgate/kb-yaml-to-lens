# Dashboard Decompiling Guide: Converting Kibana JSON to YAML

This guide provides instructions for converting Kibana dashboard JSON files into YAML format for kb-yaml-to-lens. It is designed to be consumed by LLMs (Large Language Models) to perform conversions efficiently.

## Quick Reference

**Complete Documentation**: For full schema reference and examples, use [llms-full.txt](https://strawgate.com/kb-yaml-to-lens/llms-full.txt) which contains all project documentation.

**Workflow**: `kb-dashboard disassemble` → Convert to YAML → `kb-dashboard compile` → Validate

## Disassembly

Break dashboard JSON into components:

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

### Incremental Approach

Convert one panel at a time and validate after each addition:

1. Create minimal dashboard structure
2. Add first panel
3. Compile: `kb-dashboard compile`
4. Fix errors if any
5. Repeat for remaining panels

### Minimal YAML

Omit fields that match defaults. Common defaults:

**Dashboard Level:**

- `use_margins: true`
- `sync_colors: false`
- `sync_cursor: true`
- `sync_tooltips: false`
- `hide_panel_titles: false`

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
  grid: {x: 0, y: 0, w: 48, h: 3}
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
  grid: {x: 0, y: 3, w: 24, h: 15}
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
  grid: {x: 24, y: 3, w: 24, h: 15}
  lens:
    type: pie
    data_view: logs-*
    slice_by:
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

Reference [Dashboard Controls](controls/config.md) for complete options.

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
Reference [Filters & Queries](filters/config.md) for filter conversion.

## Panel Type Reference

| Kibana Type | YAML Type | Documentation |
| ----------- | -------------------------- | ---------------------------------------- |
| `lnsMetric` | `lens.type: metric` | [Metric Charts](panels/metric.md) |
| `lnsPie` | `lens.type: pie` | [Pie Charts](panels/pie.md) |
| `lnsXY` | `lens.type: line/bar/area` | [XY Charts](panels/xy.md) |
| `lnsGauge` | `lens.type: gauge` | [Gauge Charts](panels/gauge.md) |
| `lnsDatatable` | `lens.type: table` | [Datatable Charts](panels/datatable.md) |
| `markdown` | `markdown` | [Markdown Panels](panels/markdown.md) |
| `links` | `links` | [Links Panels](panels/links.md) |

For ES|QL-based panels, see [ES|QL Panels](panels/esql.md).

## Validation

### Compile

```bash
kb-dashboard compile --input-dir my-yaml/ --output-dir compiled/
```

### Compare Structure

Use the comparison helper script to quickly check panel counts and types:

```bash
scripts/compare_panel_counts.sh original.ndjson compiled/output.ndjson
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

   Use the comparison helper script to analyze differences:

   ```bash
   python3 scripts/compare_dashboards.py /tmp/original_disassembled /tmp/compiled_disassembled
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
   - Chart type matches (`seriesType` in original → `type` in YAML)
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

- ✅ **Expected (safe):** Panel IDs differ, minor query formatting, panel order variations
- ⚠️ **Needs investigation:** Panel count mismatch, visualization type changes, missing dimensions/metrics, field name differences

**Verification checklist:**

Before considering a conversion complete:

- [ ] YAML compiles without errors
- [ ] Panel counts match (or differences are documented)
- [ ] Panel types match (lens, visualization, links, markdown)
- [ ] Chart configurations preserved (type, stacking, legends)
- [ ] All dimensions and breakdowns accounted for
- [ ] Size parameters match original values
- [ ] Field names and aggregations verified

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
  dimensions:
    - field: '@timestamp'
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
  dimensions:
    - field: '@timestamp'
      type: date_histogram
  breakdown:
    - field: host.name
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
Error: Panel type 'vega' is not supported
```

**Solution:** See [supported panel types](panels/base.md). For unsupported panels, either:

- Create placeholder markdown panel
- Skip the panel and document it

### Reference Resolution

```text
Error: Data view reference 'logs-*' not found
```

**Solution:** Ensure data views exist in target Kibana instance or are defined in YAML.

## Complete Example

**Disassembled Panel (001_panel-2_lens.json):**

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
                  "col1": {"operationType": "count", "label": "Count"}
                }
              }
            }
          }
        }
      },
      "references": [{"type": "index-pattern", "id": "logs-*"}]
    }
  }
}
```

**Converted YAML:**

```yaml
---
dashboards:
  - name: Application Monitoring
    description: Real-time application metrics
    panels:
      - title: Total Documents
        grid: {x: 0, y: 3, w: 24, h: 15}
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
- **Examples**: [Complete Examples](examples/index.md)
- **Aerospike Examples**: [Complex real-world dashboards](https://github.com/strawgate/kb-yaml-to-lens/tree/main/docs/examples/aerospike)
- **Panel Type Docs**: [Panel Types Overview](panels/base.md)
- **Controls**: [Dashboard Controls](controls/config.md)
- **Filters**: [Filters & Queries](filters/config.md)
- **Advanced Topics**: [ES|QL Views](advanced/esql-views.md), [Color Assignments](advanced/color-assignments.md)
