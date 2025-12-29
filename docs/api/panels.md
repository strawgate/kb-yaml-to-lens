# Panels

Panel types and compilation logic.

## Base Panel Configuration

::: dashboard_compiler.panels.base.BasePanel
    options:
      show_source: true

## Markdown Panels

Display rich text content using markdown syntax.

### API Reference

::: dashboard_compiler.panels.markdown.config.MarkdownPanel
    options:
      show_source: true

For configuration details and examples, see the [Markdown Panel Configuration](../../src/dashboard_compiler/panels/markdown/markdown.md).

## Links Panels

Display collections of clickable links.

### API Reference

::: dashboard_compiler.panels.links.config.LinksPanel
    options:
      show_source: true

For configuration details and examples, see the [Links Panel Configuration](../../src/dashboard_compiler/panels/links/links.md).

## Image Panels

Embed images in your dashboard.

### API Reference

::: dashboard_compiler.panels.images.config.ImagePanel
    options:
      show_source: true

For configuration details and examples, see the [Image Panel Configuration](../../src/dashboard_compiler/panels/images/image.md).

## Search Panels

Display search results from Elasticsearch.

### API Reference

::: dashboard_compiler.panels.search.config.SearchPanel
    options:
      show_source: true

For configuration details and examples, see the [Search Panel Configuration](../../src/dashboard_compiler/panels/search/search.md).

## Lens Panel

Lens panels are used to create data visualizations including metrics, pie charts, and XY charts.

### API Reference

::: dashboard_compiler.panels.charts.config.LensPanel
    options:
      show_source: true

### Metric Charts

Display key performance indicators.

For configuration details and examples, see the [Metric Chart Panel Configuration](../../src/dashboard_compiler/panels/charts/metric/config.md).

### Pie Charts

Create pie chart visualizations to show distribution of categorical data.

For configuration details and examples, see the [Pie Chart Panel Configuration](../../src/dashboard_compiler/panels/charts/pie/config.md).

### XY Charts

Create line, bar, and area charts for time series and other data.

For configuration details and examples, see the [XY Chart Panel Configuration](../../src/dashboard_compiler/panels/charts/xy/config.md).

## Lens Multi-Layer Panel

::: dashboard_compiler.panels.charts.config.LensMultiLayerPanel
    options:
      show_source: true

## ESQL Panel

::: dashboard_compiler.panels.charts.config.ESQLPanel
    options:
      show_source: true
