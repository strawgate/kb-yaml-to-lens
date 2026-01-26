# Panels

Panel types and compilation logic.

## Base Panel Configuration

::: kb_dashboard_core.panels.base.BasePanel
    options:
      show_source: true

## Markdown Panels

Display rich text content using markdown syntax.

### API Reference

::: kb_dashboard_core.panels.markdown.config.MarkdownPanel
    options:
      show_source: true

For configuration details and examples, see the [Markdown Panel Configuration](../panels/markdown.md).

## Links Panels

Display collections of clickable links.

### API Reference

::: kb_dashboard_core.panels.links.config.LinksPanel
    options:
      show_source: true

For configuration details and examples, see the [Links Panel Configuration](../panels/links.md).

## Image Panels

Embed images in your dashboard.

### API Reference

::: kb_dashboard_core.panels.images.config.ImagePanel
    options:
      show_source: true

For configuration details and examples, see the [Image Panel Configuration](../panels/image.md).

## Search Panels

Display search results from Elasticsearch.

### API Reference

::: kb_dashboard_core.panels.search.config.SearchPanel
    options:
      show_source: true

For configuration details and examples, see the [Search Panel Configuration](../panels/search.md).

## Lens Panel

Lens panels are used to create data visualizations including metrics, pie charts, and XY charts.

### API Reference

::: kb_dashboard_core.panels.charts.config.LensPanel
    options:
      show_source: true

### Metric Charts

Display key performance indicators.

For configuration details and examples, see the [Metric Chart Panel Configuration](../panels/metric.md).

### Pie Charts

Create pie chart visualizations to show distribution of categorical data.

For configuration details and examples, see the [Pie Chart Panel Configuration](../panels/pie.md).

### Heatmap Charts

Create heatmap visualizations to show patterns across two categorical dimensions.

For configuration details and examples, see the [Heatmap Chart Panel Configuration](../panels/heatmap.md).

::: kb_dashboard_core.panels.charts.heatmap.config.LensHeatmapChart
    options:
      show_source: true

::: kb_dashboard_core.panels.charts.heatmap.config.ESQLHeatmapChart
    options:
      show_source: true

### XY Charts

Create line, bar, and area charts for time series and other data.

For configuration details and examples, see the [XY Chart Panel Configuration](../panels/xy.md).

## ESQL Panel

::: kb_dashboard_core.panels.charts.config.ESQLPanel
    options:
      show_source: true
