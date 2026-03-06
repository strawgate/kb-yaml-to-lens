"""Tests for collapsible dashboard section compilation."""

import pytest

from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.dashboard_compiler import render
from kb_dashboard_core.shared.config import stable_id_generator
from tests.conftest import de_json_kbn_dashboard


def test_dashboard_sections_compile_with_panel_assignments() -> None:
    """Panels assigned to sections compile to gridData.sectionId and attributes.sections."""
    dashboard = Dashboard(
        name='Sections Dashboard',
        sections=[{'id': 'perf', 'title': 'Performance', 'collapsed': True}],
        panels=[
            {
                'id': 'top',
                'title': 'Top Level',
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 6},
                'markdown': {'content': '# Top'},
            },
            {
                'id': 'inside-perf',
                'title': 'CPU Usage',
                'section': 'perf',
                'position': {'x': 0, 'y': 6},
                'size': {'w': 24, 'h': 6},
                'markdown': {'content': '# CPU'},
            },
        ],
    )

    compiled = de_json_kbn_dashboard(render(dashboard=dashboard).model_dump(by_alias=True))
    attributes = compiled['attributes']

    assert attributes['sections'] == [{'title': 'Performance', 'collapsed': True, 'gridData': {'y': 6, 'i': 'perf'}}]

    panels_by_id = {panel['panelIndex']: panel for panel in attributes['panelsJSON']}
    assert panels_by_id['inside-perf']['gridData']['sectionId'] == 'perf'
    assert 'sectionId' not in panels_by_id['top']['gridData']


def test_section_reference_can_resolve_by_title_with_generated_id() -> None:
    """Panel section references can target a section by title when id is omitted."""
    dashboard = Dashboard(
        name='Sections by Title Dashboard',
        sections=[{'title': 'Latency'}],
        panels=[
            {
                'id': 'latency-panel',
                'title': 'Latency',
                'section': 'Latency',
                'position': {'x': 0, 'y': 7},
                'size': {'w': 24, 'h': 6},
                'markdown': {'content': '# Latency'},
            }
        ],
    )

    compiled = de_json_kbn_dashboard(render(dashboard=dashboard).model_dump(by_alias=True))
    expected_section_id = stable_id_generator(['section', 'Latency'])

    assert compiled['attributes']['sections'] == [
        {'title': 'Latency', 'gridData': {'y': 7, 'i': expected_section_id}}
    ]
    assert compiled['attributes']['panelsJSON'][0]['gridData']['sectionId'] == expected_section_id


def test_unknown_section_reference_raises_error() -> None:
    """Compiling fails when a panel references a non-existent section."""
    dashboard = Dashboard(
        name='Invalid Section Reference',
        sections=[{'id': 'known', 'title': 'Known'}],
        panels=[
            {
                'id': 'panel-1',
                'title': 'Panel',
                'section': 'missing',
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 6},
                'markdown': {'content': '# Missing'},
            }
        ],
    )

    with pytest.raises(ValueError, match='references unknown section'):
        _ = render(dashboard=dashboard)
