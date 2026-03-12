"""Tests for grid extractor — extracting panel layout info for the VS Code preview."""

import textwrap
from pathlib import Path

import pytest

from dashboard_compiler.lsp.grid_extractor import extract_grid_layout


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_yaml(tmp_path: Path, content: str) -> Path:
    yaml_path = tmp_path / 'dashboard.yaml'
    yaml_path.write_text(textwrap.dedent(content), encoding='utf-8')
    return yaml_path


# ---------------------------------------------------------------------------
# Basic extraction (no sections)
# ---------------------------------------------------------------------------

class TestBasicExtraction:
    """Grid extraction for dashboards without collapsible sections."""

    def test_single_panel(self, tmp_path: Path) -> None:
        yaml_path = _write_yaml(tmp_path, """
            dashboards:
              - name: "Simple"
                panels:
                  - title: "Panel A"
                    size: {w: 48, h: 6}
                    markdown:
                      content: "Hello"
        """)
        result = extract_grid_layout(yaml_path.as_posix())
        assert result.title == "Simple"
        assert len(result.panels) == 1
        p = result.panels[0]
        assert p.title == "Panel A"
        assert p.grid.x == 0
        assert p.grid.y == 0
        assert p.grid.w == 48
        assert p.grid.h == 6
        assert p.type == "markdown"
        assert p.panels == []

    def test_two_panels_auto_layout(self, tmp_path: Path) -> None:
        yaml_path = _write_yaml(tmp_path, """
            dashboards:
              - name: "Two Panels"
                panels:
                  - title: "A"
                    size: {w: 24, h: 4}
                    markdown:
                      content: "A"
                  - title: "B"
                    size: {w: 24, h: 4}
                    markdown:
                      content: "B"
        """)
        result = extract_grid_layout(yaml_path.as_posix())
        assert len(result.panels) == 2
        # Side by side (both fit in 48 columns)
        a, b = result.panels
        assert a.grid.y == 0
        assert b.grid.y == 0
        assert a.grid.x != b.grid.x


# ---------------------------------------------------------------------------
# Sections in layout flow
# ---------------------------------------------------------------------------

class TestSectionLayout:
    """Sections participate in auto-layout with correct Y coordinates."""

    def test_section_gets_auto_position(self, tmp_path: Path) -> None:
        """A section without explicit position gets placed after preceding panels."""
        yaml_path = _write_yaml(tmp_path, """
            dashboards:
              - name: "With Section"
                panels:
                  - title: "Header"
                    size: {w: 48, h: 6}
                    markdown:
                      content: "Top"
                  - title: "Details"
                    section:
                      panels:
                        - title: "Inner"
                          size: {w: 48, h: 8}
                          markdown:
                            content: "Inside"
        """)
        result = extract_grid_layout(yaml_path.as_posix())
        assert len(result.panels) == 2

        header, section = result.panels
        assert header.grid.y == 0
        assert header.grid.h == 6

        # Section positioned after header
        assert section.grid.y == 6
        assert section.grid.h == 1  # Always h=1 in output
        assert section.type == "section"

    def test_panel_after_section_not_overlapping(self, tmp_path: Path) -> None:
        """Panels after a section are placed below the section's full footprint."""
        yaml_path = _write_yaml(tmp_path, """
            dashboards:
              - name: "Section Then Panel"
                panels:
                  - title: "Top"
                    size: {w: 48, h: 4}
                    markdown:
                      content: "Top"
                  - title: "My Section"
                    section:
                      panels:
                        - title: "Inner A"
                          size: {w: 48, h: 10}
                          markdown:
                            content: "A"
                  - title: "Bottom"
                    size: {w: 48, h: 4}
                    markdown:
                      content: "Bottom"
        """)
        result = extract_grid_layout(yaml_path.as_posix())
        assert len(result.panels) == 3

        top, section, bottom = result.panels
        # Top panel: y=0, h=4
        assert top.grid.y == 0
        # Section: y=4, h=1 (but inner content is 10 rows)
        assert section.grid.y == 4
        assert section.grid.h == 1
        # Bottom panel must start after section header (1) + inner content (10) = y >= 15
        assert bottom.grid.y >= section.grid.y + 1 + 10

    def test_multiple_consecutive_sections(self, tmp_path: Path) -> None:
        """Multiple sections in a row each get correct Y positions."""
        yaml_path = _write_yaml(tmp_path, """
            dashboards:
              - name: "Multi Section"
                panels:
                  - title: "Section A"
                    section:
                      panels:
                        - title: "Inner A"
                          size: {w: 48, h: 6}
                          markdown:
                            content: "A"
                  - title: "Section B"
                    section:
                      panels:
                        - title: "Inner B"
                          size: {w: 48, h: 8}
                          markdown:
                            content: "B"
        """)
        result = extract_grid_layout(yaml_path.as_posix())
        assert len(result.panels) == 2

        sec_a, sec_b = result.panels
        assert sec_a.grid.y == 0
        assert sec_a.grid.h == 1
        # Section B starts after Section A header (1) + inner content (6) = 7
        assert sec_b.grid.y >= sec_a.grid.y + 1 + 6


# ---------------------------------------------------------------------------
# Section inner panels
# ---------------------------------------------------------------------------

class TestSectionInnerPanels:
    """Inner panels use relative coordinates within the section."""

    def test_inner_panels_have_relative_coordinates(self, tmp_path: Path) -> None:
        """Inner panel Y coordinates start at 0, not at the section's outer Y."""
        yaml_path = _write_yaml(tmp_path, """
            dashboards:
              - name: "Inner Coords"
                panels:
                  - title: "Spacer"
                    size: {w: 48, h: 20}
                    markdown:
                      content: "Spacer"
                  - title: "My Section"
                    section:
                      panels:
                        - title: "Inner"
                          size: {w: 48, h: 8}
                          markdown:
                            content: "Inside"
        """)
        result = extract_grid_layout(yaml_path.as_posix())
        section = result.panels[1]
        assert section.grid.y == 20  # After the spacer

        # Inner panel coordinates are relative to section body
        assert len(section.panels) == 1
        inner = section.panels[0]
        assert inner.grid.y == 0  # Relative, not absolute
        assert inner.grid.x == 0

    def test_multiple_inner_panels_auto_layout(self, tmp_path: Path) -> None:
        """Inner panels get auto-laid out within the section's coordinate space."""
        yaml_path = _write_yaml(tmp_path, """
            dashboards:
              - name: "Multi Inner"
                panels:
                  - title: "Section"
                    section:
                      panels:
                        - title: "Left"
                          size: {w: 16, h: 8}
                          markdown:
                            content: "L"
                        - title: "Middle"
                          size: {w: 16, h: 8}
                          markdown:
                            content: "M"
                        - title: "Right"
                          size: {w: 16, h: 8}
                          markdown:
                            content: "R"
        """)
        result = extract_grid_layout(yaml_path.as_posix())
        section = result.panels[0]
        assert len(section.panels) == 3

        # All three fit in one row (16*3 = 48)
        for inner in section.panels:
            assert inner.grid.y == 0
            assert inner.grid.w == 16
        # Different x positions
        xs = [p.grid.x for p in section.panels]
        assert len(set(xs)) == 3

    def test_inner_panels_with_explicit_positions(self, tmp_path: Path) -> None:
        """Inner panels with explicit positions are marked as pinned."""
        yaml_path = _write_yaml(tmp_path, """
            dashboards:
              - name: "Pinned Inner"
                panels:
                  - title: "Section"
                    section:
                      panels:
                        - title: "Pinned"
                          size: {w: 24, h: 8}
                          position: {x: 10, y: 5}
                          markdown:
                            content: "P"
        """)
        result = extract_grid_layout(yaml_path.as_posix())
        section = result.panels[0]
        inner = section.panels[0]
        assert inner.grid.x == 10
        assert inner.grid.y == 5
        assert inner.is_pinned is True


# ---------------------------------------------------------------------------
# Empty sections
# ---------------------------------------------------------------------------

class TestEmptySection:
    """Empty sections have no inner panels and minimal footprint."""

    def test_empty_section(self, tmp_path: Path) -> None:
        yaml_path = _write_yaml(tmp_path, """
            dashboards:
              - name: "Empty Section"
                panels:
                  - title: "Empty"
                    section:
                      panels: []
                  - title: "After"
                    size: {w: 48, h: 4}
                    markdown:
                      content: "After"
        """)
        result = extract_grid_layout(yaml_path.as_posix())
        assert len(result.panels) == 2

        section, after = result.panels
        assert section.grid.h == 1
        assert section.panels == []
        # Panel after empty section starts right after it (section footprint = 1)
        assert after.grid.y == 1

    def test_section_without_panels_key(self, tmp_path: Path) -> None:
        yaml_path = _write_yaml(tmp_path, """
            dashboards:
              - name: "No Panels Key"
                panels:
                  - title: "Bare Section"
                    section:
                      collapsed: true
        """)
        result = extract_grid_layout(yaml_path.as_posix())
        assert len(result.panels) == 1
        assert result.panels[0].type == "section"
        assert result.panels[0].panels == []


# ---------------------------------------------------------------------------
# Section metadata
# ---------------------------------------------------------------------------

class TestSectionMetadata:
    """Section grid info has correct IDs, titles, and types."""

    def test_section_type_is_section(self, tmp_path: Path) -> None:
        yaml_path = _write_yaml(tmp_path, """
            dashboards:
              - name: "Type Check"
                panels:
                  - title: "My Section"
                    section:
                      panels: []
        """)
        result = extract_grid_layout(yaml_path.as_posix())
        assert result.panels[0].type == "section"

    def test_section_with_explicit_id(self, tmp_path: Path) -> None:
        yaml_path = _write_yaml(tmp_path, """
            dashboards:
              - name: "ID Check"
                panels:
                  - id: "custom-section-id"
                    title: "My Section"
                    section:
                      panels: []
        """)
        result = extract_grid_layout(yaml_path.as_posix())
        assert result.panels[0].id == "custom-section-id"

    def test_section_auto_id(self, tmp_path: Path) -> None:
        yaml_path = _write_yaml(tmp_path, """
            dashboards:
              - name: "Auto ID"
                panels:
                  - title: "Health Metrics"
                    section:
                      panels: []
        """)
        result = extract_grid_layout(yaml_path.as_posix())
        assert result.panels[0].id == "section_Health Metrics"

    def test_section_width_is_full(self, tmp_path: Path) -> None:
        yaml_path = _write_yaml(tmp_path, """
            dashboards:
              - name: "Width Check"
                panels:
                  - title: "Section"
                    section:
                      panels: []
        """)
        result = extract_grid_layout(yaml_path.as_posix())
        assert result.panels[0].grid.w == 48


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

class TestErrorCases:
    """Edge cases and error handling."""

    def test_no_dashboards_raises(self, tmp_path: Path) -> None:
        yaml_path = _write_yaml(tmp_path, """
            dashboards: []
        """)
        with pytest.raises(ValueError, match="No dashboards found"):
            extract_grid_layout(yaml_path.as_posix())

    def test_invalid_index_raises(self, tmp_path: Path) -> None:
        yaml_path = _write_yaml(tmp_path, """
            dashboards:
              - name: "Only One"
                panels:
                  - title: "P"
                    size: {w: 48, h: 4}
                    markdown:
                      content: "X"
        """)
        with pytest.raises(ValueError, match="out of range"):
            extract_grid_layout(yaml_path.as_posix(), dashboard_index=5)
