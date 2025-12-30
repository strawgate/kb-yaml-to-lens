# Gauge Chart Panel Configuration

The Gauge chart panel displays a single metric value with optional min/max ranges and goal indicators, typically used for KPIs and progress tracking toward targets or thresholds.

## A Poem for the Progress Trackers

_For those who measure how close we are to the goal:_

```text
Not just a number on the screen,
But progress toward a target seen.
A gauge that fills from left to right,
From zero darkness into light.

Where are we now? How far to go?
The gauge will always let you know.
From minimum to maximum range,
Watch the colored needle change.

A goal line drawn across the way—
"You're almost there!" the markers say.
Arc or bullet, circle, bar:
The gauge reveals just where you are.

CPU usage, quota met,
Performance targets? No sweat.
Not just data, but direction clear—
The gauge tracks progress through the year.
```

---

## Minimal Configuration Example

```yaml
dashboards:
  - name: "KPI Dashboard"
    panels:
      - type: charts
        title: "CPU Usage"
        grid: { x: 0, y: 0, w: 3, h: 2 }
        chart:
          type: gauge
          data_view: "metrics-*"
          metric:
            aggregation: average
            field: system.cpu.total.pct
```

## Static Values Example

You can use static numeric values for min/max/goal instead of field-based metrics:

```yaml
dashboards:
  - name: "Performance Dashboard"
    panels:
      - type: charts
        title: "Response Time"
        grid: { x: 0, y: 0, w: 4, h: 3 }
        chart:
          type: gauge
          data_view: "logs-*"
          metric:
            aggregation: average
            field: response_time_ms
          minimum: 0        # Static value
          maximum: 1000     # Static value
          goal: 500         # Static value
          appearance:
            shape: arc
            color_mode: palette
```

## Full Configuration Options

### Lens Gauge Chart

| YAML Key | Data Type | Description | Default | Required |
| ---------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['gauge']` | Specifies the chart type as gauge. | `'gauge'` | No |
| `data_view` | `string` | The data view that determines the data for the gauge chart. | N/A | Yes |
| `metric` | `LensMetricTypes` | The primary metric to display (main value shown in the gauge). | N/A | Yes |
| `minimum` | `LensMetricTypes \| int \| float \| None` | Optional minimum value for the gauge range. Can be a metric (field-based) or a static numeric value. | `None` | No |
| `maximum` | `LensMetricTypes \| int \| float \| None` | Optional maximum value for the gauge range. Can be a metric (field-based) or a static numeric value. | `None` | No |
| `goal` | `LensMetricTypes \| int \| float \| None` | Optional goal/target value shown as a reference. Can be a metric (field-based) or a static numeric value. | `None` | No |
| `appearance` | `GaugeAppearance \| None` | Visual appearance configuration for the gauge. | `None` | No |

### ESQL Gauge Chart

| YAML Key | Data Type | Description | Default | Required |
| ---------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['gauge']` | Specifies the chart type as gauge. | `'gauge'` | No |
| `metric` | `ESQLMetricTypes` | The primary metric to display (main value shown in the gauge). | N/A | Yes |
| `minimum` | `ESQLMetricTypes \| int \| float \| None` | Optional minimum value for the gauge range. Can be a metric (field-based) or a static numeric value. | `None` | No |
| `maximum` | `ESQLMetricTypes \| int \| float \| None` | Optional maximum value for the gauge range. Can be a metric (field-based) or a static numeric value. | `None` | No |
| `goal` | `ESQLMetricTypes \| int \| float \| None` | Optional goal/target value shown as a reference. Can be a metric (field-based) or a static numeric value. | `None` | No |
| `appearance` | `GaugeAppearance \| None` | Visual appearance configuration for the gauge. | `None` | No |

### Gauge Appearance Options

| YAML Key | Data Type | Description | Default | Required |
| ---------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------- | ---------------- | -------- |
| `shape` | `'horizontalBullet' \| 'verticalBullet' \| 'arc' \| 'circle' \| None` | The shape of the gauge visualization. | `'arc'` | No |
| `ticks_position` | `'auto' \| 'bands' \| 'hidden' \| None` | Position of tick marks on the gauge. | `'auto'` | No |
| `label_major` | `string \| None` | Major label text to display on the gauge. | `None` | No |
| `label_minor` | `string \| None` | Minor label text to display on the gauge. | `None` | No |
| `color_mode` | `'none' \| 'palette' \| None` | Color mode for the gauge visualization. | `None` | No |

## Shape Options

The `shape` parameter determines the visual style of the gauge:

- **`arc`**: Semicircular arc (180°) - default style, good for dashboards
- **`circle`**: Full circular gauge (360°) - maximizes data-ink ratio
- **`horizontalBullet`**: Linear horizontal bar - space-efficient
- **`verticalBullet`**: Linear vertical bar - good for vertical layouts

## Programmatic Usage (Python)

You can create Gauge chart panels programmatically using Python:

### Basic Gauge Example

```python
from dashboard_compiler.panels.charts.config import LensPanel
from dashboard_compiler.panels.charts.gauge.config import LensGaugeChart
from dashboard_compiler.panels.charts.lens.metrics.config import (
    LensOtherAggregatedMetric,
)
from dashboard_compiler.panels.config import Grid

# Simple gauge showing average CPU usage
gauge_chart = LensGaugeChart(
    data_view='metrics-*',
    metric=LensOtherAggregatedMetric(
        aggregation='average', field='system.cpu.total.pct'
    ),
)

panel = LensPanel(
    title='CPU Usage',
    grid=Grid(x=0, y=0, w=6, h=4),
    chart=gauge_chart,
)
```

### Gauge with Min/Max/Goal Example

```python
from dashboard_compiler.panels.charts.config import LensPanel
from dashboard_compiler.panels.charts.gauge.config import (
    GaugeAppearance,
    LensGaugeChart,
)
from dashboard_compiler.panels.charts.lens.metrics.config import (
    LensOtherAggregatedMetric,
    LensSumAggregatedMetric,
)
from dashboard_compiler.panels.config import Grid

# Gauge with range and goal indicator
gauge_chart = LensGaugeChart(
    data_view='sales-*',
    metric=LensSumAggregatedMetric(
        aggregation='sum', field='revenue', label='Current Revenue'
    ),
    minimum=LensOtherAggregatedMetric(aggregation='min', field='revenue'),
    maximum=LensOtherAggregatedMetric(aggregation='max', field='revenue'),
    goal=LensOtherAggregatedMetric(aggregation='average', field='revenue_target'),
    appearance=GaugeAppearance(
        shape='arc',
        color_mode='palette',
    ),
)

panel = LensPanel(
    title='Revenue vs Target',
    grid=Grid(x=0, y=0, w=6, h=4),
    chart=gauge_chart,
)
```

### ESQL Gauge Example

```python
from dashboard_compiler.panels.charts.config import ESQLPanel
from dashboard_compiler.panels.charts.esql.columns.config import ESQLMetric
from dashboard_compiler.panels.charts.gauge.config import (
    ESQLGaugeChart,
    GaugeAppearance,
)
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.queries.config import ESQLQuery

# ESQL-based gauge with static min/max/goal
gauge_chart = ESQLGaugeChart(
    metric=ESQLMetric(field='avg_cpu'),
    minimum=0,  # Static value
    maximum=100,  # Static value
    goal=80,  # Static value
    appearance=GaugeAppearance(
        shape='horizontalBullet',
    ),
)

panel = ESQLPanel(
    title='Average CPU Usage',
    grid=Grid(x=0, y=0, w=6, h=4),
    esql=ESQLQuery('FROM metrics-* | STATS avg_cpu = AVG(system.cpu.total.pct)'),
    chart=gauge_chart,
)
```

## Related

- [Base Panel Configuration](./base.md)
- [Dashboard Configuration](../dashboard/dashboard.md)
- [Metric Charts](./metric.md)
