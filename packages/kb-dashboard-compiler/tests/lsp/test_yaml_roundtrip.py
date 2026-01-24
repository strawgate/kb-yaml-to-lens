"""Tests for round-trip YAML preservation."""

import textwrap
from pathlib import Path

from dashboard_compiler.lsp import grid_updater


def test_roundtrip_preserves_end_of_line_comments(tmp_path: Path) -> None:
    """Verify end-of-line comments are preserved after grid update."""
    content = textwrap.dedent("""\
        dashboards:
          - name: "Test Dashboard"  # Dashboard name comment
            panels:
              - id: "panel-a"
                title: "Markdown A"  # Title comment
                size: {w: 10, h: 5}  # Size comment
                position: {x: 0, y: 0}  # Position comment
                markdown:
                  content: "Hello"
        """)
    yaml_path = tmp_path / 'dashboard.yaml'
    yaml_path.write_text(content, encoding='utf-8')

    result = grid_updater.update_panel_grid(yaml_path.as_posix(), 'panel-a', {'x': 2, 'y': 3, 'w': 12, 'h': 6})
    assert result['success'] is True

    updated_content = yaml_path.read_text(encoding='utf-8')
    assert '# Dashboard name comment' in updated_content
    assert '# Title comment' in updated_content
    assert '# Size comment' in updated_content
    assert '# Position comment' in updated_content


def test_roundtrip_preserves_block_comments(tmp_path: Path) -> None:
    """Verify block comments above properties are preserved."""
    content = textwrap.dedent("""\
        dashboards:
          # This is the main dashboard
          - name: "Test Dashboard"
            # Panels section contains all visualization panels
            panels:
              # First panel - displays welcome message
              - id: "panel-a"
                title: "Markdown A"
                size: {w: 10, h: 5}
                position: {x: 0, y: 0}
                markdown:
                  content: "Hello"
        """)
    yaml_path = tmp_path / 'dashboard.yaml'
    yaml_path.write_text(content, encoding='utf-8')

    result = grid_updater.update_panel_grid(yaml_path.as_posix(), 'panel-a', {'x': 5, 'y': 10, 'w': 20, 'h': 15})
    assert result['success'] is True

    updated_content = yaml_path.read_text(encoding='utf-8')
    assert '# This is the main dashboard' in updated_content
    assert '# Panels section contains all visualization panels' in updated_content
    assert '# First panel - displays welcome message' in updated_content


def test_roundtrip_preserves_inline_flow_style(tmp_path: Path) -> None:
    """Verify inline flow style is preserved for size and position."""
    content = textwrap.dedent("""\
        dashboards:
          - name: "Test Dashboard"
            panels:
              - id: "panel-a"
                title: "Markdown A"
                size: {w: 10, h: 5}
                position: {x: 0, y: 0}
                markdown:
                  content: "Hello"
        """)
    yaml_path = tmp_path / 'dashboard.yaml'
    yaml_path.write_text(content, encoding='utf-8')

    result = grid_updater.update_panel_grid(yaml_path.as_posix(), 'panel-a', {'x': 1, 'y': 2, 'w': 8, 'h': 4})
    assert result['success'] is True

    updated_content = yaml_path.read_text(encoding='utf-8')
    assert 'size: {w: 8, h: 4}' in updated_content
    assert 'position: {x: 1, y: 2}' in updated_content


def test_roundtrip_preserves_blank_lines(tmp_path: Path) -> None:
    """Verify blank lines between sections are preserved."""
    content = textwrap.dedent("""\
        dashboards:

          - name: "Test Dashboard"

            panels:

              - id: "panel-a"
                title: "Markdown A"
                size: {w: 10, h: 5}
                position: {x: 0, y: 0}
                markdown:
                  content: "Hello"

              - id: "panel-b"
                title: "Markdown B"
                size: {w: 10, h: 5}
                position: {x: 10, y: 0}
                markdown:
                  content: "World"
        """)
    yaml_path = tmp_path / 'dashboard.yaml'
    yaml_path.write_text(content, encoding='utf-8')

    result = grid_updater.update_panel_grid(yaml_path.as_posix(), 'panel-a', {'x': 0, 'y': 0, 'w': 5, 'h': 3})
    assert result['success'] is True

    updated_content = yaml_path.read_text(encoding='utf-8')
    assert '\n\n' in updated_content


def test_roundtrip_preserves_key_ordering(tmp_path: Path) -> None:
    """Verify key ordering within panels is preserved."""
    content = textwrap.dedent("""\
        dashboards:
          - name: "Test Dashboard"
            panels:
              - id: "panel-a"
                title: "Markdown A"
                size: {w: 10, h: 5}
                position: {x: 0, y: 0}
                markdown:
                  content: "Hello"
        """)
    yaml_path = tmp_path / 'dashboard.yaml'
    yaml_path.write_text(content, encoding='utf-8')

    result = grid_updater.update_panel_grid(yaml_path.as_posix(), 'panel-a', {'x': 3, 'y': 4, 'w': 15, 'h': 10})
    assert result['success'] is True

    updated_content = yaml_path.read_text(encoding='utf-8')
    id_pos = updated_content.find('id:')
    title_pos = updated_content.find('title:')
    size_pos = updated_content.find('size:')
    position_pos = updated_content.find('position:')
    markdown_pos = updated_content.find('markdown:')

    assert id_pos < title_pos < size_pos < position_pos < markdown_pos


def test_roundtrip_with_anchors_and_aliases(tmp_path: Path) -> None:
    """Verify YAML anchors and aliases are preserved."""
    content = textwrap.dedent("""\
        defaults: &default_size
          w: 10
          h: 5

        dashboards:
          - name: "Test Dashboard"
            panels:
              - id: "panel-a"
                title: "Markdown A"
                size: *default_size
                position: {x: 0, y: 0}
                markdown:
                  content: "Hello"
              - id: "panel-b"
                title: "Markdown B"
                size: {w: 20, h: 10}
                position: {x: 10, y: 0}
                markdown:
                  content: "World"
        """)
    yaml_path = tmp_path / 'dashboard.yaml'
    yaml_path.write_text(content, encoding='utf-8')

    grid_updater.update_panel_grid(yaml_path.as_posix(), 'panel-b', {'x': 5, 'y': 5, 'w': 25, 'h': 12})

    updated_content = yaml_path.read_text(encoding='utf-8')
    assert '&default_size' in updated_content
    assert '*default_size' in updated_content


def test_updating_aliased_panel_does_not_modify_anchor(tmp_path: Path) -> None:
    """Verify updating a panel with aliased size does not modify the anchor."""
    content = textwrap.dedent("""\
        defaults: &default_size
          w: 10
          h: 5

        dashboards:
          - name: "Test Dashboard"
            panels:
              - id: "panel-a"
                title: "Markdown A"
                size: *default_size
                position: {x: 0, y: 0}
                markdown:
                  content: "Hello"
              - id: "panel-b"
                title: "Markdown B"
                size: *default_size
                position: {x: 10, y: 0}
                markdown:
                  content: "World"
        """)
    yaml_path = tmp_path / 'dashboard.yaml'
    yaml_path.write_text(content, encoding='utf-8')

    result = grid_updater.update_panel_grid(yaml_path.as_posix(), 'panel-a', {'x': 5, 'y': 5, 'w': 20, 'h': 15})
    assert result['success'] is True

    updated_content = yaml_path.read_text(encoding='utf-8')
    assert '&default_size' in updated_content
    assert 'w: 10' in updated_content
    assert 'h: 5' in updated_content
    assert 'w: 20' in updated_content
    assert 'h: 15' in updated_content


def test_roundtrip_multi_dashboard_file(tmp_path: Path) -> None:
    """Verify updating specific dashboard in multi-dashboard file."""
    content = textwrap.dedent("""\
        dashboards:
          # First dashboard
          - name: "Dashboard One"
            panels:
              - id: "d1-panel"
                title: "D1 Panel"
                size: {w: 10, h: 5}
                position: {x: 0, y: 0}
                markdown:
                  content: "First"

          # Second dashboard
          - name: "Dashboard Two"
            panels:
              - id: "d2-panel"
                title: "D2 Panel"
                size: {w: 15, h: 8}
                position: {x: 5, y: 5}
                markdown:
                  content: "Second"
        """)
    yaml_path = tmp_path / 'dashboard.yaml'
    yaml_path.write_text(content, encoding='utf-8')

    result = grid_updater.update_panel_grid(yaml_path.as_posix(), 'd2-panel', {'x': 10, 'y': 10, 'w': 20, 'h': 12}, dashboard_index=1)
    assert result['success'] is True

    updated_content = yaml_path.read_text(encoding='utf-8')
    assert '# First dashboard' in updated_content
    assert '# Second dashboard' in updated_content
    assert 'x: 10' in updated_content
    assert 'y: 10' in updated_content
