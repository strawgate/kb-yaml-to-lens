# Waffle Chart Panel Configuration

The Waffle chart panel visualizes categorical data as a grid of colored squares, where each square represents a proportion of the whole. Waffle charts support exactly one metric and an optional breakdown.

---

## Lens Waffle Charts

::: kb_dashboard_core.panels.charts.waffle.config.LensWaffleChart
    options:
      show_root_heading: false
      heading_level: 3

## Waffle Chart Legend

For comprehensive guidance on legend configuration, see the [Legend Configuration Guide](../guides/legend-configuration.md).

::: kb_dashboard_core.panels.charts.waffle.config.WaffleLegend
    options:
      show_root_heading: false
      heading_level: 3

## Waffle Chart Appearance

::: kb_dashboard_core.panels.charts.waffle.config.WaffleAppearance
    options:
      show_root_heading: false
      heading_level: 3

::: kb_dashboard_core.panels.charts.waffle.config.WaffleValuesConfig
    options:
      show_root_heading: false
      heading_level: 3

## ES|QL Waffle Charts

::: kb_dashboard_core.panels.charts.waffle.config.ESQLWaffleChart
    options:
      show_root_heading: false
      heading_level: 3

## Related

- [Mosaic Chart Configuration](./mosaic.md)
- [Pie Chart Configuration](./pie.md)
- [Base Panel Configuration](./base.md)
- [Dashboard Configuration](../dashboard/dashboard.md)
