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

### Example

```python
from dashboard_compiler.panels.markdown.config import MarkdownPanel
from dashboard_compiler.panels.config import Grid

panel = MarkdownPanel(
    type='markdown',
    grid=Grid(x=0, y=0, w=24, h=15),
    content="""
# Dashboard Title

This is a **markdown** panel with:
- Lists
- **Bold** and *italic* text
- [Links](https://example.com)
    """,
)
```

## Links Panels

Display collections of clickable links.

### API Reference

::: dashboard_compiler.panels.links.config.LinksPanel
    options:
      show_source: true

### Example

```python
from dashboard_compiler.panels.links.config import LinksPanel, UrlLink
from dashboard_compiler.panels.config import Grid

panel = LinksPanel(
    type='links',
    grid=Grid(x=0, y=0, w=24, h=10),
    links=[
        UrlLink(
            label='Documentation',
            url='https://example.com/docs',
        ),
        UrlLink(
            label='API Reference',
            url='https://example.com/api',
        ),
    ],
)
```

## Image Panels

Embed images in your dashboard.

### API Reference

::: dashboard_compiler.panels.images.config.ImagePanel
    options:
      show_source: true

### Example

```python
from dashboard_compiler.panels.images.config import ImagePanel
from dashboard_compiler.panels.config import Grid

panel = ImagePanel(
    type='image',
    grid=Grid(x=0, y=0, w=24, h=20),
    url='https://example.com/logo.png',
)
```

## Search Panels

Display search results from Elasticsearch.

### API Reference

::: dashboard_compiler.panels.search.config.SearchPanel
    options:
      show_source: true

### Example

```python
from dashboard_compiler.panels.search.config import SearchPanel
from dashboard_compiler.panels.config import Grid

panel = SearchPanel(
    type='search',
    grid=Grid(x=0, y=0, w=48, h=20),
    data_view='logs-*',
)
```

## Lens Panel

Lens panels are used to create data visualizations including metrics, pie charts, and XY charts.

### API Reference

::: dashboard_compiler.panels.charts.config.LensPanel
    options:
      show_source: true

### Metric Charts

Display key performance indicators.

#### Example: Count Metric

```python
from dashboard_compiler.panels.lens.config import LensPanel
from dashboard_compiler.panels.charts.metric.config import LensMetricChart
from dashboard_compiler.panels.charts.lens.metrics.config import Count
from dashboard_compiler.panels.config import Grid

# Simple count metric
count_chart = LensMetricChart(
    type='metric',
    data_view='logs-*',
    primary=Count(),
)

panel = LensPanel(
    type='lens',
    title='Total Documents',
    grid=Grid(x=0, y=0, w=24, h=15),
    chart=count_chart,
)
```

#### Example: Average Metric

```python
from dashboard_compiler.panels.charts.lens.metrics.config import Average

# Average metric with field
avg_chart = LensMetricChart(
    type='metric',
    data_view='logs-*',
    primary=Average(field='response_time'),
)

panel = LensPanel(
    type='lens',
    title='Avg Response Time',
    grid=Grid(x=0, y=0, w=24, h=15),
    chart=avg_chart,
)
```

### Pie Charts

Create pie chart visualizations to show distribution of categorical data.

#### Example

```python
from dashboard_compiler.panels.lens.config import LensPanel
from dashboard_compiler.panels.charts.pie.config import LensPieChart
from dashboard_compiler.panels.charts.lens.dimensions.config import Terms
from dashboard_compiler.panels.charts.lens.metrics.config import Count
from dashboard_compiler.panels.config import Grid

pie_chart = LensPieChart(
    type='pie',
    data_view='logs-*',
    slices=Terms(field='status'),
    metric=Count(),
)

panel = LensPanel(
    type='lens',
    title='Status Distribution',
    grid=Grid(x=0, y=0, w=24, h=15),
    chart=pie_chart,
)
```

### XY Charts

Create line, bar, and area charts for time series and other data.

#### Example: Time Series Line Chart

```python
from dashboard_compiler.panels.lens.config import LensPanel
from dashboard_compiler.panels.charts.xy.config import LensXYChart, Layer
from dashboard_compiler.panels.charts.lens.dimensions.config import DateHistogram
from dashboard_compiler.panels.charts.lens.metrics.config import Count
from dashboard_compiler.panels.config import Grid

# Time series line chart
layer = Layer(
    type='line',
    x_axis=DateHistogram(field='@timestamp'),
    metrics=[Count()],
)

xy_chart = LensXYChart(
    type='xy',
    data_view='logs-*',
    layers=[layer],
)

panel = LensPanel(
    type='lens',
    title='Documents Over Time',
    grid=Grid(x=0, y=0, w=48, h=20),
    chart=xy_chart,
)
```

## Lens Multi-Layer Panel

::: dashboard_compiler.panels.charts.config.LensMultiLayerPanel
    options:
      show_source: true

## ESQL Panel

::: dashboard_compiler.panels.charts.config.ESQLPanel
    options:
      show_source: true
