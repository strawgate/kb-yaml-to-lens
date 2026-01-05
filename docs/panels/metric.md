# Metric Chart Panel Configuration

The Metric chart panel displays a single value or a small set of key metrics, often used for KPIs or summary statistics.

## A Poem for the Dashboard Architects

_For those who distill chaos into a single number:_

```text
One number to rule them all,
One metric standing proud and tall.
From millions of logs, a truth extracted,
A KPI that comes perfectly compacted.

When executives ask "How are we doing?"
Your metric chart stops their stewing.
No need for graphs or tables wide,
Just one big number, full of pride.

Primary, secondary, maximum too,
These metrics tell the story true.
COUNT the users, SUM the sales,
AVERAGE the latency before the system fails.

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
      - title: "Total Revenue"
        grid: { x: 0, y: 0, w: 12, h: 2 }
        lens:
          type: metric
          data_view: "sales-data"
          primary:
            aggregation: sum
            field: revenue
```

## Formula Metric Example

Formula metrics allow you to create custom calculations using Kibana's formula syntax:

```yaml
dashboards:
  - name: "Error Monitoring"
    panels:
      - title: "Error Rate"
        grid: { x: 0, y: 0, w: 12, h: 2 }
        lens:
          type: metric
          data_view: "logs-*"
          primary:
            formula: "count(kql='status:error') / count() * 100"
            label: "Error Rate %"
            format:
              type: percent
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
| `color` | `ColorMapping \| None` | Color palette mapping for the metric. See [Color Mapping Configuration](base.md#color-mapping-configuration). | `None` | No |

### ESQL Metric Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------- | -------------------------------- | ------------------------------------------------------------- | ---------- | -------- |
| `type` | `Literal['metric']` | Specifies the chart type as metric. | `'metric'` | No |
| `primary` | `ESQLMetricTypes` | The primary metric to display (main value). | N/A | Yes |
| `secondary` | `ESQLMetricTypes \| None` | Optional secondary metric to display alongside the primary. | `None` | No |
| `maximum` | `ESQLMetricTypes \| None` | Optional maximum metric for comparison or thresholds. | `None` | No |
| `breakdown` | `ESQLDimensionTypes \| None` | Optional breakdown dimension for splitting the metric. | `None` | No |
| `color` | `ColorMapping \| None` | Color palette mapping for the metric. See [Color Mapping Configuration](base.md#color-mapping-configuration). | `None` | No |

## Programmatic Usage (Python)

You can create Metric chart panels programmatically using Python:

### Count Metric Example

```python
from dashboard_compiler.panels.charts.config import (
    LensMetricPanelConfig,
    LensPanel,
)
from dashboard_compiler.panels.charts.lens.metrics.config import (
    LensCountAggregatedMetric,
)
from dashboard_compiler.panels.config import Grid

panel = LensPanel(
    title='Total Documents',
    grid=Grid(x=0, y=0, w=24, h=15),
    lens=LensMetricPanelConfig(
        type='metric',
        data_view='logs-*',
        primary=LensCountAggregatedMetric(),
    ),
)
```

### Average Metric Example

```python
from dashboard_compiler.panels.charts.config import (
    LensMetricPanelConfig,
    LensPanel,
)
from dashboard_compiler.panels.charts.lens.metrics.config import (
    LensOtherAggregatedMetric,
)
from dashboard_compiler.panels.config import Grid

panel = LensPanel(
    title='Avg Response Time',
    grid=Grid(x=0, y=0, w=24, h=15),
    lens=LensMetricPanelConfig(
        type='metric',
        data_view='logs-*',
        primary=LensOtherAggregatedMetric(aggregation='average', field='response_time'),
    ),
)
```

### Formula Metric Example

```python
from dashboard_compiler.panels.charts.config import (
    LensMetricPanelConfig,
    LensPanel,
)
from dashboard_compiler.panels.charts.lens.metrics.config import (
    LensFormulaMetric,
    LensMetricFormat,
)
from dashboard_compiler.panels.config import Grid

panel = LensPanel(
    title='Error Rate',
    grid=Grid(x=0, y=0, w=24, h=15),
    lens=LensMetricPanelConfig(
        type='metric',
        data_view='logs-*',
        primary=LensFormulaMetric(
            formula="count(kql='status:error') / count() * 100",
            label='Error Rate %',
            format=LensMetricFormat(type='percent'),
        ),
    ),
)
```

## Related

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
