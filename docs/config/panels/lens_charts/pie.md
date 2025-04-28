# Pie Chart (Lens Pie)

The `pie` Lens chart type is used to visualize data as slices of a pie, representing the proportion of each category.

```yaml
chart:
  type: pie           # (Required) Visualization type: pie.
  id: string          # (Optional) Unique identifier for the chart.
  dimensions: list    # (Required) Defines the "Slice by" dimension. Max length 1.
  metrics: list       # (Required) Defines the "Size by" metric. Max length 1.
```

## Fields

*   `type` (required, string): Specifies the chart type. Must be `pie`.
*   `id` (optional, string): A unique identifier for the chart.
*   `dimensions` (required, list of objects): Defines the dimension used to slice the pie. This list should contain exactly one object, typically a `terms` aggregation. See [Dimension Object](../components/dimension.md).
*   `metrics` (required, list of objects): Defines the metric used to determine the size of each pie slice. This list should contain exactly one object. See [Metric Object](../components/metric.md).

## Example

```yaml
dashboard:
  title: Pie Chart Example
  panels:
    - panel:
        type: lens
        grid: { x: 0, y: 0, w: 24, h: 15 }
        index_pattern: logs-*
        chart:
          type: pie
          dimensions:
            - field: event.outcome
              type: terms
              label: Event Outcome
          metrics:
            - type: count
              label: Number of Events
```

## Related Structures

*   [Dimension Object](../components/dimension.md)
*   [Metric Object](../components/metric.md)