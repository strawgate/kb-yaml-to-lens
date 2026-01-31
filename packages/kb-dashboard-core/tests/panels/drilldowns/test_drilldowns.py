"""Tests for drilldown compilation from config models to view models."""

from typing import Any

from dirty_equals import IsStr
from inline_snapshot import snapshot

from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.dashboard_compiler import render
from kb_dashboard_core.panels.drilldowns import (
    DASHBOARD_TO_DASHBOARD_DRILLDOWN,
    URL_DRILLDOWN,
    DashboardDrilldown,
    DrilldownTrigger,
    UrlDrilldown,
    compile_drilldowns,
)
from kb_dashboard_core.panels.drilldowns.compile import compile_dashboard_drilldown, compile_trigger, compile_url_drilldown


class TestCompileTrigger:
    """Tests for compile_trigger function."""

    def test_click_trigger(self) -> None:
        """Test that click trigger compiles to VALUE_CLICK_TRIGGER."""
        result = compile_trigger(DrilldownTrigger.click)
        assert result == 'VALUE_CLICK_TRIGGER'

    def test_filter_trigger(self) -> None:
        """Test that filter trigger compiles to FILTER_TRIGGER."""
        result = compile_trigger(DrilldownTrigger.filter)
        assert result == 'FILTER_TRIGGER'

    def test_range_trigger(self) -> None:
        """Test that range trigger compiles to SELECT_RANGE_TRIGGER."""
        result = compile_trigger(DrilldownTrigger.range)
        assert result == 'SELECT_RANGE_TRIGGER'


class TestCompileDashboardDrilldown:
    """Tests for compile_dashboard_drilldown function."""

    def test_basic_dashboard_drilldown(self) -> None:
        """Test compiling a basic dashboard drilldown."""
        drilldown = DashboardDrilldown(
            name='Go to Details',
            dashboard='dashboard-123',
        )
        reference, event = compile_dashboard_drilldown(drilldown, order=0)

        assert reference.model_dump(by_alias=True) == snapshot(
            {
                'type': 'dashboard',
                'id': 'dashboard-123',
                'name': IsStr(regex=r'drilldown:DASHBOARD_TO_DASHBOARD_DRILLDOWN:.*:dashboardId'),
            }
        )

        assert event.model_dump(by_alias=True) == snapshot(
            {
                'eventId': IsStr(),
                'triggers': ['VALUE_CLICK_TRIGGER'],
                'action': {
                    'factoryId': DASHBOARD_TO_DASHBOARD_DRILLDOWN,
                    'name': 'Go to Details',
                    'config': {
                        'useCurrentFilters': True,
                        'useCurrentDateRange': True,
                    },
                },
            }
        )

    def test_dashboard_drilldown_with_custom_id(self) -> None:
        """Test that custom drilldown ID is used when provided."""
        drilldown = DashboardDrilldown(
            id='custom-drilldown-id',
            name='Go to Dashboard',
            dashboard='dashboard-456',
        )
        reference, event = compile_dashboard_drilldown(drilldown, order=0)

        assert event.eventId == 'custom-drilldown-id'
        assert reference.name == 'drilldown:DASHBOARD_TO_DASHBOARD_DRILLDOWN:custom-drilldown-id:dashboardId'

    def test_dashboard_drilldown_without_filters(self) -> None:
        """Test dashboard drilldown with filters disabled."""
        drilldown = DashboardDrilldown(
            name='Go to Dashboard',
            dashboard='dashboard-789',
            with_filters=False,
        )
        _reference, event = compile_dashboard_drilldown(drilldown, order=0)

        assert event.action.config['useCurrentFilters'] is False
        assert event.action.config['useCurrentDateRange'] is True

    def test_dashboard_drilldown_without_time(self) -> None:
        """Test dashboard drilldown with time range disabled."""
        drilldown = DashboardDrilldown(
            name='Go to Dashboard',
            dashboard='dashboard-abc',
            with_time=False,
        )
        _reference, event = compile_dashboard_drilldown(drilldown, order=0)

        assert event.action.config['useCurrentFilters'] is True
        assert event.action.config['useCurrentDateRange'] is False

    def test_dashboard_drilldown_with_multiple_triggers(self) -> None:
        """Test dashboard drilldown with multiple triggers."""
        drilldown = DashboardDrilldown(
            name='Go to Dashboard',
            dashboard='dashboard-xyz',
            triggers=[DrilldownTrigger.click, DrilldownTrigger.filter, DrilldownTrigger.range],
        )
        _reference, event = compile_dashboard_drilldown(drilldown, order=0)

        assert event.triggers == ['VALUE_CLICK_TRIGGER', 'FILTER_TRIGGER', 'SELECT_RANGE_TRIGGER']


class TestCompileUrlDrilldown:
    """Tests for compile_url_drilldown function."""

    def test_basic_url_drilldown(self) -> None:
        """Test compiling a basic URL drilldown."""
        drilldown = UrlDrilldown(
            name='Open URL',
            url='https://example.com/{{context.panel.query}}',
        )
        event = compile_url_drilldown(drilldown, order=0)

        assert event.model_dump(by_alias=True) == snapshot(
            {
                'eventId': IsStr(),
                'triggers': ['VALUE_CLICK_TRIGGER'],
                'action': {
                    'factoryId': URL_DRILLDOWN,
                    'name': 'Open URL',
                    'config': {
                        'url': {'template': 'https://example.com/{{context.panel.query}}'},
                        'openInNewTab': False,
                        'encodeUrl': True,
                    },
                },
            }
        )

    def test_url_drilldown_with_custom_id(self) -> None:
        """Test that custom drilldown ID is used when provided."""
        drilldown = UrlDrilldown(
            id='custom-url-id',
            name='Open URL',
            url='https://example.com',
        )
        event = compile_url_drilldown(drilldown, order=0)

        assert event.eventId == 'custom-url-id'

    def test_url_drilldown_new_tab(self) -> None:
        """Test URL drilldown with new tab enabled."""
        drilldown = UrlDrilldown(
            name='Open URL',
            url='https://example.com',
            new_tab=True,
        )
        event = compile_url_drilldown(drilldown, order=0)

        assert event.action.config['openInNewTab'] is True

    def test_url_drilldown_without_encoding(self) -> None:
        """Test URL drilldown with URL encoding disabled."""
        drilldown = UrlDrilldown(
            name='Open URL',
            url='https://example.com',
            encode_url=False,
        )
        event = compile_url_drilldown(drilldown, order=0)

        assert event.action.config['encodeUrl'] is False

    def test_url_drilldown_with_range_trigger(self) -> None:
        """Test URL drilldown with range trigger."""
        drilldown = UrlDrilldown(
            name='Open URL',
            url='https://example.com',
            triggers=[DrilldownTrigger.range],
        )
        event = compile_url_drilldown(drilldown, order=0)

        assert event.triggers == ['SELECT_RANGE_TRIGGER']


class TestCompileDrilldowns:
    """Tests for compile_drilldowns function."""

    def test_empty_drilldowns(self) -> None:
        """Test compiling empty drilldowns list."""
        references, enhancements = compile_drilldowns([])

        assert references == []
        assert enhancements.model_dump(by_alias=True) == snapshot(
            {
                'dynamicActions': {'events': []},
            }
        )

    def test_single_dashboard_drilldown(self) -> None:
        """Test compiling a single dashboard drilldown."""
        drilldown = DashboardDrilldown(
            name='Go to Details',
            dashboard='dashboard-123',
        )
        references, enhancements = compile_drilldowns([drilldown])

        assert len(references) == 1
        assert references[0].type == 'dashboard'
        assert references[0].id == 'dashboard-123'

        assert len(enhancements.dynamicActions.events) == 1
        assert enhancements.dynamicActions.events[0].action.factoryId == DASHBOARD_TO_DASHBOARD_DRILLDOWN

    def test_single_url_drilldown(self) -> None:
        """Test compiling a single URL drilldown."""
        drilldown = UrlDrilldown(
            name='Open URL',
            url='https://example.com',
        )
        references, enhancements = compile_drilldowns([drilldown])

        assert len(references) == 0  # URL drilldowns don't create references
        assert len(enhancements.dynamicActions.events) == 1
        assert enhancements.dynamicActions.events[0].action.factoryId == URL_DRILLDOWN

    def test_mixed_drilldowns(self) -> None:
        """Test compiling a mix of dashboard and URL drilldowns."""
        drilldowns = [
            DashboardDrilldown(name='Dashboard 1', dashboard='dash-1'),
            UrlDrilldown(name='URL 1', url='https://example.com/1'),
            DashboardDrilldown(name='Dashboard 2', dashboard='dash-2'),
            UrlDrilldown(name='URL 2', url='https://example.com/2'),
        ]
        references, enhancements = compile_drilldowns(drilldowns)

        # Only dashboard drilldowns create references
        assert len(references) == 2
        assert references[0].id == 'dash-1'
        assert references[1].id == 'dash-2'

        # All drilldowns create events
        assert len(enhancements.dynamicActions.events) == 4

    def test_order_affects_stable_id_generation(self) -> None:
        """Test that different orders produce different stable IDs."""
        drilldown = DashboardDrilldown(
            name='Same Name',
            dashboard='same-dashboard',
        )
        _ref1, event1 = compile_dashboard_drilldown(drilldown, order=0)
        _ref2, event2 = compile_dashboard_drilldown(drilldown, order=1)

        # Same drilldown at different positions should have different IDs
        assert event1.eventId != event2.eventId


class TestDrilldownsInDashboard:
    """Integration tests for drilldowns in full dashboard compilation."""

    def test_lens_panel_with_dashboard_drilldown(self) -> None:
        """Test that dashboard drilldown references bubble up to dashboard level."""
        dashboard = Dashboard(
            name='Test Dashboard with Drilldowns',
            panels=[
                {
                    'title': 'Metric with Drilldown',
                    'id': 'metric-panel-1',
                    'position': {'x': 0, 'y': 0},
                    'size': {'w': 24, 'h': 15},
                    'lens': {
                        'type': 'metric',
                        'data_view': 'metrics-*',
                        'primary': {'aggregation': 'count', 'id': 'metric1'},
                    },
                    'drilldowns': [
                        {
                            'name': 'Go to Details',
                            'dashboard': 'details-dashboard-id',
                            'id': 'drill-1',
                        },
                    ],
                }
            ],
        )

        kbn_dashboard = render(dashboard=dashboard)
        references = [ref.model_dump() for ref in kbn_dashboard.references]

        # Check that both the index pattern and dashboard references are present
        assert any(ref['type'] == 'index-pattern' for ref in references)
        assert any(ref['type'] == 'dashboard' and ref['id'] == 'details-dashboard-id' for ref in references)

    def test_lens_panel_with_url_drilldown(self) -> None:
        """Test that URL drilldown does not create external references."""
        dashboard = Dashboard(
            name='Test Dashboard with URL Drilldown',
            panels=[
                {
                    'title': 'Metric with URL Drilldown',
                    'id': 'metric-panel-2',
                    'position': {'x': 0, 'y': 0},
                    'size': {'w': 24, 'h': 15},
                    'lens': {
                        'type': 'metric',
                        'data_view': 'metrics-*',
                        'primary': {'aggregation': 'count', 'id': 'metric1'},
                    },
                    'drilldowns': [
                        {
                            'name': 'Open External',
                            'url': 'https://example.com/details',
                            'new_tab': True,
                        },
                    ],
                }
            ],
        )

        kbn_dashboard = render(dashboard=dashboard)
        references = [ref.model_dump() for ref in kbn_dashboard.references]

        # Only index pattern reference should exist (no dashboard reference for URL drilldowns)
        assert len([ref for ref in references if ref['type'] == 'dashboard']) == 0
        assert any(ref['type'] == 'index-pattern' for ref in references)

    def test_lens_panel_with_multiple_drilldowns(self) -> None:
        """Test panel with both dashboard and URL drilldowns."""
        dashboard = Dashboard(
            name='Test Dashboard with Multiple Drilldowns',
            panels=[
                {
                    'title': 'Metric with Multiple Drilldowns',
                    'id': 'metric-panel-3',
                    'position': {'x': 0, 'y': 0},
                    'size': {'w': 24, 'h': 15},
                    'lens': {
                        'type': 'metric',
                        'data_view': 'metrics-*',
                        'primary': {'aggregation': 'count', 'id': 'metric1'},
                    },
                    'drilldowns': [
                        {
                            'name': 'Dashboard Drilldown',
                            'dashboard': 'target-dashboard',
                            'id': 'dash-drill',
                        },
                        {
                            'name': 'URL Drilldown',
                            'url': 'https://external.com/page',
                            'id': 'url-drill',
                        },
                    ],
                }
            ],
        )

        kbn_dashboard = render(dashboard=dashboard)
        references = [ref.model_dump() for ref in kbn_dashboard.references]

        # Check dashboard reference exists
        dashboard_refs = [ref for ref in references if ref['type'] == 'dashboard']
        assert len(dashboard_refs) == 1
        assert dashboard_refs[0]['id'] == 'target-dashboard'

    def test_esql_panel_with_drilldown(self) -> None:
        """Test that ESQL panels support drilldowns."""
        dashboard = Dashboard(
            name='Test ESQL Dashboard with Drilldown',
            panels=[
                {
                    'title': 'ESQL Metric with Drilldown',
                    'id': 'esql-panel-1',
                    'position': {'x': 0, 'y': 0},
                    'size': {'w': 24, 'h': 15},
                    'esql': {
                        'type': 'metric',
                        'query': 'FROM logs-* | STATS count()',
                        'primary': {'field': 'count(*)', 'id': 'metric1'},
                    },
                    'drilldowns': [
                        {
                            'name': 'View Details',
                            'dashboard': 'log-details-dashboard',
                        },
                    ],
                }
            ],
        )

        kbn_dashboard = render(dashboard=dashboard)
        references = [ref.model_dump() for ref in kbn_dashboard.references]

        # Dashboard reference should exist
        dashboard_refs = [ref for ref in references if ref['type'] == 'dashboard']
        assert len(dashboard_refs) == 1
        assert dashboard_refs[0]['id'] == 'log-details-dashboard'

    def test_drilldown_with_filter_trigger(self) -> None:
        """Test drilldown with filter trigger type."""
        dashboard = Dashboard(
            name='Test Dashboard with Filter Trigger',
            panels=[
                {
                    'title': 'Panel with Filter Trigger Drilldown',
                    'id': 'panel-with-filter-trigger',
                    'position': {'x': 0, 'y': 0},
                    'size': {'w': 24, 'h': 15},
                    'lens': {
                        'type': 'metric',
                        'data_view': 'metrics-*',
                        'primary': {'aggregation': 'count', 'id': 'metric1'},
                    },
                    'drilldowns': [
                        {
                            'name': 'Filter Drilldown',
                            'dashboard': 'filtered-dashboard',
                            'triggers': [DrilldownTrigger.filter],
                        },
                    ],
                }
            ],
        )

        kbn_dashboard = render(dashboard=dashboard)

        # The dashboard should compile without errors
        assert kbn_dashboard.attributes.title == 'Test Dashboard with Filter Trigger'


def compile_panel_drilldown_snapshot(panel_config: dict[str, Any]) -> dict[str, Any]:
    """Compile a panel and extract drilldown enhancements for snapshot testing."""
    from kb_dashboard_core.panels.charts.compile import compile_charts_panel_config
    from kb_dashboard_core.panels.charts.config import LensPanel

    panel = LensPanel.model_validate(
        {
            'position': {'x': 0, 'y': 0},
            'size': {'w': 24, 'h': 15},
            **panel_config,
        }
    )
    _references, embeddable_config = compile_charts_panel_config(panel)
    return embeddable_config.model_dump(by_alias=True)['enhancements']


class TestDrilldownEnhancementsInPanelConfig:
    """Tests for drilldown enhancements in panel embeddable config."""

    def test_panel_without_drilldowns(self) -> None:
        """Test that panel without drilldowns has empty events array."""
        result = compile_panel_drilldown_snapshot(
            {
                'lens': {
                    'type': 'metric',
                    'data_view': 'metrics-*',
                    'primary': {'aggregation': 'count', 'id': 'metric1'},
                },
            }
        )

        assert result == snapshot(
            {
                'dynamicActions': {'events': []},
            }
        )

    def test_panel_with_dashboard_drilldown(self) -> None:
        """Test panel with dashboard drilldown has correct enhancements structure."""
        result = compile_panel_drilldown_snapshot(
            {
                'lens': {
                    'type': 'metric',
                    'data_view': 'metrics-*',
                    'primary': {'aggregation': 'count', 'id': 'metric1'},
                },
                'drilldowns': [
                    {
                        'name': 'Go to Dashboard',
                        'dashboard': 'target-dash',
                        'id': 'dd-1',
                    },
                ],
            }
        )

        assert result == snapshot(
            {
                'dynamicActions': {
                    'events': [
                        {
                            'eventId': 'dd-1',
                            'triggers': ['VALUE_CLICK_TRIGGER'],
                            'action': {
                                'factoryId': 'DASHBOARD_TO_DASHBOARD_DRILLDOWN',
                                'name': 'Go to Dashboard',
                                'config': {
                                    'useCurrentFilters': True,
                                    'useCurrentDateRange': True,
                                },
                            },
                        }
                    ],
                },
            }
        )

    def test_panel_with_url_drilldown(self) -> None:
        """Test panel with URL drilldown has correct enhancements structure."""
        result = compile_panel_drilldown_snapshot(
            {
                'lens': {
                    'type': 'metric',
                    'data_view': 'metrics-*',
                    'primary': {'aggregation': 'count', 'id': 'metric1'},
                },
                'drilldowns': [
                    {
                        'name': 'Open Docs',
                        'url': 'https://docs.example.com/{{event.value}}',
                        'id': 'url-1',
                        'new_tab': True,
                        'encode_url': True,
                    },
                ],
            }
        )

        assert result == snapshot(
            {
                'dynamicActions': {
                    'events': [
                        {
                            'eventId': 'url-1',
                            'triggers': ['VALUE_CLICK_TRIGGER'],
                            'action': {
                                'factoryId': 'URL_DRILLDOWN',
                                'name': 'Open Docs',
                                'config': {
                                    'url': {'template': 'https://docs.example.com/{{event.value}}'},
                                    'openInNewTab': True,
                                    'encodeUrl': True,
                                },
                            },
                        }
                    ],
                },
            }
        )
