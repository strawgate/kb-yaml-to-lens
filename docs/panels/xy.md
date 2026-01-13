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

## Lens Bar Charts

::: dashboard_compiler.panels.charts.xy.config.LensBarChart
    options:
      show_root_heading: false
      heading_level: 3

## Lens Line Charts

::: dashboard_compiler.panels.charts.xy.config.LensLineChart
    options:
      show_root_heading: false
      heading_level: 3

## Lens Area Charts

::: dashboard_compiler.panels.charts.xy.config.LensAreaChart
    options:
      show_root_heading: false
      heading_level: 3

## Chart Appearance Options

### Bar Chart Appearance

::: dashboard_compiler.panels.charts.xy.config.BarChartAppearance
    options:
      show_root_heading: false
      heading_level: 4

### Line Chart Appearance

::: dashboard_compiler.panels.charts.xy.config.LineChartAppearance
    options:
      show_root_heading: false
      heading_level: 4

### Area Chart Appearance

::: dashboard_compiler.panels.charts.xy.config.AreaChartAppearance
    options:
      show_root_heading: false
      heading_level: 4

## Axis Configuration

::: dashboard_compiler.panels.charts.xy.config.AxisConfig
    options:
      show_root_heading: false
      heading_level: 3

::: dashboard_compiler.panels.charts.xy.config.AxisExtent
    options:
      show_root_heading: false
      heading_level: 3

### Axis Customization Examples

Customize axis titles, bounds, and scale types to better represent your data:

#### Custom Axis Titles

```yaml
dashboards:
  - name: "Custom Axis Titles"
    panels:
      - title: "Request Latency Over Time"
        size: {w: 24, h: 15}
        lens:
          type: line
          data_view: "logs-*"
          dimension:
            field: "@timestamp"
            type: date_histogram
          metrics:
            - aggregation: average
              field: "response.time"
              label: "Avg Latency"
          appearance:
            x_axis:
              title: "Time (UTC)"
            y_left_axis:
              title: "Response Time (milliseconds)"
```

#### Custom Axis Bounds

Set explicit minimum and maximum values for the Y-axis:

```yaml
dashboards:
  - name: "Custom Axis Bounds"
    panels:
      - title: "CPU Usage (0-100%)"
        size: {w: 24, h: 15}
        lens:
          type: area
          data_view: "metrics-*"
          dimension:
            field: "@timestamp"
            type: date_histogram
          metrics:
            - aggregation: average
              field: "system.cpu.usage"
              label: "CPU %"
          appearance:
            y_left_axis:
              title: "CPU Usage"
              extent:
                mode: custom
                min: 0
                max: 100
```

#### Logarithmic Scale

Use logarithmic scale for data with exponential growth:

```yaml
dashboards:
  - name: "Logarithmic Scale"
    panels:
      - title: "Event Count (Log Scale)"
        size: {w: 24, h: 15}
        lens:
          type: bar
          data_view: "logs-*"
          dimension:
            field: "service.name"
            type: values
          metrics:
            - aggregation: count
              label: "Event Count"
          appearance:
            y_left_axis:
              title: "Count (log scale)"
              scale: log
```

#### Data Bounds Mode

Automatically fit the axis to the actual data range:

```yaml
dashboards:
  - name: "Data Bounds Mode"
    panels:
      - title: "Response Time"
        size: {w: 24, h: 15}
        lens:
          type: line
          data_view: "logs-*"
          dimension:
            field: "@timestamp"
            type: date_histogram
          metrics:
            - aggregation: average
              field: "response.time"
          appearance:
            y_left_axis:
              extent:
                mode: data_bounds  # Fit to actual data
```

#### Dual Axis Charts

Configure different scales for left and right Y-axes:

```yaml
dashboards:
  - name: "Dual Axis Chart"
    panels:
      - title: "Requests vs Response Time"
        size: {w: 24, h: 15}
        lens:
          type: line
          data_view: "logs-*"
          dimension:
            field: "@timestamp"
            type: date_histogram
          metrics:
            - aggregation: count
              label: "Request Count"
              axis: left
            - aggregation: average
              field: "response.time"
              label: "Avg Response (ms)"
              axis: right
          appearance:
            y_left_axis:
              title: "Request Count"
              extent:
                mode: data_bounds
            y_right_axis:
              title: "Response Time (ms)"
              extent:
                mode: custom
                min: 0
                max: 1000
```

## Legend Configuration

For comprehensive guidance on legend configuration, see the [Legend Configuration Guide](../advanced/legend-configuration.md).

::: dashboard_compiler.panels.charts.xy.config.XYLegend
    options:
      show_root_heading: false
      heading_level: 3

## Reference Lines

Reference lines are implemented as separate layers in multi-layer panels. This allows you to combine data visualizations with threshold lines in a single chart.

::: dashboard_compiler.panels.charts.xy.config.LensReferenceLineLayer
    options:
      show_root_heading: false
      heading_level: 3

::: dashboard_compiler.panels.charts.xy.config.XYReferenceLine
    options:
      show_root_heading: false
      heading_level: 3

### Reference Line Examples

Reference lines help highlight important thresholds, targets, or limits in your charts. Below are comprehensive examples showing different styling options and use cases.

#### Basic Reference Line

Add a simple horizontal line to mark a threshold:

```yaml
dashboards:
  - name: "Basic Reference Line"
    panels:
      - title: "Response Time with SLA Threshold"
        size: {w: 24, h: 15}
        lens:
          type: line
          data_view: "logs-*"
          dimension:
            field: "@timestamp"
            type: date_histogram
          metrics:
            - aggregation: average
              field: "response.time"
              label: "Avg Response Time"
          layers:
            - type: reference_line
              data_view: "logs-*"
              reference_lines:
                - value: 500
                  label: "SLA Limit (500ms)"
```

#### Styled Reference Lines

Customize line color, width, and style:

```yaml
dashboards:
  - name: "Styled Reference Lines"
    panels:
      - title: "CPU Usage with Multiple Thresholds"
        size: {w: 24, h: 15}
        lens:
          type: area
          data_view: "metrics-*"
          dimension:
            field: "@timestamp"
            type: date_histogram
          metrics:
            - aggregation: average
              field: "system.cpu.usage"
              label: "CPU %"
          layers:
            - type: reference_line
              data_view: "metrics-*"
              reference_lines:
                # Warning threshold (yellow, dashed)
                - value: 70
                  label: "Warning"
                  color: "#FFA500"
                  line_width: 2
                  line_style: dashed
                # Critical threshold (red, solid)
                - value: 90
                  label: "Critical"
                  color: "#BD271E"
                  line_width: 3
                  line_style: solid
                # Target (green, dotted)
                - value: 50
                  label: "Target"
                  color: "#00BF6F"
                  line_width: 2
                  line_style: dotted
```

#### Reference Lines with Fill

Fill the area above or below a reference line:

```yaml
dashboards:
  - name: "Reference Lines with Fill"
    panels:
      - title: "Error Rate with Acceptable Range"
        size: {w: 24, h: 15}
        lens:
          type: line
          data_view: "logs-*"
          dimension:
            field: "@timestamp"
            type: date_histogram
          metrics:
            - formula: "count(kql='log.level:error') / count() * 100"
              label: "Error Rate %"
          layers:
            - type: reference_line
              data_view: "logs-*"
              reference_lines:
                # Fill above this line in red (danger zone)
                - value: 5
                  label: "Max Acceptable Error Rate"
                  color: "#BD271E"
                  line_width: 2
                  fill: above
                # Fill below this line in green (safe zone)
                - value: 1
                  label: "Target Error Rate"
                  color: "#00BF6F"
                  line_width: 1
                  fill: below
```

#### Reference Lines with Icons

Add icons to reference lines for visual emphasis:

```yaml
dashboards:
  - name: "Reference Lines with Icons"
    panels:
      - title: "Memory Usage with Limits"
        size: {w: 24, h: 15}
        lens:
          type: area
          data_view: "metrics-*"
          dimension:
            field: "@timestamp"
            type: date_histogram
          metrics:
            - aggregation: max
              field: "system.memory.used.pct"
              label: "Memory Usage %"
          layers:
            - type: reference_line
              data_view: "metrics-*"
              reference_lines:
                - value: 80
                  label: "Warning Level"
                  color: "#FFA500"
                  line_width: 2
                  icon: "alert"
                  icon_position: right
                - value: 95
                  label: "Critical Level"
                  color: "#BD271E"
                  line_width: 3
                  icon: "error"
                  icon_position: right
```

#### Multiple Metrics with Reference Lines

Combine multiple data series with reference lines:

```yaml
dashboards:
  - name: "Multi-Metric with Thresholds"
    panels:
      - title: "Request Metrics with SLA"
        size: {w: 24, h: 15}
        lens:
          type: line
          data_view: "logs-*"
          dimension:
            field: "@timestamp"
            type: date_histogram
          metrics:
            - aggregation: average
              field: "response.time"
              label: "Avg Response Time"
              axis: left
            - aggregation: percentile
              field: "response.time"
              percentile: 95
              label: "P95 Response Time"
              axis: left
          layers:
            - type: reference_line
              data_view: "logs-*"
              reference_lines:
                - value: 500
                  label: "SLA: Avg < 500ms"
                  color: "#0077CC"
                  line_width: 2
                  line_style: solid
                  axis: left
                - value: 1000
                  label: "SLA: P95 < 1000ms"
                  color: "#9170B8"
                  line_width: 2
                  line_style: dashed
                  axis: left
```

#### Dynamic Reference Lines (Formula-Based)

While reference lines are typically static values, you can use formulas in your metrics to create threshold-aware visualizations:

```yaml
dashboards:
  - name: "Threshold-Aware Visualization"
    panels:
      - title: "Requests Above Threshold"
        size: {w: 24, h: 15}
        lens:
          type: bar
          data_view: "logs-*"
          dimension:
            field: "@timestamp"
            type: date_histogram
          metrics:
            - aggregation: count
              label: "Total Requests"
            - formula: "count() - 1000"
              label: "Requests Above Threshold (1000)"
          layers:
            - type: reference_line
              data_view: "logs-*"
              reference_lines:
                - value: 1000
                  label: "Threshold"
                  color: "#BD271E"
                  line_width: 2
```

### Reference Line Best Practices

1. **Use Semantic Colors**: Match colors to meaning (green = good, yellow = warning, red = critical)
2. **Limit the Number**: Too many reference lines create visual clutter (3-4 maximum recommended)
3. **Clear Labels**: Always label reference lines so users understand what they represent
4. **Appropriate Fill**: Use fill sparingly and only when it adds clarity
5. **Consistent Styling**: Use the same styling patterns across dashboards for similar thresholds

## ES|QL XY Charts

::: dashboard_compiler.panels.charts.xy.config.ESQLBarChart
    options:
      show_root_heading: false
      heading_level: 3

::: dashboard_compiler.panels.charts.xy.config.ESQLLineChart
    options:
      show_root_heading: false
      heading_level: 3

::: dashboard_compiler.panels.charts.xy.config.ESQLAreaChart
    options:
      show_root_heading: false
      heading_level: 3

## Related

- [Base Panel Configuration](./base.md)
- [Dashboard Configuration](../dashboard/dashboard.md)
