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
        size: {w: 12, h: 2}
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
        size: {w: 12, h: 2}
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
| `maximum` | `LensMetricTypes \| None` | Optional maximum metric for comparison or progress bar scale. | `None` | No |
| `breakdown` | `LensDimensionTypes \| None` | Optional breakdown dimension for splitting the metric. | `None` | No |
| `appearance` | `MetricAppearance \| None` | Visual appearance configuration. See [Metric Appearance](#metric-appearance). | `None` | No |
| `titles_and_text` | `MetricTitlesAndText \| None` | Titles and text formatting options. See [Metric Titles and Text](#metric-titles-and-text). | `None` | No |

Color thresholds and `apply_to` are configured on the primary metric's `color` field (e.g., `primary.color.thresholds`, `primary.color.apply_to`). Legacy chart-level `color` and `apply_to` are not accepted in `0.4.0`; run `kb-dashboard upgrade` to migrate old files.

#### Metric Appearance

| YAML Key | Data Type | Description | Default | Required |
| ----------- | -------------------------------- | ------------------------------------------------------------- | ---------- | -------- |
| `primary.icon` | `string \| None` | Icon identifier to display alongside the primary metric value. | `None` | No |
| `primary.icon_position` | `Literal['left', 'right'] \| None` | Horizontal alignment of the icon relative to the primary metric value. | `None` | No |
| `primary.background_chart.type` | `Literal['line', 'bar', 'none'] \| None` | Background chart mode for the primary metric. | `None` | No |
| `primary.background_chart.direction` | `Literal['horizontal', 'vertical'] \| None` | Direction for bar background charts. Only valid when type is `bar`. | `None` | No |
| `primary.font_size` | `Literal['default', 'fit', 'custom'] \| None` | Font size mode for the primary metric value. | `None` | No |
| `primary.position` | `Literal['top', 'bottom'] \| None` | Vertical position of the primary metric value within the panel. | `None` | No |
| `primary.alignment` | `Literal['left', 'center', 'right'] \| None` | Text alignment for the primary metric value. | `None` | No |
| `secondary.alignment` | `Literal['left', 'center', 'right'] \| None` | Text alignment for the secondary metric value. | `None` | No |
| `secondary.label.text` | `string \| None` | Custom label text for the secondary metric. | `None` | No |
| `secondary.label.position` | `Literal['before', 'after'] \| None` | Position of the secondary label relative to the value. | `None` | No |
| `breakdown.column_count` | `int \| None` | Maximum number of columns when displaying broken-down metrics. Minimum value is `1`. | `None` | No |

#### Metric Titles and Text

| YAML Key | Data Type | Description | Default | Required |
| ----------- | -------------------------------- | ------------------------------------------------------------- | ---------- | -------- |
| `subtitle` | `string \| None` | Custom subtitle text displayed below the metric title. | `None` | No |
| `alignment` | `Literal['left', 'center', 'right'] \| None` | Text alignment for the metric title and subtitle. | `None` | No |
| `weight` | `Literal['bold', 'normal', 'lighter'] \| None` | Font weight for the metric title. | `None` | No |

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
- `format`: Number formatting (see [Format Configuration Options](#format-configuration-options) for details)
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
| `maximum` | `ESQLMetricTypes \| None` | Optional maximum metric for comparison or progress bar scale. | `None` | No |
| `breakdown` | `ESQLDimensionTypes \| None` | Optional breakdown dimension for splitting the metric. | `None` | No |
| `appearance` | `MetricAppearance \| None` | Visual appearance configuration. See [Metric Appearance](#metric-appearance). | `None` | No |
| `titles_and_text` | `MetricTitlesAndText \| None` | Titles and text formatting options. See [Metric Titles and Text](#metric-titles-and-text). | `None` | No |

Color thresholds and `apply_to` are configured on the primary metric's `color` field (e.g., `primary.color.thresholds`, `primary.color.apply_to`). Legacy chart-level `color` and `apply_to` are not accepted in `0.4.0`; run `kb-dashboard upgrade` to migrate old files.

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

## Color Mode

Use `primary.color.apply_to` to control how metric colors are applied:

- `value`: apply colors to metric value text
- `background`: apply colors to metric background (default)

```yaml
dashboards:
  - name: "Metric Color Modes"
    panels:
      - title: "Error Rate (Value Colors)"
        size: {w: 8, h: 4}
        lens:
          type: metric
          data_view: "logs-*"
          primary:
            formula: "count(kql='event.outcome:failure') / count() * 100"
            label: "Error Rate"
            color:
              apply_to: value
            format:
              type: percent

      - title: "Availability (Background Colors)"
        size: {w: 8, h: 4}
        position: {x: 8, y: 0}
        lens:
          type: metric
          data_view: "logs-*"
          primary:
            formula: "count(kql='event.outcome:success') / count() * 100"
            label: "Availability"
            color:
              apply_to: background
            format:
              type: percent
```

## Styling Options

Metric panels support a variety of styling options to control layout, alignment, and typography.

### Subtitle and Secondary Label

Add contextual information with custom subtitles and secondary metric labels:

```yaml
dashboards:
  - name: "Styled Metrics"
    panels:
      - title: "CPU Usage"
        size: {w: 12, h: 4}
        lens:
          type: metric
          data_view: "metrics-*"
          appearance:
            secondary:
              label:
                text: "vs. previous day"
                position: after
          titles_and_text:
            subtitle: "Last 24 hours"
          primary:
            aggregation: average
            field: system.cpu.total.norm.pct
            format:
              type: percent
          secondary:
            aggregation: average
            field: system.cpu.total.norm.pct
            filter:
              kql: "@timestamp < now-1d"
```

### Progress Bar

Display a progress bar below the metric value to show progress toward a maximum:

```yaml
dashboards:
  - name: "Progress Metrics"
    panels:
      - title: "Disk Usage"
        size: {w: 12, h: 4}
        lens:
          type: metric
          data_view: "metrics-*"
          appearance:
            primary:
              background_chart:
                type: bar
                direction: horizontal
          primary:
            aggregation: average
            field: system.filesystem.used.pct
            format:
              type: percent
          maximum:
            value: 1
```

### Icon

Add an icon alongside the metric value:

```yaml
dashboards:
  - name: "Icon Metrics"
    panels:
      - title: "Uptrend Indicator"
        size: {w: 12, h: 4}
        lens:
          type: metric
          data_view: "metrics-*"
          appearance:
            primary:
              icon: sortUp
              icon_position: right
          primary:
            aggregation: count
```

### Text Alignment and Typography

Control alignment and font properties for different parts of the metric:

```yaml
dashboards:
  - name: "Aligned Metrics"
    panels:
      - title: "Centered KPI"
        size: {w: 12, h: 4}
        lens:
          type: metric
          data_view: "metrics-*"
          appearance:
            primary:
              font_size: fit
              position: top
              alignment: center
            secondary:
              alignment: center
          titles_and_text:
            alignment: center
            weight: bold
          primary:
            aggregation: count
            label: "Total Events"
```

### Breakdown Columns

Control the number of columns when using breakdown dimensions:

```yaml
dashboards:
  - name: "Multi-Column Metrics"
    panels:
      - title: "Events by Host"
        size: {w: 24, h: 8}
        lens:
          type: metric
          data_view: "metrics-*"
          appearance:
            breakdown:
              column_count: 4
          primary:
            aggregation: count
          breakdown:
            type: values
            field: host.name
```

## Programmatic Usage (Python)

You can create Metric chart panels programmatically using Python:

### Count Metric Example

```python
from kb_dashboard_core.panels.charts.config import (
    LensMetricPanelConfig,
    LensPanel,
)
from kb_dashboard_core.panels.charts.metric.metrics import (
    MetricLensCountAggregatedMetric,
)
from kb_dashboard_core.panels.config import Position, Size

panel = LensPanel(
    title='Total Documents',
    position=Position(x=0, y=0),
    size=Size(w=24, h=15),
    lens=LensMetricPanelConfig(
        type='metric',
        data_view='logs-*',
        primary=MetricLensCountAggregatedMetric(),
    ),
)
```

### Average Metric Example

```python
from kb_dashboard_core.panels.charts.config import (
    LensMetricPanelConfig,
    LensPanel,
)
from kb_dashboard_core.panels.charts.metric.metrics import (
    MetricLensOtherAggregatedMetric,
)
from kb_dashboard_core.panels.config import Position, Size

panel = LensPanel(
    title='Avg Response Time',
    position=Position(x=0, y=0),
    size=Size(w=24, h=15),
    lens=LensMetricPanelConfig(
        type='metric',
        data_view='logs-*',
        primary=MetricLensOtherAggregatedMetric(
            aggregation='average', field='response_time'
        ),
    ),
)
```

### Formula Metric Example

```python
from kb_dashboard_core.panels.charts.config import (
    LensMetricPanelConfig,
    LensPanel,
)
from kb_dashboard_core.panels.charts.lens.metrics.config import LensMetricFormat
from kb_dashboard_core.panels.charts.metric.metrics import MetricLensFormulaMetric
from kb_dashboard_core.panels.config import Position, Size

panel = LensPanel(
    title='Error Rate',
    position=Position(x=0, y=0),
    size=Size(w=24, h=15),
    lens=LensMetricPanelConfig(
        type='metric',
        data_view='logs-*',
        primary=MetricLensFormulaMetric(
            formula="count(kql='status:error') / count() * 100",
            label='Error Rate %',
            format=LensMetricFormat(type='percent'),
        ),
    ),
)
```

## Number Formatting

Metric charts support various number formatting options to display values in a user-friendly way. You can add suffixes, use compact notation, or apply custom number patterns.

### Format Configuration Options

The `format` field accepts an object with the following properties:

| YAML Key | Data Type | Description | Default | Required |
| -------- | --------- | ----------- | ------- | -------- |
| `type` | `string` | Format type: `'number'`, `'bytes'`, `'bits'`, `'percent'`, `'duration'` | `'number'` | No |
| `suffix` | `string` | Custom text appended to the formatted value | `''` | No |
| `prefix` | `string` | Custom text prepended to the formatted value | `''` | No |
| `compact` | `boolean` | Enable compact notation (e.g., 1.2K instead of 1200) | `false` | No |
| `pattern` | `string` | Custom numeral.js format pattern (e.g., `'0,0.00'`) | `null` | No |

### Suffix Formatting

Add custom text after metric values to provide context:

```yaml
dashboards:
  - name: "Metrics with Suffixes"
    panels:
      - title: "Request Rate"
        size: {w: 12, h: 4}
        lens:
          type: metric
          data_view: "logs-*"
          primary:
            aggregation: count
            label: "Requests"
            format:
              type: number
              suffix: " req/sec"

      - title: "Active Users"
        size: {w: 12, h: 4}
        position: {x: 12, y: 0}
        lens:
          type: metric
          data_view: "logs-*"
          primary:
            aggregation: unique_count
            field: "user.id"
            label: "Users"
            format:
              type: number
              suffix: " users"
```

### Compact Notation

Use compact notation to display large numbers in a more readable format (e.g., 1.2K instead of 1200):

```yaml
dashboards:
  - name: "Compact Metrics"
    panels:
      - title: "Total Events (Compact)"
        size: {w: 12, h: 4}
        lens:
          type: metric
          data_view: "logs-*"
          primary:
            aggregation: count
            label: "Events"
            format:
              type: number
              compact: true  # Displays as 1.2M, 500K, etc.
```

### Custom Number Patterns

Apply custom formatting patterns using numeral.js syntax:

```yaml
dashboards:
  - name: "Formatted Metrics"
    panels:
      - title: "Revenue (Currency)"
        size: {w: 12, h: 4}
        lens:
          type: metric
          data_view: "sales-*"
          primary:
            aggregation: sum
            field: "transaction.amount"
            label: "Total Revenue"
            format:
              type: custom
              pattern: "0,0.00"  # Comma separators, 2 decimals

      - title: "Success Rate"
        size: {w: 12, h: 4}
        position: {x: 12, y: 0}
        lens:
          type: metric
          data_view: "logs-*"
          primary:
            formula: "count(kql='status:success') / count() * 100"
            label: "Success Rate"
            format:
              type: custom
              pattern: "0.0a"    # 1 decimal + suffix (K, M, etc.)
              suffix: "%"
```

### Combining Format Options

You can combine multiple formatting options for maximum flexibility:

```yaml
dashboards:
  - name: "Combined Formatting"
    panels:
      - title: "Bandwidth Usage"
        size: {w: 12, h: 4}
        lens:
          type: metric
          data_view: "network-*"
          primary:
            aggregation: sum
            field: "network.bytes"
            label: "Total Bandwidth"
            format:
              type: bytes       # Built-in bytes format
              compact: true     # Use compact notation (MB, GB)
              suffix: "/day"    # Add custom suffix
```

For more examples of metric formatting, see [metric-formatting-examples.yaml](../examples/metric-formatting-examples.yaml).

## Related

- [Base Panel Configuration](./base.md)
- [Dashboard Configuration](../dashboard/dashboard.md)
- [Metric Formatting Examples](../examples/metric-formatting-examples.yaml)
