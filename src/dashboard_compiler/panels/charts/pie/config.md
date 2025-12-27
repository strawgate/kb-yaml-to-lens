# Pie Chart Panel Configuration

The Pie chart panel visualizes data as a pie or donut chart, useful for showing proportions of a whole.

## Minimal Configuration Example

```yaml
dashboard:
  name: "Traffic Sources"
  panels:
    - type: pie
      title: "Website Traffic Sources"
      grid: { x: 0, y: 0, w: 6, h: 6 }
      data:
        index: "traffic-data"
        category: "source"
        value: "visits"
```

## Full Configuration Options

| YAML Key      | Data Type        | Description                        | Default | Required |
| ------------- | ---------------- | ---------------------------------- | ------- | -------- |
| `type`        | `Literal['pie']` | Specifies the panel type.          | N/A     | Yes      |
| `title`       | `string`         | Title of the panel.                | `""`    | No       |
| `grid`        | `Grid` object    | Position and size of the panel.    | N/A     | Yes      |
| `data`        | `object`         | Data source and field mapping.     | N/A     | Yes      |
| `category`    | `string`         | Field for pie slices (categories). | N/A     | Yes      |
| `value`       | `string`         | Field for values (size of slices). | N/A     | Yes      |
| `donut`       | `boolean`        | Display as donut chart.            | `false` | No       |
| `color`       | `string/list`    | Color(s) for slices.               | `null`  | No       |
| `legend`      | `object`         | Legend display options.            | `null`  | No       |
| `description` | `string`         | Panel description.                 | `""`    | No       |

## Programmatic Usage (Python)

You can create Pie chart panels programmatically using Python:

```python
from dashboard_compiler.panels.charts.config import LensPanel
from dashboard_compiler.panels.charts.lens.dimensions.config import (
    LensTopValuesDimension,
)
from dashboard_compiler.panels.charts.lens.metrics.config import (
    LensCountAggregatedMetric,
)
from dashboard_compiler.panels.charts.pie.config import LensPieChart
from dashboard_compiler.panels.config import Grid

pie_chart = LensPieChart(
    data_view='logs-*',
    slice_by=[LensTopValuesDimension(field='status')],
    metric=LensCountAggregatedMetric(aggregation='count'),
)

panel = LensPanel(
    title='Status Distribution',
    grid=Grid(x=0, y=0, w=24, h=15),
    chart=pie_chart,
)
```

## Related

- [Base Panel Configuration](../../base.md)
- [Dashboard Configuration](../../../dashboard/dashboard.md)
