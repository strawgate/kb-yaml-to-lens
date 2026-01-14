"""Test the compilation of collapsible sections from config models to view models."""

import json
from typing import TYPE_CHECKING

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.sections.compile import compile_section
from dashboard_compiler.sections.config import Section

if TYPE_CHECKING:
    from dashboard_compiler.dashboard.view import KbnDashboard


def test_compile_section_basic() -> None:
    """Test the compilation of a basic section."""
    section = Section(
        title='System Metrics',
    )
    kbn_section = compile_section(section, section_y=0)
    result = kbn_section.model_dump(by_alias=True)

    assert result['title'] == 'System Metrics'
    assert result['gridData'] == {'y': 0}
    assert 'uid' in result  # UID is generated
    assert 'collapsed' not in result  # Not collapsed by default


def test_compile_section_collapsed() -> None:
    """Test the compilation of a collapsed section."""
    section = Section(
        title='Advanced Options',
        collapsed=True,
    )
    kbn_section = compile_section(section, section_y=10)
    result = kbn_section.model_dump(by_alias=True)

    assert result['title'] == 'Advanced Options'
    assert result['collapsed'] is True
    assert result['gridData'] == {'y': 10}
    assert 'uid' in result


def test_compile_section_with_custom_id() -> None:
    """Test the compilation of a section with a custom ID."""
    section = Section(
        id='custom-section-id',
        title='Custom Section',
    )
    kbn_section = compile_section(section, section_y=5)
    result = kbn_section.model_dump(by_alias=True)

    assert result['uid'] == 'custom-section-id'
    assert result['title'] == 'Custom Section'
    assert result['gridData'] == {'y': 5}


def test_section_dashboard_integration() -> None:
    """Test that sections integrate correctly with dashboard compilation."""
    dashboard = Dashboard(
        name='Dashboard with Sections',
        sections=[
            {
                'title': 'System Metrics',
                'collapsed': False,
                'panels': [
                    {
                        'title': 'CPU Overview',
                        'size': {'w': 24, 'h': 10},
                        'position': {'x': 0, 'y': 0},
                        'markdown': {'content': 'CPU metrics here'},
                    },
                ],
            },
            {
                'title': 'Network Metrics',
                'collapsed': True,
                'panels': [
                    {
                        'title': 'Network Traffic',
                        'size': {'w': 24, 'h': 10},
                        'position': {'x': 0, 'y': 0},
                        'markdown': {'content': 'Network metrics here'},
                    },
                ],
            },
        ],
    )

    kbn_dashboard: KbnDashboard = render(dashboard=dashboard)

    # Check sections are present
    assert kbn_dashboard.attributes.sections is not None
    assert len(kbn_dashboard.attributes.sections) == 2

    # Check section properties
    sections = kbn_dashboard.attributes.sections
    assert sections[0].title == 'System Metrics'
    assert sections[0].gridData.y == 0
    assert sections[1].title == 'Network Metrics'
    assert sections[1].collapsed is True
    assert sections[1].gridData.y == 11  # After first section's panel (0 + 10 + 1)


def test_section_panels_have_section_id() -> None:
    """Test that panels within sections have the sectionId in their gridData."""
    dashboard = Dashboard(
        name='Dashboard with Section Panels',
        sections=[
            {
                'title': 'Test Section',
                'panels': [
                    {
                        'title': 'Panel in Section',
                        'size': {'w': 24, 'h': 10},
                        'position': {'x': 0, 'y': 0},
                        'markdown': {'content': 'Content'},
                    },
                ],
            },
        ],
    )

    kbn_dashboard: KbnDashboard = render(dashboard=dashboard)

    # Get the panelsJSON as a list of dicts
    panels_json_str = kbn_dashboard.attributes.model_dump(by_alias=True)['panelsJSON']
    panels = json.loads(panels_json_str)

    assert len(panels) == 1
    # Panel should have sectionId in gridData
    assert 'sectionId' in panels[0]['gridData']


def test_dashboard_without_sections_has_no_sections_field() -> None:
    """Test that dashboards without sections don't include the sections field."""
    dashboard = Dashboard(
        name='Dashboard without Sections',
        panels=[
            {
                'title': 'Global Panel',
                'size': {'w': 24, 'h': 10},
                'position': {'x': 0, 'y': 0},
                'markdown': {'content': 'Content'},
            },
        ],
    )

    kbn_dashboard: KbnDashboard = render(dashboard=dashboard)

    # sections should be None (not serialized)
    assert kbn_dashboard.attributes.sections is None

    # When serialized, 'sections' should not appear
    attrs_dict = kbn_dashboard.attributes.model_dump(by_alias=True)
    assert 'sections' not in attrs_dict


def test_section_with_explicit_y_position() -> None:
    """Test that sections respect explicit y positions."""
    dashboard = Dashboard(
        name='Dashboard with Positioned Sections',
        sections=[
            {
                'title': 'Top Section',
                'y': 0,
                'panels': [
                    {
                        'title': 'Panel A',
                        'size': {'w': 24, 'h': 10},
                        'position': {'x': 0, 'y': 0},
                        'markdown': {'content': 'A'},
                    },
                ],
            },
            {
                'title': 'Bottom Section',
                'y': 50,
                'panels': [
                    {
                        'title': 'Panel B',
                        'size': {'w': 24, 'h': 10},
                        'position': {'x': 0, 'y': 0},
                        'markdown': {'content': 'B'},
                    },
                ],
            },
        ],
    )

    kbn_dashboard: KbnDashboard = render(dashboard=dashboard)

    assert kbn_dashboard.attributes.sections is not None
    sections = kbn_dashboard.attributes.sections

    assert sections[0].gridData.y == 0
    assert sections[1].gridData.y == 50
