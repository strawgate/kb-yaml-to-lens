# Treemap Chart Panel Configuration

The Treemap chart panel visualizes hierarchical data as nested rectangles, where each rectangle's size represents a metric value. Treemap charts support one or more metrics and require at least one breakdown (maximum two breakdowns).

---

## Lens Treemap Charts

::: kb_dashboard_core.panels.charts.treemap.config.LensTreemapChart
    options:
      show_root_heading: false
      heading_level: 3

## Treemap Chart Legend

For comprehensive guidance on legend configuration, see the [Legend Configuration Guide](../guides/legend-configuration.md).

::: kb_dashboard_core.panels.charts.treemap.config.TreemapLegend
    options:
      show_root_heading: false
      heading_level: 3

## Treemap Chart Appearance

::: kb_dashboard_core.panels.charts.treemap.config.TreemapAppearance
    options:
      show_root_heading: false
      heading_level: 3

::: kb_dashboard_core.panels.charts.treemap.config.TreemapCategoriesConfig
    options:
      show_root_heading: false
      heading_level: 3

::: kb_dashboard_core.panels.charts.treemap.config.TreemapValuesConfig
    options:
      show_root_heading: false
      heading_level: 3

## ES|QL Treemap Charts

::: kb_dashboard_core.panels.charts.treemap.config.ESQLTreemapChart
    options:
      show_root_heading: false
      heading_level: 3

## Related

- [Mosaic Chart Configuration](./mosaic.md)
- [Pie Chart Configuration](./pie.md)
- [Base Panel Configuration](./base.md)
- [Dashboard Configuration](../dashboard/dashboard.md)
