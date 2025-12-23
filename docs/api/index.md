# API Reference

This section contains the API documentation for the Dashboard Compiler.

## Core Modules

- **[Dashboard](dashboard.md)** – Dashboard configuration and compilation
- **[Panels](panels.md)** – Panel types and compilation logic
- **[Controls](controls.md)** – Control group configuration
- **[Filters](filters.md)** – Filter compilation
- **[Queries](queries.md)** – Query compilation

## Programmatic API

The Dashboard Compiler provides a full programmatic API for creating dashboards in Python code.
For comprehensive examples and patterns, see the [Programmatic Usage Guide](../programmatic-usage.md).

### Quick Example

```python
from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.markdown.config import MarkdownPanel

# Create a dashboard
dashboard = Dashboard(name='My Dashboard')

# Add a panel
dashboard.add_panel(MarkdownPanel(
    type='markdown',
    grid=Grid(x=0, y=0, w=24, h=15),
    content='# Hello World',
))

# Render to Kibana format
kbn_dashboard = render(dashboard)
output = kbn_dashboard.model_dump_json(by_alias=True, exclude_none=True)
```

### Core Functions

The Dashboard Compiler provides these core functions for programmatic usage:

::: dashboard_compiler.dashboard_compiler
    options:
      show_source: true
      members:
        - load
        - render
        - dump
