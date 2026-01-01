"""Test minimum version detection for dashboards."""

from dashboard_compiler.dashboard.compile import compile_dashboard
from dashboard_compiler.dashboard.config import Dashboard


def test_baseline_dashboard_version() -> None:
    """Test that a basic dashboard has baseline version 8.8.0."""
    dashboard = Dashboard(
        name='Basic Dashboard',
        description='No special features',
    )

    kbn_dashboard = compile_dashboard(dashboard)
    assert kbn_dashboard.coreMigrationVersion == '8.8.0'


def test_esql_static_control_dashboard_version() -> None:
    """Test that dashboards with ES|QL static controls require 8.19.0."""
    dashboard = Dashboard(
        name='ES|QL Controls Dashboard',
        controls=[
            {
                'type': 'esql_static',
                'variable_name': 'status_code',
                'available_options': ['200', '404', '500'],
                'title': 'Status Code',
            }
        ],
    )

    kbn_dashboard = compile_dashboard(dashboard)
    assert kbn_dashboard.coreMigrationVersion == '8.19.0'


def test_esql_query_control_dashboard_version() -> None:
    """Test that dashboards with ES|QL query controls require 8.19.0."""
    dashboard = Dashboard(
        name='ES|QL Query Controls Dashboard',
        controls=[
            {
                'type': 'esql_query',
                'variable_name': 'status_code',
                'esql_query': 'FROM logs-* | STATS by status | KEEP status',
                'title': 'Status Code',
            }
        ],
    )

    kbn_dashboard = compile_dashboard(dashboard)
    assert kbn_dashboard.coreMigrationVersion == '8.19.0'


def test_esql_chart_dashboard_version() -> None:
    """Test that dashboards with ES|QL charts require 8.13.0."""
    dashboard = Dashboard(
        name='ES|QL Chart Dashboard',
        panels=[
            {
                'esql': {
                    'type': 'metric',
                    'query': 'FROM logs-* | STATS count = COUNT(*)',
                    'primary': {'field': 'count', 'id': 'metric1'},
                },
                'grid': {'x': 0, 'y': 0, 'w': 12, 'h': 8},
            }
        ],
    )

    kbn_dashboard = compile_dashboard(dashboard)
    assert kbn_dashboard.coreMigrationVersion == '8.13.0'


def test_esql_control_and_chart_dashboard_version() -> None:
    """Test that dashboards with both ES|QL controls and charts use max version (8.19.0)."""
    dashboard = Dashboard(
        name='ES|QL Full Dashboard',
        controls=[
            {
                'type': 'esql_query',
                'variable_name': 'status_code',
                'esql_query': 'FROM logs-* | STATS by status | KEEP status',
                'title': 'Status Code',
            }
        ],
        panels=[
            {
                'esql': {
                    'type': 'metric',
                    'query': 'FROM logs-* | WHERE status == ?status_code | STATS count = COUNT(*)',
                    'primary': {'field': 'count', 'id': 'metric1'},
                },
                'grid': {'x': 0, 'y': 0, 'w': 12, 'h': 8},
            }
        ],
    )

    kbn_dashboard = compile_dashboard(dashboard)
    assert kbn_dashboard.coreMigrationVersion == '8.19.0'
