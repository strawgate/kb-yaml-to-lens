# Programmatic Usage Guide

This guide shows you how to create Kibana dashboards entirely in Python code using the Dashboard Compiler API, without writing any YAML configuration files.

## Why Use Python Code?

While YAML is great for simple, static dashboards, creating dashboards programmatically offers several advantages:

- **Dynamic Generation**: Create dashboards based on runtime data, configuration, or external sources
- **Reusability**: Build helper functions and templates for common dashboard patterns
- **Type Safety**: Leverage Pydantic models for validation and IDE autocomplete
- **Programmatic Logic**: Use loops, conditionals, and functions to generate complex layouts
- **Integration**: Easily integrate dashboard creation into your existing Python workflows

## Installation

Install the Dashboard Compiler using [uv](https://github.com/astral-sh/uv):

```bash
uv sync
```

## Quick Start

Here's a minimal example of creating a dashboard programmatically:

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
    name='Dashboard Name',              # Required: Display name
    description='Dashboard description', # Optional: Description
    data_view='logs-*',                 # Optional: Default data view
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

## Panel Types

The Dashboard Compiler supports various panel types for different visualization needs. For detailed examples and API reference for each panel type, see the [Panels API documentation](api/panels.md).

**Available Panel Types:**

- **[Markdown Panels](api/panels.md#markdown-panels)** - Display rich text content using markdown syntax
- **[Metric Charts](api/panels.md#metric-charts)** - Display key performance indicators (KPIs)
- **[Pie Charts](api/panels.md#pie-charts)** - Show distribution of categorical data
- **[XY Charts](api/panels.md#xy-charts)** - Create line, bar, and area charts for time series data
- **[Links Panels](api/panels.md#links-panels)** - Display collections of links
- **[Image Panels](api/panels.md#image-panels)** - Embed images in dashboards
- **[Search Panels](api/panels.md#search-panels)** - Display search results

## Filters and Controls

### Global Filters

Add filters that apply to all panels in the dashboard:

```python
from dashboard_compiler.filters.config import Phrase, Range, Exists

# Phrase filter
dashboard.add_filter(Phrase(
    field='environment',
    value='production',
))

# Range filter
dashboard.add_filter(Range(
    field='response_time',
    gte=0,
    lte=1000,
))

# Exists filter
dashboard.add_filter(Exists(field='error.message'))
```

### Interactive Controls

Add interactive controls for filtering data:

```python
from dashboard_compiler.controls.config import (
    OptionsListControl,
    RangeSliderControl,
    TimeSliderControl,
)

# Options list (dropdown filter)
dashboard.add_control(OptionsListControl(
    field='log.level',
    title='Log Level',
    width='medium',
))

# Range slider
dashboard.add_control(RangeSliderControl(
    field='bytes',
    title='Response Size',
    min=0,
    max=10000,
    step=100,
    width='medium',
))

# Time slider
dashboard.add_control(TimeSliderControl(
    title='Time Range',
    width='large',
))
```

### Queries

Add global queries to your dashboard:

```python
from dashboard_compiler.queries.config import KQL, Lucene

# KQL query
dashboard.query = KQL(query='status:200 OR status:404')

# Lucene query
dashboard.query = Lucene(query='status:(200 OR 404)')
```

## Dynamic Dashboard Generation

One of the key benefits of programmatic dashboards is the ability to generate them dynamically:

### Generating Panels from Configuration

```python
metrics_config = [
    {'name': 'CPU Usage', 'field': 'cpu_percent'},
    {'name': 'Memory Usage', 'field': 'memory_percent'},
    {'name': 'Disk I/O', 'field': 'disk_io'},
]

for i, metric in enumerate(metrics_config):
    chart = LensMetricChart(
        type='metric',
        data_view='metrics-*',
        primary=Average(field=metric['field']),
    )

    panel = LensPanel(
        type='lens',
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
        primary=Average(field=field),
    )

    return LensPanel(
        type='lens',
        title=title,
        grid=Grid(x=x, y=y, w=24, h=15),
        chart=chart,
    )

# Use the helper function
dashboard.add_panel(create_metric_panel('Avg Response Time', 'response_time', 0, 0))
dashboard.add_panel(create_metric_panel('Avg Bytes', 'bytes', 24, 0))
```

### Conditional Panel Creation

```python
# Only add error metrics if error logging is enabled
if config.get('enable_error_tracking'):
    error_panel = LensPanel(
        type='lens',
        title='Error Rate',
        grid=Grid(x=0, y=15, w=24, h=15),
        chart=LensMetricChart(
            type='metric',
            data_view='logs-*',
            primary=Count(),
        ),
    )
    dashboard.add_panel(error_panel)
```

## Rendering and Export

### Rendering to Kibana Format

Convert your dashboard to Kibana's NDJSON format:

```python
from dashboard_compiler.dashboard_compiler import render

kbn_dashboard = render(dashboard)
output = kbn_dashboard.model_dump_json(by_alias=True, exclude_none=True)
```

### Saving to File

```python
with open('dashboard.ndjson', 'w') as f:
    f.write(output)
```

### Saving Multiple Dashboards

```python
from dashboard_compiler.dashboard_compiler import dump

dashboards = [dashboard1, dashboard2, dashboard3]
dump(dashboards, 'dashboards.yaml')
```

### Direct Upload to Kibana

Use the Kibana client for direct upload:

```python
from dashboard_compiler.kibana_client import KibanaClient

client = KibanaClient(
    url='http://localhost:5601',
    username='elastic',
    password='changeme',
)

# Upload the rendered dashboard
client.import_dashboard(output, overwrite=True)
```

## Advanced Patterns

### Dashboard Templates

Create reusable dashboard templates:

```python
class DashboardTemplate:
    """Base template for creating standardized dashboards."""

    def __init__(self, name: str, data_view: str):
        self.dashboard = Dashboard(name=name, data_view=data_view)

    def add_header(self, content: str):
        """Add a standard header panel."""
        panel = MarkdownPanel(
            type='markdown',
            grid=Grid(x=0, y=0, w=48, h=8),
            content=content,
        )
        self.dashboard.add_panel(panel)
        return self

    def add_metric_row(self, metrics: list[dict]):
        """Add a row of metric panels."""
        for i, metric in enumerate(metrics):
            chart = LensMetricChart(
                type='metric',
                data_view=self.dashboard.data_view,
                primary=Average(field=metric['field']),
            )
            panel = LensPanel(
                type='lens',
                title=metric['title'],
                grid=Grid(
                    x=i * (48 // len(metrics)),
                    y=8,
                    w=48 // len(metrics),
                    h=15,
                ),
                chart=chart,
            )
            self.dashboard.add_panel(panel)
        return self

    def build(self) -> Dashboard:
        """Return the built dashboard."""
        return self.dashboard

# Usage
template = DashboardTemplate('System Metrics', 'metrics-*')
dashboard = (template
    .add_header('# System Performance Dashboard')
    .add_metric_row([
        {'title': 'CPU', 'field': 'cpu_percent'},
        {'title': 'Memory', 'field': 'memory_percent'},
        {'title': 'Disk', 'field': 'disk_percent'},
    ])
    .build())
```

### Loading from External Sources

```python
import json

# Load dashboard structure from JSON
with open('dashboard_config.json') as f:
    config = json.load(f)

dashboard = Dashboard(name=config['name'])

for panel_config in config['panels']:
    if panel_config['type'] == 'markdown':
        panel = MarkdownPanel(**panel_config)
    elif panel_config['type'] == 'metric':
        # Create metric panel based on config
        panel = create_metric_from_config(panel_config)

    dashboard.add_panel(panel)
```

### Generating from Database Queries

```python
# Example: Generate a dashboard from database metadata
def create_dashboard_from_db_schema(connection, table_name: str) -> Dashboard:
    """Create a monitoring dashboard based on database table schema."""
    dashboard = Dashboard(
        name=f'{table_name} Monitoring',
        description=f'Auto-generated dashboard for {table_name}',
    )

    # Query database for numeric columns
    cursor = connection.execute(f"DESCRIBE {table_name}")
    numeric_columns = [row[0] for row in cursor if row[1] in ('int', 'float', 'decimal')]

    # Create a metric panel for each numeric column
    for i, column in enumerate(numeric_columns):
        panel = create_metric_panel(
            title=f'Avg {column}',
            field=column,
            x=(i % 3) * 16,
            y=(i // 3) * 15,
        )
        dashboard.add_panel(panel)

    return dashboard
```

## Complete Example

Here's a comprehensive example putting it all together:

```python
from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.markdown.config import MarkdownPanel
from dashboard_compiler.panels.lens.config import LensPanel
from dashboard_compiler.panels.charts.metric.config import LensMetricChart
from dashboard_compiler.panels.charts.lens.metrics.config import Count, Average
from dashboard_compiler.filters.config import Phrase
from dashboard_compiler.controls.config import OptionsListControl
from dashboard_compiler.queries.config import KQL

# Create dashboard
dashboard = Dashboard(
    name='Production Monitoring Dashboard',
    description='Real-time production metrics and logs',
    data_view='logs-production-*',
)

# Add global query and filter
dashboard.query = KQL(query='NOT error.message:null')
dashboard.add_filter(Phrase(field='environment', value='production'))

# Add control
dashboard.add_control(OptionsListControl(
    field='service.name',
    title='Service',
    width='medium',
))

# Add header
header = MarkdownPanel(
    type='markdown',
    grid=Grid(x=0, y=0, w=48, h=8),
    content='# Production Monitoring\n\nReal-time metrics and performance indicators.',
)
dashboard.add_panel(header)

# Add metrics row
metrics = [
    {'title': 'Total Requests', 'field': None, 'agg': Count()},
    {'title': 'Avg Response Time', 'field': 'response_time', 'agg': Average(field='response_time')},
    {'title': 'Avg Bytes', 'field': 'bytes', 'agg': Average(field='bytes')},
    {'title': 'Error Count', 'field': None, 'agg': Count()},
]

for i, metric in enumerate(metrics):
    chart = LensMetricChart(
        type='metric',
        data_view='logs-production-*',
        primary=metric['agg'],
    )
    panel = LensPanel(
        type='lens',
        title=metric['title'],
        grid=Grid(x=i * 12, y=8, w=12, h=12),
        chart=chart,
    )
    dashboard.add_panel(panel)

# Render and export
kbn_dashboard = render(dashboard)
output = kbn_dashboard.model_dump_json(by_alias=True, exclude_none=True)

# Save to file
with open('production_dashboard.ndjson', 'w') as f:
    f.write(output)

print('Dashboard created successfully!')
```

## API Reference

For complete API documentation, see:

- [Dashboard API](api/dashboard.md)
- [Panels API](api/panels.md)
- [Controls API](api/controls.md)
- [Filters API](api/filters.md)
- [Queries API](api/queries.md)

## Example Scripts

Check out the [`examples/`](https://github.com/strawgate/kb-yaml-to-lens/tree/main/examples) directory for
ready-to-run example scripts demonstrating various patterns and use cases.

## Next Steps

- Explore the [API Reference](api/index.md) for detailed documentation
- Check out the [examples directory](https://github.com/strawgate/kb-yaml-to-lens/tree/main/examples) for more code samples
- Read the [YAML Reference](yaml_reference.md) to understand all available configuration options
- See [Contributing](CONTRIBUTING.md) to add new panel types or features
