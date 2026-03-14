# Legend Configuration Guide

Legends help users understand what colors, lines, and shapes represent in their charts. This guide covers legend configuration options across different chart types in the kb-yaml-to-lens compiler.

## Overview

The legend displays a mapping between visual elements (colors, patterns, etc.) and the data they represent. Different chart types support different legend options:

- **XY Charts** (line, bar, area): Support position, size, visibility, and label truncation
- **Pie Charts**: Support position (via width), visibility, nested legends, and label truncation
- **Heatmap Charts**: Support position and visibility for the color scale legend

## Legend Options by Chart Type

### XY Chart Legends

XY charts (line, bar, and area charts) provide comprehensive legend customization:

```yaml
dashboards:
  - name: "XY Chart with Legend"
    panels:
      - title: "Request Count by Service"
        size: {w: 24, h: 15}
        lens:
          type: line
          data_view: "logs-*"
          dimension:
            field: "@timestamp"
            type: date_histogram
          breakdown:
            field: "service.name"
            type: values
          metrics:
            - aggregation: count
          legend:
            visible: show              # show, hide, or auto
            position: right             # top, bottom, left, or right
            size: medium                # small, medium, large, extra_large
            show_single_series: false   # Show legend even with one series
            truncate_labels: 1          # Lines to truncate labels (0-5)
```

**Available Options:**

| Option | Values | Description | Default | Required |
| ------ | ------ | ----------- | ------- | -------- |
| `visible` | `show`, `hide`, `auto` | Control legend visibility | `show` | No |
| `position` | `top`, `bottom`, `left`, `right` | Legend placement | `right` | No |
| `size` | `small`, `medium`, `large`, `extra_large` | Legend width/height | Auto | No |
| `show_single_series` | `true`, `false` | Show legend for single series | `false` | No |
| `truncate_labels` | `0` to `5` | Lines before truncation (0 = no truncation) | `1` | No |

### Pie Chart Legends

Pie charts have a simplified legend configuration focused on label formatting:

```yaml
dashboards:
  - name: "Pie Chart with Legend"
    panels:
      - title: "Traffic by Source"
        size: {w: 24, h: 15}
        lens:
          type: pie
          data_view: "logs-*"
          dimensions:
            - field: "traffic.source"
              type: values
          metrics:
            - aggregation: count
          legend:
            visible: auto              # show, hide, or auto
            width: medium               # small, medium, large, extra_large
            truncate_labels: 1          # Lines to truncate labels (0-5)
            nested: false               # Nested format for multi-level pies
            show_single_series: false   # Show legend for single series
```

**Available Options:**

| Option | Values | Description | Default | Required |
| ------ | ------ | ----------- | ------- | -------- |
| `visible` | `show`, `hide`, `auto` | Control legend visibility | `auto` | No |
| `width` | `small`, `medium`, `large`, `extra_large` | Legend width | `medium` | No |
| `truncate_labels` | `0` to `5` | Lines before truncation (0 = no truncation) | `1` | No |
| `nested` | `true`, `false` | Nested format for multi-level pies | `false` | No |
| `show_single_series` | `true`, `false` | Show legend for single series | `false` | No |

### Heatmap Chart Legends

Heatmap charts display a color scale legend:

```yaml
dashboards:
  - name: "Heatmap with Legend"
    panels:
      - title: "Activity Heatmap"
        size: {w: 24, h: 15}
        lens:
          type: heatmap
          data_view: "logs-*"
          x_axis:
            field: "@timestamp"
            type: date_histogram
          y_axis:
            field: "service.name"
            type: values
          value:
            aggregation: count
          legend:
            visible: show    # show or hide (auto not supported)
            position: right  # top, bottom, left, or right
```

**Available Options:**

| Option | Values | Description | Default | Required |
| ------ | ------ | ----------- | ------- | -------- |
| `visible` | `show`, `hide` | Control legend visibility (auto not supported) | `show` | No |
| `position` | `top`, `bottom`, `left`, `right` | Legend placement | `right` | No |

**Note:** Heatmap legends do not support the `auto` visibility option. Use `show` or `hide` explicitly.

## Best Practices

### 1. Choose Appropriate Visibility

- **Use `show`** when the legend is essential for understanding the chart (e.g., multiple series with similar colors)
- **Use `hide`** when the chart is self-explanatory or space is limited (e.g., single metric over time)
- **Use `auto`** (XY and Pie only) to let Kibana decide based on the data

### 2. Optimize Legend Position

- **Right position** (default): Works well for most time series charts
- **Bottom position**: Better for wide dashboards or charts with many series
- **Top position**: Useful when you want the legend prominently displayed
- **Left position**: Rarely used, but can work for charts with long series names

### 3. Manage Long Labels

Use `truncate_labels` to prevent legends from taking up too much space:

```yaml
legend:
  truncate_labels: 2  # Truncate to 2 lines
```

Set to `0` to disable truncation if you need to see full labels:

```yaml
legend:
  truncate_labels: 0  # No truncation
```

### 4. Size Considerations

Choose legend size based on the number of series and label length:

```yaml
# For many series or long labels
legend:
  size: large

# For few series with short labels
legend:
  size: small
```

### 5. Single Series Charts

For single-series charts, consider hiding the legend to save space:

```yaml
legend:
  show_single_series: false  # Default - hide legend for single series
```

Or show it for consistency across dashboards:

```yaml
legend:
  show_single_series: true  # Always show legend
```

## Common Patterns

### Pattern 1: Hide Legend for Simple Time Series

```yaml
lens:
  type: line
  data_view: "logs-*"
  dimension:
    field: "@timestamp"
    type: date_histogram
  metrics:
    - aggregation: count
      label: "Total Requests"
  legend:
    visible: hide  # Single metric doesn't need legend
```

### Pattern 2: Bottom Legend for Wide Charts

```yaml
lens:
  type: bar
  data_view: "logs-*"
  dimension:
    field: "service.name"
    type: values
  breakdown:
    field: "http.response.status_code"
    type: values
    size: 10
  metrics:
    - aggregation: count
  legend:
    position: bottom  # Better for many categories
    size: small
    truncate_labels: 1
```

### Pattern 3: Nested Pie Chart Legend

```yaml
lens:
  type: pie
  data_view: "logs-*"
  dimensions:
    - field: "service.name"
      type: values
    - field: "http.response.status_code"
      type: values
  metrics:
    - aggregation: count
  legend:
    visible: show
    nested: true       # Hierarchical legend for multi-level pie
    width: large
    truncate_labels: 2
```

### Pattern 4: Compact Heatmap Legend

```yaml
lens:
  type: heatmap
  data_view: "logs-*"
  x_axis:
    field: "@timestamp"
    type: date_histogram
  y_axis:
    field: "host.name"
    type: values
  value:
    aggregation: average
    field: "cpu.usage"
  legend:
    visible: show
    position: bottom  # Save horizontal space
```

## Examples

For comprehensive examples of legend configurations across different chart types, see:

- [XY Chart Examples](../panels/xy.md)
- [Pie Chart Examples](../panels/pie.md)
- [Heatmap Examples](../examples/heatmap-examples.yaml)

## Related Documentation

- [XY Charts](../panels/xy.md) - XY chart configuration and legend options
- [Pie Charts](../panels/pie.md) - Pie chart configuration and legend options
- [Heatmap Charts](../panels/heatmap.md) - Heatmap chart configuration and legend options
- [Base Panel Configuration](../panels/base.md) - Common panel configuration options
