# Tag Cloud Chart Panel Configuration

The Tag Cloud chart panel visualizes term frequency as a word cloud, where the size of each tag is proportional to its metric value. This is useful for showing the most common or significant terms in your data.

## Lens Tagcloud Charts

::: dashboard_compiler.panels.charts.tagcloud.config.LensTagcloudChart
    options:
      show_root_heading: false
      heading_level: 3

## ESQL Tagcloud Charts

::: dashboard_compiler.panels.charts.tagcloud.config.ESQLTagcloudChart
    options:
      show_root_heading: false
      heading_level: 3

## Tagcloud Appearance

::: dashboard_compiler.panels.charts.tagcloud.config.TagcloudAppearance
    options:
      show_root_heading: false
      heading_level: 3

### Orientation Options

::: dashboard_compiler.panels.charts.tagcloud.config.TagcloudOrientationEnum
    options:
      show_root_heading: false
      heading_level: 4

## Related

- [Base Panel Configuration](base.md)
- [Lens Panel Configuration](lens.md) (see sections on Dimensions and Metrics)
- [ESQL Panel Configuration](esql.md) (see section on ESQL Columns)
- [Dashboard Configuration](../dashboard/dashboard.md)
