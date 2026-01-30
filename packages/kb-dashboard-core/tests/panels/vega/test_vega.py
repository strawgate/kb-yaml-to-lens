"""Test the compilation of vega panels from config models to view models."""

from typing import TYPE_CHECKING, Any

import pytest
from inline_snapshot import snapshot

from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.dashboard_compiler import render
from kb_dashboard_core.panels.vega.compile import compile_vega_panel_config
from kb_dashboard_core.panels.vega.config import VegaPanel

if TYPE_CHECKING:
    from kb_dashboard_core.dashboard.view import KbnDashboard


def compile_vega_panel_snapshot(config: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compile vega panel config and return dict for snapshot testing."""
    vega_panel = VegaPanel(size={'w': 24, 'h': 15}, position={'x': 0, 'y': 0}, **config)
    kbn_references, kbn_panel_config = compile_vega_panel_config(vega_panel=vega_panel)
    kbn_panel_as_dict = kbn_panel_config.model_dump(by_alias=True)
    kbn_references_as_dicts = [ref.model_dump(by_alias=True) for ref in kbn_references]
    return kbn_references_as_dicts, kbn_panel_as_dict


def test_compile_vega_panel_basic() -> None:
    """Test the compilation of a basic vega panel."""
    references, result = compile_vega_panel_snapshot(
        {
            'vega': {
                'spec': {
                    '$schema': 'https://vega.github.io/schema/vega/v3.json',
                    'width': 100,
                    'height': 30,
                    'marks': [
                        {
                            'type': 'text',
                            'encode': {
                                'update': {
                                    'text': {'value': 'Hello Vega!'},
                                },
                            },
                        },
                    ],
                },
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'enhancements': {'dynamicActions': {'events': []}},
            'savedVis': {
                'id': '',
                'title': '',
                'description': '',
                'type': 'vega',
                'params': {
                    'spec': (
                        '{"$schema": "https://vega.github.io/schema/vega/v3.json", '
                        '"width": 100, "height": 30, '
                        '"marks": [{"type": "text", "encode": {"update": {"text": {"value": "Hello Vega!"}}}}]}'
                    )
                },
                'uiState': {},
                'data': {'aggs': [], 'searchSource': {'query': {'query': '', 'language': 'kuery'}, 'filter': []}},
            },
        }
    )


def test_compile_vega_panel_with_title_and_description() -> None:
    """Test the compilation of a vega panel with title and description."""
    references, result = compile_vega_panel_snapshot(
        {
            'title': 'My Vega Chart',
            'description': 'A custom vega visualization',
            'vega': {
                'spec': {
                    '$schema': 'https://vega.github.io/schema/vega-lite/v5.json',
                    'mark': 'bar',
                    'data': {'values': []},
                },
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'enhancements': {'dynamicActions': {'events': []}},
            'savedVis': {
                'id': '',
                'title': 'My Vega Chart',
                'description': 'A custom vega visualization',
                'type': 'vega',
                'params': {'spec': '{"$schema": "https://vega.github.io/schema/vega-lite/v5.json", "mark": "bar", "data": {"values": []}}'},
                'uiState': {},
                'data': {'aggs': [], 'searchSource': {'query': {'query': '', 'language': 'kuery'}, 'filter': []}},
            },
        }
    )


def test_compile_vega_panel_with_hidden_title() -> None:
    """Test the compilation of a vega panel with hidden title."""
    references, result = compile_vega_panel_snapshot(
        {
            'title': 'Hidden Title',
            'hide_title': True,
            'vega': {
                'spec': {
                    '$schema': 'https://vega.github.io/schema/vega/v3.json',
                },
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'enhancements': {'dynamicActions': {'events': []}},
            'hidePanelTitles': True,
            'savedVis': {
                'id': '',
                'title': 'Hidden Title',
                'description': '',
                'type': 'vega',
                'params': {'spec': '{"$schema": "https://vega.github.io/schema/vega/v3.json"}'},
                'uiState': {},
                'data': {'aggs': [], 'searchSource': {'query': {'query': '', 'language': 'kuery'}, 'filter': []}},
            },
        }
    )


def test_vega_panel_spec_rejects_string() -> None:
    """Test that vega panel spec rejects string input."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match='Input should be a valid dictionary'):
        VegaPanel(
            size={'w': 24, 'h': 15},
            position={'x': 0, 'y': 0},
            vega={'spec': '{"$schema": "https://vega.github.io/schema/vega/v3.json"}'},
        )


def test_vega_panel_dashboard_references_bubble_up() -> None:
    """Test that vega panel references bubble up to dashboard level correctly.

    Vega panels have no external references, so the dashboard's references array should be empty.
    """
    dashboard = Dashboard(
        name='Test Vega Dashboard',
        panels=[
            {
                'title': 'Test Vega',
                'id': 'vega-panel-1',
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 15},
                'vega': {
                    'spec': {
                        '$schema': 'https://vega.github.io/schema/vega/v3.json',
                        'width': 100,
                        'height': 30,
                    },
                },
            }
        ],
    )

    kbn_dashboard: KbnDashboard = render(dashboard=dashboard)
    references = [ref.model_dump() for ref in kbn_dashboard.references]

    assert references == snapshot([])
