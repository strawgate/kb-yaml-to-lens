#!/usr/bin/env python3
"""Example: Creating a dashboard with multiple panels programmatically.

This example demonstrates how to build a more complex dashboard with multiple
panels of different types arranged in a grid layout.
"""

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.panels.charts.config import LensPanel
from dashboard_compiler.panels.charts.lens.metrics.config import LensCountAggregatedMetric, LensOtherAggregatedMetric
from dashboard_compiler.panels.charts.metric.config import LensMetricChart
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.markdown.config import MarkdownPanel

# Create a new dashboard
dashboard = Dashboard(
    name='Multi-Panel Dashboard',
    description='A dashboard with multiple visualization types',
    data_view='logs-*',  # Default data view for all panels
)

# Panel 1: Header with markdown
header_panel = MarkdownPanel(
    type='markdown',
    grid=Grid(x=0, y=0, w=48, h=8),
    content='# System Monitoring Dashboard\n\nReal-time metrics and statistics for system monitoring.',
)

# Panel 2: Document count metric
count_metric = LensPanel(
    type='charts',
    title='Total Documents',
    grid=Grid(x=0, y=8, w=12, h=12),
    chart=LensMetricChart(
        type='metric',
        data_view='logs-*',
        primary=LensCountAggregatedMetric(aggregation='count'),
    ),
)

# Panel 3: Average bytes metric
avg_metric = LensPanel(
    type='charts',
    title='Average Bytes',
    grid=Grid(x=12, y=8, w=12, h=12),
    chart=LensMetricChart(
        type='metric',
        data_view='logs-*',
        primary=LensOtherAggregatedMetric(aggregation='average', field='bytes'),
    ),
)

# Panel 4: Response time metric
response_metric = LensPanel(
    type='charts',
    title='Avg Response Time',
    grid=Grid(x=24, y=8, w=12, h=12),
    chart=LensMetricChart(
        type='metric',
        data_view='logs-*',
        primary=LensOtherAggregatedMetric(aggregation='average', field='response_time'),
    ),
)

# Panel 5: Error count metric
error_metric = LensPanel(
    type='charts',
    title='Error Count',
    grid=Grid(x=36, y=8, w=12, h=12),
    chart=LensMetricChart(
        type='metric',
        data_view='logs-*',
        primary=LensCountAggregatedMetric(aggregation='count'),
    ),
)

# Add all panels to the dashboard
dashboard.add_panel(header_panel)
dashboard.add_panel(count_metric)
dashboard.add_panel(avg_metric)
dashboard.add_panel(response_metric)
dashboard.add_panel(error_metric)

# Render the dashboard to Kibana format
kbn_dashboard = render(dashboard)

# Export to NDJSON format
output = kbn_dashboard.model_dump_json(by_alias=True, exclude_none=True)
print(output)
