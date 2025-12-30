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
The XY chart says: "Here I am."
Stacked or unstacked, the choice is yours,
Percentage mode for ratio scores.

Dimensions set the horizontal stage,
Metrics show what happens, page by page.
Break it down by service, host, or zone—
No pattern goes by, unknown.

From request counts to error rates,
Your time series sits and waits.
So here's to charts, both line and bar,
That show exactly where things are.
```

---

## Minimal Configuration Example

```yaml
dashboards:
  - name: "Time Series Dashboard"
    panels:
      - type: charts
        title: "Events Over Time"
        grid: { x: 0, y: 0, w: 48, h: 6 }
        chart:
          type: line
          data_view: "logs-*"
          dimensions:
            - type: date_histogram
              field: "@timestamp"
          metrics:
            - aggregation: count
```

## Example with Custom Colors

```yaml
dashboards:
  - name: "Service Performance"
    panels:
      - type: charts
        title: "Response Times by Service"
        grid: { x: 0, y: 0, w: 12, h: 6 }
        chart:
          type: line
          data_view: "metrics-*"
          dimensions:
            - field: "@timestamp"
          breakdown:
            field: "service.name"
            type: values
          metrics:
            - aggregation: average
              field: response_time
          color:
            palette: 'eui_amsterdam_color_blind'
            assignments:
              - values: ['web-frontend']
                color: '#00BF6F'
              - values: ['api-gateway']
                color: '#0077CC'
              - values: ['database']
                color: '#FFA500'
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
| `color` | `ColorMapping \| None` | Color palette mapping for the chart. See [Color Mapping Configuration](base.md#color-mapping-configuration). | `None` | No |

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
| `color` | `ColorMapping \| None` | Color palette mapping for the chart. See [Color Mapping Configuration](base.md#color-mapping-configuration). | `None` | No |

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
| `color` | `ColorMapping \| None` | Color palette mapping for the chart. See [Color Mapping Configuration](base.md#color-mapping-configuration). | `None` | No |

#### XYLegend Options

| YAML Key | Data Type | Description | Default | Required |
| ---------- | -------------------------------------------------------- | ------------------------------------------------- | ------- | -------- |
| `visible` | `bool \| None` | Whether the legend is visible. | `None` | No |
| `position` | `Literal['top', 'bottom', 'left', 'right'] \| None` | Position of the legend (Kibana defaults to 'right'). | `None` | No |

### Chart Appearance Options

XY charts support appearance customization through the `appearance` field. The available options depend on the chart type:

#### Bar Chart Appearance

For bar charts (`type: bar`), the following appearance options are available:

| YAML Key | Data Type | Description | Default | Required |
| -------------- | --------------- | -------------------------------------------- | ------- | -------- |
| `min_bar_height` | `float \| None` | The minimum height for bars in bar charts (in pixels). | `None` | No |

**Example**:

```yaml
chart:
  type: bar
  data_view: "logs-*"
  appearance:
    min_bar_height: 5.0
  # ... other fields
```

#### Line Chart Appearance

For line charts (`type: line`), the following appearance options are available:

| YAML Key | Data Type | Description | Default | Required |
| ------------------- | -------------------------------------------------------------------------------------------- | ---------------------------------------------------- | ------- | -------- |
| `fitting_function` | `Literal['Linear'] \| None` | The fitting function to apply to line charts for smoothing. | `None` | No |
| `emphasize_fitting` | `bool \| None` | If `true`, emphasize the fitting function line. | `false` | No |
| `curve_type` | `Literal['linear', 'cardinal', 'catmull-rom', 'natural', 'step', 'step-after', 'step-before', 'monotone-x'] \| None` | The curve interpolation type for line charts. | `None` | No |

**Example**:

```yaml
chart:
  type: line
  data_view: "metrics-*"
  appearance:
    fitting_function: Linear
    emphasize_fitting: true
    curve_type: monotone-x
  # ... other fields
```

#### Area Chart Appearance

For area charts (`type: area`), all line chart appearance options are available, plus:

| YAML Key | Data Type | Description | Default | Required |
| -------------- | --------------- | ------------------------------------------------------ | ------- | -------- |
| `fill_opacity` | `float \| None` | The fill opacity for area charts (0.0 to 1.0). | `None` | No |

**Example**:

```yaml
chart:
  type: area
  data_view: "metrics-*"
  appearance:
    fill_opacity: 0.7
    curve_type: cardinal
  # ... other fields
```

## Reference Lines (Multi-Layer Panels)

Reference lines are implemented as separate layers in multi-layer panels. This allows you to combine data visualizations with threshold lines in a single chart.

### Basic Reference Line Example

```yaml
dashboards:
  - name: "Service Level Dashboard"
    panels:
    - type: multi_layer_charts
      title: "Response Time with SLA"
      grid: { x: 0, y: 0, w: 24, h: 12 }
      layers:
        # Data layer
        - type: line
          data_view: "metrics-*"
          dimensions:
            - type: date_histogram
              field: "@timestamp"
          metrics:
            - aggregation: "average"
              field: "response_time"
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
from dashboard_compiler.panels.charts.config import LensMultiLayerPanel
from dashboard_compiler.panels.charts.lens.dimensions.config import (
    LensDateHistogramDimension,
)
from dashboard_compiler.panels.charts.lens.metrics.config import (
    LensCountAggregatedMetric,
)
from dashboard_compiler.panels.charts.xy.config import (
    LensLineChart,
    LensReferenceLineLayer,
    XYReferenceLine,
)
from dashboard_compiler.panels.config import Grid

# Create a multi-layer panel with data layer and reference line layer
panel = LensMultiLayerPanel(
    title='Documents Over Time with Thresholds',
    grid=Grid(x=0, y=0, w=48, h=20),
    layers=[
        # Data layer
        LensLineChart(
            data_view='logs-*',
            dimensions=[LensDateHistogramDimension(field='@timestamp')],
            metrics=[LensCountAggregatedMetric(aggregation='count')],
        ),
        # Reference line layer
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
)
```

## Related

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
