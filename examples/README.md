# Dashboard Compiler - Programmatic Examples

This directory contains Python examples demonstrating how to create Kibana dashboards
programmatically using the Dashboard Compiler API, without writing any YAML.

## Why Programmatic Dashboards?

While YAML is great for simple, static dashboards, creating dashboards in Python code offers several advantages:

- **Dynamic Generation**: Create dashboards based on runtime data, configuration files, or external sources
- **Reusability**: Build helper functions and templates for common dashboard patterns
- **Type Safety**: Leverage Pydantic models for validation and IDE autocomplete
- **Programmatic Logic**: Use loops, conditionals, and functions to generate complex layouts
- **Integration**: Easily integrate dashboard creation into your existing Python workflows

## Examples

### Basic Examples

- **[basic_markdown.py](basic_markdown.py)** - Simple dashboard with a markdown panel
- **[basic_metric.py](basic_metric.py)** - Dashboard with a single metric visualization

### Intermediate Examples

- **[multi_panel.py](multi_panel.py)** - Dashboard with multiple panels of different types
- **[with_filters_controls.py](with_filters_controls.py)** - Dashboard with global filters and interactive controls

### Advanced Examples

- **[dynamic_generation.py](dynamic_generation.py)** - Generate dashboards dynamically from configuration data

## Running the Examples

### Prerequisites

Install the Dashboard Compiler package:

```bash
uv sync
```

### Running an Example

Execute any example script to see the generated NDJSON output:

```bash
# Run with Python directly
python examples/basic_markdown.py

# Or use uv
uv run examples/basic_markdown.py
```

The script will output NDJSON format that can be imported into Kibana.

### Saving Output to a File

To save the generated dashboard to a file:

```bash
python examples/basic_markdown.py > my_dashboard.ndjson
```

### Uploading to Kibana

You can pipe the output to a file and use the `kb-dashboard` CLI to upload it, or modify the example
to use the `dashboard_compiler.kibana_client` module for direct upload.

Example using the CLI:

```bash
# Generate and save to file
python examples/basic_markdown.py > dashboard.ndjson

# Upload to Kibana
kb-dashboard compile --input-dir . --upload --kibana-url http://localhost:5601
```

## Key Concepts

### Creating a Dashboard

```python
from dashboard_compiler.dashboard.config import Dashboard

dashboard = Dashboard(
    name='My Dashboard',
    description='Created programmatically',
)
```

### Adding Panels

```python
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.markdown.config import MarkdownPanel

panel = MarkdownPanel(
    type='markdown',
    grid=Grid(x=0, y=0, w=24, h=15),
    content='# Hello World',
)

dashboard.add_panel(panel)
```

### Rendering to Kibana Format

```python
from dashboard_compiler.dashboard_compiler import render

kbn_dashboard = render(dashboard)
output = kbn_dashboard.model_dump_json(by_alias=True, exclude_none=True)
```

## Grid Layout

Kibana uses a 48-column grid system. Common panel widths:

- **Full width**: `w=48`
- **Half width**: `w=24`
- **Third width**: `w=16`
- **Quarter width**: `w=12`

Heights are flexible, but common values are:

- **Small**: `h=8`
- **Medium**: `h=15`
- **Large**: `h=20`

## Next Steps

- Review the [API Reference](../docs/api/index.md) for complete documentation
- Check out the [Programmatic Usage Guide](../docs/programmatic-usage.md) for detailed patterns
- Explore the test files in `tests/` for more advanced usage examples

## Contributing

Found an interesting use case? Consider contributing a new example! See [CONTRIBUTING.md](../CONTRIBUTING.md)
for guidelines.
