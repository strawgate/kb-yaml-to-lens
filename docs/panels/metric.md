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
      - title: "Total Hosts"
        grid: { x: 0, y: 0, w: 12, h: 2 }
        lens:
          type: metric
          data_view: "metrics-*"
          primary:
            aggregation: unique_count
            field: resource.attributes.host.name
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

#### Lens Metric Types

The `primary`, `secondary`, and `maximum` fields accept these metric configurations:

| Metric Type | Description | Key Fields | Example Use Case |
| ----------- | ----------- | ---------- | ---------------- |
| **Count** | Count documents or unique values | `aggregation: 'count' \| 'unique_count'`, `field` (optional) | Count total requests or unique users |
| **Sum** | Sum numeric field values | `aggregation: 'sum'`, `field` | Total revenue or bytes transferred |
| **Aggregation** | Other aggregations (avg, min, max, median, etc.) | `aggregation`, `field` | Average response time or max CPU usage |
| **Last Value** | Most recent value of a field | `aggregation: 'last_value'`, `field` | Latest status or most recent reading |
| **Percentile** | Calculate percentile of values | `aggregation: 'percentile'`, `field`, `percentile` | 95th percentile latency |
| **Percentile Rank** | Calculate rank of a value | `aggregation: 'percentile_rank'`, `field`, `rank` | What % of requests are faster than 500ms |
| **Formula** | Custom calculation using Kibana formula syntax | `formula`, `label` (optional), `format` (optional) | `count(kql='status:error') / count() * 100` |
| **Static Value** | Fixed numeric value | `value`, `label` (optional) | Target threshold or goal value |

**Common Fields:**

All metric types except Static Value support:

- `label`: Custom display label
- `format`: Number formatting (`number`, `bytes`, `bits`, `percent`, `duration`)
- `filter`: KQL filter to apply before aggregation

**Additional Field Details:**

- **Count**: Optional `field` (for counting specific field values), optional `exclude_zeros` (exclude zero values from count)
- **Sum**: Required `field`, optional `exclude_zeros` (exclude zero values from sum)
- **Last Value**: Required `field`, optional `date_field` (determines sort order for finding the most recent value)

**Examples:**

```yaml
# Count metric
primary:
  aggregation: count
  label: "Total Requests"

# Average metric
primary:
  aggregation: average
  field: response_time_ms
  label: "Avg Response Time"
  format:
    type: duration

# Formula metric
primary:
  formula: "count(kql='status:error') / count() * 100"
  label: "Error Rate %"
  format:
    type: percent
```

### ESQL Metric Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------- | -------------------------------- | ------------------------------------------------------------- | ---------- | -------- |
| `type` | `Literal['metric']` | Specifies the chart type as metric. | `'metric'` | No |
| `primary` | `ESQLMetricTypes` | The primary metric to display (main value). | N/A | Yes |
| `secondary` | `ESQLMetricTypes \| None` | Optional secondary metric to display alongside the primary. | `None` | No |
| `maximum` | `ESQLMetricTypes \| None` | Optional maximum metric for comparison or thresholds. | `None` | No |
| `breakdown` | `ESQLDimensionTypes \| None` | Optional breakdown dimension for splitting the metric. | `None` | No |
| `color` | `ColorMapping \| None` | Color palette mapping for the metric. See [Color Mapping Configuration](base.md#color-mapping-configuration). | `None` | No |

#### ESQL Metric Types

The `primary`, `secondary`, and `maximum` fields accept these metric configurations:

| Metric Type | Description | Key Fields | Example Use Case |
| ----------- | ----------- | ---------- | ---------------- |
| **ESQL Metric** | Reference a column from your ESQL query result | `field` | Any aggregated value from STATS clause |
| **Static Value** | Fixed numeric value | `value`, `label` (optional) | Target threshold or goal value |

**ESQL metrics** reference columns produced by your ESQL query. The `field` must match a column name in your query result.

**Example:**

```yaml
# ESQL metric referencing query result column
esql:
  type: metric
  query: |
    FROM logs-*
    | STATS
        total_requests = COUNT(*),
        avg_duration = AVG(event.duration),
        error_rate = COUNT(kql='event.outcome:failure') / COUNT(*) * 100
  primary:
    field: "total_requests"  # References column from STATS
  secondary:
    field: "avg_duration"    # References column from STATS
  maximum:
    field: "error_rate"      # References column from STATS
```

The ESQL query determines what metrics are available - each column in your STATS clause becomes a metric you can reference.

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

- [Base Panel Configuration](./base.md)
- [Dashboard Configuration](../dashboard/dashboard.md)
