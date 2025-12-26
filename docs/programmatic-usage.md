# Programmatic Usage

The Dashboard Compiler provides a full programmatic API for creating dashboards in Python code, without writing any YAML configuration files.

## Why Use Python Code?

While YAML is great for simple, static dashboards, creating dashboards programmatically offers several advantages:

- **Dynamic Generation**: Create dashboards based on runtime data, configuration, or external sources
- **Reusability**: Build helper functions and templates for common dashboard patterns
- **Type Safety**: Leverage Pydantic models for validation and IDE autocomplete
- **Programmatic Logic**: Use loops, conditionals, and functions to generate complex layouts
- **Integration**: Easily integrate dashboard creation into your existing Python workflows

## Quick Example

```python
from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.markdown.config import MarkdownPanel

# Create a dashboard
dashboard = Dashboard(
    name='My First Dashboard',
    description='Created in Python',
)

# Add a markdown panel
panel = MarkdownPanel(
    type='markdown',
    grid=Grid(x=0, y=0, w=24, h=15),
    content='# Hello from Python!',
)
dashboard.add_panel(panel)

# Render to Kibana format
kbn_dashboard = render(dashboard)
output = kbn_dashboard.model_dump_json(by_alias=True, exclude_none=True)
print(output)
```

## Core Concepts

### Dashboard Object

The `Dashboard` class is the main entry point for creating dashboards:

```python
from dashboard_compiler.dashboard.config import Dashboard

dashboard = Dashboard(
    name='Dashboard Name',  # Required: Display name
    description='Dashboard description',  # Optional: Description
    data_view='logs-*',  # Optional: Default data view
)
```

### Grid Layout

Kibana uses a 48-column grid system. Panels are positioned using the `Grid` class:

```python
from dashboard_compiler.panels.config import Grid

# Full-width panel
grid = Grid(x=0, y=0, w=48, h=15)

# Half-width panels (left and right)
left_grid = Grid(x=0, y=0, w=24, h=15)
right_grid = Grid(x=24, y=0, w=24, h=15)

# Quarter-width panels
grid1 = Grid(x=0, y=0, w=12, h=15)
grid2 = Grid(x=12, y=0, w=12, h=15)
grid3 = Grid(x=24, y=0, w=12, h=15)
grid4 = Grid(x=36, y=0, w=12, h=15)
```

**Grid Parameters:**

- `x`: Horizontal position (0-47)
- `y`: Vertical position (0+)
- `w`: Width in grid units (1-48)
- `h`: Height in grid units (1+)

### Adding Panels

Use the `add_panel()` method to add panels to your dashboard:

```python
dashboard.add_panel(panel)
```

This method returns the dashboard instance, allowing for method chaining:

```python
dashboard.add_panel(panel1).add_panel(panel2).add_panel(panel3)
```

## Dynamic Dashboard Generation

One of the key benefits of programmatic dashboards is the ability to generate them dynamically:

### Generating Panels from Configuration

```python
from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.charts.config import LensPanel
from dashboard_compiler.panels.charts.lens.metrics.config import (
    LensOtherAggregatedMetric,
)
from dashboard_compiler.panels.charts.metric.config import LensMetricChart
from dashboard_compiler.panels.config import Grid

dashboard = Dashboard(name='Metrics Dashboard')

metrics_config = [
    {'name': 'CPU Usage', 'field': 'cpu_percent'},
    {'name': 'Memory Usage', 'field': 'memory_percent'},
    {'name': 'Disk I/O', 'field': 'disk_io'},
]

for i, metric in enumerate(metrics_config):
    chart = LensMetricChart(
        type='metric',
        data_view='metrics-*',
        primary=LensOtherAggregatedMetric(aggregation='average', field=metric['field']),
    )

    panel = LensPanel(
        type='charts',
        title=metric['name'],
        grid=Grid(
            x=(i % 3) * 16,  # 3 columns
            y=(i // 3) * 15,
            w=16,
            h=15,
        ),
        chart=chart,
    )

    dashboard.add_panel(panel)
```

### Building Reusable Helper Functions

```python
def create_metric_panel(title: str, field: str, x: int, y: int) -> LensPanel:
    """Helper function to create a standard metric panel."""
    chart = LensMetricChart(
        type='metric',
        data_view='logs-*',
        primary=LensOtherAggregatedMetric(aggregation='average', field=field),
    )

    return LensPanel(
        type='charts',
        title=title,
        grid=Grid(x=x, y=y, w=24, h=15),
        chart=chart,
    )

# Use the helper function
dashboard.add_panel(create_metric_panel('Avg Response Time', 'response_time', 0, 0))
dashboard.add_panel(create_metric_panel('Avg Bytes', 'bytes', 24, 0))
```

## Filters and Controls

### Global Filters

Add filters that apply to all panels in the dashboard:

```python
from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.filters.config import ExistsFilter, PhraseFilter, RangeFilter

dashboard = Dashboard(name='Filtered Dashboard')

# Phrase filter
dashboard.add_filter(
    PhraseFilter(
        field='environment',
        equals='production',
    )
)

# Range filter
dashboard.add_filter(
    RangeFilter(
        field='response_time',
        gte='0',
        lte='1000',
    )
)

# Exists filter
dashboard.add_filter(ExistsFilter(exists='error.message'))
```

### Interactive Controls

Add interactive controls for filtering data:

```python
from dashboard_compiler.controls.config import (
    OptionsListControl,
    RangeSliderControl,
)
from dashboard_compiler.dashboard.config import Dashboard

dashboard = Dashboard(name='Dashboard with Controls')

# Options list (dropdown filter)
dashboard.add_control(
    OptionsListControl(
        field='log.level',
        label='Log Level',
        width='medium',
        data_view='logs-*',
    )
)

# Range slider
dashboard.add_control(
    RangeSliderControl(
        field='bytes',
        label='Response Size',
        step=100,
        width='medium',
        data_view='logs-*',
    )
)
```

## Rendering and Export

### Rendering to Kibana Format

Convert your dashboard to Kibana's NDJSON format:

```python
from pathlib import Path

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import render

dashboard = Dashboard(name='My Dashboard')
kbn_dashboard = render(dashboard)
output = kbn_dashboard.model_dump_json(by_alias=True, exclude_none=True)

# Save to file
Path('dashboard.ndjson').write_text(output)
```

### Saving Multiple Dashboards

```python
from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import dump

dashboard1 = Dashboard(name='Dashboard 1')
dashboard2 = Dashboard(name='Dashboard 2')
dashboard3 = Dashboard(name='Dashboard 3')

dashboards = [dashboard1, dashboard2, dashboard3]
dump(dashboards, 'dashboards.ndjson')
```

## Panel Types

The Dashboard Compiler supports various panel types. For detailed examples and API reference for each panel type, see the **[Panels API Reference](api/panels.md)**.

**Available Panel Types:**

- **[Markdown Panels](api/panels.md#markdown-panels)** - Display rich text content
- **[Metric Charts](api/panels.md#metric-charts)** - Display key performance indicators (KPIs)
- **[Pie Charts](api/panels.md#pie-charts)** - Show distribution of categorical data
- **[XY Charts](api/panels.md#xy-charts)** - Create line, bar, and area charts for time series data
- **[Links Panels](api/panels.md#links-panels)** - Display collections of links
- **[Image Panels](api/panels.md#image-panels)** - Embed images in dashboards
- **[Search Panels](api/panels.md#search-panels)** - Display search results

## API Reference

For detailed API documentation and more examples, see:

- **[API Reference](api/index.md)** - Complete API documentation
- **[Panels](api/panels.md)** - Panel types with Python examples
- **[Dashboard](api/dashboard.md)** - Dashboard configuration
- **[Controls](api/controls.md)** - Control group configuration
- **[Filters](api/filters.md)** - Filter compilation
- **[Queries](api/queries.md)** - Query compilation
