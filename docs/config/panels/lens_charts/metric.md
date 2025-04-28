# Metric Chart (Lens Metric)

The `metric` Lens chart type is used to display a single numerical value, often with optional color thresholding.

```yaml
chart:
  type: metric        # (Required) Visualization type: metric.
  id: string          # (Optional) Unique identifier for the chart.
  metrics: list       # (Required) Defines the metric to display. Max length 1.
  palette: object     # (Optional) Defines color stops based on value.
```

## Fields

*   `type` (required, string): Specifies the chart type. Must be `metric`.
*   `id` (optional, string): A unique identifier for the chart.
*   `metrics` (required, list of objects): Defines the metric to be displayed. This list should contain exactly one object. See [Metric Object](../components/metric.md).
*   `palette` (optional, object): Defines color thresholds for the metric value. See [Palette Object](#palette-object).

## Example

```yaml
dashboard:
  title: Metric Chart Example
  panels:
    - panel:
        type: lens
        grid: { x: 0, y: 0, w: 12, h: 8 }
        index_pattern: logs-*
        chart:
          type: metric
          metrics:
            - type: unique_count
              field: user.id
              label: Unique Users
          palette:
            type: custom
            stops:
              - color: "#209280" # Green
                stop: null
              - color: "#d6bf57" # Yellow
                stop: 100
              - color: "#cc5642" # Red
                stop: 500
```

## Related Structures

*   [Metric Object](../components/metric.md)
*   [Palette Object](#palette-object)

### Palette Object

The `palette` object defines color stops for thresholding in a metric visualization.

```yaml
palette:
  type: custom      # (Required) Currently only 'custom' is supported.
  stops: list       # (Required) List of color stops.
    - color: string # (Required) Hex color code (e.g., "#cc5642").
      stop: number  # (Required) Threshold value for this color. Use `null` for the base/default color (lowest threshold). Order matters.
```

#### Fields

*   `type` (required, string): Must be `custom`.
*   `stops` (required, list of objects): A list of color stop objects. The order matters, defining the thresholds from lowest to highest.
    *   `color` (required, string): The hex color code (e.g., `#RRGGBB`) to use when the metric value is at or above the `stop` value.
    *   `stop` (required, number or null): The threshold value. Use `null` for the base color that applies below the first numerical threshold.