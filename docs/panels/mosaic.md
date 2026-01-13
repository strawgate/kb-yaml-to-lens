# Mosaic Chart Panel Configuration

The Mosaic chart panel visualizes multi-dimensional categorical data as proportional rectangles, showing how categories nest and relate to each other.

## A Poem for the Mosaic Mavens

_For those who appreciate art in their analytics:_

```text
In rectangles stacked and sized with care,
Your data's proportions laid out fair,
From left to right, the mosaic grows,
Each colored tile a story shows.

Where pie charts spin in circles round,
The mosaic keeps your data grounded—
Categories stack, dimensions nest,
Proportions clear from east to west.

Like stained glass windows tell their tales,
Your metrics shine in colored scales.
Traffic, users, bytes, and more—
Each rectangle opens up a door.

So when your data needs to flex,
And show relationships complex,
Don't settle for a simple chart—
Make your dashboards work of art!
```

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
