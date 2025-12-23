#!/usr/bin/env python3
"""Example: Creating a basic markdown dashboard programmatically.

This example demonstrates how to create a simple dashboard with a markdown panel
using Python code instead of YAML configuration.
"""

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.markdown.config import MarkdownPanel

# Create a new dashboard
dashboard = Dashboard(
    name='My Programmatic Dashboard',
    description='Created entirely in Python code',
)

# Create a markdown panel with custom content
markdown_panel = MarkdownPanel(
    type='markdown',
    grid=Grid(x=0, y=0, w=24, h=15),
    content="""# Hello from Python!

This dashboard was created programmatically using the Dashboard Compiler API.

## Features

- **No YAML required** - Build dashboards entirely in code
- **Type safety** - Leverage Pydantic models for validation
- **Composable** - Create reusable dashboard components
- **Dynamic** - Generate dashboards from data or templates

## Next Steps

Check out the other examples to see more advanced usage patterns!
""",
)

# Add the panel to the dashboard
dashboard.add_panel(markdown_panel)

# Render the dashboard to Kibana format
kbn_dashboard = render(dashboard)

# Export to NDJSON format (suitable for importing into Kibana)
output = kbn_dashboard.model_dump_json(by_alias=True, exclude_none=True)
print(output)
