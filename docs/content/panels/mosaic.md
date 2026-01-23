# Mosaic Chart Panel Configuration

The Mosaic chart panel visualizes categorical data as proportional rectangles, showing category distributions at a glance. Mosaic charts support exactly one metric, one dimension, and an optional breakdown.

---

## Lens Mosaic Charts

::: dashboard_compiler.panels.charts.mosaic.config.LensMosaicChart
    options:
      show_root_heading: false
      heading_level: 3

## Mosaic Chart Legend

For comprehensive guidance on legend configuration, see the [Legend Configuration Guide](../advanced/legend-configuration.md).

::: dashboard_compiler.panels.charts.mosaic.config.MosaicLegend
    options:
      show_root_heading: false
      heading_level: 3

## Mosaic Chart Titles and Text

::: dashboard_compiler.panels.charts.mosaic.config.MosaicTitlesAndText
    options:
      show_root_heading: false
      heading_level: 3

## ES|QL Mosaic Charts

::: dashboard_compiler.panels.charts.mosaic.config.ESQLMosaicChart
    options:
      show_root_heading: false
      heading_level: 3

## Related

- [Pie Chart Configuration](./pie.md)
- [Base Panel Configuration](./base.md)
- [Dashboard Configuration](../dashboard/dashboard.md)
