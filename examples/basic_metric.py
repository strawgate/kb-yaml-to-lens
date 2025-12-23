#!/usr/bin/env python3
"""Example: Creating a metric dashboard programmatically.

This example shows how to create a dashboard with a metric panel that displays
a count of documents.
"""

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.panels.charts.config import LensPanel
from dashboard_compiler.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from dashboard_compiler.panels.charts.metric.config import LensMetricChart
from dashboard_compiler.panels.config import Grid

# Create a new dashboard
dashboard = Dashboard(
    name='Document Count Dashboard',
    description='A simple metric showing document count',
)

# Create a metric chart that counts documents
metric_chart = LensMetricChart(
    type='metric',
    data_view='logs-*',
    primary=LensCountAggregatedMetric(aggregation='count'),
)

# Create a Lens panel containing the metric chart
metric_panel = LensPanel(
    type='charts',
    title='Total Documents',
    grid=Grid(x=0, y=0, w=24, h=15),
    chart=metric_chart,
)

# Add the panel to the dashboard
dashboard.add_panel(metric_panel)

# Render the dashboard to Kibana format
kbn_dashboard = render(dashboard)

# Export to NDJSON format
output = kbn_dashboard.model_dump_json(by_alias=True, exclude_none=True)
print(output)
