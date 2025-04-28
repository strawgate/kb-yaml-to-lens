# Base Lens Chart and Common Structures

This document describes the common base structure for all Lens chart types and the common nested objects used for formatting.

## Base Lens Chart Object

All specific Lens chart types inherit from a base chart object.

```yaml
chart:
  id: string          # (Optional) Unique identifier for the chart.
  type: string        # (Required) Visualization type (e.g., bar, pie, area, line, table, metric).
  # --- Visualization Type Specific Fields Below ---
```

## Fields

*   `id` (optional, string): A unique identifier for the chart. If not provided, Kibana will generate one.
*   `type` (required, string): The specific type of Lens visualization. See the documentation for each chart type for valid values.

## Axis Object

The `axis` object defines formatting options for chart axes.

```yaml
axis:
  bottom: object    # (Optional) Bottom axis formatting.
  left: object      # (Optional) Left axis formatting.
  right: object     # (Optional) Right axis formatting.
```

### Fields

*   `bottom` (optional, object): Formatting for the bottom axis. See [Bottom Axis Formatting](#bottom-axis-formatting).
*   `left` (optional, object): Formatting for the left axis. See [Left Axis Formatting](#left-axis-formatting).
*   `right` (optional, object): Formatting for the right axis. See [Right Axis Formatting](#right-axis-formatting).

### Bottom Axis Formatting

```yaml
bottom:
  title: string   # (Optional) Axis title. Set to null to hide.
  scale: string   # (Optional) Axis scale type (linear, log, square, sqrt).
  gridlines: boolean # (Optional) Show gridlines.
  tick_labels: boolean # (Optional) Show tick labels.
  orientation: string # (Optional) Axis label orientation (horizontal, vertical, rotated).
  min: any        # (Optional) Minimum value ("auto" or number).
  max: any        # (Optional) Maximum value ("auto" or number).
  show_current_time_marker: boolean # (Optional) Show current time marker.
```

### Left Axis Formatting

```yaml
left:
  title: string   # (Optional) Axis title. Set to null to hide.
  scale: string   # (Optional) Axis scale type (linear, log, square, sqrt).
  gridlines: boolean # (Optional) Show gridlines.
  tick_labels: boolean # (Optional) Show tick labels.
  orientation: string # (Optional) Axis label orientation (horizontal, vertical, rotated).
  min: any        # (Optional) Minimum value ("auto" or number).
  max: any        # (Optional) Maximum value ("auto" or number).
```

### Right Axis Formatting

```yaml
right:
  title: string   # (Optional) Axis title. Set to null to hide.
  scale: string   # (Optional) Axis scale type (linear, log, square, sqrt).
  gridlines: boolean # (Optional) Show gridlines.
  tick_labels: boolean # (Optional) Show tick labels.
  orientation: string # (Optional) Axis label orientation (horizontal, vertical, rotated).
  min: any        # (Optional) Minimum value ("auto" or number).
  max: any        # (Optional) Maximum value ("auto" or number).
  metrics: list   # (Optional) List of metrics to display on the right axis. See [Metric Object](../components/metric.md).
```

## Legend Object

The `legend` object defines formatting options for the chart legend.

```yaml
legend:
  is_visible: boolean # (Optional) Show legend. Defaults to true.
  position: string  # (Optional) Legend position (right, left, top, bottom). Defaults to "right".
```

## Fields

*   `is_visible` (optional, boolean): If set to `false`, the legend will be hidden. Defaults to `true`.
*   `position` (optional, string): The position of the legend. Valid values are `right`, `left`, `top`, and `bottom`. Defaults to `right`.

## Appearance Object

The `appearance` object defines general appearance options for the chart.

```yaml
appearance:
  value_labels: string # (Optional) Show value labels (hide, show).
  fitting_function: string # (Optional) Fitting function (Linear).
  emphasize_fitting: boolean # (Optional) Emphasize the fitting function.
  curve_type: string # (Optional) Curve type (linear, cardinal, catmull-rom, natural, step, step-after, step-before, monotone-x).
  fill_opacity: number # (Optional) Fill opacity for area charts.
  min_bar_height: number # (Optional) Minimum bar height for bar charts.
  hide_endzones: boolean # (Optional) Hide endzones for date_histogram.
```

## Fields

*   `value_labels` (optional, string): Controls the visibility of value labels on chart elements. Can be `hide` or `show`.
*   `fitting_function` (optional, string): Specifies a fitting function for line/area charts. Currently only `Linear` is supported.
*   `emphasize_fitting` (optional, boolean): If set to `true`, the fitting function will be emphasized.
*   `curve_type` (optional, string): Specifies the curve type for line/area charts. Valid values include `linear`, `cardinal`, `catmull-rom`, `natural`, `step`, `step-after`, `step-before`, and `monotone-x`.
*   `fill_opacity` (optional, number): Sets the fill opacity for area charts (0.0 to 1.0).
*   `min_bar_height` (optional, number): Sets the minimum height for bars in bar charts.
*   `hide_endzones` (optional, boolean): If set to `true`, hides the endzones for date histogram visualizations.