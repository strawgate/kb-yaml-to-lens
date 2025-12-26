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

| YAML Key      | Data Type         | Description                                      | Required |
|--------------|-------------------|--------------------------------------------------|----------|
| `type`       | `Literal['xy']`   | Specifies the panel type.                        | Yes      |
| `title`      | `string`          | Title of the panel.                              | No       |
| `grid`       | `Grid` object     | Position and size of the panel.                  | Yes      |
| `data`       | `object`          | Data source and field mapping.                   | Yes      |
| `x_axis`     | `string`          | Field for X-axis (typically timestamp).          | Yes      |
| `metrics`    | `list`            | List of metrics to display.                      | Yes      |
| `chart_type` | `string`          | Chart type: 'line', 'bar', or 'area'.            | No       |
| `legend`     | `object`          | Legend display options.                          | No       |
| `description`| `string`          | Panel description.                               | No       |

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
    type='line',
    data_view='logs-*',
    dimensions=[LensDateHistogramDimension(field='@timestamp')],
    breakdown=None,
    metrics=[LensCountAggregatedMetric(aggregation='count')],
)

panel = LensPanel(
    type='charts',
    title='Documents Over Time',
    grid=Grid(x=0, y=0, w=48, h=20),
    chart=line_chart,
)
```

## Related

- [Base Panel Configuration](../../base.md)
- [Dashboard Configuration](../../../dashboard/dashboard.md)
