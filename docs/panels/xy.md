# XY Chart Panel Configuration

The XY chart panel creates line, bar, and area charts for time series and other data visualizations.

## A Poem for the Time Series Enthusiasts

_For those who see patterns across the timeline:_

```text
Lines that rise and bars that fall,
Area charts that show it all.
X-axis marching through the time,
Y-axis tracking every climb.

When incidents spike at 2 AM,
Your XY charts help us understand them.
Stacked or unstacked, the choice is yours,
Percentage mode for ratio scores.

Dimensions define the horizontal way,
Metrics show values throughout the day.
Breakdown by service, host, or zone,
Every pattern clearly shown.

From request counts to error rates,
Your time series never hesitates.
So here's to charts both line and bar,
That help us see how systems are!
```

---

## Minimal Configuration Example

```yaml
dashboards:
  - name: "Time Series Dashboard"
    panels:
      - title: "Events Over Time"
        grid: { x: 0, y: 0, w: 48, h: 6 }
        lens:
          type: line
          data_view: "logs-*"
          dimensions:
            - type: date_histogram
              field: "@timestamp"
          metrics:
            - aggregation: count
```

## Full Configuration Options

### Lens Bar Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------------- | ----------------------------------------------- | -------------------------------------------------------------------- | ----------- | -------- |
| `type` | `Literal['bar']` | Specifies the chart type as bar. | `'bar'` | No |
| `mode` | `Literal['stacked', 'unstacked', 'percentage']` | Stacking mode for bar charts. | `'stacked'` | No |
| `data_view` | `string` | The data view to use for the chart. | N/A | Yes |
| `dimensions` | `list[LensDimensionTypes]` | Defines the dimensions (e.g., X-axis) for the chart. | `[]` | No |
| `metrics` | `list[LensMetricTypes]` | Defines the metrics (e.g., Y-axis values) for the chart. | `[]` | No |
| `breakdown` | `LensDimensionTypes \| None` | Optional dimension to split the series by (creates multiple series). | `None` | No |
| `appearance` | `XYAppearance \| None` | Chart appearance formatting options. | `None` | No |
| `titles_and_text` | `XYTitlesAndText \| None` | Titles and text formatting options. | `None` | No |
| `legend` | `XYLegend \| None` | Legend formatting options. | `None` | No |

### Lens Line Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------------- | ------------------------------- | -------------------------------------------------------------------- | -------- | -------- |
| `type` | `Literal['line']` | Specifies the chart type as line. | `'line'` | No |
| `data_view` | `string` | The data view to use for the chart. | N/A | Yes |
| `dimensions` | `list[LensDimensionTypes]` | Defines the dimensions (e.g., X-axis) for the chart. | `[]` | No |
| `metrics` | `list[LensMetricTypes]` | Defines the metrics (e.g., Y-axis values) for the chart. | `[]` | No |
| `breakdown` | `LensDimensionTypes \| None` | Optional dimension to split the series by (creates multiple series). | `None` | No |
| `appearance` | `XYAppearance \| None` | Chart appearance formatting options. | `None` | No |
| `titles_and_text` | `XYTitlesAndText \| None` | Titles and text formatting options. | `None` | No |
| `legend` | `XYLegend \| None` | Legend formatting options. | `None` | No |

### Lens Area Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------------- | ----------------------------------------------- | -------------------------------------------------------------------- | ----------- | -------- |
| `type` | `Literal['area']` | Specifies the chart type as area. | `'area'` | No |
| `mode` | `Literal['stacked', 'unstacked', 'percentage']` | Stacking mode for area charts. | `'stacked'` | No |
| `data_view` | `string` | The data view to use for the chart. | N/A | Yes |
| `dimensions` | `list[LensDimensionTypes]` | Defines the dimensions (e.g., X-axis) for the chart. | `[]` | No |
| `metrics` | `list[LensMetricTypes]` | Defines the metrics (e.g., Y-axis values) for the chart. | `[]` | No |
| `breakdown` | `LensDimensionTypes \| None` | Optional dimension to split the series by (creates multiple series). | `None` | No |
| `appearance` | `XYAppearance \| None` | Chart appearance formatting options. | `None` | No |
| `titles_and_text` | `XYTitlesAndText \| None` | Titles and text formatting options. | `None` | No |
| `legend` | `XYLegend \| None` | Legend formatting options. | `None` | No |

#### XYLegend Options

| YAML Key | Data Type | Description | Default | Required |
| ---------- | -------------------------------------------------------- | ------------------------------------------------- | ------- | -------- |
| `visible` | `bool \| None` | Whether the legend is visible. | `None` | No |
| `position` | `Literal['top', 'bottom', 'left', 'right'] \| None` | Position of the legend (Kibana defaults to 'right'). | `None` | No |

## Reference Lines (Multi-Layer Panels)

Reference lines are implemented as separate layers in multi-layer panels. This allows you to combine data visualizations with threshold lines in a single chart.

### Basic Reference Line Example

```yaml
dashboards:
  - name: "Service Level Dashboard"
    panels:
    - title: "Response Time with SLA"
      grid: { x: 0, y: 0, w: 24, h: 12 }
      lens:
        # Base data layer
        type: line
        data_view: "metrics-*"
        dimensions:
          - type: date_histogram
            field: "@timestamp"
        metrics:
          - aggregation: "average"
            field: "response_time"
        # Additional layers
        layers:
          # Reference line layer
          - type: reference_line
            data_view: "metrics-*"
            reference_lines:
              - label: "SLA Threshold"
                value: 500.0
                color: "#FF0000"
                line_style: "dashed"
```

### Reference Line Layer Configuration

| YAML Key | Data Type | Description | Default | Required |
| --------------- | ------------------------------- | --------------------------------------------------------- | ------- | -------- |
| `type` | `Literal['reference_line']` | Specifies the layer type as reference line. | N/A | Yes |
| `data_view` | `string` | The data view (required for Kibana compatibility). | N/A | Yes |
| `reference_lines` | `list[XYReferenceLine]` | List of reference lines to display in this layer. | `[]` | No |

### Individual Reference Line Options

| YAML Key | Data Type | Description | Default | Required |
| --------------- | ----------------------------------------------------------- | ------------------------------------------------------- | -------- | -------- |
| `value` | `float \| XYReferenceLineValue` | The y-axis value for the reference line. | N/A | Yes |
| `label` | `string \| None` | Label text displayed on the reference line. | `None` | No |
| `id` | `string \| None` | Optional unique identifier for the reference line. | `None` | No |
| `axis` | `Literal['left', 'right'] \| None` | Which y-axis to assign the reference line to. | `'left'` | No |
| `color` | `string \| None` | Color of the reference line (hex code). | Kibana Default | No |
| `line_width` | `int \| None` | Width of the reference line (1-10). | Kibana Default | No |
| `line_style` | `Literal['solid', 'dashed', 'dotted'] \| None` | Style of the reference line. | Kibana Default | No |
| `fill` | `Literal['above', 'below', 'none'] \| None` | Fill area above or below the line. | `None` | No |
| `icon` | `string \| None` | Icon to display on the reference line. | `None` | No |
| `icon_position` | `Literal['auto', 'left', 'right', 'above', 'below'] \| None` | Position of the icon relative to the line. | `None` | No |

### ESQL Bar/Line/Area Charts

ESQL chart configuration is similar to Lens charts, but uses `ESQLDimensionTypes` and `ESQLMetricTypes` instead, and does not require a `data_view` field.

## Programmatic Usage (Python)

You can create XY chart panels with reference lines programmatically using Python:

```python
from dashboard_compiler.panels.charts.config import LensPanel, LensPanelConfig
from dashboard_compiler.panels.charts.lens.dimensions.config import (
    LensDateHistogramDimension,
)
from dashboard_compiler.panels.charts.lens.metrics.config import (
    LensCountAggregatedMetric,
)
from dashboard_compiler.panels.charts.xy.config import (
    LensReferenceLineLayer,
    XYReferenceLine,
)
from dashboard_compiler.panels.config import Grid

# Create a multi-layer panel with data layer and reference line layer
panel = LensPanel(
    title='Documents Over Time with Thresholds',
    grid=Grid(x=0, y=0, w=48, h=20),
    lens=LensPanelConfig(
        type='line',
        data_view='logs-*',
        dimensions=[LensDateHistogramDimension(field='@timestamp')],
        metrics=[LensCountAggregatedMetric(aggregation='count')],
        layers=[
            # Additional reference line layer
            LensReferenceLineLayer(
                data_view='logs-*',
                reference_lines=[
                    XYReferenceLine(
                        label='SLA Threshold',
                        value=500.0,
                        color='#FF0000',
                        line_style='dashed',
                        line_width=2,
                    ),
                    XYReferenceLine(
                        label='Target',
                        value=200.0,
                        color='#00FF00',
                        line_style='solid',
                    ),
                ],
            ),
        ],
    ),
)
```

## Related

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
