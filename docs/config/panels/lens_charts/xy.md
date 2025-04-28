# Bar, Area, and Line Charts (Lens XY)

These Lens chart types (`bar`, `area`, `line`) are used to visualize data along two axes, typically a time or categorical dimension on the x-axis and one or more metrics on the y-axis.

```yaml
chart:
  type: string        # (Required) Visualization type: bar, area, or line.
  id: string          # (Optional) Unique identifier for the chart.
  mode: string        # (Optional, for bar, area) Stacking mode (stacked, unstacked, percentage). Defaults to "unstacked".
  dimensions: list    # (Required) Defines the dimensions (e.g., X-axis, Break down by). Min length 1.
  metrics: list       # (Required) Defines the values (e.g., Y-axis). Min length 1.
  axis: object        # (Optional) Axis formatting options.
  legend: object      # (Optional) Legend formatting options.
  appearance: object  # (Optional) Chart appearance options.
```

## Fields

*   `type` (required, string): Specifies the chart type. Must be one of `bar`, `area`, or `line`.
*   `id` (optional, string): A unique identifier for the chart.
*   `mode` (optional, string): Specifies the stacking mode for `bar` and `area` charts. Valid values are `stacked`, `unstacked`, and `percentage`. Defaults to `unstacked`. This field is not applicable to `line` charts.
*   `dimensions` (required, list of objects): Defines the dimensions used in the chart, typically for the x-axis or for breaking down the data into series. Requires at least one dimension. See [Dimension Object](../components/dimension.md).
*   `metrics` (required, list of objects): Defines the metrics used in the chart, typically for the y-axis. Requires at least one metric. See [Metric Object](../components/metric.md).
*   `axis` (optional, object): Formatting options for the chart axes. See [Axis Object](../base.md#axis-object).
*   `legend` (optional, object): Formatting options for the chart legend. See [Legend Object](../base.md#legend-object).
*   `appearance` (optional, object): General appearance options for the chart. See [Appearance Object](../base.md#appearance-object).

## Example

```yaml
dashboard:
  title: Line Chart Example
  panels:
    - panel:
        type: lens
        grid: { x: 0, y: 0, w: 24, h: 15 }
        index_pattern: logs-*
        chart:
          type: line
          dimensions:
            - field: "@timestamp"
              type: date_histogram
              interval: auto
          metrics:
            - type: count
              label: Event Count
```

## Related Structures

*   [Dimension Object](../components/dimension.md)
*   [Metric Object](../components/metric.md)
*   [Axis Object](../base.md#axis-object)
*   [Legend Object](../base.md#legend-object)
*   [Appearance Object](../base.md#appearance-object)