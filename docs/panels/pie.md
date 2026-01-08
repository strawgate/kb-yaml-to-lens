# Pie Chart Panel Configuration

The Pie chart panel visualizes data as a pie or donut chart, useful for showing proportions of a whole.

## A Poem for the Proportion Perfectionists

_For those who love a good slice of data:_

```text
They say you can't have it all—
Pie charts beg to differ, y'all!
Round and round the data goes,
Each slice sized by what it shows.

Who's got the biggest piece of pie?
Just look—it catches every eye.
Donut hole? Small, medium, large?
Pick your style; you're in charge.

"Inside" or "auto" for the labels,
"Percent" values—crisp and stable.
Legend positioned left or right,
Colors keeping categories bright.

From traffic sources to error types,
Status codes and payment stripes—
Your data served up, fresh and whole:
Every slice helps reach your goal!
```

---

## Minimal Configuration Example

```yaml
dashboards:
  - name: "Traffic Sources"
    panels:
      - title: "Website Traffic Sources"
        grid: { x: 0, y: 0, w: 24, h: 6 }
        lens:
          type: pie
          data_view: "metrics-*"
          slice_by:
            - field: "resource.attributes.os.type"
              type: values
          metrics:
            - aggregation: unique_count
              field: resource.attributes.host.name
```

## Example with Custom Colors

```yaml
dashboards:
  - name: "Operating System Distribution"
    panels:
      - title: "Host Count by OS Type"
        grid: { x: 0, y: 0, w: 6, h: 6 }
        lens:
          type: pie
          data_view: "metrics-*"
          slice_by:
            - field: "resource.attributes.os.type"
              type: values
          metrics:
            - aggregation: unique_count
              field: resource.attributes.host.name
          color:
            palette: 'eui_amsterdam_color_blind'
            assignments:
              - values: ['linux']
                color: '#00BF6F'  # Green for Linux
              - values: ['windows']
                color: '#006BB4'  # Blue for Windows
              - values: ['darwin']
                color: '#98A2B3'  # Gray for macOS
```

## Full Configuration Options

### Lens Pie Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------------- | ---------------------------------- | ---------------------------------------------------------------------------- | ------- | -------- |
| `type` | `Literal['pie']` | Specifies the chart type as pie. | `'pie'` | No |
| `data_view` | `string` | The data view that determines the data for the pie chart. | N/A | Yes |
| `metrics` | `list[LensMetricTypes]` | Metrics for sizing the slices. | N/A | Yes |
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
| `metrics` | `list[ESQLMetricTypes]` | Metrics for sizing the slices. | N/A | Yes |
| `slice_by` | `list[ESQLDimensionTypes]` | Dimensions that determine the slices (first is primary, rest are secondary). | N/A | Yes |
| `esql` | `string` | The ES\|QL query that determines the data for the pie chart. | N/A | Yes |
| `appearance` | `PieChartAppearance \| None` | Chart appearance options (e.g., donut size). | `None` | No |
| `titles_and_text` | `PieTitlesAndText \| None` | Formatting options for titles and text. | `None` | No |
| `legend` | `PieLegend \| None` | Legend formatting options. | `None` | No |
| `color` | `ColorMapping \| None` | Color palette mapping for the chart. | `None` | No |

## Programmatic Usage (Python)

You can create Pie chart panels programmatically using Python:

```python
from dashboard_compiler.panels.charts.config import (
    LensPanel,
    LensPiePanelConfig,
)
from dashboard_compiler.panels.charts.lens.dimensions.config import (
    LensTopValuesDimension,
)
from dashboard_compiler.panels.charts.lens.metrics.config import (
    LensCountAggregatedMetric,
)
from dashboard_compiler.panels.config import Grid

panel = LensPanel(
    title='Status Distribution',
    grid=Grid(x=0, y=0, w=24, h=15),
    lens=LensPiePanelConfig(
        type='pie',
        data_view='logs-*',
        slice_by=[LensTopValuesDimension(field='status')],
        metrics=[LensCountAggregatedMetric()],
    ),
)
```

## Related

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
