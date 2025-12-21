"""Test the compilation of links panels from config models to view models."""

import re
from typing import Any

import pytest

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
    assert references == []
    assert result['attributes']['layout'] == 'horizontal'
    assert len(result['attributes']['links']) == 1
    link = result['attributes']['links'][0]
    assert link['label'] == ''
    assert link['type'] == 'externalLink'
    assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', link['id'])
    assert link['destination'] == 'https://elastic.co'
    assert link['order'] == 0
    assert result['enhancements'] == {}


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
    assert references == []
    assert result['attributes']['layout'] == 'horizontal'
    assert len(result['attributes']['links']) == 1
    link = result['attributes']['links'][0]
    assert link['label'] == ''
    assert link['type'] == 'externalLink'
    # Note: URL links currently generate new IDs even when one is provided
    assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', link['id'])
    assert link['destination'] == 'https://elastic.co'
    assert link['order'] == 0
    assert result['enhancements'] == {}


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
    assert references == []
    assert result['attributes']['layout'] == 'horizontal'
    assert len(result['attributes']['links']) == 1
    link = result['attributes']['links'][0]
    assert link['label'] == 'Custom Label'
    assert link['type'] == 'externalLink'
    assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', link['id'])
    assert link['destination'] == 'https://elastic.co'
    assert link['order'] == 0
    assert result['enhancements'] == {}


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
    assert references == []
    assert result['attributes']['layout'] == 'horizontal'
    assert len(result['attributes']['links']) == 1
    link = result['attributes']['links'][0]
    assert link['label'] == 'Custom Label'
    assert link['type'] == 'externalLink'
    assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', link['id'])
    assert link['destination'] == 'https://elastic.co'
    assert link['order'] == 0
    assert link['options'] == {'encodeUrl': False, 'openInNewTab': False}
    assert result['enhancements'] == {}


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
    assert len(references) == 1
    assert references[0]['id'] == '71a1e537-15ed-4891-b102-4ef0f314a037'
    assert references[0]['name'] == 'link_f1057dc0-1132-4143-8a58-ccbc853aee46_dashboard'
    assert references[0]['type'] == 'dashboard'

    assert result['attributes']['layout'] == 'vertical'
    assert len(result['attributes']['links']) == 1
    link = result['attributes']['links'][0]
    assert link['label'] == 'Go to Dashboard'
    assert link['type'] == 'dashboardLink'
    assert link['id'] == 'f1057dc0-1132-4143-8a58-ccbc853aee46'
    assert link['order'] == 0
    assert link['destinationRefName'] == 'link_f1057dc0-1132-4143-8a58-ccbc853aee46_dashboard'
    assert result['enhancements'] == {}


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
    assert len(references) == 1
    assert references[0]['id'] == '71a1e537-15ed-4891-b102-4ef0f314a037'
    assert references[0]['name'] == 'link_f1057dc0-1132-4143-8a58-ccbc853aee46_dashboard'
    assert references[0]['type'] == 'dashboard'

    assert result['attributes']['layout'] == 'vertical'
    assert len(result['attributes']['links']) == 1
    link = result['attributes']['links'][0]
    assert link['label'] == 'Go to Dashboard'
    assert link['type'] == 'dashboardLink'
    assert link['id'] == 'f1057dc0-1132-4143-8a58-ccbc853aee46'
    assert link['order'] == 0
    assert link['destinationRefName'] == 'link_f1057dc0-1132-4143-8a58-ccbc853aee46_dashboard'
    assert link['options'] == {'openInNewTab': True, 'useCurrentDateRange': False, 'useCurrentFilters': False}
    assert result['enhancements'] == {}
