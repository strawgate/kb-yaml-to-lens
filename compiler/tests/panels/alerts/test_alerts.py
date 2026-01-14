"""Test the compilation of alerts panels from config models to view models."""

from typing import TYPE_CHECKING, Any

from inline_snapshot import snapshot

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.panels.alerts.compile import compile_alerts_panel_config
from dashboard_compiler.panels.alerts.config import AlertsPanel

if TYPE_CHECKING:
    from dashboard_compiler.dashboard.view import KbnDashboard


def compile_alerts_panel_snapshot(config: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compile alerts panel config and return dict for snapshot testing."""
    alerts_panel = AlertsPanel(size={'w': 48, 'h': 20}, position={'x': 0, 'y': 0}, **config)
    kbn_references, kbn_panel_config = compile_alerts_panel_config(alerts_panel=alerts_panel)
    kbn_panel_as_dict = kbn_panel_config.model_dump(by_alias=True)
    kbn_references_as_dicts = [ref.model_dump(by_alias=True) for ref in kbn_references]
    return kbn_references_as_dicts, kbn_panel_as_dict


def test_compile_alerts_panel_observability() -> None:
    """Test the compilation of an observability alerts panel."""
    references, result = compile_alerts_panel_snapshot(
        {
            'alerts': {
                'solution': 'observability',
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'enhancements': {},
            'tableConfig': {
                'query': {
                    'filters': [],
                    'type': 'alertsFilters',
                },
                'solution': 'observability',
            },
        }
    )


def test_compile_alerts_panel_security() -> None:
    """Test the compilation of a security alerts panel."""
    references, result = compile_alerts_panel_snapshot(
        {
            'alerts': {
                'solution': 'security',
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'enhancements': {},
            'tableConfig': {
                'query': {
                    'filters': [],
                    'type': 'alertsFilters',
                },
                'solution': 'security',
            },
        }
    )


def test_compile_alerts_panel_stack() -> None:
    """Test the compilation of a stack alerts panel."""
    references, result = compile_alerts_panel_snapshot(
        {
            'alerts': {
                'solution': 'stack',
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'enhancements': {},
            'tableConfig': {
                'query': {
                    'filters': [],
                    'type': 'alertsFilters',
                },
                'solution': 'stack',
            },
        }
    )


def test_compile_alerts_panel_with_filters() -> None:
    """Test the compilation of an alerts panel with filters."""
    references, result = compile_alerts_panel_snapshot(
        {
            'alerts': {
                'solution': 'observability',
                'filters': [
                    {'field': 'kibana.alert.rule.name', 'values': ['CPU Usage Alert', 'Memory Usage Alert']},
                    {'field': 'kibana.alert.status', 'values': ['active']},
                ],
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'enhancements': {},
            'tableConfig': {
                'query': {
                    'filters': [
                        {'field': 'kibana.alert.rule.name', 'values': ['CPU Usage Alert', 'Memory Usage Alert']},
                        {'field': 'kibana.alert.status', 'values': ['active']},
                    ],
                    'type': 'alertsFilters',
                },
                'solution': 'observability',
            },
        }
    )


def test_compile_alerts_panel_with_single_filter() -> None:
    """Test the compilation of an alerts panel with a single filter."""
    references, result = compile_alerts_panel_snapshot(
        {
            'alerts': {
                'solution': 'security',
                'filters': [
                    {'field': 'kibana.alert.severity', 'values': ['critical']},
                ],
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'enhancements': {},
            'tableConfig': {
                'query': {
                    'filters': [
                        {'field': 'kibana.alert.severity', 'values': ['critical']},
                    ],
                    'type': 'alertsFilters',
                },
                'solution': 'security',
            },
        }
    )


def test_alerts_panel_dashboard_integration() -> None:
    """Test that alerts panel integrates correctly with dashboard compilation."""
    dashboard = Dashboard(
        name='Test Alerts Dashboard',
        panels=[
            {
                'title': 'Active Alerts',
                'id': 'alerts-panel-1',
                'size': {'w': 48, 'h': 20},
                'position': {'x': 0, 'y': 0},
                'alerts': {
                    'solution': 'observability',
                },
            }
        ],
    )

    kbn_dashboard: KbnDashboard = render(dashboard=dashboard)
    references = [ref.model_dump() for ref in kbn_dashboard.references]

    # Alerts panels have no external references
    assert references == snapshot([])
