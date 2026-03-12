"""Tests for collapsible dashboard section panels."""

from typing import Any

from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.dashboard_compiler import render
from kb_dashboard_core.panels.collapsible import CollapsiblePanel, SectionConfig
from kb_dashboard_core.panels.config import Position, Size
from kb_dashboard_core.panels.markdown import MarkdownPanel
from kb_dashboard_core.panels.markdown.config import MarkdownPanelConfig
from kb_dashboard_core.shared.config import stable_id_generator
from tests.conftest import de_json_kbn_dashboard


def _compile(dashboard: Dashboard) -> dict[str, Any]:
    return de_json_kbn_dashboard(render(dashboard=dashboard).model_dump(by_alias=True))


def _get_attrs(result: dict[str, Any]) -> dict[str, Any]:
    return result['attributes']


def _get_panels(result: dict[str, Any]) -> list[dict[str, Any]]:
    return _get_attrs(result)['panelsJSON']


def _get_sections(result: dict[str, Any]) -> list[dict[str, Any]]:
    return _get_attrs(result)['sections']


class TestBasicSection:
    """Test basic section with explicit positions."""

    def test_section_with_explicit_positions(self) -> None:
        """Verify section panels render correctly with explicit position coordinates."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                MarkdownPanel(
                    title='Top Panel',
                    position=Position(x=0, y=0),
                    size=Size(w=48, h=6),
                    markdown=MarkdownPanelConfig(content='# Top'),
                ),
                CollapsiblePanel(
                    title='My Section',
                    position=Position(x=0, y=6),
                    section=SectionConfig(
                        collapsed=True,
                        panels=[
                            MarkdownPanel(
                                title='Inner Panel',
                                position=Position(x=0, y=0),
                                size=Size(w=48, h=12),
                                markdown=MarkdownPanelConfig(content='# Inner'),
                            ),
                        ],
                    ),
                ),
                MarkdownPanel(
                    title='Bottom Panel',
                    position=Position(x=0, y=7),
                    size=Size(w=48, h=6),
                    markdown=MarkdownPanelConfig(content='# Bottom'),
                ),
            ],
        )

        result = _compile(dashboard)
        panels = _get_panels(result)
        sections = _get_sections(result)

        # Should have 3 panels: top, inner (from section), bottom
        assert len(panels) == 3

        # Top panel has no sectionId
        top_panel = panels[0]
        assert top_panel['gridData']['y'] == 0
        assert 'sectionId' not in top_panel['gridData']

        # Inner panel has sectionId and relative y=0
        inner_panel = panels[1]
        assert inner_panel['gridData']['y'] == 0
        section_id = inner_panel['gridData']['sectionId']
        assert section_id is not None

        # Bottom panel has no sectionId
        bottom_panel = panels[2]
        assert bottom_panel['gridData']['y'] == 7
        assert 'sectionId' not in bottom_panel['gridData']

        # Sections array has exactly one entry
        assert len(sections) == 1
        assert sections[0]['title'] == 'My Section'
        assert sections[0]['gridData']['y'] == 6
        assert sections[0]['gridData']['i'] == section_id


class TestSectionWithAutogrid:
    """Test section with autogrid (no explicit positions)."""

    def test_autogrid_positions(self) -> None:
        """Verify autogrid correctly positions panels around a collapsible section."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                MarkdownPanel(
                    title='Panel 1',
                    size=Size(w=48, h=8),
                    markdown=MarkdownPanelConfig(content='# P1'),
                ),
                CollapsiblePanel(
                    title='Auto Section',
                    section=SectionConfig(
                        panels=[
                            MarkdownPanel(
                                title='Inner Auto',
                                size=Size(w=48, h=12),
                                markdown=MarkdownPanelConfig(content='# Inner'),
                            ),
                        ],
                    ),
                ),
                MarkdownPanel(
                    title='Panel 3',
                    size=Size(w=48, h=8),
                    markdown=MarkdownPanelConfig(content='# P3'),
                ),
            ],
        )

        result = _compile(dashboard)
        panels = _get_panels(result)
        sections = _get_sections(result)

        # Panel 1 at y=0 (autogrid)
        assert panels[0]['gridData']['y'] == 0
        assert 'sectionId' not in panels[0]['gridData']

        # Section header at y=8 (after panel 1 of h=8)
        assert sections[0]['gridData']['y'] == 8

        # Inner panel has relative coords starting at y=0
        inner_panel = panels[1]
        assert inner_panel['gridData']['y'] == 0
        assert inner_panel['gridData']['sectionId'] == sections[0]['gridData']['i']

        # Panel 3 placed after section header row (y=8 + h=1 = 9)
        assert panels[2]['gridData']['y'] == 9
        assert 'sectionId' not in panels[2]['gridData']


class TestSectionMultipleInnerPanels:
    """Test section with multiple inner panels."""

    def test_multiple_inner_panels(self) -> None:
        """Verify multiple inner panels are laid out correctly within a section."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                CollapsiblePanel(
                    title='Big Section',
                    section=SectionConfig(
                        panels=[
                            MarkdownPanel(
                                title='Inner 1',
                                size=Size(w=24, h=8),
                                markdown=MarkdownPanelConfig(content='# I1'),
                            ),
                            MarkdownPanel(
                                title='Inner 2',
                                size=Size(w=24, h=8),
                                markdown=MarkdownPanelConfig(content='# I2'),
                            ),
                            MarkdownPanel(
                                title='Inner 3',
                                size=Size(w=48, h=6),
                                markdown=MarkdownPanelConfig(content='# I3'),
                            ),
                        ],
                    ),
                ),
            ],
        )

        result = _compile(dashboard)
        panels = _get_panels(result)
        sections = _get_sections(result)

        section_id = sections[0]['gridData']['i']

        # All 3 inner panels should have sectionId
        assert len(panels) == 3
        for panel in panels:
            assert panel['gridData']['sectionId'] == section_id

        # Inner autogrid runs independently: first two side by side at y=0, third at y=8
        assert panels[0]['gridData']['y'] == 0
        assert panels[0]['gridData']['x'] == 0
        assert panels[1]['gridData']['y'] == 0
        assert panels[1]['gridData']['x'] == 24
        assert panels[2]['gridData']['y'] == 8
        assert panels[2]['gridData']['x'] == 0


class TestMultipleSections:
    """Test multiple collapsible sections."""

    def test_two_sections(self) -> None:
        """Verify two consecutive collapsible sections have distinct IDs and panels."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                CollapsiblePanel(
                    title='Section A',
                    section=SectionConfig(
                        panels=[
                            MarkdownPanel(
                                title='A Inner',
                                size=Size(w=48, h=8),
                                markdown=MarkdownPanelConfig(content='# A'),
                            ),
                        ],
                    ),
                ),
                CollapsiblePanel(
                    title='Section B',
                    section=SectionConfig(
                        panels=[
                            MarkdownPanel(
                                title='B Inner',
                                size=Size(w=48, h=8),
                                markdown=MarkdownPanelConfig(content='# B'),
                            ),
                        ],
                    ),
                ),
            ],
        )

        result = _compile(dashboard)
        panels = _get_panels(result)
        sections = _get_sections(result)

        # Two sections
        assert len(sections) == 2
        assert sections[0]['title'] == 'Section A'
        assert sections[1]['title'] == 'Section B'

        # Each inner panel has the correct sectionId
        section_a_id = sections[0]['gridData']['i']
        section_b_id = sections[1]['gridData']['i']
        assert section_a_id != section_b_id

        assert panels[0]['gridData']['sectionId'] == section_a_id
        assert panels[1]['gridData']['sectionId'] == section_b_id


class TestCollapsedState:
    """Test collapsed state handling."""

    def test_collapsed_true(self) -> None:
        """Verify collapsed=True is preserved in the rendered output."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                CollapsiblePanel(
                    title='Collapsed Section',
                    section=SectionConfig(
                        collapsed=True,
                        panels=[
                            MarkdownPanel(
                                title='Inner',
                                size=Size(w=48, h=8),
                                markdown=MarkdownPanelConfig(content='# I'),
                            ),
                        ],
                    ),
                ),
            ],
        )

        result = _compile(dashboard)
        sections = _get_sections(result)
        assert sections[0]['collapsed'] is True

    def test_collapsed_false(self) -> None:
        """Verify collapsed=False is present in the serialized output."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                CollapsiblePanel(
                    title='Explicit False Section',
                    section=SectionConfig(
                        collapsed=False,
                        panels=[
                            MarkdownPanel(
                                title='Inner',
                                size=Size(w=48, h=8),
                                markdown=MarkdownPanelConfig(content='# I'),
                            ),
                        ],
                    ),
                ),
            ],
        )

        result = _compile(dashboard)
        sections = _get_sections(result)
        assert 'collapsed' in sections[0]
        assert sections[0]['collapsed'] is False

    def test_collapsed_none_omitted(self) -> None:
        """Verify collapsed key is omitted when not explicitly set."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                CollapsiblePanel(
                    title='Default Section',
                    section=SectionConfig(
                        panels=[
                            MarkdownPanel(
                                title='Inner',
                                size=Size(w=48, h=8),
                                markdown=MarkdownPanelConfig(content='# I'),
                            ),
                        ],
                    ),
                ),
            ],
        )

        result = _compile(dashboard)
        sections = _get_sections(result)
        assert 'collapsed' not in sections[0]


class TestNoSections:
    """Test dashboard without sections."""

    def test_no_sections_key(self) -> None:
        """Verify sections key is absent when dashboard has no collapsible panels."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                MarkdownPanel(
                    title='Regular Panel',
                    size=Size(w=48, h=8),
                    markdown=MarkdownPanelConfig(content='# Regular'),
                ),
            ],
        )

        result = _compile(dashboard)
        attrs = _get_attrs(result)
        assert 'sections' not in attrs


class TestSectionIdGeneration:
    """Test section ID generation."""

    def test_explicit_id(self) -> None:
        """Verify a custom section ID is used when explicitly provided."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                CollapsiblePanel(
                    id='my-custom-section-id',
                    title='Custom ID Section',
                    section=SectionConfig(
                        panels=[
                            MarkdownPanel(
                                title='Inner',
                                size=Size(w=48, h=8),
                                markdown=MarkdownPanelConfig(content='# I'),
                            ),
                        ],
                    ),
                ),
            ],
        )

        result = _compile(dashboard)
        sections = _get_sections(result)
        assert sections[0]['gridData']['i'] == 'my-custom-section-id'

        # Inner panel uses the custom section id
        panels = _get_panels(result)
        assert panels[0]['gridData']['sectionId'] == 'my-custom-section-id'

    def test_auto_generated_id(self) -> None:
        """Verify section ID is auto-generated from the section title."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                CollapsiblePanel(
                    title='Auto ID Section',
                    section=SectionConfig(
                        panels=[
                            MarkdownPanel(
                                title='Inner',
                                size=Size(w=48, h=8),
                                markdown=MarkdownPanelConfig(content='# I'),
                            ),
                        ],
                    ),
                ),
            ],
        )

        result = _compile(dashboard)
        sections = _get_sections(result)
        expected_id = stable_id_generator(['section', 'Auto ID Section'])
        assert sections[0]['gridData']['i'] == expected_id


class TestSectionIdNotOnNonSectionPanels:
    """Test that sectionId is NOT present on non-section panels."""

    def test_no_section_id_on_outer_panels(self) -> None:
        """Verify sectionId is only present on inner panels, not outer ones."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                MarkdownPanel(
                    title='Before',
                    size=Size(w=48, h=6),
                    markdown=MarkdownPanelConfig(content='# Before'),
                ),
                CollapsiblePanel(
                    title='Section',
                    section=SectionConfig(
                        panels=[
                            MarkdownPanel(
                                title='Inner',
                                size=Size(w=48, h=8),
                                markdown=MarkdownPanelConfig(content='# Inner'),
                            ),
                        ],
                    ),
                ),
                MarkdownPanel(
                    title='After',
                    size=Size(w=48, h=6),
                    markdown=MarkdownPanelConfig(content='# After'),
                ),
            ],
        )

        result = _compile(dashboard)
        panels = _get_panels(result)

        # Before panel (index 0) - no sectionId
        assert 'sectionId' not in panels[0]['gridData']

        # Inner panel (index 1) - has sectionId
        assert 'sectionId' in panels[1]['gridData']

        # After panel (index 2) - no sectionId
        assert 'sectionId' not in panels[2]['gridData']


class TestInnerPanelRelativeCoordinates:
    """Test that inner panel Y coordinates are relative to section, not absolute."""

    def test_inner_y_is_relative(self) -> None:
        """Verify inner panel Y coordinates are relative to the section, not absolute."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                MarkdownPanel(
                    title='Top',
                    position=Position(x=0, y=0),
                    size=Size(w=48, h=20),
                    markdown=MarkdownPanelConfig(content='# Top'),
                ),
                CollapsiblePanel(
                    title='Section at Y=20',
                    position=Position(x=0, y=20),
                    section=SectionConfig(
                        panels=[
                            MarkdownPanel(
                                title='Inner First',
                                size=Size(w=48, h=12),
                                markdown=MarkdownPanelConfig(content='# First'),
                            ),
                            MarkdownPanel(
                                title='Inner Second',
                                size=Size(w=48, h=8),
                                markdown=MarkdownPanelConfig(content='# Second'),
                            ),
                        ],
                    ),
                ),
            ],
        )

        result = _compile(dashboard)
        panels = _get_panels(result)
        sections = _get_sections(result)

        # Section header is at y=20 in outer grid
        assert sections[0]['gridData']['y'] == 20

        # Inner panels have relative Y coordinates starting from 0
        inner_panels = [p for p in panels if 'sectionId' in p['gridData']]
        assert len(inner_panels) == 2

        # First inner panel at y=0 (relative)
        assert inner_panels[0]['gridData']['y'] == 0

        # Second inner panel at y=12 (relative, after first panel of h=12)
        assert inner_panels[1]['gridData']['y'] == 12

        # Neither inner panel has the outer grid Y coordinate
        for ip in inner_panels:
            assert ip['gridData']['y'] != 20


class TestEmptySection:
    """Test collapsible panel with an empty panels list."""

    def test_empty_section_panels(self) -> None:
        """Verify a CollapsiblePanel with no inner panels produces a section but no sectionId on panels."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                CollapsiblePanel(
                    title='Empty Section',
                    section=SectionConfig(
                        panels=[],
                    ),
                ),
            ],
        )

        result = _compile(dashboard)
        panels = _get_panels(result)
        sections = _get_sections(result)

        # The sections array should have one entry
        assert len(sections) == 1
        assert sections[0]['title'] == 'Empty Section'

        # No panels should have a sectionId
        for panel in panels:
            assert 'sectionId' not in panel['gridData']

        # The section should have valid gridData with y and i
        assert 'y' in sections[0]['gridData']
        assert 'i' in sections[0]['gridData']


class TestNestedCollapsiblePrevention:
    """Test that nesting CollapsiblePanels inside other CollapsiblePanels is rejected."""

    def test_nested_collapsible_raises(self) -> None:
        """Verify that placing a CollapsiblePanel inside another CollapsiblePanel raises an error."""
        import pytest
        from pydantic import ValidationError

        with pytest.raises((ValidationError, ValueError)):
            Dashboard(
                name='Test Dashboard',
                panels=[
                    CollapsiblePanel(
                        title='Outer Section',
                        section=SectionConfig(
                            panels=[
                                CollapsiblePanel(
                                    title='Inner Section',
                                    section=SectionConfig(
                                        panels=[
                                            MarkdownPanel(
                                                title='Deep Inner',
                                                size=Size(w=48, h=8),
                                                markdown=MarkdownPanelConfig(content='# Deep'),
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
            )


class TestSectionIdCollision:
    """Test behavior when multiple sections could produce the same auto-generated ID."""

    def test_duplicate_titles_produce_same_id(self) -> None:
        """Verify that duplicate section titles produce the same stable ID (known limitation)."""
        id_a = stable_id_generator(['section', 'Same Title'])
        id_b = stable_id_generator(['section', 'Same Title'])
        assert id_a == id_b

    def test_explicit_ids_avoid_collision(self) -> None:
        """Verify that explicit IDs can be used to differentiate sections with the same title."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                CollapsiblePanel(
                    id='section-a',
                    title='Same Title',
                    section=SectionConfig(
                        panels=[
                            MarkdownPanel(
                                title='Inner A',
                                size=Size(w=48, h=8),
                                markdown=MarkdownPanelConfig(content='# A'),
                            ),
                        ],
                    ),
                ),
                CollapsiblePanel(
                    id='section-b',
                    title='Same Title',
                    section=SectionConfig(
                        panels=[
                            MarkdownPanel(
                                title='Inner B',
                                size=Size(w=48, h=8),
                                markdown=MarkdownPanelConfig(content='# B'),
                            ),
                        ],
                    ),
                ),
            ],
        )

        result = _compile(dashboard)
        sections = _get_sections(result)

        assert len(sections) == 2
        assert sections[0]['gridData']['i'] == 'section-a'
        assert sections[1]['gridData']['i'] == 'section-b'
        assert sections[0]['gridData']['i'] != sections[1]['gridData']['i']
