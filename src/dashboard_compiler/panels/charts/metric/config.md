# Metric Chart Panel Configuration

The Metric chart panel displays a single value or a small set of key metrics, often used for KPIs or summary statistics.

## Minimal Configuration Example

```yaml
dashboard:
  name: "KPI Dashboard"
  panels:
    - type: metric
      title: "Total Revenue"
      grid: { x: 0, y: 0, w: 3, h: 2 }
      data:
        index: "sales-data"
        value: "revenue"
```

## Full Configuration Options

| YAML Key      | Data Type         | Description                                      | Required |
|--------------|-------------------|--------------------------------------------------|----------|
| `type`       | `Literal['metric']`| Specifies the panel type.                        | Yes      |
| `title`      | `string`          | Title of the panel.                              | No       |
| `grid`       | `Grid` object     | Position and size of the panel.                  | Yes      |
| `data`       | `object`          | Data source and field mapping.                   | Yes      |
| `value`      | `string`          | Field for the metric value.                      | Yes      |
| `color`      | `string`          | Color for the metric display.                    | No       |
| `description`| `string`          | Panel description.                               | No       |

## Programmatic Usage (Python)

You can create Metric chart panels programmatically using Python:

### Count Metric Example

```python
from dashboard_compiler.panels.charts.config import LensPanel
from dashboard_compiler.panels.charts.lens.metrics.config import (
    LensCountAggregatedMetric,
)
from dashboard_compiler.panels.charts.metric.config import LensMetricChart
from dashboard_compiler.panels.config import Grid

# Simple count metric
count_chart = LensMetricChart(
    type='metric',
    data_view='logs-*',
    primary=LensCountAggregatedMetric(aggregation='count'),
)

panel = LensPanel(
    type='charts',
    title='Total Documents',
    grid=Grid(x=0, y=0, w=24, h=15),
    chart=count_chart,
)
```

### Average Metric Example

```python
from dashboard_compiler.panels.charts.config import LensPanel
from dashboard_compiler.panels.charts.lens.metrics.config import (
    LensOtherAggregatedMetric,
)
from dashboard_compiler.panels.charts.metric.config import LensMetricChart
from dashboard_compiler.panels.config import Grid

# Average metric with field
avg_chart = LensMetricChart(
    type='metric',
    data_view='logs-*',
    primary=LensOtherAggregatedMetric(aggregation='average', field='response_time'),
)

panel = LensPanel(
    type='charts',
    title='Avg Response Time',
    grid=Grid(x=0, y=0, w=24, h=15),
    chart=avg_chart,
)
```

## Related

- [Base Panel Configuration](../../base.md)
- [Dashboard Configuration](../../../dashboard/dashboard.md)
