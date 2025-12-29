# XY Chart Panel Configuration

The XY chart panel creates line, bar, and area charts for time series and other data visualizations.

## Minimal Configuration Example

```yaml
dashboards:
-
  name: "Time Series Dashboard"
  panels:
    - type: xy
      title: "Events Over Time"
      grid: { x: 0, y: 0, w: 12, h: 6 }
      data:
        index: "logs-*"
        x_axis: "@timestamp"
        metric: "count"
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
| `reference_lines` | `list[XYReferenceLine] \| None` | Reference lines to display for threshold visualization. | `None` | No |
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
| `reference_lines` | `list[XYReferenceLine] \| None` | Reference lines to display for threshold visualization. | `None` | No |
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
| `reference_lines` | `list[XYReferenceLine] \| None` | Reference lines to display for threshold visualization. | `None` | No |
| `appearance` | `XYAppearance \| None` | Chart appearance formatting options. | `None` | No |
| `titles_and_text` | `XYTitlesAndText \| None` | Titles and text formatting options. | `None` | No |
| `legend` | `XYLegend \| None` | Legend formatting options. | `None` | No |

#### XYLegend Options

| YAML Key | Data Type | Description | Default | Required |
| --------- | ----------------- | ------------------------------ | ------- | -------- |
| `visible` | `bool \| None` | Whether the legend is visible. | `None` | No |

## Reference Lines

Reference lines allow you to display horizontal threshold lines on XY charts for visualizing SLAs, targets, or other important values.

### Basic Reference Line Example

```yaml
dashboards:
-
  name: "Service Level Dashboard"
  panels:
    - type: xy
      title: "Response Time with SLA"
      grid: { x: 0, y: 0, w: 24, h: 12 }
      data:
        index: "metrics-*"
        x_axis: "@timestamp"
        metric: "avg response_time"
        reference_lines:
          - label: "SLA Threshold"
            value: 500.0
            color: "#FF0000"
            line_style: "dashed"
```

### Advanced Reference Line Features

```yaml
dashboards:
-
  name: "Performance Monitoring"
  panels:
    - type: xy
      title: "Request Rate with Thresholds"
      grid: { x: 0, y: 0, w: 24, h: 12 }
      data:
        index: "metrics-*"
        x_axis: "@timestamp"
        metric: "count"
        reference_lines:
          - label: "Critical Threshold"
            value: 1000.0
            axis: "left"
            color: "#E7664C"
            line_style: "dotted"
            line_width: 3
            fill: "above"
            icon: "alert"
            icon_position: "above"
          - label: "Warning Threshold"
            value: 750.0
            color: "#F5A623"
            line_style: "dashed"
            line_width: 2
          - label: "Target"
            value: 500.0
            color: "#00FF00"
            line_style: "solid"
```

### Reference Line Configuration Options

| YAML Key | Data Type | Description | Default | Required |
| --------------- | ----------------------------------------------------------- | ------------------------------------------------------- | -------- | -------- |
| `value` | `float \| XYReferenceLineValue` | The y-axis value for the reference line. | N/A | Yes |
| `label` | `string \| None` | Label text displayed on the reference line. | `None` | No |
| `id` | `string \| None` | Optional unique identifier for the reference line. | `None` | No |
| `axis` | `Literal['left', 'right'] \| None` | Which y-axis to assign the reference line to. | `'left'` | No |
| `color` | `string \| None` | Color of the reference line (hex code). | Kibana Default | No |
| `line_width` | `int \| None` | Width of the reference line (1-10). | Kibana Default | No |
| `line_style` | `Literal['solid', 'dashed', 'dotted'] \| None` | Style of the reference line. | Kibana Default | No |
| `fill` | `Literal['above', 'below', 'none'] \| None` | Fill area above or below the line. | `None` | No |
| `icon` | `string \| None` | Icon to display on the reference line. | `None` | No |
| `icon_position` | `Literal['auto', 'left', 'right', 'above', 'below'] \| None` | Position of the icon relative to the line. | `None` | No |

### XYReferenceLineValue Object

For more explicit configuration, you can use an object format for the value:

```yaml
reference_lines:
  - label: "Threshold"
    value:
      type: "static"
      value: 500.0
    color: "#FF0000"
```

| YAML Key | Data Type | Description | Default | Required |
| -------- | -------------------- | ------------------------------------------ | --------- | -------- |
| `type` | `Literal['static']` | Type of reference line value. | `'static'` | No |
| `value` | `float` | The numeric value for the reference line. | N/A | Yes |

### ESQL Bar/Line/Area Charts

ESQL chart configuration is similar to Lens charts, but uses `ESQLDimensionTypes` and `ESQLMetricTypes` instead, and does not require a `data_view` field.

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
from dashboard_compiler.panels.charts.xy.config import (
    LensLineChart,
    XYReferenceLine,
)
from dashboard_compiler.panels.config import Grid

# Time series line chart with reference lines
line_chart = LensLineChart(
    data_view='logs-*',
    dimensions=[LensDateHistogramDimension(field='@timestamp')],
    breakdown=None,
    metrics=[LensCountAggregatedMetric(aggregation='count')],
    reference_lines=[
        XYReferenceLine(
            label='SLA Threshold',
            value=500.0,
            color='#FF0000',
            line_style='dashed',
            line_width=2,
        ),
        XYReferenceLine(
            label='Target',
            value=200.0,
            color='#00FF00',
            line_style='solid',
        ),
    ],
)

panel = LensPanel(
    title='Documents Over Time with Thresholds',
    grid=Grid(x=0, y=0, w=48, h=20),
    chart=line_chart,
)
```

## Related

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
