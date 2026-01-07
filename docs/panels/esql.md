# ESQL Panel Configuration

ESQL panels leverage the power of Elasticsearch Query Language (ESQL) to create visualizations. This allows for more complex data transformations and aggregations directly within the query that feeds the chart.

The `ESQLPanel` is the primary container. Its `esql` field holds the ESQL query, and its `chart` field defines the specific type of visualization (e.g., `metric`, `pie`).

## A Poem for the Query Wizards

_For those who wield the power of Elasticsearch Query Language:_

```text
FROM the indexes, data flows,
WHERE the data goes, nobody knows.
STATS works on numbers, ORDER shows the best,
LIMIT lets the engine rest.

ESQL queries, powerful and clean,
Transforming data never seen!
Complex aggregations, custom math,
Your query blazes the perfect path.

No need for pre-defined fields to bind,
You shape your metrics, well-defined.
FROM, BY, and STATS aligned,
Column names thoughtfully designed.

So here's to those who love to query,
With ESQL power, never weary!
Direct from Elasticsearch's core,
Your visualizations are never a bore!
```

---

## Minimal Configuration Examples

**Minimal ESQL Metric Chart:**

```yaml
dashboards:
  - name: "ESQL Metrics Dashboard"
    panels:
      - title: "Total Processed Events"
        grid: { x: 0, y: 0, w: 16, h: 3 }
        esql:
          type: metric
          query: |
            FROM logs-*
            | STATS total_events = COUNT(*)
          primary:
            field: "total_events"
```

!!! tip "Advanced: Query Reuse with YAML Anchors"
    ES|QL queries can also be defined as arrays, enabling reuse patterns with YAML anchors. This lets you define base queries once and extend them across multiple panels. See [ES|QL Query Reuse with YAML Anchors](../advanced/esql-views.md) for detailed patterns and examples.

**Minimal ESQL Pie Chart:**

```yaml
dashboards:
  - name: "ESQL Event Analysis"
    panels:
      - title: "Events by Type (ESQL)"
        grid: { x: 16, y: 0, w: 32, h: 3 }
        esql:
          type: pie # Specifies an ESQLPieChart
          query: |
            FROM logs-*
            | STATS event_count = COUNT(*) BY event.category
            | ORDER event_count DESC
            | LIMIT 5
          metrics:
            - field: "event_count"
          slice_by:
            - field: "event.category"
```

## Full Configuration Options

### ESQL Panel (`type: charts` with an `esql` field)

This is the main object for an ESQL-based visualization. It inherits from the [Base Panel Configuration](base.md). The presence of the `esql` field distinguishes it from a Lens panel.

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ------------------------------- | -------- |
| `type` | `Literal['charts']` | Specifies the panel type. For ESQL panels, this is `charts`. | `charts` | Yes |
| `id` | `string` | A unique identifier for the panel. Inherited from BasePanel. | Generated ID | No |
| `title` | `string` | The title displayed on the panel header. Inherited from BasePanel. | `""` (empty string) | No |
| `hide_title` | `boolean` | If `true`, the panel title will be hidden. Inherited from BasePanel. | `false` | No |
| `description` | `string` | A brief description of the panel. Inherited from BasePanel. | `""` (empty string, if `None`) | No |
| `grid` | `Grid` object | Defines the panel's position and size. Inherited from BasePanel. See [Grid Object Configuration](base.md#grid-object-configuration-grid). | N/A | Yes |
| `esql` | `string` or `ESQLQuery` object | The ESQL query string. See [Queries Documentation](../queries/config.md#esql-query). | N/A | Yes |
| `chart` | `ESQLChartTypes` object | Defines the actual ESQL visualization configuration. This can be [ESQL Metric Chart](#esql-metric-chart-charttype-metric), [ESQL Pie Chart](#esql-pie-chart-charttype-pie), [ESQL Bar Chart](#esql-bar-chart-charttype-bar), [ESQL Line Chart](#esql-line-chart-charttype-line), or [ESQL Area Chart](#esql-area-chart-charttype-area). | N/A | Yes |

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
| `metrics` | `ESQLMetric \| list[ESQLMetric]` object | A single metric or list of metrics that determine the size of each slice. Each `field` refers to an ESQL result column. See [ESQL Metric Column](#esql-metric-column). | N/A | Yes |
| `slice_by` | `list of ESQLDimension` objects | One or more dimensions that determine how the pie is sliced. Each `field` refers to an ESQL result column. See [ESQL Dimension Column](#esql-dimension-column). | N/A | Yes |
| `appearance` | `PieChartAppearance` object | Formatting options for the chart appearance. See [Pie Chart Appearance](#pie-chart-appearance-formatting-appearance-field) (shared with Lens). | `None` | No |
| `titles_and_text` | `PieTitlesAndText` object | Formatting options for slice labels and values. See [Pie Titles and Text](#pie-titles-and-text-formatting-titles_and_text-field) (shared with Lens). | `None` | No |
| `legend` | `PieLegend` object | Formatting options for the chart legend. See [Pie Legend](#pie-legend-formatting-legend-field) (shared with Lens). | `None` | No |
| `color` | `ColorMapping` object | Formatting options for the chart color palette. See [Color Mapping](#color-mapping-formatting-color-field) (shared with Lens). | `None` | No |

**Example (ESQL Pie Chart):**

```yaml
# Within an ESQLPanel's 'chart' field:
# type: pie
# metrics:
#   field: "error_count"  # Column from ESQL: ... | STATS error_count = COUNT(error.code) BY error.type
# slice_by:
#   - field: "error_type" # Column from ESQL
# appearance:
#   donut: "small"
```

---

## ESQL Bar Chart (`chart.type: bar`)

Displays bar chart visualizations with data sourced from an ESQL query. Supports stacked, unstacked, and percentage modes. The `field` names in the chart configuration **must** correspond to column names produced by the ESQL query.

| YAML Key | Data Type | Description | Kibana Default | Required |
| ----------------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['bar']` | Specifies the chart type as an ESQL Bar visualization. | `bar` | Yes |
| `id` | `string` | An optional unique identifier for this specific chart layer. | Generated ID | No |
| `mode` | `Literal['stacked', 'unstacked', 'percentage']` | Stacking mode for bar charts. | `'stacked'` | No |
| `dimensions` | `list of ESQLDimension` objects | One or more dimensions that determine the X-axis. Each `field` refers to an ESQL result column. See [ESQL Dimension Column](#esql-dimension-column). | N/A | Yes |
| `metrics` | `list of ESQLMetric` objects | One or more metrics that determine the Y-axis values. Each `field` refers to an ESQL result column. See [ESQL Metric Column](#esql-metric-column). | N/A | Yes |
| `breakdown` | `ESQLDimension` object | An optional dimension to split the series by. Its `field` refers to an ESQL result column. See [ESQL Dimension Column](#esql-dimension-column). | `None` | No |
| `appearance` | `XYAppearance` object | Formatting options for chart appearance. See [XY Chart Appearance](#xy-chart-appearance-formatting-appearance-field). | `None` | No |
| `legend` | `XYLegend` object | Formatting options for the chart legend. See [XY Legend](#xy-legend-formatting-legend-field). | `None` | No |
| `color` | `ColorMapping` object | Formatting options for the chart color palette. See [Color Mapping](#color-mapping-formatting-color-field) (shared with other chart types). | `None` | No |

**Example (ESQL Bar Chart):**

```yaml
# Within an ESQLPanel's 'chart' field:
# type: bar
# mode: stacked
# dimensions:
#   - field: "@timestamp"  # Column from ESQL: ... | STATS ... BY @timestamp = BUCKET(@timestamp, 1 hour)
# metrics:
#   - field: "event_count"  # Column from ESQL: ... | STATS event_count = COUNT(*)
# breakdown:
#   field: "event.category"  # Column from ESQL: ... BY event.category
```

---

## ESQL Line Chart (`chart.type: line`)

Displays line chart visualizations with data sourced from an ESQL query. The `field` names in the chart configuration **must** correspond to column names produced by the ESQL query.

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['line']` | Specifies the chart type as an ESQL Line visualization. | `line` | Yes |
| `id` | `string` | An optional unique identifier for this specific chart layer. | Generated ID | No |
| `dimensions` | `list of ESQLDimension` objects | One or more dimensions that determine the X-axis. Each `field` refers to an ESQL result column. See [ESQL Dimension Column](#esql-dimension-column). | N/A | Yes |
| `metrics` | `list of ESQLMetric` objects | One or more metrics that determine the Y-axis values. Each `field` refers to an ESQL result column. See [ESQL Metric Column](#esql-metric-column). | N/A | Yes |
| `breakdown` | `ESQLDimension` object | An optional dimension to split the series by. Its `field` refers to an ESQL result column. See [ESQL Dimension Column](#esql-dimension-column). | `None` | No |
| `appearance` | `XYAppearance` object | Formatting options for chart appearance. See [XY Chart Appearance](#xy-chart-appearance-formatting-appearance-field). | `None` | No |
| `legend` | `XYLegend` object | Formatting options for the chart legend. See [XY Legend](#xy-legend-formatting-legend-field). | `None` | No |
| `color` | `ColorMapping` object | Formatting options for the chart color palette. See [Color Mapping](#color-mapping-formatting-color-field) (shared with other chart types). | `None` | No |

**Example (ESQL Line Chart):**

```yaml
# Within an ESQLPanel's 'chart' field:
# type: line
# dimensions:
#   - field: "@timestamp"  # Column from ESQL: ... | STATS ... BY @timestamp = BUCKET(@timestamp, 1 hour)
# metrics:
#   - field: "avg_response_time"  # Column from ESQL: ... | STATS avg_response_time = AVG(response.time)
# breakdown:
#   field: "service.name"  # Column from ESQL: ... BY service.name
```

---

## ESQL Area Chart (`chart.type: area`)

Displays area chart visualizations with data sourced from an ESQL query. Supports stacked, unstacked, and percentage modes. The `field` names in the chart configuration **must** correspond to column names produced by the ESQL query.

| YAML Key | Data Type | Description | Kibana Default | Required |
| ----------------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['area']` | Specifies the chart type as an ESQL Area visualization. | `area` | Yes |
| `id` | `string` | An optional unique identifier for this specific chart layer. | Generated ID | No |
| `mode` | `Literal['stacked', 'unstacked', 'percentage']` | Stacking mode for area charts. | `'stacked'` | No |
| `dimensions` | `list of ESQLDimension` objects | One or more dimensions that determine the X-axis. Each `field` refers to an ESQL result column. See [ESQL Dimension Column](#esql-dimension-column). | N/A | Yes |
| `metrics` | `list of ESQLMetric` objects | One or more metrics that determine the Y-axis values. Each `field` refers to an ESQL result column. See [ESQL Metric Column](#esql-metric-column). | N/A | Yes |
| `breakdown` | `ESQLDimension` object | An optional dimension to split the series by. Its `field` refers to an ESQL result column. See [ESQL Dimension Column](#esql-dimension-column). | `None` | No |
| `appearance` | `XYAppearance` object | Formatting options for chart appearance. See [XY Chart Appearance](#xy-chart-appearance-formatting-appearance-field). | `None` | No |
| `legend` | `XYLegend` object | Formatting options for the chart legend. See [XY Legend](#xy-legend-formatting-legend-field). | `None` | No |
| `color` | `ColorMapping` object | Formatting options for the chart color palette. See [Color Mapping](#color-mapping-formatting-color-field) (shared with other chart types). | `None` | No |

**Example (ESQL Area Chart):**

```yaml
# Within an ESQLPanel's 'chart' field:
# type: area
# mode: stacked
# dimensions:
#   - field: "@timestamp"  # Column from ESQL: ... | STATS ... BY @timestamp = BUCKET(@timestamp, 1 hour)
# metrics:
#   - field: "bytes_total"  # Column from ESQL: ... | STATS bytes_total = SUM(bytes)
# breakdown:
#   field: "host.name"  # Column from ESQL: ... BY host.name
```

---

## ESQL Columns

For ESQL panels, the `primary`, `secondary`, `maximum` (in metric charts) and `metrics`, `slice_by` (in pie charts) fields refer to columns that **must be present in the output of your ESQL query**.

### ESQL Metric Column

Used to specify a metric column from your ESQL query result.

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | --------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `id` | `string` | An optional unique identifier for this metric column definition. | Generated ID | No |
| `field` | `string` | The name of the column in your ESQL query result that represents the metric value. | N/A | Yes |
| `label` | `string` | An optional display label for the metric. | `None` | No |
| `format` | `ESQLMetricFormat` object | Optional format configuration for the metric. See [ESQL Metric Format](#esql-metric-format). | `None` | No |

#### ESQL Metric Format

Configure how metric values are displayed (number format, suffix, decimal places, etc.).

**Standard Format Types:**

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | --------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['number', 'bytes', 'bits', 'percent', 'duration']` | The format type for the metric. | N/A | Yes |
| `decimals` | `integer` | Number of decimal places to display. If not specified, defaults to 2 for number/bytes/percent/duration, 0 for bits. | Type-dependent | No |
| `suffix` | `string` | Optional suffix to display after the number (e.g., 'KB', 'ms'). | `None` | No |
| `compact` | `boolean` | Whether to display the number in a compact format (e.g., '1.2K' instead of '1200'). | `None` | No |
| `pattern` | `string` | Optional Numeral.js pattern for custom formatting. Controls decimal places, thousands separators, and more (e.g., '0,0.00' for 2 decimals with comma separator, '0.0000' for 4 decimals). Note: `decimals` provides a simpler way to control decimal places without a pattern. | `None` | No |

**Custom Format Type:**

For completely custom number formatting, use:

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | --------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['custom']` | Indicates a custom format pattern. | `'custom'` | Yes |
| `pattern` | `string` | Numeral.js pattern for custom formatting (e.g., '0,0.[0000]', '0.00%'). | N/A | Yes |

**Example (Metric with Format):**

```yaml
# Within an ESQL chart's metrics field:
metrics:
  - field: "total_bytes"
    label: "Total Data"
    format:
      type: bytes
      decimals: 1  # Show 1 decimal place
  - field: "event_count"
    label: "Events"
    format:
      type: number
      decimals: 0  # No decimal places
  - field: "avg_response_time"
    label: "Avg Response Time"
    format:
      type: number
      decimals: 2  # 2 decimal places
      suffix: "ms"
  - field: "success_rate"
    label: "Success Rate"
    format:
      type: percent
      decimals: 1  # 1 decimal place for percentages
  - field: "precise_value"
    label: "Precise Value"
    format:
      type: number
      pattern: "0,0.0000"  # Pattern for custom thousands separator and 4 decimals
```

### ESQL Dimension Column

Used to specify a dimension/grouping column from your ESQL query result.

| YAML Key | Data Type | Description | Kibana Default | Required |
| ---------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `id` | `string` | An optional unique identifier for this dimension column definition. | Generated ID | No |
| `field` | `string` | The name of the column in your ESQL query result that represents the dimension. | N/A | Yes |
| `collapse` | `Literal['sum', 'avg', 'min', 'max'] \| None` | Aggregation function to apply when collapsing dimension values (e.g., for multi-value fields or breakdowns). | `None` | No |

---

## Pie Chart Specific Formatting (Shared with Lens)

ESQL Pie Charts share the same formatting options for appearance, titles/text, legend, and colors as Lens Pie Charts.

### Pie Chart Appearance Formatting (`appearance` field)

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | ------------------------------------- | ------------------------------------------------ | ---------------- | -------- |
| `donut` | `Literal['small', 'medium', 'large']` | If set, creates a donut chart with the specified hole size. If not specified, Kibana displays as a pie chart (no donut hole). | `None` | No |

### Pie Titles and Text Formatting (`titles_and_text` field)

| YAML Key | Data Type | Description | Kibana Default | Required |
| ---------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `slice_labels` | `Literal['hide', 'inside', 'auto']` | How to display labels for each slice. | `None` | No |
| `slice_values` | `Literal['hide', 'integer', 'percent']` | How to display the value for each slice. | `None` | No |
| `value_decimal_places` | `integer` (0-10) | Number of decimal places for slice values. | `None` | No |

### Pie Legend Formatting (`legend` field)

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `visible` | `Literal['show', 'hide', 'auto']` | Controls legend visibility. | `None` | No |
| `width` | `Literal['small', 'medium', 'large', 'extra_large']` | Width of the legend area. | `None` | No |
| `truncate_labels` | `integer` (0-5) | Max number of lines for legend labels before truncating. `0` disables truncation. | `None` | No |

### Color Mapping Formatting (`color` field)

| YAML Key | Data Type | Description | Kibana Default | Required |
| --------- | --------- | ------------------------------------------------ | ---------------- | -------- |
| `palette` | `string` | The ID of the color palette to use (e.g., `default`, `elasticColors`). | `default` | Yes |

---

## XY Chart Specific Formatting (Shared with Lens)

ESQL XY Charts (bar, line, area) share the same formatting options for appearance and legend as Lens XY Charts.

### XY Chart Appearance Formatting (`appearance` field)

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------- | ------------------------ | -------------------------------------------------------- | ------- | -------- |
| `x_axis` | `AxisConfig \| None` | Configuration for the X-axis (horizontal axis). | `None` | No |
| `y_left_axis` | `AxisConfig \| None` | Configuration for the left Y-axis (primary vertical axis). | `None` | No |
| `y_right_axis` | `AxisConfig \| None` | Configuration for the right Y-axis (secondary vertical axis). | `None` | No |
| `series` | `list[XYSeries] \| None` | Per-series visual configuration (axis assignment, colors). | `None` | No |

#### AxisConfig Options

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | ------------------------------------------------ | ---------------------------------------------- | ------- | -------- |
| `title` | `str \| None` | Custom title for the axis. | `None` | No |
| `scale` | `Literal['linear', 'log', 'sqrt', 'time'] \| None` | Scale type for the axis. | `None` | No |
| `extent` | `AxisExtent \| None` | Axis bounds/range configuration. | `None` | No |

#### AxisExtent Options

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------- | -------------------------------------------- | --------------------------------------------------------- | ------- | -------- |
| `mode` | `Literal['full', 'data_bounds', 'custom']` | Extent mode: 'full' (entire range), 'data_bounds' (fit to data), 'custom' (manual bounds). | N/A | Yes |
| `min` | `float \| None` | Minimum bound (required when mode is 'custom'). | `None` | Conditional |
| `max` | `float \| None` | Maximum bound (required when mode is 'custom'). | `None` | Conditional |
| `enforce` | `bool \| None` | Whether to enforce the bounds strictly. | `None` | No |
| `nice_values` | `bool \| None` | Whether to round bounds to nice values. | `None` | No |

#### XYSeries Options

| YAML Key | Data Type | Description | Kibana Default | Required |
| ----------- | ------------------------------------------------- | ------------------------------------------------------------ | ------- | -------- |
| `metric_id` | `str` | ID of the metric this series configuration applies to. | N/A | Yes |
| `axis` | `Literal['left', 'right'] \| None` | Which Y-axis this series is assigned to (for dual-axis charts). | `None` | No |
| `color` | `str \| None` | Hex color code for the series (e.g., '#2196F3'). | `None` | No |

### XY Legend Formatting (`legend` field)

| YAML Key | Data Type | Description | Kibana Default | Required |
| ---------- | -------------------------------------------------------- | ------------------------------------------------- | ------- | -------- |
| `visible` | `bool \| None` | Whether the legend is visible. | `None` | No |
| `position` | `Literal['top', 'bottom', 'left', 'right'] \| None` | Position of the legend (Kibana defaults to 'right'). | `None` | No |

---

## Related Documentation

* [Base Panel Configuration](base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
* [Queries Configuration](../queries/config.md#esql-query)
* Elasticsearch ESQL Reference (external)
