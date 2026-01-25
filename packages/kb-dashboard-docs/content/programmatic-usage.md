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
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.dashboard_compiler import render
from kb_dashboard_core.panels.config import Size
from kb_dashboard_core.panels.markdown.config import MarkdownPanel, MarkdownPanelConfig

# Create a dashboard
dashboard = Dashboard(
    name='My First Dashboard',
    description='Created in Python',
)

# Add a markdown panel
panel = MarkdownPanel(
    size=Size(w=24, h=15),
    markdown=MarkdownPanelConfig(
        content='# Hello from Python!',
    ),
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
from kb_dashboard_core.dashboard.config import Dashboard

dashboard = Dashboard(
    name='Dashboard Name',  # Required: Display name
    description='Dashboard description',  # Optional: Description
)
```

### Panel Sizing

Kibana uses a 48-column grid system for output. Panels are sized using the `Size` class, with optional `Position` for explicit positioning:

```python
from kb_dashboard_core.panels.config import Position, Size

# Full-width panel (auto-positioned)
size = Size(w=48, h=15)

# Half-width panels
size_half = Size(w=24, h=15)

# Quarter-width panels
size_quarter = Size(w=12, h=15)

# Explicit position when needed
position = Position(x=0, y=0)
```

**Size Parameters:**

- `w`: Width in grid units (1-48)
- `h`: Height in grid units (1+)

**Position Parameters (optional):**

- `x`: Horizontal position (0-47)
- `y`: Vertical position (0+)

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
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.charts.config import (
    LensMetricPanelConfig,
    LensPanel,
)
from kb_dashboard_core.panels.charts.lens.metrics.config import (
    LensOtherAggregatedMetric,
)
from kb_dashboard_core.panels.config import Size

dashboard = Dashboard(name='Metrics Dashboard')

metrics_config = [
    {'name': 'CPU Usage', 'field': 'cpu_percent'},
    {'name': 'Memory Usage', 'field': 'memory_percent'},
    {'name': 'Disk I/O', 'field': 'disk_io'},
]

for metric in metrics_config:
    panel = LensPanel(
        title=metric['name'],
        size=Size(
            w=16,
            h=15,
        ),
        lens=LensMetricPanelConfig(
            type='metric',
            data_view='metrics-*',
            primary=LensOtherAggregatedMetric(
                aggregation='average', field=metric['field']
            ),
        ),
    )

    dashboard.add_panel(panel)
```

### Building Reusable Helper Functions

```python
def create_metric_panel(title: str, field: str) -> LensPanel:
    """Helper function to create a standard metric panel."""
    return LensPanel(
        title=title,
        size=Size(w=24, h=15),  # Auto-positioned
        lens=LensMetricPanelConfig(
            type='metric',
            data_view='logs-*',
            primary=LensOtherAggregatedMetric(aggregation='average', field=field),
        ),
    )

# Use the helper function
dashboard.add_panel(create_metric_panel('Avg Response Time', 'response_time'))
dashboard.add_panel(create_metric_panel('Avg Bytes', 'bytes'))
```

## Filters and Controls

### Global Filters

Add filters that apply to all panels in the dashboard:

```python
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.filters.config import ExistsFilter, PhraseFilter, RangeFilter

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
from kb_dashboard_core.controls.config import (
    OptionsListControl,
    RangeSliderControl,
)
from kb_dashboard_core.dashboard.config import Dashboard

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

from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.dashboard_compiler import render

dashboard = Dashboard(name='My Dashboard')
kbn_dashboard = render(dashboard)
output = kbn_dashboard.model_dump_json(by_alias=True, exclude_none=True)

# Save to file
Path('dashboard.ndjson').write_text(output)
```

### Saving Multiple Dashboards

```python
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.dashboard_compiler import dump

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
