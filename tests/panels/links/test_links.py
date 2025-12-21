"""Test the compilation of links panels from config models to view models."""

import re
from typing import Any

import pytest
from inline_snapshot import snapshot

from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.links.compile import compile_links_panel_config
from dashboard_compiler.panels.links.config import LinksPanel


@pytest.fixture
def compile_links_panel_snapshot():
    """Fixture that returns a function to compile links panels and return dict for snapshot."""

    def _compile(config: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        panel_grid = Grid(x=0, y=0, w=24, h=10)
        links_panel = LinksPanel(grid=panel_grid, **config)
        kbn_references, kbn_panel_config = compile_links_panel_config(links_panel=links_panel)
        kbn_panel_as_dict = kbn_panel_config.model_dump(by_alias=True)
        kbn_references_as_dicts = [ref.model_dump(by_alias=True) for ref in kbn_references]
        return kbn_references_as_dicts, kbn_panel_as_dict

    return _compile


def test_compile_links_panel_basic_url(compile_links_panel_snapshot) -> None:
    """Test the compilation of a basic URL link with no label."""
    references, result = compile_links_panel_snapshot(
        {
            'type': 'links',
            'links': [
                {'url': 'https://elastic.co'},
            ],
        }
    )
    assert references == snapshot([])
    # Note: URL links generate dynamic UUIDs, so we validate the UUID format separately
    link_id = result['attributes']['links'][0]['id']
    assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', link_id)
    result['attributes']['links'][0]['id'] = 'DYNAMIC_UUID'
    assert result == snapshot(
        {
            'attributes': {'layout': 'horizontal', 'links': [{'label': '', 'type': 'externalLink', 'id': 'DYNAMIC_UUID', 'destination': 'https://elastic.co', 'order': 0}]},
            'enhancements': {},
        }
    )


def test_compile_links_panel_custom_id(compile_links_panel_snapshot) -> None:
    """Test the compilation of a custom ID (note: URL links currently ignore provided IDs)."""
    references, result = compile_links_panel_snapshot(
        {
            'type': 'links',
            'links': [
                {
                    'url': 'https://elastic.co',
                    'id': '16da766e-c67a-4d2e-9eec-c477af79f374',
                },
            ],
        }
    )
    assert references == snapshot([])
    # Note: URL links currently generate new IDs even when one is provided
    link_id = result['attributes']['links'][0]['id']
    assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', link_id)
    result['attributes']['links'][0]['id'] = 'DYNAMIC_UUID'
    assert result == snapshot(
        {
            'attributes': {'layout': 'horizontal', 'links': [{'label': '', 'type': 'externalLink', 'id': 'DYNAMIC_UUID', 'destination': 'https://elastic.co', 'order': 0}]},
            'enhancements': {},
        }
    )


def test_compile_links_panel_with_label(compile_links_panel_snapshot) -> None:
    """Test the compilation of a basic URL link with a label."""
    references, result = compile_links_panel_snapshot(
        {
            'type': 'links',
            'links': [
                {'url': 'https://elastic.co', 'label': 'Custom Label'},
            ],
        }
    )
    assert references == snapshot([])
    # Note: URL links generate dynamic UUIDs, so we validate the UUID format separately
    link_id = result['attributes']['links'][0]['id']
    assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', link_id)
    result['attributes']['links'][0]['id'] = 'DYNAMIC_UUID'
    assert result == snapshot(
        {
            'attributes': {'layout': 'horizontal', 'links': [{'label': 'Custom Label', 'type': 'externalLink', 'id': 'DYNAMIC_UUID', 'destination': 'https://elastic.co', 'order': 0}]},
            'enhancements': {},
        }
    )


def test_compile_links_panel_inverted_options(compile_links_panel_snapshot) -> None:
    """Test the compilation of a basic URL link with all options inverted."""
    references, result = compile_links_panel_snapshot(
        {
            'type': 'links',
            'links': [
                {'url': 'https://elastic.co', 'label': 'Custom Label', 'new_tab': False, 'encode': False},
            ],
        }
    )
    assert references == snapshot([])
    # Note: URL links generate dynamic UUIDs, so we validate the UUID format separately
    link_id = result['attributes']['links'][0]['id']
    assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', link_id)
    result['attributes']['links'][0]['id'] = 'DYNAMIC_UUID'
    assert result == snapshot(
        {
            'attributes': {
                'layout': 'horizontal',
                'links': [
                    {
                        'label': 'Custom Label',
                        'type': 'externalLink',
                        'id': 'DYNAMIC_UUID',
                        'destination': 'https://elastic.co',
                        'order': 0,
                        'options': {'encodeUrl': False, 'openInNewTab': False},
                    }
                ],
            },
            'enhancements': {},
        }
    )


def test_compile_links_panel_dashboard_link(compile_links_panel_snapshot) -> None:
    """Test the compilation of a basic Dashboard link."""
    references, result = compile_links_panel_snapshot(
        {
            'type': 'links',
            'id': '74522ed1-eb91-4b8a-bcbe-ffa0ff9c9abf',
            'layout': 'vertical',
            'links': [
                {
                    'dashboard': '71a1e537-15ed-4891-b102-4ef0f314a037',
                    'label': 'Go to Dashboard',
                    'id': 'f1057dc0-1132-4143-8a58-ccbc853aee46',
                },
            ],
        }
    )
    assert references == snapshot([{'id': '71a1e537-15ed-4891-b102-4ef0f314a037', 'name': 'link_f1057dc0-1132-4143-8a58-ccbc853aee46_dashboard', 'type': 'dashboard'}])
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


def test_compile_links_panel_dashboard_link_inverted_options(compile_links_panel_snapshot) -> None:
    """Test the compilation of a basic Dashboard link with all options inverted."""
    references, result = compile_links_panel_snapshot(
        {
            'type': 'links',
            'id': '71a1e537-eb91-4b8a-bcbe-ffa0ff9c9abf',
            'layout': 'vertical',
            'links': [
                {
                    'dashboard': '71a1e537-15ed-4891-b102-4ef0f314a037',
                    'label': 'Go to Dashboard',
                    'id': 'f1057dc0-1132-4143-8a58-ccbc853aee46',
                    'with_time': False,
                    'with_filters': False,
                    'new_tab': True,
                },
            ],
        }
    )
    assert references == snapshot([{'id': '71a1e537-15ed-4891-b102-4ef0f314a037', 'name': 'link_f1057dc0-1132-4143-8a58-ccbc853aee46_dashboard', 'type': 'dashboard'}])
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
