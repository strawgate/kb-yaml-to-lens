"""Gauge chart models and compilation logic."""

from dashboard_compiler.panels.charts.gauge.compile import compile_esql_gauge_chart, compile_lens_gauge_chart
from dashboard_compiler.panels.charts.gauge.config import ESQLGaugeChart, LensGaugeChart

__all__ = [
    'ESQLGaugeChart',
    'LensGaugeChart',
    'compile_esql_gauge_chart',
    'compile_lens_gauge_chart',
]
