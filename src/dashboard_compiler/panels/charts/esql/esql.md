# ESQL Panel Configuration

ESQL panels leverage the power of Elasticsearch Query Language (ESQL) to create visualizations. This allows for more complex data transformations and aggregations directly within the query that feeds the chart.

The `ESQLPanel` is the primary container. Its `esql` field holds the ESQL query, and its `chart` field defines the specific type of visualization (e.g., `metric`, `pie`).

## Minimal Configuration Examples

**Minimal ESQL Metric Chart:**

```yaml
# Within a dashboard's 'panels' list:
# - type: charts  # This is the ESQLPanel type (distinguished by `esql` field)
#   title: "Total Processed Events"
#   grid: { x: 0, y: 0, w: 4, h: 3 }
#   esql: |
#     FROM my_event_stream
#     | STATS total_events = COUNT(event_id)
#   chart:
#     type: metric
#     primary:
#       field: "total_events" # Must match a column name from ESQL query

# For a complete dashboard structure:
dashboards:
-
  name: "ESQL Metrics Dashboard"
  panels:
    - type: charts
      title: "Total Processed Events"
      grid: { x: 0, y: 0, w: 4, h: 3 }
      esql: |
        FROM my_event_stream
        | STATS total_events = COUNT(event_id)
      chart:
        type: metric # Specifies an ESQLMetricChart
        primary:
          field: "total_events"
          # Label can be inferred from field if not provided
```

**Minimal ESQL Pie Chart:**

```yaml
# Within a dashboard's 'panels' list:
# - type: charts
#   title: "Events by Type (ESQL)"
#   grid: { x: 4, y: 0, w: 8, h: 3 }
#   esql: |
#     FROM my_event_stream
#     | STATS event_count = COUNT(event_id) BY event_type
#     | LIMIT 5
#   chart:
#     type: pie
#     metric:
#       field: "event_count" # Must match a metric column from ESQL
#     slice_by:
#       - field: "event_type"  # Must match a dimension column from ESQL

# For a complete dashboard structure:
dashboards:
-
  name: "ESQL Event Analysis"
  panels:
    - type: charts
      title: "Events by Type (ESQL)"
      grid: { x: 4, y: 0, w: 8, h: 3 }
      esql: |
        FROM my_event_stream
        | STATS event_count = COUNT(event_id) BY event_type
        | ORDER event_count DESC
        | LIMIT 5
      chart:
        type: pie # Specifies an ESQLPieChart
        metric:
          field: "event_count"
        slice_by:
          - field: "event_type"
```

## Full Configuration Options

### ESQL Panel (`type: charts` with an `esql` field)

This is the main object for an ESQL-based visualization. It inherits from the [Base Panel Configuration](../base.md). The presence of the `esql` field distinguishes it from a Lens panel.

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ------------------------------- | -------- |
| `type` | `Literal['charts']` | Specifies the panel type. For ESQL panels, this is `charts`. | `charts` | Yes |
| `id` | `string` | A unique identifier for the panel. Inherited from BasePanel. | Generated ID | No |
| `title` | `string` | The title displayed on the panel header. Inherited from BasePanel. | `""` (empty string) | No |
| `hide_title` | `boolean` | If `true`, the panel title will be hidden. Inherited from BasePanel. | `false` | No |
| `description` | `string` | A brief description of the panel. Inherited from BasePanel. | `""` (empty string, if `None`) | No |
| `grid` | `Grid` object | Defines the panel's position and size. Inherited from BasePanel. See [Grid Object Configuration](../base.md#grid-object-configuration). | N/A | Yes |
| `esql` | `string` or `ESQLQuery` object | The ESQL query string. See [Queries Documentation](../../queries/config.md#esql-query). | N/A | Yes |
| `chart` | `ESQLChartTypes` object | Defines the actual ESQL visualization configuration. This will be one of [ESQL Metric Chart](#esql-metric-chart-charttype-metric) or [ESQL Pie Chart](#esql-pie-chart-charttype-pie). | N/A | Yes |

---

## ESQL Metric Chart (`chart.type: metric`)

Displays a single primary metric derived from an ESQL query, optionally with a secondary metric, a maximum value, and a breakdown dimension. The `field` names in the chart configuration **must** correspond to column names produced by the ESQL query.

| YAML Key | Data Type | Description | Kibana Default | Required |
| ----------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['metric']` | Specifies the chart type as an ESQL Metric visualization. | `metric` | Yes |
| `id` | `string` | An optional unique identifier for this specific chart layer. | Generated ID | No |
| `primary` | `ESQLMetric` object | The primary metric to display. Its `field` refers to an ESQL result column. See [ESQL Metric Column](#esql-metric-column). | N/A | Yes |
| `secondary` | `ESQLMetric` object | An optional secondary metric. Its `field` refers to an ESQL result column. See [ESQL Metric Column](#esql-metric-column). | `None` | No |
| `maximum` | `ESQLMetric` object | An optional maximum metric. Its `field` refers to an ESQL result column. See [ESQL Metric Column](#esql-metric-column). | `None` | No |
| `breakdown` | `ESQLDimension` object | An optional dimension to break down the metric by. Its `field` refers to an ESQL result column. See [ESQL Dimension Column](#esql-dimension-column). | `None` | No |

**Example (ESQL Metric Chart):**

```yaml
# Within an ESQLPanel's 'chart' field:
# type: metric
# primary:
#   field: "avg_response_time" # Column from ESQL: ... | STATS avg_response_time = AVG(response.time)
# secondary:
#   field: "p95_response_time" # Column from ESQL: ... | STATS p95_response_time = PERCENTILE(response.time, 95.0)
# breakdown:
#   field: "service_name"      # Column from ESQL: ... BY service_name
```

---

## ESQL Pie Chart (`chart.type: pie`)

Visualizes proportions of categories using slices of a pie or a donut chart, with data sourced from an ESQL query. The `field` names in the chart configuration **must** correspond to column names produced by the ESQL query.

| YAML Key | Data Type | Description | Kibana Default | Required |
| ----------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['pie']` | Specifies the chart type as an ESQL Pie visualization. | `pie` | Yes |
| `id` | `string` | An optional unique identifier for this specific chart layer. | Generated ID | No |
| `metric` | `ESQLMetric` object | The metric that determines the size of each slice. Its `field` refers to an ESQL result column. See [ESQL Metric Column](#esql-metric-column). | N/A | Yes |
| `slice_by` | `list of ESQLDimension` objects | One or more dimensions that determine how the pie is sliced. Each `field` refers to an ESQL result column. See [ESQL Dimension Column](#esql-dimension-column). | N/A | Yes |
| `appearance` | `PieChartAppearance` object | Formatting options for the chart appearance. See [Pie Chart Appearance](#pie-chart-appearance-formatting-appearance-field) (shared with Lens). | `None` | No |
| `titles_and_text` | `PieTitlesAndText` object | Formatting options for slice labels and values. See [Pie Titles and Text](#pie-titles-and-text-formatting-titles_and_text-field) (shared with Lens). | `None` | No |
| `legend` | `PieLegend` object | Formatting options for the chart legend. See [Pie Legend](#pie-legend-formatting-legend-field) (shared with Lens). | `None` | No |
| `color` | `ColorMapping` object | Formatting options for the chart color palette. See [Color Mapping](#color-mapping-formatting-color-field) (shared with Lens). | `None` | No |

**Example (ESQL Pie Chart):**

```yaml
# Within an ESQLPanel's 'chart' field:
# type: pie
# metric:
#   field: "error_count"  # Column from ESQL: ... | STATS error_count = COUNT(error.code) BY error.type
# slice_by:
#   - field: "error_type" # Column from ESQL
# appearance:
#   donut: "small"
```

---

## ESQL Columns

For ESQL panels, the `primary`, `secondary`, `maximum` (in metric charts) and `metric`, `slice_by` (in pie charts) fields refer to columns that **must be present in the output of your ESQL query**.

### ESQL Metric Column

Used to specify a metric column from your ESQL query result.

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | --------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `id` | `string` | An optional unique identifier for this metric column definition. | Generated ID | No |
| `field` | `string` | The name of the column in your ESQL query result that represents the metric value. | N/A | Yes |

### ESQL Dimension Column

Used to specify a dimension/grouping column from your ESQL query result.

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | --------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `id` | `string` | An optional unique identifier for this dimension column definition. | Generated ID | No |
| `field` | `string` | The name of the column in your ESQL query result that represents the dimension. | N/A | Yes |

---

## Pie Chart Specific Formatting (Shared with Lens)

ESQL Pie Charts share the same formatting options for appearance, titles/text, legend, and colors as Lens Pie Charts.

### Pie Chart Appearance Formatting (`appearance` field)

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | ------------------------------------- | ------------------------------------------------ | ---------------- | -------- |
| `donut` | `Literal['small', 'medium', 'large']` | If set, creates a donut chart with the specified hole size. | `None` (pie) | No |

### Pie Titles and Text Formatting (`titles_and_text` field)

| YAML Key | Data Type | Description | Kibana Default | Required |
| ---------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `slice_labels` | `Literal['hide', 'inside', 'auto']` | How to display labels for each slice. | `auto` | No |
| `slice_values` | `Literal['hide', 'integer', 'percent']` | How to display the value for each slice. | `percent` | No |
| `value_decimal_places` | `integer` (0-10) | Number of decimal places for slice values. | `2` | No |

### Pie Legend Formatting (`legend` field)

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `visible` | `Literal['show', 'hide', 'auto']` | Controls legend visibility. | `auto` | No |
| `width` | `Literal['small', 'medium', 'large', 'extra_large']` | Width of the legend area. | `medium` | No |
| `truncate_labels` | `integer` (0-5) | Max number of lines for legend labels before truncating. `0` disables truncation. | `1` | No |

### Color Mapping Formatting (`color` field)

| YAML Key | Data Type | Description | Kibana Default | Required |
| --------- | --------- | ------------------------------------------------ | ---------------- | -------- |
| `palette` | `string` | The ID of the color palette to use (e.g., `default`, `elasticColors`). | `default` | Yes |

## Related Documentation

* [Base Panel Configuration](../base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
* [Queries Configuration](../../queries/config.md#esql-query)
* Elasticsearch ESQL Reference (external)
