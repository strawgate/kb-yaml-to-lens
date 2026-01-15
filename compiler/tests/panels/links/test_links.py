"""Test the compilation of links panels from config models to view models."""

from typing import TYPE_CHECKING, Any

import pytest
from dirty_equals import IsUUID
from inline_snapshot import snapshot

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.panels.links.compile import compile_links_panel_config
from dashboard_compiler.panels.links.config import LinksPanel, get_link_type

if TYPE_CHECKING:
    from dashboard_compiler.dashboard.view import KbnDashboard


def compile_links_panel_snapshot(config: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compile links panel config and return dict for snapshot testing."""
    links_panel = LinksPanel(size={'w': 24, 'h': 10}, position={'x': 0, 'y': 0}, **config)
    kbn_references, kbn_panel_config = compile_links_panel_config(links_panel=links_panel)
    kbn_panel_as_dict = kbn_panel_config.model_dump(by_alias=True)
    kbn_references_as_dicts = [ref.model_dump(by_alias=True) for ref in kbn_references]
    return kbn_references_as_dicts, kbn_panel_as_dict


def test_compile_links_panel_basic_url() -> None:
    """Test the compilation of a basic URL link with no label."""
    references, result = compile_links_panel_snapshot(
        {
            'links': {
                'items': [
                    {'url': 'https://elastic.co'},
                ],
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'attributes': {
                'layout': 'horizontal',
                'links': [{'label': '', 'type': 'externalLink', 'id': IsUUID, 'destination': 'https://elastic.co', 'order': 0}],
            },
            'enhancements': {},
        }
    )


def test_compile_links_panel_custom_id() -> None:
    """Test the compilation of a custom ID (note: URL links currently ignore provided IDs)."""
    references, result = compile_links_panel_snapshot(
        {
            'links': {
                'items': [
                    {
                        'url': 'https://elastic.co',
                        'id': '16da766e-c67a-4d2e-9eec-c477af79f374',
                    },
                ],
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'attributes': {
                'layout': 'horizontal',
                'links': [{'label': '', 'type': 'externalLink', 'id': IsUUID, 'destination': 'https://elastic.co', 'order': 0}],
            },
            'enhancements': {},
        }
    )


def test_compile_links_panel_with_label() -> None:
    """Test the compilation of a basic URL link with a label."""
    references, result = compile_links_panel_snapshot(
        {
            'links': {
                'items': [
                    {'url': 'https://elastic.co', 'label': 'Custom Label'},
                ],
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'attributes': {
                'layout': 'horizontal',
                'links': [{'label': 'Custom Label', 'type': 'externalLink', 'id': IsUUID, 'destination': 'https://elastic.co', 'order': 0}],
            },
            'enhancements': {},
        }
    )


def test_compile_links_panel_inverted_options() -> None:
    """Test the compilation of a basic URL link with all options inverted."""
    references, result = compile_links_panel_snapshot(
        {
            'links': {
                'items': [
                    {'url': 'https://elastic.co', 'label': 'Custom Label', 'new_tab': False, 'encode': False},
                ],
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'attributes': {
                'layout': 'horizontal',
                'links': [
                    {
                        'label': 'Custom Label',
                        'type': 'externalLink',
                        'id': IsUUID,
                        'destination': 'https://elastic.co',
                        'order': 0,
                        'options': {'encodeUrl': False, 'openInNewTab': False},
                    }
                ],
            },
            'enhancements': {},
        }
    )


def test_compile_links_panel_dashboard_link() -> None:
    """Test the compilation of a basic Dashboard link."""
    references, result = compile_links_panel_snapshot(
        {
            'id': '74522ed1-eb91-4b8a-bcbe-ffa0ff9c9abf',
            'links': {
                'layout': 'vertical',
                'items': [
                    {
                        'dashboard': '71a1e537-15ed-4891-b102-4ef0f314a037',
                        'label': 'Go to Dashboard',
                        'id': 'f1057dc0-1132-4143-8a58-ccbc853aee46',
                    },
                ],
            },
        }
    )
    assert references == snapshot(
        [{'id': '71a1e537-15ed-4891-b102-4ef0f314a037', 'name': 'link_f1057dc0-1132-4143-8a58-ccbc853aee46_dashboard', 'type': 'dashboard'}]
    )
    assert result == snapshot(
        {
            'attributes': {
                'layout': 'vertical',
                'links': [
                    {
                        'label': 'Go to Dashboard',
                        'type': 'dashboardLink',
                        'id': 'f1057dc0-1132-4143-8a58-ccbc853aee46',
                        'order': 0,
                        'destinationRefName': 'link_f1057dc0-1132-4143-8a58-ccbc853aee46_dashboard',
                    }
                ],
            },
            'enhancements': {},
        }
    )


def test_compile_links_panel_dashboard_link_inverted_options() -> None:
    """Test the compilation of a basic Dashboard link with all options inverted."""
    references, result = compile_links_panel_snapshot(
        {
            'id': '71a1e537-eb91-4b8a-bcbe-ffa0ff9c9abf',
            'links': {
                'layout': 'vertical',
                'items': [
                    {
                        'dashboard': '71a1e537-15ed-4891-b102-4ef0f314a037',
                        'label': 'Go to Dashboard',
                        'id': 'f1057dc0-1132-4143-8a58-ccbc853aee46',
                        'with_time': False,
                        'with_filters': False,
                        'new_tab': True,
                    },
                ],
            },
        }
    )
    assert references == snapshot(
        [{'id': '71a1e537-15ed-4891-b102-4ef0f314a037', 'name': 'link_f1057dc0-1132-4143-8a58-ccbc853aee46_dashboard', 'type': 'dashboard'}]
    )
    assert result == snapshot(
        {
            'attributes': {
                'layout': 'vertical',
                'links': [
                    {
                        'label': 'Go to Dashboard',
                        'type': 'dashboardLink',
                        'id': 'f1057dc0-1132-4143-8a58-ccbc853aee46',
                        'order': 0,
                        'destinationRefName': 'link_f1057dc0-1132-4143-8a58-ccbc853aee46_dashboard',
                        'options': {'openInNewTab': True, 'useCurrentDateRange': False, 'useCurrentFilters': False},
                    }
                ],
            },
            'enhancements': {},
        }
    )


def test_get_link_type_raises_error_for_invalid_dict() -> None:
    """Test that get_link_type raises ValueError for dict without url or dashboard keys."""
    invalid_dict = {'label': 'Test', 'id': '123'}
    with pytest.raises(ValueError, match='Cannot determine link type from dict with keys'):
        _ = get_link_type(invalid_dict)


def test_get_link_type_raises_error_for_invalid_object() -> None:
    """Test that get_link_type raises ValueError for object without url or dashboard attributes."""

    class InvalidLink:
        """Invalid link type for testing."""

        def __init__(self) -> None:
            """Initialize invalid link."""
            self.label: str = 'test'

    invalid_obj = InvalidLink()
    with pytest.raises(ValueError, match='Cannot determine link type from object'):
        _ = get_link_type(invalid_obj)


def test_links_panel_url_link_dashboard_references_bubble_up() -> None:
    """Test that URL link panels have no references at dashboard level.

    URL links don't reference any Kibana saved objects, so the dashboard's references array should be empty.
    """
    dashboard = Dashboard(
        name='Test Links Dashboard',
        panels=[
            {
                'title': 'Test Links',
                'id': 'links-panel-1',
                'grid': {'x': 0, 'y': 0, 'w': 24, 'h': 4},
                'links': {
                    'items': [
                        {'url': 'https://elastic.co', 'label': 'Elastic'},
                    ],
                },
            }
        ],
    )

    kbn_dashboard: KbnDashboard = render(dashboard=dashboard)
    references = [ref.model_dump() for ref in kbn_dashboard.references]

    assert references == snapshot([])


def test_links_panel_dashboard_link_references_bubble_up() -> None:
    """Test that dashboard link references bubble up to dashboard level correctly.

    Dashboard links reference other dashboards, so these references should appear
    at the dashboard's top-level references array with proper panel namespacing.
    """
    dashboard = Dashboard(
        name='Test Dashboard Links',
        panels=[
            {
                'title': 'Navigation Links',
                'id': 'links-panel-1',
                'grid': {'x': 0, 'y': 0, 'w': 24, 'h': 4},
                'links': {
                    'items': [
                        {
                            'dashboard': '71a1e537-15ed-4891-b102-4ef0f314a037',
                            'label': 'Go to Dashboard',
                            'id': 'link-1',
                        },
                    ],
                },
            }
        ],
    )

    kbn_dashboard: KbnDashboard = render(dashboard=dashboard)
    references = [ref.model_dump() for ref in kbn_dashboard.references]

    assert references == snapshot(
        [{'id': '71a1e537-15ed-4891-b102-4ef0f314a037', 'name': 'links-panel-1:link_link-1_dashboard', 'type': 'dashboard'}]
    )


def test_compile_links_panel_dashboard_link_partial_options() -> None:
    """Test dashboard link with partial options defaults to opening in same tab.

    When with_time or with_filters is set but new_tab is not explicitly set,
    the link should open in the same tab (matching Kibana's default behavior).
    """
    references, result = compile_links_panel_snapshot(
        {
            'id': '71a1e537-eb91-4b8a-bcbe-ffa0ff9c9abf',
            'links': {
                'layout': 'vertical',
                'items': [
                    {
                        'dashboard': '71a1e537-15ed-4891-b102-4ef0f314a037',
                        'label': 'Go to Dashboard',
                        'id': 'f1057dc0-1132-4143-8a58-ccbc853aee46',
                        'with_time': True,
                    },
                ],
            },
        }
    )
    assert references == snapshot(
        [{'id': '71a1e537-15ed-4891-b102-4ef0f314a037', 'name': 'link_f1057dc0-1132-4143-8a58-ccbc853aee46_dashboard', 'type': 'dashboard'}]
    )
    assert result == snapshot(
        {
            'attributes': {
                'layout': 'vertical',
                'links': [
                    {
                        'label': 'Go to Dashboard',
                        'type': 'dashboardLink',
                        'id': 'f1057dc0-1132-4143-8a58-ccbc853aee46',
                        'order': 0,
                        'destinationRefName': 'link_f1057dc0-1132-4143-8a58-ccbc853aee46_dashboard',
                        'options': {'openInNewTab': False, 'useCurrentDateRange': True, 'useCurrentFilters': True},
                    }
                ],
            },
            'enhancements': {},
        }
    )


def test_compile_links_panel_url_link_encode_only() -> None:
    """Test URL link with encode option but no new_tab defaults to same tab.

    When encode is set but new_tab is not explicitly set,
    the link should open in the same tab (matching Kibana's default behavior).
    """
    references, result = compile_links_panel_snapshot(
        {
            'links': {
                'items': [
                    {'url': 'https://elastic.co', 'label': 'Custom Label', 'encode': True},
                ],
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'attributes': {
                'layout': 'horizontal',
                'links': [
                    {
                        'label': 'Custom Label',
                        'type': 'externalLink',
                        'id': IsUUID,
                        'destination': 'https://elastic.co',
                        'order': 0,
                        'options': {'encodeUrl': True, 'openInNewTab': False},
                    }
                ],
            },
            'enhancements': {},
        }
    )
