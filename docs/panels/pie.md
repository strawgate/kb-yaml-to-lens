# Pie Chart Panel Configuration

The Pie chart panel visualizes data as a pie or donut chart, useful for showing proportions of a whole.

## A Poem for the Proportion Perfectionists

_For those who love a good slice of data:_

```text
Round and round the data goes,
Each slice sized by what it shows.
Pie or donut, take your pick,
Small or large, or medium-thick!

When you need to see the shares,
How traffic splits between the pairs,
Which service takes the biggest slice,
Your pie chart makes it clear and nice.

"Inside" or "auto" for the labels,
"Percent" or "integer" on the tables,
Legend positioned left or right,
Colors making categories bright.

From traffic sources to error types,
Status codes and payment stripes,
Every portion of the whole,
Displayed to help you reach your goal!
```

---

## Minimal Configuration Example

```yaml
dashboards:
  - name: "Traffic Sources"
    panels:
      - type: charts
        title: "Website Traffic Sources"
        grid: { x: 0, y: 0, w: 24, h: 6 }
        chart:
          type: pie
          data_view: "traffic-data"
          slice_by:
            - field: "source"
              type: values
          metric:
            aggregation: sum
            field: visits
```

## Full Configuration Options

### Lens Pie Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------------- | ---------------------------------- | ---------------------------------------------------------------------------- | ------- | -------- |
| `type` | `Literal['pie']` | Specifies the chart type as pie. | `'pie'` | No |
| `data_view` | `string` | The data view that determines the data for the pie chart. | N/A | Yes |
| `metric` | `LensMetricTypes \| None` | A metric for single metric charts (size of slices). | `None` | No |
| `metrics` | `list[LensMetricTypes] \| None` | Multiple metrics for multi-metric charts. | `None` | No |
| `slice_by` | `list[LensDimensionTypes]` | Dimensions that determine the slices (first is primary, rest are secondary). | N/A | Yes |
| `appearance` | `PieChartAppearance \| None` | Chart appearance options (e.g., donut size). | `None` | No |
| `titles_and_text` | `PieTitlesAndText \| None` | Formatting options for titles and text. | `None` | No |
| `legend` | `PieLegend \| None` | Legend formatting options. | `None` | No |
| `color` | `ColorMapping \| None` | Color palette mapping for the chart. | `None` | No |

#### PieChartAppearance Options

| YAML Key | Data Type | Description | Default | Required |
| -------- | ----------------------------------------------- | ------------------------------------------------------------------ | ------- | -------- |
| `donut` | `Literal['small', 'medium', 'large'] \| None` | Controls the size of the donut hole. If not specified, Kibana displays as a pie chart (no donut hole). | `None` | No |

#### PieTitlesAndText Options

| YAML Key | Data Type | Description | Default | Required |
| ---------------------- | ------------------------------------------------- | ----------------------------------------------------------------- | ------- | -------- |
| `slice_labels` | `Literal['hide', 'inside', 'auto'] \| None` | Controls slice label visibility. | `None` | No |
| `slice_values` | `Literal['hide', 'integer', 'percent'] \| None` | Controls slice value display. | `None` | No |
| `value_decimal_places` | `int \| None` | Number of decimal places for values (0-10). | `None` | No |

#### PieLegend Options

| YAML Key | Data Type | Description | Default | Required |
| ----------------- | -------------------------------------------------------------- | ------------------------------------------------------------------- | ------- | -------- |
| `visible` | `Literal['show', 'hide', 'auto'] \| None` | Legend visibility. | `None` | No |
| `width` | `Literal['small', 'medium', 'large', 'extra_large'] \| None` | Legend width. | `None` | No |
| `truncate_labels` | `int \| None` | Lines to truncate labels to (0-5, 0=disable). | `None` | No |
| `nested` | `bool \| None` | Show legend in nested format for multi-level pie charts. | `None` | No |

### ESQL Pie Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------------- | ----------------------------------- | ---------------------------------------------------------------------------- | ------- | -------- |
| `type` | `Literal['pie']` | Specifies the chart type as pie. | `'pie'` | No |
| `metric` | `ESQLMetricTypes \| None` | A metric for single metric charts (size of slices). | `None` | No |
| `metrics` | `list[ESQLMetricTypes] \| None` | Multiple metrics for multi-metric charts. | `None` | No |
| `slice_by` | `list[ESQLDimensionTypes]` | Dimensions that determine the slices (first is primary, rest are secondary). | N/A | Yes |
| `esql` | `string` | The ES\|QL query that determines the data for the pie chart. | N/A | Yes |
| `appearance` | `PieChartAppearance \| None` | Chart appearance options (e.g., donut size). | `None` | No |
| `titles_and_text` | `PieTitlesAndText \| None` | Formatting options for titles and text. | `None` | No |
| `legend` | `PieLegend \| None` | Legend formatting options. | `None` | No |
| `color` | `ColorMapping \| None` | Color palette mapping for the chart. | `None` | No |

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

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
