# Gauge Chart Panel Configuration

The Gauge chart panel displays a single metric value with optional min/max ranges and goal indicators, typically used for KPIs and progress tracking toward targets or thresholds.

## Lens Gauge Charts

::: dashboard_compiler.panels.charts.gauge.config.LensGaugeChart
    options:
      show_root_heading: false
      heading_level: 3

## Gauge Appearance

::: dashboard_compiler.panels.charts.gauge.config.GaugeAppearance
    options:
      show_root_heading: false
      heading_level: 3

## ES|QL Gauge Charts

::: dashboard_compiler.panels.charts.gauge.config.ESQLGaugeChart
    options:
      show_root_heading: false
      heading_level: 3

## Related

- [Base Panel Configuration](./base.md)
- [Dashboard Configuration](../dashboard/dashboard.md)
- [Metric Charts](./metric.md)
