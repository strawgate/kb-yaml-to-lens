# XY Chart Panel Configuration

The XY chart panel creates line, bar, and area charts for time series and other data visualizations.

## Minimal Configuration Example

```yaml
dashboard:
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

| YAML Key          | Data Type                                       | Description                                                          | Default     | Required |
| ----------------- | ----------------------------------------------- | -------------------------------------------------------------------- | ----------- | -------- |
| `type`            | `Literal['bar']`                                | Specifies the chart type as bar.                                     | `'bar'`     | No       |
| `mode`            | `Literal['stacked', 'unstacked', 'percentage']` | Stacking mode for bar charts.                                        | `'stacked'` | No       |
| `data_view`       | `string`                                        | The data view to use for the chart.                                  | N/A         | Yes      |
| `dimensions`      | `list[LensDimensionTypes]`                      | Defines the dimensions (e.g., X-axis) for the chart.                 | `[]`        | No       |
| `metrics`         | `list[LensMetricTypes]`                         | Defines the metrics (e.g., Y-axis values) for the chart.             | `[]`        | No       |
| `breakdown`       | `LensDimensionTypes` \| `None`                  | Optional dimension to split the series by (creates multiple series). | `None`      | No       |
| `appearance`      | `XYAppearance` \| `None`                        | Chart appearance formatting options.                                 | `None`      | No       |
| `titles_and_text` | `XYTitlesAndText` \| `None`                     | Titles and text formatting options.                                  | `None`      | No       |
| `legend`          | `XYLegend` \| `None`                            | Legend formatting options.                                           | `None`      | No       |

### Lens Line Chart

| YAML Key          | Data Type                       | Description                                                          | Default  | Required |
| ----------------- | ------------------------------- | -------------------------------------------------------------------- | -------- | -------- |
| `type`            | `Literal['line']`               | Specifies the chart type as line.                                    | `'line'` | No       |
| `data_view`       | `string`                        | The data view to use for the chart.                                  | N/A      | Yes      |
| `dimensions`      | `list[LensDimensionTypes]`      | Defines the dimensions (e.g., X-axis) for the chart.                 | `[]`     | No       |
| `metrics`         | `list[LensMetricTypes]`         | Defines the metrics (e.g., Y-axis values) for the chart.             | `[]`     | No       |
| `breakdown`       | `LensDimensionTypes` \| `None`  | Optional dimension to split the series by (creates multiple series). | `None`   | No       |
| `appearance`      | `XYAppearance` \| `None`        | Chart appearance formatting options.                                 | `None`   | No       |
| `titles_and_text` | `XYTitlesAndText` \| `None`     | Titles and text formatting options.                                  | `None`   | No       |
| `legend`          | `XYLegend` \| `None`            | Legend formatting options.                                           | `None`   | No       |

### Lens Area Chart

| YAML Key          | Data Type                                       | Description                                                          | Default     | Required |
| ----------------- | ----------------------------------------------- | -------------------------------------------------------------------- | ----------- | -------- |
| `type`            | `Literal['area']`                               | Specifies the chart type as area.                                    | `'area'`    | No       |
| `mode`            | `Literal['stacked', 'unstacked', 'percentage']` | Stacking mode for area charts.                                       | `'stacked'` | No       |
| `data_view`       | `string`                                        | The data view to use for the chart.                                  | N/A         | Yes      |
| `dimensions`      | `list[LensDimensionTypes]`                      | Defines the dimensions (e.g., X-axis) for the chart.                 | `[]`        | No       |
| `metrics`         | `list[LensMetricTypes]`                         | Defines the metrics (e.g., Y-axis values) for the chart.             | `[]`        | No       |
| `breakdown`       | `LensDimensionTypes` \| `None`                  | Optional dimension to split the series by (creates multiple series). | `None`      | No       |
| `appearance`      | `XYAppearance` \| `None`                        | Chart appearance formatting options.                                 | `None`      | No       |
| `titles_and_text` | `XYTitlesAndText` \| `None`                     | Titles and text formatting options.                                  | `None`      | No       |
| `legend`          | `XYLegend` \| `None`                            | Legend formatting options.                                           | `None`      | No       |

#### XYLegend Options

| YAML Key  | Data Type         | Description                    | Default | Required |
| --------- | ----------------- | ------------------------------ | ------- | -------- |
| `visible` | `bool` \| `None`  | Whether the legend is visible. | `None`  | No       |

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

- [Base Panel Configuration](../../base.md)
- [Dashboard Configuration](../../../dashboard/dashboard.md)
