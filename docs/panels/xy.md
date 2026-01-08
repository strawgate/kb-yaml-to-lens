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

## Legend Configuration

::: dashboard_compiler.panels.charts.xy.config.XYLegend
    options:
      show_root_heading: false
      heading_level: 3

## Migration Guide: Series Configuration

**Breaking Change**: As of this version, series configuration has been moved from `appearance.series` to individual metric definitions.

### Before (Old API)

```yaml
lens:
  type: line
  data_view: "logs-*"
  dimension:
    type: date_histogram
    field: "@timestamp"
  metrics:
    - aggregation: count
      id: "metric1"
    - aggregation: average
      field: "error_rate"
      id: "metric2"
  appearance:
    series:
      - metric_id: "metric1"
        axis: left
        color: "#2196F3"
      - metric_id: "metric2"
        axis: right
        color: "#FF5252"
```

### After (New API)

```yaml
lens:
  type: line
  data_view: "logs-*"
  dimension:
    type: date_histogram
    field: "@timestamp"
  metrics:
    - aggregation: count
      id: "metric1"
      axis: left
      color: "#2196F3"
    - aggregation: average
      field: "error_rate"
      id: "metric2"
      axis: right
      color: "#FF5252"
```

### Migration Steps

1. For each item in `appearance.series`, find the corresponding metric by `metric_id`
2. Move the `axis` and `color` properties directly onto the metric definition
3. Remove the `appearance.series` section entirely

This change makes the configuration more intuitive by keeping visual properties with their metric definitions rather than in a separate section.

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
