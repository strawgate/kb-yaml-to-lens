#!/usr/bin/env python3
"""Example: Creating a dashboard with filters and controls programmatically.

This example demonstrates how to add global filters and interactive controls
to a dashboard for enhanced filtering and exploration capabilities.
"""

from dashboard_compiler.controls.config import OptionsListControl, RangeSliderControl
from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.filters.config import PhraseFilter, RangeFilter
from dashboard_compiler.panels.charts.config import LensPanel
from dashboard_compiler.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from dashboard_compiler.panels.charts.metric.config import LensMetricChart
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.queries.config import KqlQuery

# Create a new dashboard
dashboard = Dashboard(
    name='Dashboard with Filters and Controls',
    description='Demonstrates global filters and interactive controls',
    data_view='logs-*',
    query=KqlQuery(kql='status:200 OR status:404'),
)

# Add global filters
# Filter 1: Only show logs from production environment
production_filter = PhraseFilter(
    field='environment',
    equals='production',
)
dashboard.add_filter(production_filter)

# Filter 2: Only show logs with response time in a specific range
response_time_filter = RangeFilter(
    field='response_time',
    gte='0',
    lte='1000',
)
dashboard.add_filter(response_time_filter)

# Add interactive controls
# Control 1: Options list for selecting log level
log_level_control = OptionsListControl(
    field='log.level',
    label='Log Level',
    width='medium',
    fill_width=True,
    data_view='logs-*',
)
dashboard.add_control(log_level_control)

# Control 2: Range slider for bytes
bytes_control = RangeSliderControl(
    field='bytes',
    label='Bytes Range',
    width='medium',
    fill_width=True,
    step=100,
    data_view='logs-*',
)
dashboard.add_control(bytes_control)

# Add a metric panel to visualize the filtered data
metric_panel = LensPanel(
    type='charts',
    title='Filtered Document Count',
    grid=Grid(x=0, y=0, w=24, h=15),
    chart=LensMetricChart(
        type='metric',
        data_view='logs-*',
        primary=LensCountAggregatedMetric(aggregation='count'),
    ),
)
dashboard.add_panel(metric_panel)

# Render the dashboard to Kibana format
kbn_dashboard = render(dashboard)

# Export to NDJSON format
output = kbn_dashboard.model_dump_json(by_alias=True, exclude_none=True)
print(output)
