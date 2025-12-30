# Metric Chart Panel Configuration

The Metric chart panel displays a single value or a small set of key metrics, often used for KPIs or summary statistics.

## A Poem for the Dashboard Architects

_For those who distill chaos into a single number:_

```text
One number to rule them all,
One metric standing proud and tall.
From millions of logs, a truth extracted,
A KPI perfectly compacted.

When executives ask "How are we doing?"
Your metric chart saves us from our undoing.
No need for graphs or tables wide,
Just one big number, full of pride.

Primary, secondary, maximum too,
These metrics tell the story true.
COUNT the users, SUM the sales,
AVERAGE the latency when the system fails.

So here's to metrics, bold and bright,
That make our dashboards such a sight!
A single value, clear and clean,
The most important number ever seen!
```

---

## Minimal Configuration Example

```yaml
dashboards:
  - name: "KPI Dashboard"
    panels:
      - type: charts
        title: "Total Revenue"
        grid: { x: 0, y: 0, w: 12, h: 2 }
        chart:
          type: metric
          data_view: "sales-data"
          primary:
            aggregation: sum
            field: revenue
```

## Full Configuration Options

### Lens Metric Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------- | -------------------------------- | ------------------------------------------------------------- | ---------- | -------- |
| `type` | `Literal['metric']` | Specifies the chart type as metric. | `'metric'` | No |
| `data_view` | `string` | The data view that determines the data for the metric chart. | N/A | Yes |
| `primary` | `LensMetricTypes` | The primary metric to display (main value). | N/A | Yes |
| `secondary` | `LensMetricTypes \| None` | Optional secondary metric to display alongside the primary. | `None` | No |
| `maximum` | `LensMetricTypes \| None` | Optional maximum metric for comparison or thresholds. | `None` | No |
| `breakdown` | `LensDimensionTypes \| None` | Optional breakdown dimension for splitting the metric. | `None` | No |

### ESQL Metric Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------- | -------------------------------- | ------------------------------------------------------------- | ---------- | -------- |
| `type` | `Literal['metric']` | Specifies the chart type as metric. | `'metric'` | No |
| `primary` | `ESQLMetricTypes` | The primary metric to display (main value). | N/A | Yes |
| `secondary` | `ESQLMetricTypes \| None` | Optional secondary metric to display alongside the primary. | `None` | No |
| `maximum` | `ESQLMetricTypes \| None` | Optional maximum metric for comparison or thresholds. | `None` | No |
| `breakdown` | `ESQLDimensionTypes \| None` | Optional breakdown dimension for splitting the metric. | `None` | No |

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
    data_view='logs-*',
    primary=LensCountAggregatedMetric(aggregation='count'),
)

panel = LensPanel(
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
    data_view='logs-*',
    primary=LensOtherAggregatedMetric(aggregation='average', field='response_time'),
)

panel = LensPanel(
    title='Avg Response Time',
    grid=Grid(x=0, y=0, w=24, h=15),
    chart=avg_chart,
)
```

## Related

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
