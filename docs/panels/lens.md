# Lens Panel Configuration

Lens panels in Kibana provide a flexible and user-friendly way to create various types of visualizations, such as metric displays, pie charts, bar charts, line charts, and more. This document covers the YAML configuration for Lens panels using this compiler.

The `LensPanel` is the primary container. Its `chart` field will define the specific type of visualization (e.g., `metric`, `pie`).

## A Poem for the Lens Pioneers

_For those who craft visualizations with elegant flexibility:_

```text
Lens is the lens through which we see,
Data's patterns, wild and free.
From metrics bold to pies that slice,
Lens makes visualizations nice!

Dimensions group and metrics measure,
Aggregations are your treasure.
count(), sum(), unique_count() too,
Percentiles showing p95 for you.

Date histograms march through time,
Top values sorted, so sublime.
Filters, intervals, formula power,
Lens transforms data by the hour!

So here's to Lens, both strong and smart,
The beating visualization heart.
With data views and layers deep,
Your dashboard promises to keep!
```

---

## Minimal Configuration Examples

**Minimal Lens Metric Chart:**

```yaml
dashboards:
  - name: "Key Metrics Dashboard"
    panels:
      - type: charts
        title: "Total Users"
        grid: { x: 0, y: 0, w: 4, h: 3 }
        query: # Optional panel-specific query
          kql: "event.dataset:website.visits"
        chart:
          type: metric # Specifies a LensMetricChart
          primary:
            aggregation: "unique_count"
            field: "user.id"
            label: "Unique Visitors"
```

**Minimal Lens Pie Chart:**

```yaml
dashboards:
  - name: "Traffic Analysis"
    panels:
      - type: charts
        title: "Traffic by Source"
        grid: { x: 4, y: 0, w: 8, h: 3 }
        chart:
          type: pie # Specifies a LensPieChart
          data_view: "weblogs-*"
          metric:
            aggregation: "count"
            label: "Sessions"
          slice_by:
            - type: values
              field: "source.medium"
              label: "Traffic Source"
              size: 5 # Top 5 sources
```

## Full Configuration Options

### Lens Panel (`type: charts`)

This is the main object for a Lens-based visualization. It inherits from the [Base Panel Configuration](base.md).

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ------------------------------- | -------- |
| `type` | `Literal['charts']` | Specifies the panel type as a Lens panel. | `charts` | Yes |
| `id` | `string` | A unique identifier for the panel. Inherited from BasePanel. | Generated ID | No |
| `title` | `string` | The title displayed on the panel header. Inherited from BasePanel. | `""` (empty string) | No |
| `hide_title` | `boolean` | If `true`, the panel title will be hidden. Inherited from BasePanel. | `false` | No |
| `description` | `string` | A brief description of the panel. Inherited from BasePanel. | `""` (empty string, if `None`) | No |
| `grid` | `Grid` object | Defines the panel's position and size. Inherited from BasePanel. See [Grid Object Configuration](base.md#grid-object-configuration). | N/A | Yes |
| `query` | `LegacyQueryTypes` object (KQL or Lucene) | A panel-specific query to filter data for this Lens visualization. See [Queries Documentation](../queries/config.md). | `None` (uses dashboard query) | No |
| `filters` | `list of FilterTypes` | A list of panel-specific filters. See [Filters Documentation](../filters/config.md). | `[]` (empty list) | No |
| `chart` | `LensChartTypes` object | Defines the actual Lens visualization configuration. This will be one of [Lens Metric Chart](#lens-metric-chart-charttype-metric) or [Lens Pie Chart](#lens-pie-chart-charttype-pie). | N/A | Yes |
| `layers` | `list of MultiLayerChartTypes` | For multi-layer charts (e.g., multiple pie charts on one panel). _Currently, only `LensPieChart` is supported as a multi-layer type._ | `None` | No |

**Note on `layers` vs `chart`**:

* Use the `chart` field for single-layer visualizations (most common use case, e.g., one metric display, one pie chart).
* Use the `layers` field if you need to define multiple, distinct visualizations within the same Lens panel (e.g., overlaying different chart types or configurations). If `layers` is used, the `chart` field should not be.

---

## Lens Metric Chart (`chart.type: metric`)

Displays a single primary metric, optionally with a secondary metric, a maximum value, and a breakdown dimension.

| YAML Key | Data Type | Description | Kibana Default | Required |
| ----------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['metric']` | Specifies the chart type as a Lens Metric visualization. | `metric` | Yes |
| `id` | `string` | An optional unique identifier for this specific chart layer. | Generated ID | No |
| `primary` | `LensMetricTypes` object | The primary metric to display. This is the main value shown. See [Lens Metrics](#lens-metrics-primary-secondary-maximum-for-metric-metric-for-pie). | N/A | Yes |
| `secondary` | `LensMetricTypes` object | An optional secondary metric to display alongside the primary. See [Lens Metrics](#lens-metrics-primary-secondary-maximum-for-metric-metric-for-pie). | `None` | No |
| `maximum` | `LensMetricTypes` object | An optional maximum metric, often used for context (e.g., showing a value out of a total). See [Lens Metrics](#lens-metrics-primary-secondary-maximum-for-metric-metric-for-pie). | `None` | No |
| `breakdown` | `LensDimensionTypes` object | An optional dimension to break down the metric by (e.g., showing primary metric per country). See [Lens Dimensions](#lens-dimensions-breakdown-for-metric-slice_by-for-pie). | `None` | No |

**Example (Lens Metric Chart):**

```yaml
# Within a LensPanel's 'chart' field:
# type: metric
# primary:
#   aggregation: "sum"
#   field: "bytes_transferred"
#   label: "Total Data"
#   format: { type: "bytes" }
# secondary:
#   aggregation: "average"
#   field: "response_time_ms"
#   label: "Avg Response"
#   format: { type: "duration", suffix: " ms" }
# breakdown:
#   type: values
#   field: "host.name"
#   size: 3
#   label: "Top Hosts"
```

---

## Lens Pie Chart (`chart.type: pie`)

Visualizes proportions of categories using slices of a pie or a donut chart.

| YAML Key | Data Type | Description | Kibana Default | Required |
| ----------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['pie']` | Specifies the chart type as a Lens Pie visualization. | `pie` | Yes |
| `id` | `string` | An optional unique identifier for this specific chart layer. | Generated ID | No |
| `data_view` | `string` | The ID or title of the data view (index pattern) for this pie chart. | N/A | Yes |
| `metric` | `LensMetricTypes` object | The metric that determines the size of each slice. See [Lens Metrics](#lens-metrics-primary-secondary-maximum-for-metric-metric-for-pie). | N/A | Yes |
| `slice_by` | `list of LensDimensionTypes` objects | One or more dimensions that determine how the pie is sliced. See [Lens Dimensions](#lens-dimensions-breakdown-for-metric-slice_by-for-pie). | N/A | Yes |
| `appearance` | `PieChartAppearance` object | Formatting options for the chart appearance. See [Pie Chart Appearance](#pie-chart-appearance-appearance-field). | `None` | No |
| `titles_and_text` | `PieTitlesAndText` object | Formatting options for slice labels and values. See [Pie Titles and Text](#pie-titles-and-text-titles_and_text-field). | `None` | No |
| `legend` | `PieLegend` object | Formatting options for the chart legend. See [Pie Legend](#pie-legend-legend-field). | `None` | No |
| `color` | `ColorMapping` object | Formatting options for the chart color palette. See [Color Mapping](#color-mapping-color-field). | `None` | No |

**Example (Lens Pie Chart):**

```yaml
# Within a LensPanel's 'chart' field:
# type: pie
# data_view: "ecommerce-orders"
# metric:
#   aggregation: "sum"
#   field: "order_value"
#   label: "Total Order Value"
# slice_by:
#   - type: values
#     field: "product.category"
#     size: 5
#     label: "Product Category"
# appearance:
#   donut: "medium"
# legend:
#   visible: "show"
#   width: "large"
# titles_and_text:
#   slice_labels: "inside"
#   slice_values: "percent"
```

---

## Lens Dimensions (`breakdown` for Metric, `slice_by` for Pie)

Dimensions define how data is grouped or bucketed in Lens visualizations.

### Common Dimension Fields (`BaseLensDimension`)

All specific dimension types below can include:

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | --------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `id` | `string` | An optional unique identifier for the dimension. | Generated ID | No |
| `label` | `string` | A custom display label for the dimension. If not provided, a label is inferred. | Inferred | No |

### Top Values Dimension (`type: values`)

Groups data by the most frequent unique values of a field.

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------------ | ----------------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['values']` | Specifies the dimension type. | `values` | Yes |
| `field` | `string` | The field to get top values from. | N/A | Yes |
| `size` | `integer` | The number of top values to display. | `3` | No |
| `sort` | `Sort` object | How to sort the terms. `by` can be a metric label or `_term` (alphabetical). `direction` is `asc` or `desc`. | Sort by metric, `desc` | No |
| `other_bucket` | `boolean` | If `true`, groups remaining values into an "Other" bucket. | `true` | No |
| `missing_bucket` | `boolean` | If `true`, creates a bucket for documents where the field is missing. | `false` | No |
| `include` | `list of strings` | A list of specific terms to include. | `None` | No |
| `exclude` | `list of strings` | A list of specific terms to exclude. | `None` | No |
| `include_is_regex` | `boolean` | If `true`, treats `include` values as regex patterns. | `false` | No |
| `exclude_is_regex` | `boolean` | If `true`, treats `exclude` values as regex patterns. | `false` | No |

### Date Histogram Dimension (`type: date_histogram`)

Groups data into time-based buckets (e.g., per hour, day).

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['date_histogram']` | Specifies the dimension type. | `date_histogram` | Yes |
| `field` | `string` | The date field to use for the histogram. | N/A | Yes |
| `minimum_interval` | `string` | The time interval (e.g., `auto`, `1h`, `1d`, `1w`). | `auto` | No |
| `partial_intervals` | `boolean` | If `true`, includes buckets for time periods that are only partially covered by the data. | `true` | No |
| `collapse` | `CollapseAggregationEnum` | For stacked charts, how to aggregate values within the same time bucket if multiple series exist. (`sum`, `min`, `max`, `avg`) | `None` | No |

### Filters Dimension (`type: filters`)

Creates buckets based on a list of custom KQL/Lucene queries.

| YAML Key | Data Type | Description | Kibana Default | Required |
| --------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['filters']` | Specifies the dimension type. | `filters` | Yes |
| `filters` | `list of LensFiltersDimensionFilter` objects | A list of filter definitions. Each filter object has `query` (KQL/Lucene) and an optional `label`. | N/A | Yes |

**`LensFiltersDimensionFilter` Object:**

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | ------------------------- | ------------------------------------------------ | ---------------- | -------- |
| `query` | `LegacyQueryTypes` object | The KQL or Lucene query for this filter bucket. | N/A | Yes |
| `label` | `string` | A display label for this filter bucket. | Query string | No |

### Intervals Dimension (`type: intervals`)

Groups data into numeric ranges (buckets).

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['intervals']` | Specifies the dimension type. | `intervals` | Yes |
| `field` | `string` | The numeric field to create intervals from. | N/A | Yes |
| `intervals` | `list of LensIntervalsDimensionInterval` objects | A list of custom interval ranges. If not provided, `granularity` is used. | `None` | No |
| `granularity` | `integer` (1-7) | Divides the field into evenly spaced intervals. 1 is coarsest, 7 is finest. | `4` | No |
| `collapse` | `CollapseAggregationEnum` | For stacked charts, how to aggregate values within the same interval if multiple series exist. (`sum`, `min`, `max`, `avg`) | `None` | No |
| `empty_bucket` | `boolean` | If `true`, shows a bucket for documents with missing values for the field. | `false` | No |

**`LensIntervalsDimensionInterval` Object:**

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | --------- | ------------------------------------------------ | ---------------- | -------- |
| `from` | `integer` | The start of the interval (inclusive). | `None` | No |
| `to` | `integer` | The end of the interval (exclusive). | `None` | No |
| `label` | `string` | A display label for this interval bucket. | Auto-generated | No |

---

## Lens Metrics (`primary`, `secondary`, `maximum` for Metric; `metric` for Pie)

Metrics define the calculations performed on your data (e.g., count, sum, average).

### Common Metric Fields (`BaseLensMetric`)

All specific metric types below can include:

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | ------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `id` | `string` | An optional unique identifier for the metric. | Generated ID | No |
| `label` | `string` | A custom display label for the metric. If not provided, a label is inferred. | Inferred | No |
| `format` | `LensMetricFormatTypes` object | How to format the metric's value (e.g., number, bytes, percent). See [Metric Formatting](#metric-formatting-format-field-within-a-metric). | Default for type | No |
| `filter` | `LegacyQueryTypes` object | A KQL or Lucene query to filter data _before_ this metric is calculated. | `None` | No |

### Aggregated Metric Types

These metrics perform an aggregation on a field.

**Count / Unique Count (`aggregation: count` or `aggregation: unique_count`)**

| YAML Key | Data Type | Description | Kibana Default | Required |
| --------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `aggregation` | `Literal['count', 'unique_count']` | Type of count. | N/A | Yes |
| `field` | `string` | For `unique_count`, the field whose unique values are counted. For `count`, optional (counts all documents if `None`). | `None` for `count` | No (Yes for `unique_count`) |
| `exclude_zeros` | `boolean` | If `true`, zero values are excluded from the aggregation. | `true` | No |

**Sum (`aggregation: sum`)**

| YAML Key | Data Type | Description | Kibana Default | Required |
| --------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `aggregation` | `Literal['sum']` | Specifies sum aggregation. | `sum` | Yes |
| `field` | `string` | The numeric field to sum. | N/A | Yes |
| `exclude_zeros` | `boolean` | If `true`, zero values are excluded from the sum. | `true` | No |

**Min, Max, Average, Median (`aggregation: min` / `max` / `average` / `median`)**

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `aggregation` | `Literal['min', 'max', 'average', 'median']` | The aggregation type. | N/A | Yes |
| `field` | `string` | The numeric field for the aggregation. | N/A | Yes |

**Last Value (`aggregation: last_value`)**

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `aggregation` | `Literal['last_value']` | Retrieves the most recent value of a field. | `last_value` | Yes |
| `field` | `string` | The field whose last value is retrieved. | N/A | Yes |
| `date_field` | `string` | The date field used to determine the "last" value. | `@timestamp` | No |

**Percentile (`aggregation: percentile`)**

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `aggregation` | `Literal['percentile']` | Calculates the value at a specific percentile. | `percentile` | Yes |
| `field` | `string` | The numeric field for percentile calculation. | N/A | Yes |
| `percentile` | `integer` | The percentile to calculate (e.g., `95` for 95th percentile). | N/A | Yes |

**Percentile Rank (`aggregation: percentile_rank`)**

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `aggregation` | `Literal['percentile_rank']` | Determines the rank of a specific value within the dataset. | `percentile_rank` | Yes |
| `field` | `string` | The numeric field for percentile rank calculation. | N/A | Yes |
| `rank` | `integer` | The value for which to find the percentile rank. | N/A | Yes |

### Formula Metric

Allows custom calculations using a formula string. _Note: Formula structure is complex and detailed parsing/compilation for its internal operations is not fully covered here but is handled by the compiler._

| YAML Key | Data Type | Description | Kibana Default | Required |
| --------- | --------- | ------------------------------------------------ | ---------------- | -------- |
| `formula` | `string` | The formula string (e.g., `count() / unique_count(user.id)`). | N/A | Yes |

---

## Metric Formatting (`format` field within a metric)

Defines how metric values are displayed.

### Standard Format (`format.type: number` / `bytes` / `bits` / `percent` / `duration`)

| YAML Key | Data Type | Description | Kibana Default | Required |
| --------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['number', 'bytes', 'bits', 'percent', 'duration']` | The general type of formatting. | N/A | Yes |
| `suffix` | `string` | A suffix to append to the value (e.g., "ms", " GB"). | `None` | No |
| `compact` | `boolean` | If `true`, uses compact notation (e.g., "1K" instead of "1000"). | `None` (false) | No |
| `pattern` | `string` | A Numeral.js format pattern (used if `type` is `number` or `percent`). | Default for type | No |

**Default Decimal Places (Kibana):**

* `number`: 2
* `bytes`: 2
* `bits`: 0
* `percent`: 2
* `duration`: 0 (Kibana often uses smart duration formatting like "1m 30s")

### Custom Format (`format.type: custom`)

| YAML Key | Data Type | Description | Kibana Default | Required |
| --------- | --------------------- | ------------------------------------------------ | ---------------- | -------- |
| `type` | `Literal['custom']` | Specifies custom formatting. | `custom` | Yes |
| `pattern` | `string` | A Numeral.js format pattern. | N/A | Yes |

---

## Pie Chart Specific Formatting

These objects are used within the `LensPieChart` configuration.

### Pie Chart Appearance (`appearance` field)

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | ------------------------------------- | ------------------------------------------------ | ---------------- | -------- |
| `donut` | `Literal['small', 'medium', 'large']` | If set, creates a donut chart with the specified hole size. | `None` (pie) | No |

### Pie Titles and Text (`titles_and_text` field)

| YAML Key | Data Type | Description | Kibana Default | Required |
| ---------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `slice_labels` | `Literal['hide', 'inside', 'auto']` | How to display labels for each slice. | `auto` | No |
| `slice_values` | `Literal['hide', 'integer', 'percent']` | How to display the value for each slice. | `percent` | No |
| `value_decimal_places` | `integer` (0-10) | Number of decimal places for slice values. | `2` | No |

### Pie Legend (`legend` field)

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `visible` | `Literal['show', 'hide', 'auto']` | Controls legend visibility. | `auto` | No |
| `width` | `Literal['small', 'medium', 'large', 'extra_large']` | Width of the legend area. | `medium` | No |
| `truncate_labels` | `integer` (0-5) | Max number of lines for legend labels before truncating. `0` disables truncation. | `1` | No |

### Color Mapping (`color` field)

| YAML Key | Data Type | Description | Kibana Default | Required |
| --------- | --------- | ------------------------------------------------ | ---------------- | -------- |
| `palette` | `string` | The ID of the color palette to use (e.g., `default`, `elasticColors`). | `default` | Yes |

## Related Documentation

* [Base Panel Configuration](base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
* [Queries Configuration](../queries/config.md)
* [Filters Configuration](../filters/config.md)
