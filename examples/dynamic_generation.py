#!/usr/bin/env python3
"""Example: Dynamically generating dashboard panels from data.

This example shows how to use Python's control flow (loops, conditionals, etc.)
to dynamically generate dashboard panels based on data structures or configuration.
"""

from dashboard_compiler.panels.lens.config import LensPanel

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.panels.charts.lens.metrics.config import Average, Count
from dashboard_compiler.panels.charts.metric.config import LensMetricChart
from dashboard_compiler.panels.config import Grid

# Configuration: List of metrics to monitor
metrics_config = [
    {'name': 'CPU Usage', 'field': 'cpu_percent', 'aggregation': 'average'},
    {'name': 'Memory Usage', 'field': 'memory_percent', 'aggregation': 'average'},
    {'name': 'Disk I/O', 'field': 'disk_io', 'aggregation': 'average'},
    {'name': 'Network Traffic', 'field': 'network_bytes', 'aggregation': 'average'},
    {'name': 'Active Connections', 'field': None, 'aggregation': 'count'},
    {'name': 'Error Rate', 'field': None, 'aggregation': 'count'},
]

# Create a new dashboard
dashboard = Dashboard(
    name='Dynamically Generated Dashboard',
    description='Generated from a metrics configuration list',
)

# Dynamically generate metric panels
for i, metric in enumerate(metrics_config):
    # Calculate grid position (2 columns)
    col = i % 2
    row = i // 2

    # Create the appropriate metric based on configuration
    if metric['aggregation'] == 'count':
        primary_metric = Count()
    elif metric['aggregation'] == 'average':
        primary_metric = Average(field=metric['field'])
    else:
        # Default to count if unknown aggregation
        primary_metric = Count()

    # Create the chart
    chart = LensMetricChart(
        type='metric',
        data_view='metrics-*',
        primary=primary_metric,
    )

    # Create the panel with calculated grid position
    panel = LensPanel(
        type='lens',
        title=metric['name'],
        grid=Grid(
            x=col * 24,  # Each panel is 24 units wide
            y=row * 15,  # Each panel is 15 units tall
            w=24,
            h=15,
        ),
        chart=chart,
    )

    # Add to dashboard
    dashboard.add_panel(panel)

# Render the dashboard to Kibana format
kbn_dashboard = render(dashboard)

# Export to NDJSON format
output = kbn_dashboard.model_dump_json(by_alias=True, exclude_none=True)
print(output)

# You could also save to a file:
# with open('generated_dashboard.ndjson', 'w') as f:
#     f.write(output)
