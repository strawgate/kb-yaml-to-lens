# XY Chart Panel Configuration

The XY chart panel creates line, bar, and area charts for time series and other data visualizations.

## A Poem for the Time Series Enthusiasts

_For those who see patterns across the timeline:_

```text
Lines that rise and bars that fall,
Area charts that show it all.
X-axis marching slowly through time,
Y-axis tracking every climb.

When incidents spike at 2 AM,
The XY chart says: "Here I am."
Stacked or unstacked, the choice is yours,
Percentage mode for ratio scores.

Dimensions set the horizontal stage,
Metrics show what happens, page by page.
Break it down by service, host, or zone—
No pattern ever goes unknown.

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
      - title: "Events Over Time"
        grid: { x: 0, y: 0, w: 48, h: 6 }
        lens:
          type: line
          data_view: "logs-*"
          dimension:
            type: date_histogram
            field: "@timestamp"
          metrics:
            - aggregation: count
```

## Example with Custom Colors

```yaml
dashboards:
  - name: "Service Performance"
    panels:
      - title: "Response Times by Service"
        grid: { x: 0, y: 0, w: 12, h: 6 }
        lens:
          type: line
          data_view: "metrics-*"
          dimension:
            type: date_histogram
            field: "@timestamp"
          breakdown:
            type: values
            field: "service.name"
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
| `dimension` | `LensDimensionTypes \| None` | Defines the X-axis dimension for the chart (0 or 1 dimension allowed). | `None` | No |
| `metrics` | `list[LensMetricTypes]` | Defines the metrics (e.g., Y-axis values) for the chart. | `[]` | No |
| `breakdown` | `LensDimensionTypes \| None` | Optional dimension to split the series by (creates multiple series). | `None` | No |
| `appearance` | `BarChartAppearance \| None` | Chart appearance formatting options including axis configuration, series styling, and bar-specific options (min_bar_height). | `None` | No |
| `titles_and_text` | `XYTitlesAndText \| None` | Titles and text formatting options. | `None` | No |
| `legend` | `XYLegend \| None` | Legend formatting options. | `None` | No |
| `color` | `ColorMapping \| None` | Color palette mapping for the chart. See [Color Mapping Configuration](base.md#color-mapping-configuration). | `None` | No |

### Lens Line Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------------- | ------------------------------- | -------------------------------------------------------------------- | -------- | -------- |
| `type` | `Literal['line']` | Specifies the chart type as line. | `'line'` | No |
| `data_view` | `string` | The data view to use for the chart. | N/A | Yes |
| `dimension` | `LensDimensionTypes \| None` | Defines the X-axis dimension for the chart (0 or 1 dimension allowed). | `None` | No |
| `metrics` | `list[LensMetricTypes]` | Defines the metrics (e.g., Y-axis values) for the chart. | `[]` | No |
| `breakdown` | `LensDimensionTypes \| None` | Optional dimension to split the series by (creates multiple series). | `None` | No |
| `appearance` | `LineChartAppearance \| None` | Chart appearance formatting options including axis configuration, series styling, and line-specific options (missing_values, show_as_dotted, end_values, line_style). | `None` | No |
| `titles_and_text` | `XYTitlesAndText \| None` | Titles and text formatting options. | `None` | No |
| `legend` | `XYLegend \| None` | Legend formatting options. | `None` | No |
| `color` | `ColorMapping \| None` | Color palette mapping for the chart. See [Color Mapping Configuration](base.md#color-mapping-configuration). | `None` | No |
| `show_current_time_marker` | `bool \| None` | Whether to show a vertical line at the current time in time series charts. | `None` | No |
| `hide_endzones` | `bool \| None` | Whether to hide end zones in time series charts (areas where data is incomplete). | `None` | No |

### Lens Area Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------------- | ----------------------------------------------- | -------------------------------------------------------------------- | ----------- | -------- |
| `type` | `Literal['area']` | Specifies the chart type as area. | `'area'` | No |
| `mode` | `Literal['stacked', 'unstacked', 'percentage']` | Stacking mode for area charts. | `'stacked'` | No |
| `data_view` | `string` | The data view to use for the chart. | N/A | Yes |
| `dimension` | `LensDimensionTypes \| None` | Defines the X-axis dimension for the chart (0 or 1 dimension allowed). | `None` | No |
| `metrics` | `list[LensMetricTypes]` | Defines the metrics (e.g., Y-axis values) for the chart. | `[]` | No |
| `breakdown` | `LensDimensionTypes \| None` | Optional dimension to split the series by (creates multiple series). | `None` | No |
| `appearance` | `AreaChartAppearance \| None` | Chart appearance formatting options including axis configuration, series styling, line-specific options (missing_values, show_as_dotted, end_values, line_style), and area-specific options (fill_opacity). | `None` | No |
| `titles_and_text` | `XYTitlesAndText \| None` | Titles and text formatting options. | `None` | No |
| `legend` | `XYLegend \| None` | Legend formatting options. | `None` | No |
| `color` | `ColorMapping \| None` | Color palette mapping for the chart. See [Color Mapping Configuration](base.md#color-mapping-configuration). | `None` | No |
| `show_current_time_marker` | `bool \| None` | Whether to show a vertical line at the current time in time series charts. | `None` | No |
| `hide_endzones` | `bool \| None` | Whether to hide end zones in time series charts (areas where data is incomplete). | `None` | No |

#### XYLegend Options

| YAML Key | Data Type | Description | Default | Required |
| ---------- | -------------------------------------------------------- | ------------------------------------------------- | ------- | -------- |
| `visible` | `bool \| None` | Whether the legend is visible. | `None` | No |
| `position` | `Literal['top', 'bottom', 'left', 'right'] \| None` | Position of the legend (Kibana defaults to 'right'). | `None` | No |

### Chart Appearance Options

XY charts support appearance customization through the `appearance` field. The available options depend on the chart type and include both chart-type-specific options and common axis/series options.

#### Common Appearance Options (All Chart Types)

These options are available for all XY chart types (bar, line, area):

| YAML Key | Data Type | Description | Default | Required |
| ------------- | ------------------------ | -------------------------------------------------------- | ------- | -------- |
| `x_axis` | `AxisConfig \| None` | Configuration for the X-axis (horizontal axis). | `None` | No |
| `y_left_axis` | `AxisConfig \| None` | Configuration for the left Y-axis (primary vertical axis). | `None` | No |
| `y_right_axis` | `AxisConfig \| None` | Configuration for the right Y-axis (secondary vertical axis). | `None` | No |
| `series` | `list[XYSeries] \| None` | Per-series visual configuration (axis assignment, colors, line styles, etc.). | `None` | No |

#### AxisConfig Options

Defines configuration for a single axis.

| YAML Key | Data Type | Description | Default | Required |
| -------- | ------------------------------------------------ | ---------------------------------------------- | ------- | -------- |
| `title` | `str \| None` | Custom title for the axis. | `None` | No |
| `scale` | `Literal['linear', 'log', 'sqrt', 'time'] \| None` | Scale type for the axis. | `None` | No |
| `extent` | `AxisExtent \| None` | Axis bounds/range configuration. | `None` | No |

#### AxisExtent Options

Configures the bounds (range) of an axis.

| YAML Key | Data Type | Description | Default | Required |
| ------------- | -------------------------------------------- | --------------------------------------------------------- | ------- | -------- |
| `mode` | `Literal['full', 'data_bounds', 'custom']` | Extent mode: 'full' (entire range), 'data_bounds' (fit to data), 'custom' (manual bounds). | N/A | Yes |
| `min` | `float \| None` | Minimum bound (required when mode is 'custom'). | `None` | Conditional* |
| `max` | `float \| None` | Maximum bound (required when mode is 'custom'). | `None` | Conditional* |
| `enforce` | `bool \| None` | Whether to enforce the bounds strictly. | `None` | No |
| `nice_values` | `bool \| None` | Whether to round bounds to nice values. | `None` | No |

**\*Note:** When `mode='custom'`, both `min` and `max` must be specified (Kibana requirement).

#### XYSeries Options

Configures per-series visual styling and axis assignment. Used to customize individual metrics within a chart.

| YAML Key | Data Type | Description | Default | Required |
| ----------- | ------------------------------------------------- | ------------------------------------------------------------ | ------- | -------- |
| `metric_id` | `str` | ID of the metric this series configuration applies to. | N/A | Yes |
| `axis` | `Literal['left', 'right'] \| None` | Which Y-axis this series is assigned to (for dual-axis charts). | `None` | No |
| `color` | `str \| None` | Hex color code for the series (e.g., '#2196F3'). | `None` | No |

#### Bar Chart Specific Appearance

For bar charts (`type: bar`), you can use all the axis config and series options from the base appearance, plus the following bar-specific options:

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
    y_left_axis:
      title: "Count"
  # ... other fields
```

#### Line Chart Specific Appearance

For line charts (`type: line`), you can use all the axis config and series options from the base appearance, plus the following line-specific options:

| YAML Key | Data Type | Description | Default | Required |
| ------------------- | -------------------------------------------------------------------------------------------- | ---------------------------------------------------- | ------- | -------- |
| `missing_values` | `Literal['None', 'Linear', 'Carry', 'Lookahead', 'Average', 'Nearest'] \| None` | How to handle missing data points ("Missing values" in Kibana UI). Controls interpolation for gaps in your data. Options: 'None' (no interpolation), 'Linear' (linear interpolation), 'Carry' (carry forward), 'Lookahead' (use next value), 'Average' (average of neighbors), 'Nearest' (nearest value). | `None` | No |
| `show_as_dotted` | `bool \| None` | If `true`, visually distinguish interpolated data from real data points ("Show as dotted line" in Kibana UI). | `None` | No |
| `end_values` | `Literal['None', 'Zero', 'Nearest'] \| None` | How to handle the end of the time range in line/area charts ("End values" in Kibana UI). Options: 'None' (no special handling), 'Zero' (end at zero), 'Nearest' (use nearest value). | `None` | No |
| `line_style` | `Literal['linear', 'monotone-x', 'step-after'] \| None` | The line style for line/area charts ("Line style" in Kibana UI). Only 3 types are supported by Kibana: 'linear' (straight), 'monotone-x' (curved), 'step-after' (stepped). These values are automatically converted to Kibana's format (e.g., 'monotone-x' → 'CURVE_MONOTONE_X'). | `None` | No |

**Example**:

```yaml
chart:
  type: line
  data_view: "metrics-*"
  appearance:
    missing_values: Average
    show_as_dotted: true
    end_values: Zero
    line_style: monotone-x
    series:
      - metric_id: "response_time"
        color: "#2196F3"
  # ... other fields
```

#### Area Chart Specific Appearance

For area charts (`type: area`), you can use all the axis config, series options, and line-specific options, plus the following area-specific option:

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
    line_style: linear
    series:
      - metric_id: "bytes_in"
        color: "#4CAF50"
  # ... other fields
```

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
        dimension:
          type: date_histogram
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

## Usage Examples

### Dual Y-Axis Chart

Create a chart with two metrics on different Y-axes:

```yaml
dashboards:
  - name: "Performance Dashboard"
    panels:
      - title: "Request Count vs Error Rate"
        grid: { x: 0, y: 0, w: 48, h: 12 }
        lens:
          type: line
          data_view: "logs-*"
          dimension:
            type: date_histogram
            field: "@timestamp"
            id: "time"
          metrics:
            - aggregation: count
              id: "request_count"
            - aggregation: average
              field: "error.rate"
              id: "avg_error_rate"
          appearance:
            y_left_axis:
              title: "Request Count"
              scale: linear
            y_right_axis:
              title: "Error Rate (%)"
              scale: linear
            series:
              - metric_id: "request_count"
                axis: left
                color: "#2196F3"
              - metric_id: "avg_error_rate"
                axis: right
                color: "#FF5252"
```

### Custom Axis Bounds

Set explicit axis ranges:

```yaml
dashboards:
  - name: "SLA Dashboard"
    panels:
      - title: "Response Time (0-1000ms)"
        grid: { x: 0, y: 0, w: 48, h: 12 }
        lens:
          type: line
          data_view: "logs-*"
          dimension:
            type: date_histogram
            field: "@timestamp"
          metrics:
            - aggregation: average
              field: "event.duration"
          appearance:
            y_left_axis:
              title: "Response Time (ms)"
              extent:
                mode: custom
                min: 0
                max: 1000
                enforce: true
                nice_values: true
```

### Styled Series

Customize individual series appearance:

```yaml
dashboards:
  - name: "Network Dashboard"
    panels:
      - title: "Network Traffic"
        grid: { x: 0, y: 0, w: 48, h: 12 }
        lens:
          type: area
          data_view: "metrics-*"
          dimension:
            type: date_histogram
            field: "@timestamp"
          metrics:
            - aggregation: sum
              field: "network.bytes"
              id: "inbound"
              filter:
                kql: "network.direction:inbound"
            - aggregation: sum
              field: "network.bytes"
              id: "outbound"
              filter:
                kql: "network.direction:outbound"
          appearance:
            series:
              - metric_id: "inbound"
                color: "#4CAF50"
              - metric_id: "outbound"
                color: "#FF9800"
```

### Advanced Line Chart with Time Series Features

Use fitting functions, time markers, and end value handling for time series visualizations:

```yaml
dashboards:
  - name: "Time Series Analytics"
    panels:
      - title: "CPU Usage with Interpolation"
        grid: { x: 0, y: 0, w: 48, h: 12 }
        lens:
          type: line
          data_view: "metrics-*"
          dimension:
            type: date_histogram
            field: "@timestamp"
          metrics:
            - aggregation: average
              field: "system.cpu.usage"
          appearance:
            missing_values: Average
            show_as_dotted: true
            end_values: Zero
            line_style: monotone-x
          show_current_time_marker: true
          hide_endzones: true
```

## Programmatic Usage (Python)

You can create XY chart panels with reference lines programmatically using Python:

```python
from dashboard_compiler.panels.charts.config import (
    LensLinePanelConfig,
    LensPanel,
)
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
    lens=LensLinePanelConfig(
        type='line',
        data_view='logs-*',
        dimension=LensDateHistogramDimension(field='@timestamp'),
        metrics=[LensCountAggregatedMetric()],
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
