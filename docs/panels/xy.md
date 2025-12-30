# XY Chart Panel Configuration

The XY chart panel creates line, bar, and area charts for time series and other data visualizations.

## A Poem for the Time Series Enthusiasts

_For those who see patterns across the timeline:_

```text
Lines that rise and bars that fall,
Area charts that show it all.
X-axis marching through the time,
Y-axis tracking every climb.

When incidents spike at 2 AM,
Your XY charts help us understand them.
Stacked or unstacked, the choice is yours,
Percentage mode for ratio scores.

Dimensions define the horizontal way,
Metrics show values throughout the day.
Breakdown by service, host, or zone,
Every pattern clearly shown.

From request counts to error rates,
Your time series never hesitates.
So here's to charts both line and bar,
That help us see how systems are!
```

---

## Minimal Configuration Example

```yaml
dashboards:
  - name: "Time Series Dashboard"
    panels:
      - type: charts
        title: "Events Over Time"
        grid: { x: 0, y: 0, w: 48, h: 6 }
        chart:
          type: line
          data_view: "logs-*"
          dimensions:
            - field: "@timestamp"
          metrics:
            - aggregation: count
```

## Full Configuration Options

### Lens Bar Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------------- | ----------------------------------------------- | -------------------------------------------------------------------- | ----------- | -------- |
| `type` | `Literal['bar']` | Specifies the chart type as bar. | `'bar'` | No |
| `mode` | `Literal['stacked', 'unstacked', 'percentage']` | Stacking mode for bar charts. | `'stacked'` | No |
| `data_view` | `string` | The data view to use for the chart. | N/A | Yes |
| `dimensions` | `list[LensDimensionTypes]` | Defines the dimensions (e.g., X-axis) for the chart. | `[]` | No |
| `metrics` | `list[LensMetricTypes]` | Defines the metrics (e.g., Y-axis values) for the chart. | `[]` | No |
| `breakdown` | `LensDimensionTypes \| None` | Optional dimension to split the series by (creates multiple series). | `None` | No |
| `series` | `list[XYSeries] \| None` | Per-series styling and axis assignment. | `None` | No |
| `appearance` | `XYAppearance \| None` | Chart appearance formatting options. | `None` | No |
| `titles_and_text` | `XYTitlesAndText \| None` | Titles and text formatting options. | `None` | No |
| `legend` | `XYLegend \| None` | Legend formatting options. | `None` | No |

### Lens Line Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------------- | ------------------------------- | -------------------------------------------------------------------- | -------- | -------- |
| `type` | `Literal['line']` | Specifies the chart type as line. | `'line'` | No |
| `data_view` | `string` | The data view to use for the chart. | N/A | Yes |
| `dimensions` | `list[LensDimensionTypes]` | Defines the dimensions (e.g., X-axis) for the chart. | `[]` | No |
| `metrics` | `list[LensMetricTypes]` | Defines the metrics (e.g., Y-axis values) for the chart. | `[]` | No |
| `breakdown` | `LensDimensionTypes \| None` | Optional dimension to split the series by (creates multiple series). | `None` | No |
| `series` | `list[XYSeries] \| None` | Per-series styling and axis assignment. | `None` | No |
| `appearance` | `XYAppearance \| None` | Chart appearance formatting options. | `None` | No |
| `titles_and_text` | `XYTitlesAndText \| None` | Titles and text formatting options. | `None` | No |
| `legend` | `XYLegend \| None` | Legend formatting options. | `None` | No |

### Lens Area Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------------- | ----------------------------------------------- | -------------------------------------------------------------------- | ----------- | -------- |
| `type` | `Literal['area']` | Specifies the chart type as area. | `'area'` | No |
| `mode` | `Literal['stacked', 'unstacked', 'percentage']` | Stacking mode for area charts. | `'stacked'` | No |
| `data_view` | `string` | The data view to use for the chart. | N/A | Yes |
| `dimensions` | `list[LensDimensionTypes]` | Defines the dimensions (e.g., X-axis) for the chart. | `[]` | No |
| `metrics` | `list[LensMetricTypes]` | Defines the metrics (e.g., Y-axis values) for the chart. | `[]` | No |
| `breakdown` | `LensDimensionTypes \| None` | Optional dimension to split the series by (creates multiple series). | `None` | No |
| `series` | `list[XYSeries] \| None` | Per-series styling and axis assignment. | `None` | No |
| `appearance` | `XYAppearance \| None` | Chart appearance formatting options. | `None` | No |
| `titles_and_text` | `XYTitlesAndText \| None` | Titles and text formatting options. | `None` | No |
| `legend` | `XYLegend \| None` | Legend formatting options. | `None` | No |

#### XYLegend Options

| YAML Key | Data Type | Description | Default | Required |
| ---------- | -------------------------------------------------------- | ------------------------------------------------- | ------- | -------- |
| `visible` | `bool \| None` | Whether the legend is visible. | `None` | No |
| `position` | `Literal['top', 'bottom', 'left', 'right'] \| None` | Position of the legend (Kibana defaults to 'right'). | `None` | No |

#### XYAppearance Options

Configures the visual appearance of axes in XY charts. Allows customization of axis titles, scales, and extent (bounds).

| YAML Key | Data Type | Description | Default | Required |
| ------------- | ---------------------- | -------------------------------------------------------- | ------- | -------- |
| `x_axis` | `AxisConfig \| None` | Configuration for the X-axis (horizontal axis). | `None` | No |
| `y_left_axis` | `AxisConfig \| None` | Configuration for the left Y-axis (primary vertical axis). | `None` | No |
| `y_right_axis` | `AxisConfig \| None` | Configuration for the right Y-axis (secondary vertical axis). | `None` | No |

#### AxisConfig Options

Defines configuration for a single axis.

| YAML Key | Data Type | Description | Default | Required |
| -------- | -------------------------------- | ---------------------------------------------- | ------- | -------- |
| `title` | `str \| None` | Custom title for the axis. | `None` | No |
| `scale` | `Literal['linear', 'log'] \| None` | Scale type for the axis (linear or logarithmic). | `None` | No |
| `extent` | `AxisExtent \| None` | Axis bounds/range configuration. | `None` | No |

#### AxisExtent Options

Configures the bounds (range) of an axis.

| YAML Key | Data Type | Description | Default | Required |
| ------------- | -------------------------------------------- | --------------------------------------------------------- | ------- | -------- |
| `mode` | `Literal['full', 'data_bounds', 'custom']` | Extent mode: 'full' (entire range), 'data_bounds' (fit to data), 'custom' (manual bounds). | N/A | Yes |
| `min` | `float \| None` | Minimum bound (required if mode is 'custom'). | `None` | No |
| `max` | `float \| None` | Maximum bound (required if mode is 'custom'). | `None` | No |
| `enforce` | `bool \| None` | Whether to enforce the bounds strictly. | `None` | No |
| `nice_values` | `bool \| None` | Whether to round bounds to nice values. | `None` | No |

#### XYSeries Options

Configures per-series visual styling and axis assignment. Used to customize individual metrics within a chart.

| YAML Key | Data Type | Description | Default | Required |
| ----------- | ------------------------------------------------- | ------------------------------------------------------------ | ------- | -------- |
| `metric_id` | `str` | ID of the metric this series configuration applies to. | N/A | Yes |
| `axis` | `Literal['left', 'right'] \| None` | Which Y-axis this series is assigned to (for dual-axis charts). | `None` | No |
| `color` | `str \| None` | Hex color code for the series (e.g., '#2196F3'). | `None` | No |
| `line_width` | `int \| None` | Line width (1-10 pixels). | `None` | No |
| `line_style` | `Literal['solid', 'dashed', 'dotted'] \| None` | Line style for line/area charts. | `None` | No |
| `fill` | `Literal['none', 'below', 'above'] \| None` | Fill style for area charts. | `None` | No |
| `icon` | `Literal['circle', 'square', 'triangle'] \| None` | Point marker icon for line charts. | `None` | No |

### ESQL Bar/Line/Area Charts

ESQL chart configuration is similar to Lens charts, but uses `ESQLDimensionTypes` and `ESQLMetricTypes` instead, and does not require a `data_view` field.

## Usage Examples

### Dual Y-Axis Chart

Create a chart with two metrics on different Y-axes:

```yaml
dashboards:
  - name: "Performance Dashboard"
    panels:
      - type: charts
        title: "Request Count vs Error Rate"
        grid: { x: 0, y: 0, w: 48, h: 12 }
        chart:
          type: line
          data_view: "logs-*"
          dimensions:
            - field: "@timestamp"
              id: "time"
          metrics:
            - aggregation: count
              id: "request_count"
            - aggregation: average
              field: "error_rate"
              id: "avg_error_rate"
          appearance:
            y_left_axis:
              title: "Request Count"
              scale: linear
            y_right_axis:
              title: "Error Rate (%)"
              scale: linear
          series:
            - metric_id: "request_count"
              axis: left
              color: "#2196F3"
              line_width: 2
            - metric_id: "avg_error_rate"
              axis: right
              color: "#FF5252"
              line_width: 3
              line_style: dashed
```

### Custom Axis Bounds

Set explicit axis ranges:

```yaml
dashboards:
  - name: "SLA Dashboard"
    panels:
      - type: charts
        title: "Response Time (0-1000ms)"
        grid: { x: 0, y: 0, w: 48, h: 12 }
        chart:
          type: line
          data_view: "logs-*"
          dimensions:
            - field: "@timestamp"
          metrics:
            - aggregation: average
              field: "response_time_ms"
          appearance:
            y_left_axis:
              title: "Response Time (ms)"
              extent:
                mode: custom
                min: 0
                max: 1000
                enforce: true
                nice_values: true
```

### Styled Series

Customize individual series appearance:

```yaml
dashboards:
  - name: "Network Dashboard"
    panels:
      - type: charts
        title: "Network Traffic"
        grid: { x: 0, y: 0, w: 48, h: 12 }
        chart:
          type: area
          data_view: "metrics-*"
          dimensions:
            - field: "@timestamp"
          metrics:
            - aggregation: sum
              field: "bytes_in"
              id: "inbound"
            - aggregation: sum
              field: "bytes_out"
              id: "outbound"
          series:
            - metric_id: "inbound"
              color: "#4CAF50"
              fill: below
              line_style: solid
            - metric_id: "outbound"
              color: "#FF9800"
              fill: below
              line_style: dotted
```

## Programmatic Usage (Python)

You can create XY chart panels programmatically using Python:

```python
from dashboard_compiler.panels.charts.config import LensPanel
from dashboard_compiler.panels.charts.lens.dimensions.config import (
    LensDateHistogramDimension,
)
from dashboard_compiler.panels.charts.lens.metrics.config import (
    LensCountAggregatedMetric,
)
from dashboard_compiler.panels.charts.xy.config import LensLineChart
from dashboard_compiler.panels.config import Grid

# Time series line chart
line_chart = LensLineChart(
    data_view='logs-*',
    dimensions=[LensDateHistogramDimension(field='@timestamp')],
    breakdown=None,
    metrics=[LensCountAggregatedMetric(aggregation='count')],
)

panel = LensPanel(
    title='Documents Over Time',
    grid=Grid(x=0, y=0, w=48, h=20),
    chart=line_chart,
)
```

## Related

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
