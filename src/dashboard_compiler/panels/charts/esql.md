# ESQL Panel

The `esql` panel is used to display data visualizations based on an ESQL query.

```yaml
- panel:
    type: esql
    # Common panel fields (id, title, description, grid, hide_title) also apply
    query: string         # (Required) The ESQL query string.
    chart: object         # (Required) The chart configuration for the ESQL panel.
```

## Fields

* `type` (required, string): Must be `esql`.
* `query` (required, string): The ESQL query string that determines the data for the chart.
* `chart` (required, object): The chart configuration for the ESQL panel. See [ESQL Chart Types](#esql-chart-types) for details.

## ESQL Chart Types

ESQL panels can display various chart types based on the results of the ESQL query. The configuration for the chart is defined within the `chart` object.

### ESQL Pie Chart

Represents a Pie chart configuration within an ESQL panel. Pie charts are used to visualize the proportion of categories from the ESQL query results.

```yaml
chart:
  type: pie           # (Required) Must be 'pie'.
  metric: object      # (Required) The metric that determines the size of the slices.
  slice_by: list      # (Required) The dimensions that determine the slices.
  appearance: object  # (Optional) Chart appearance formatting options.
  titles_and_text: object # (Optional) Titles and text formatting options.
  legend: object      # (Optional) Legend formatting options.
```

* **Fields:**
  * `type` (required, string): Must be `pie`.
  * `metric` (required, object): A metric that determines the size of the slice of the pie chart. This should be an [ESQL Metric Object](../metrics/metric.md#esql-metric) referencing a column from the ESQL query results.
  * `slice_by` (required, list of objects): The dimensions that determine the slices of the pie chart. This is a list of [ESQL Dimension Objects](../dimensions/dimension.md#esql-dimension-type) referencing columns from the ESQL query results.
  * `appearance` (optional, object): Formatting options for the chart appearance, including donut size. See [Pie Chart Appearance](../lens.md#pie-chart-appearance) for details.
  * `titles_and_text` (optional, object): Formatting options for the chart titles and text. See [Pie Chart Titles and Text](../lens.md#pie-chart-titles-and-text) for details.
  * `legend` (optional, object): Formatting options for the chart legend. See [Pie Chart Legend](../lens.md#pie-chart-legend) for details.

### ESQL Metric Chart

Represents a Metric chart configuration within an ESQL panel. Metric charts display a single value or a list of values from the ESQL query results.

```yaml
chart:
  type: metric        # (Required) Must be 'metric'.
  primary: object     # (Required) The primary metric to display.
  secondary: object   # (Optional) An optional secondary metric.
  maximum: object     # (Optional) An optional maximum metric.
  breakdown: object   # (Optional) An optional breakdown dimension.
```

* **Fields:**
  * `type` (required, string): Must be `metric`.
  * `primary` (required, object): The primary metric to display in the chart. This should be an [ESQL Metric Object](../metrics/metric.md#esql-metric) referencing a column from the ESQL query results.
  * `secondary` (optional, object): An optional secondary metric to display alongside the primary metric. This should be an [ESQL Metric Object](../metrics/metric.md#esql-metric) referencing a column from the ESQL query results.
  * `maximum` (optional, object): An optional maximum metric to display, often used for comparison or thresholds. This should be an [ESQL Metric Object](../metrics/metric.md#esql-metric) referencing a column from the ESQL query results.
  * `breakdown` (optional, object): An optional breakdown dimension to display. This should be an [ESQL Dimension Object](../dimensions/dimension.md#esql-dimension-type) referencing a column from the ESQL query results.

## Related Documentation

* [Base Panel Object](../base.md)
* [Metric Objects](../metrics/metric.md)
* [Dimension Objects](../dimensions/dimension.md)
* [Pie Chart Appearance](../lens.md#pie-chart-appearance)
* [Pie Chart Titles and Text](../lens.md#pie-chart-titles-and-text)
* [Pie Chart Legend](../lens.md#pie-chart-legend)
