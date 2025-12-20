# Lens Panel

The `lens` panel is used to display data visualizations created with Kibana Lens.

```yaml
- panel:
    type: lens
    # Common panel fields (id, title, description, grid, hide_title) also apply
    chart: object         # (Required) The chart configuration for the Lens panel.
```

## Fields

*   `type` (required, string): Must be `lens`.
*   `chart` (required, object): The chart configuration for the Lens panel. See [Lens Chart Types](#lens-chart-types) for details.

## Lens Chart Types

Lens panels can display various chart types. The configuration for the chart is defined within the `chart` object.

### Lens Pie Chart

Represents a Pie chart configuration within a Lens panel. Pie charts are used to visualize the proportion of categories.

```yaml
chart:
  type: pie           # (Required) Must be 'pie'.
  metric: object      # (Required) The metric that determines the size of the slices.
  slice_by: list      # (Required) The dimensions that determine the slices.
  appearance: object  # (Optional) Chart appearance formatting options.
  titles_and_text: object # (Optional) Titles and text formatting options.
  legend: object      # (Optional) Legend formatting options.
```

*   **Fields:**
    *   `type` (required, string): Must be `pie`.
    *   `metric` (required, object): A metric that determines the size of the slice of the pie chart. See [Metric Objects](../metrics/metric.md) for details on Lens metric types.
    *   `slice_by` (required, list of objects): The dimensions that determine the slices of the pie chart. This is a list of Lens dimension objects. See [Dimension Objects](../dimensions/dimension.md) for details on Lens dimension types.
    *   `appearance` (optional, object): Formatting options for the chart appearance, including donut size. See [Pie Chart Appearance](#pie-chart-appearance) for details.
    *   `titles_and_text` (optional, object): Formatting options for the chart titles and text. See [Pie Chart Titles and Text](#pie-chart-titles-and-text) for details.
    *   `legend` (optional, object): Formatting options for the chart legend. See [Pie Chart Legend](#pie-chart-legend) for details.

### Lens Metric Chart

Represents a Metric chart configuration within a Lens panel. Metric charts display a single value or a list of values, often representing key performance indicators.

```yaml
chart:
  type: metric        # (Required) Must be 'metric'.
  primary: object     # (Required) The primary metric to display.
  secondary: object   # (Optional) An optional secondary metric.
  maximum: object     # (Optional) An optional maximum metric.
  breakdown: object   # (Optional) An optional breakdown dimension.
```

*   **Fields:**
    *   `type` (required, string): Must be `metric`.
    *   `primary` (required, object): The primary metric to display in the chart. This is the main value shown in the metric visualization. See [Metric Objects](../metrics/metric.md) for details on Lens metric types.
    *   `secondary` (optional, object): An optional secondary metric to display alongside the primary metric. See [Metric Objects](../metrics/metric.md) for details on Lens metric types.
    *   `maximum` (optional, object): An optional maximum metric to display, often used for comparison or thresholds. See [Metric Objects](../metrics/metric.md) for details on Lens metric types.
    *   `breakdown` (optional, object): An optional breakdown dimension to display. See [Dimension Objects](../dimensions/dimension.md) for details on Lens dimension types.

## Pie Chart Appearance

Represents chart appearance formatting options for pie charts.

```yaml
appearance:
  donut: string       # (Optional) The size of the donut hole (small, medium, large).
```

*   `donut` (optional, string): The size of the donut hole in the pie chart. Options are `small`, `medium`, or `large`.

## Pie Chart Titles and Text

Represents titles and text formatting options for pie charts.

```yaml
titles_and_text:
  slice_labels: string # (Optional) Controls slice label visibility (hide, show, auto). Defaults to "auto".
  slice_values: string # (Optional) Controls slice value display (hide, integer, percent). Defaults to "percent".
  value_decimal_places: integer # (Optional) Number of decimal places for slice values (0-10). Defaults to 2.
```

*   `slice_labels` (optional, string): Controls the visibility of slice labels in the pie chart. Valid values are `hide`, `show`, or `auto`. Kibana defaults to `auto` if not specified.
*   `slice_values` (optional, string): Controls the display of slice values in the pie chart. Valid values are `hide`, `integer`, or `percent`. Kibana defaults to `percentage` if not specified.
*   `value_decimal_places` (optional, integer): Controls the number of decimal places for slice values in the pie chart. Value should be between 0 and 10. Kibana defaults to 2, if not specified.

## Pie Chart Legend

Represents legend formatting options for pie charts.

```yaml
legend:
  visible: string     # (Optional) Visibility of the legend (show, hide, auto). Defaults to "auto".
  width: string       # (Optional) Width of the legend (small, medium, large, extra_large). Defaults to "medium".
  truncate_labels: integer # (Optional) Number of lines to truncate labels (0-5). Defaults to 1.
```

*   `visible` (optional, string): Visibility of the legend in the pie chart. Valid values are `show`, `hide`, or `auto`. Kibana defaults to `auto` if not specified.
*   `width` (optional, string): Width of the legend in the pie chart. Valid values are `small`, `medium`, `large`, or `extra_large`. Kibana defaults to `medium` if not specified.
*   `truncate_labels` (optional, integer): Number of lines to truncate the legend labels to. Value should be between 0 and 5. Kibana defaults to 1 if not specified. Set to 0 to disable truncation.

## Related Documentation

*   [Base Panel Object](../base.md)
*   [Metric Objects](../metrics/metric.md)
*   [Dimension Objects](../dimensions/dimension.md)