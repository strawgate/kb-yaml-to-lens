"""Comprehensive tests for various YAML compilation failure scenarios.

This test suite exercises many different types of errors to ensure we provide
sensible, user-friendly error messages for common mistakes.
"""

from pathlib import Path

from inline_snapshot import snapshot

from dashboard_compiler.cli import compile_yaml_to_json


class TestYamlSyntaxErrors:
    """Test various YAML syntax errors."""

    def test_unclosed_brace(self, tmp_path: Path) -> None:
        """Test error message for unclosed brace."""
        yaml_file = tmp_path / 'unclosed-brace.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      - title: Bad Panel
        size: {w: 24
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error == snapshot(
            "YAML syntax error in unclosed-brace.yaml at line 7, column 1: expected ',' or '}', but got '<stream end>'"
        )

    def test_invalid_indentation(self, tmp_path: Path) -> None:
        """Test error message for invalid indentation."""
        yaml_file = tmp_path / 'invalid-indent.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
   panels: []
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error == snapshot(
            "YAML syntax error in invalid-indent.yaml at line 4, column 4: expected <block end>, but found '<block mapping start>'"
        )


class TestMissingRequiredFields:
    """Test error messages for missing required fields."""

    def test_missing_dashboards_key(self, tmp_path: Path) -> None:
        """Test error when top-level 'dashboards' key is missing."""
        yaml_file = tmp_path / 'no-dashboards.yaml'
        yaml_file.write_text("""
panels:
  - title: Test
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error == snapshot(
            'no-dashboards.yaml: Field is required. Your YAML file must have a "dashboards:" section at the top level.'
        )

    def test_missing_dashboard_name(self, tmp_path: Path) -> None:
        """Test error when dashboard name is missing."""
        yaml_file = tmp_path / 'no-name.yaml'
        yaml_file.write_text("""
dashboards:
  - description: Test dashboard without name
    panels: []
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error == snapshot("""\
1 validation error in no-name.yaml:
  • dashboards[0].name: Field is required. Each dashboard requires a "name" field.\
""")

    def test_missing_panel_title(self, tmp_path: Path) -> None:
        """Test that panel title is optional (has default empty string)."""
        yaml_file = tmp_path / 'no-panel-title.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      - size: {w: 24, h: 12}
        position: {x: 0, y: 0}
        markdown:
          content: Hello
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        # Title is optional with default empty string
        assert error is None
        assert len(json_lines) == 1

    def test_missing_panel_grid(self, tmp_path: Path) -> None:
        """Test that panel grid is optional (has default size and position)."""
        yaml_file = tmp_path / 'no-grid.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      - title: Test Panel
        markdown:
          content: Hello
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        # Grid is optional, will use default size and position
        assert error is None
        assert len(json_lines) == 1

    def test_missing_markdown_content(self, tmp_path: Path) -> None:
        """Test error when markdown content is missing."""
        yaml_file = tmp_path / 'no-markdown-content.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      - title: Test Panel
        size: {w: 24, h: 12}
        position: {x: 0, y: 0}
        markdown: {}
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error == snapshot("""\
1 validation error in no-markdown-content.yaml:
  • dashboards[0].panels[0].markdown.content: Field is required\
""")

    def test_missing_esql_query(self, tmp_path: Path) -> None:
        """Test error when ESQL query is missing."""
        yaml_file = tmp_path / 'no-esql-query.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      - title: Test Panel
        size: {w: 24, h: 12}
        position: {x: 0, y: 0}
        esql:
          type: metric
          primary:
            field: count
            id: count_id
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error == snapshot("""\
1 validation error in no-esql-query.yaml:
  • dashboards[0].panels[0].esql.metric.query: Field is required\
""")


class TestWrongDataTypes:
    """Test error messages for wrong data types."""

    def test_dashboards_not_a_list(self, tmp_path: Path) -> None:
        """Test error when dashboards is not a list."""
        yaml_file = tmp_path / 'dashboards-not-list.yaml'
        yaml_file.write_text("""
dashboards:
  name: Test
  panels: []
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error == snapshot("""\
1 validation error in dashboards-not-list.yaml:
  • dashboards: Expected a list. Your YAML file must have a "dashboards:" section at the top level.\
""")

    def test_panels_not_a_list(self, tmp_path: Path) -> None:
        """Test error when panels is not a list."""
        yaml_file = tmp_path / 'panels-not-list.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      title: Should be a list
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error == snapshot("""\
1 validation error in panels-not-list.yaml:
  • dashboards[0].panels: Expected a list\
""")

    def test_size_not_a_dict(self, tmp_path: Path) -> None:
        """Test error when size is not a dict."""
        yaml_file = tmp_path / 'size-not-dict.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      - title: Test Panel
        size: "24,12"
        markdown:
          content: Hello
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        # Size must be a dict; non-dict values cause validation error
        assert json_lines == []
        assert error is not None
        assert 'size-not-dict.yaml' in error
        assert 'size' in error.lower()

    def test_position_coordinates_wrong_type(self, tmp_path: Path) -> None:
        """Test error when position coordinates are wrong type."""
        yaml_file = tmp_path / 'position-coords-wrong.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      - title: Test Panel
        size: {w: 24, h: 12}
        position: {x: "zero", y: 0}
        markdown:
          content: Hello
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error == snapshot("""\
1 validation error in position-coords-wrong.yaml:
  • dashboards[0].panels[0].markdown.position.x: Expected an integer value\
""")

    def test_unknown_options_field_rejected(self, tmp_path: Path) -> None:
        """Test that unknown fields are rejected by extra='forbid' behavior."""
        yaml_file = tmp_path / 'unknown-field.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    options:
      hide_panel_titles: "yes"
    panels: []
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error == snapshot("""\
1 validation error in unknown-field.yaml:
  • dashboards[0].options: Extra inputs are not permitted\
""")


class TestInvalidValues:
    """Test error messages for invalid values."""

    def test_negative_size_width(self, tmp_path: Path) -> None:
        """Test error when size width is negative."""
        yaml_file = tmp_path / 'negative-width.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      - title: Test Panel
        size: {w: -24, h: 12}
        position: {x: 0, y: 0}
        markdown:
          content: Hello
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error is not None
        assert 'negative-width.yaml' in error
        assert 'Width must be between 1 and 48, got -24' in error

    def test_size_width_too_large(self, tmp_path: Path) -> None:
        """Test error when size width exceeds maximum."""
        yaml_file = tmp_path / 'width-too-large.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      - title: Test Panel
        size: {w: 1000, h: 12}
        position: {x: 0, y: 0}
        markdown:
          content: Hello
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error is not None
        assert 'width-too-large.yaml' in error
        assert 'Width must be between 1 and 48, got 1000' in error

    def test_invalid_chart_type(self, tmp_path: Path) -> None:
        """Test error when chart type is invalid."""
        yaml_file = tmp_path / 'invalid-chart-type.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      - title: Test Panel
        size: {w: 24, h: 12}
        position: {x: 0, y: 0}
        esql:
          type: invalid_type
          query:
            - FROM logs-*
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        # fmt: off
        assert error == snapshot("1 validation error in invalid-chart-type.yaml:\n  • dashboards[0].panels[0].esql: Unknown type 'invalid_type'. Valid types: 'metric', 'gauge', 'heatmap', 'pie', 'line', 'bar', 'area', 'tagcloud', 'datatable', 'mosaic'")  # noqa: E501
        # fmt: on

    def test_empty_esql_query_list(self, tmp_path: Path) -> None:
        """Test that empty ESQL query lists are accepted."""
        yaml_file = tmp_path / 'empty-query.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      - title: Test Panel
        size: {w: 24, h: 12}
        position: {x: 0, y: 0}
        esql:
          type: metric
          primary:
            field: count
            id: count_id
          query: []
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        # Empty query lists are accepted (no minimum length validation)
        assert error is None
        assert len(json_lines) == 1


class TestStructuralIssues:
    """Test error messages for structural issues."""

    def test_overlapping_panels(self, tmp_path: Path) -> None:
        """Test error when panels overlap."""
        yaml_file = tmp_path / 'overlapping.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      - title: Panel 1
        size: {w: 24, h: 12}
        position: {x: 0, y: 0}
        markdown:
          content: First
      - title: Panel 2
        size: {w: 24, h: 12}
        position: {x: 0, y: 0}
        markdown:
          content: Second
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error is not None
        assert 'overlapping.yaml' in error
        assert 'Panel "Panel 1" at (x=0, y=0, w=24, h=12) overlaps with panel "Panel 2" at (x=0, y=0, w=24, h=12)' in error

    def test_panel_outside_grid(self, tmp_path: Path) -> None:
        """Test error when panel x-coordinate is outside valid grid."""
        yaml_file = tmp_path / 'outside-grid.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      - title: Panel Outside
        size: {w: 24, h: 12}
        position: {x: 100, y: 0}
        markdown:
          content: Outside
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error is not None
        assert 'outside-grid.yaml' in error
        assert 'Value must be <= 48' in error


class TestUnionDiscriminatorErrors:
    """Test error messages for union discriminator issues."""

    def test_panel_without_type_discriminator(self, tmp_path: Path) -> None:
        """Test error when panel has no type discriminator."""
        yaml_file = tmp_path / 'no-panel-type.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      - title: Test Panel
        size: {w: 24, h: 12}
        position: {x: 0, y: 0}
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error is not None
        assert 'no-panel-type.yaml' in error
        assert "Cannot determine panel type from dict with keys: ['title', 'size', 'position']" in error
        assert "Each panel must have exactly one type discriminator key: 'markdown', 'search', 'links', 'image', 'lens', or 'esql'" in error

    def test_multiple_panel_types(self, tmp_path: Path) -> None:
        """Test error when panel has multiple type discriminators."""
        yaml_file = tmp_path / 'multiple-types.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      - title: Test Panel
        size: {w: 24, h: 12}
        position: {x: 0, y: 0}
        markdown:
          content: Hello
        esql:
          type: metric
          query:
            - FROM logs-*
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        # Multiple discriminators are rejected (extra='forbid' behavior)
        assert json_lines == []
        assert error == snapshot(
            '1 validation error in multiple-types.yaml:\n  • dashboards[0].panels[0].markdown.esql: Extra inputs are not permitted'
        )


class TestComplexValidationErrors:
    """Test complex validation scenarios."""

    def test_single_required_field_error(self, tmp_path: Path) -> None:
        """Test error message for missing required dashboard name."""
        yaml_file = tmp_path / 'single-error.yaml'
        yaml_file.write_text("""
dashboards:
  - description: Missing name
    panels:
      - size: {w: 24, h: 12}
        position: {x: 0, y: 0}
        markdown:
          content: Hello
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error == snapshot("""\
1 validation error in single-error.yaml:
  • dashboards[0].name: Field is required. Each dashboard requires a "name" field.\
""")

    def test_deeply_nested_structure_compiles(self, tmp_path: Path) -> None:
        """Test that deeply nested structures compile successfully."""
        yaml_file = tmp_path / 'nested-structure.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    panels:
      - title: Chart Panel
        size: {w: 24, h: 12}
        position: {x: 0, y: 0}
        esql:
          type: metric
          primary:
            field: count
            id: count_id
          query:
            - FROM logs-*
            - STATS count = COUNT(*)
          breakdown:
            field: missing_required_field
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        # Deeply nested structures should compile successfully
        assert error is None
        assert len(json_lines) == 1


class TestEmptyOrMinimalFiles:
    """Test error messages for empty or minimal files."""

    def test_completely_empty_file(self, tmp_path: Path) -> None:
        """Test error when file is completely empty."""
        yaml_file = tmp_path / 'empty.yaml'
        yaml_file.write_text('')

        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error == snapshot('empty.yaml: File is empty or invalid. Expected a YAML document with a "dashboards" key.')

    def test_whitespace_only_file(self, tmp_path: Path) -> None:
        """Test error when file contains only whitespace."""
        yaml_file = tmp_path / 'whitespace.yaml'
        yaml_file.write_text('   \n  \n   ')

        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error == snapshot('whitespace.yaml: File is empty or invalid. Expected a YAML document with a "dashboards" key.')

    def test_yaml_comment_only(self, tmp_path: Path) -> None:
        """Test error when file contains only comments."""
        yaml_file = tmp_path / 'comments-only.yaml'
        yaml_file.write_text('# This is just a comment\n# No actual content')

        json_lines, error = compile_yaml_to_json(yaml_file)
        assert json_lines == []
        assert error == snapshot('comments-only.yaml: File is empty or invalid. Expected a YAML document with a "dashboards" key.')


class TestSuccessScenarios:
    """Test that valid scenarios still work correctly."""

    def test_at_symbol_in_string_is_valid(self, tmp_path: Path) -> None:
        """Test that @ symbol in strings is valid YAML."""
        yaml_file = tmp_path / 'at-in-string.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test @invalid
    panels: []
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert error is None
        assert len(json_lines) == 1

    def test_duplicate_keys_uses_last_value(self, tmp_path: Path) -> None:
        """Test that duplicate keys use the last value (PyYAML behavior)."""
        yaml_file = tmp_path / 'duplicate-keys.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Test
    name: Test2
    panels: []
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert error is None
        assert len(json_lines) == 1

    def test_minimal_valid_dashboard(self, tmp_path: Path) -> None:
        """Test that a minimal valid dashboard compiles successfully."""
        yaml_file = tmp_path / 'minimal-valid.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Minimal Dashboard
    panels:
      - title: Simple Panel
        size: {w: 24, h: 12}
        position: {x: 0, y: 0}
        markdown:
          content: Hello World
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert error is None
        assert len(json_lines) == 1

    def test_dashboard_with_multiple_panels(self, tmp_path: Path) -> None:
        """Test that a dashboard with multiple panels compiles successfully."""
        yaml_file = tmp_path / 'multi-panel.yaml'
        yaml_file.write_text("""
dashboards:
  - name: Multi Panel Dashboard
    panels:
      - title: Panel 1
        size: {w: 12, h: 12}
        position: {x: 0, y: 0}
        markdown:
          content: First
      - title: Panel 2
        size: {w: 12, h: 12}
        position: {x: 12, y: 0}
        markdown:
          content: Second
""")
        json_lines, error = compile_yaml_to_json(yaml_file)
        assert error is None
        assert len(json_lines) == 1
