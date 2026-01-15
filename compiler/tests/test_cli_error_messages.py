"""Tests for error message formatting functions."""

from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from pydantic import BaseModel, Field, ValidationError

if TYPE_CHECKING:
    from pydantic_core import ErrorDetails

from dashboard_compiler.shared.error_formatter import (
    CUSTOM_MESSAGES,
    format_error_message,
    format_validation_error,
    format_yaml_error,
    loc_to_path,
)


class TestLocToPath:
    """Tests for loc_to_path function."""

    def test_empty_loc(self) -> None:
        """Test that empty loc returns '<root>'."""
        assert loc_to_path(()) == '<root>'

    def test_simple_field(self) -> None:
        """Test simple field name."""
        assert loc_to_path(('name',)) == 'name'

    def test_nested_field(self) -> None:
        """Test nested field path."""
        assert loc_to_path(('dashboards', 'name')) == 'dashboards.name'

    def test_list_index(self) -> None:
        """Test list index formatting."""
        assert loc_to_path(('dashboards', 0)) == 'dashboards[0]'

    def test_complex_path(self) -> None:
        """Test complex nested path with indices."""
        assert loc_to_path(('dashboards', 0, 'panels', 1, 'grid')) == 'dashboards[0].panels[1].grid'

    def test_multiple_indices(self) -> None:
        """Test path with multiple consecutive indices."""
        assert loc_to_path(('items', 0, 1, 2)) == 'items[0][1][2]'

    def test_duplicate_consecutive_strings(self) -> None:
        """Test that consecutive duplicate string segments are collapsed."""
        assert loc_to_path(('dashboards', 0, 'panels', 0, 'markdown', 'markdown', 'content')) == 'dashboards[0].panels[0].markdown.content'

    def test_non_consecutive_duplicates_preserved(self) -> None:
        """Test that non-consecutive duplicate strings are preserved."""
        assert loc_to_path(('name', 'value', 'name')) == 'name.value.name'


class TestFormatErrorMessage:
    """Tests for format_error_message function."""

    def test_missing_field_uses_custom_message(self) -> None:
        """Test that missing field errors use the custom message."""
        error: ErrorDetails = {'type': 'missing', 'loc': ('name',), 'msg': 'Field required', 'input': None}
        result = format_error_message(error)
        assert result == CUSTOM_MESSAGES['missing']

    def test_value_error_extracts_message_from_ctx(self) -> None:
        """Test that value_error extracts message from context."""
        error: ErrorDetails = {
            'type': 'value_error',
            'loc': ('panels', 0, 'grid'),
            'msg': 'Value error, Panel overlaps',
            'input': None,
            'ctx': {'message': 'Panel "A" overlaps with "B"'},
        }
        result = format_error_message(error)
        assert 'Panel "A" overlaps with "B"' in result

    def test_union_tag_invalid_formats_tags(self) -> None:
        """Test that union_tag_invalid formats expected tags."""
        error: ErrorDetails = {
            'type': 'union_tag_invalid',
            'loc': ('panels', 0, 'esql'),
            'msg': 'Invalid tag',
            'input': None,
            'ctx': {'tag': 'invalid_type', 'expected_tags': "'metric', 'pie', 'bar'"},
        }
        result = format_error_message(error)
        assert 'invalid_type' in result
        assert 'metric' in result
        assert 'pie' in result

    def test_unknown_error_type_uses_original_message(self) -> None:
        """Test that unknown error types use the original message."""
        error: ErrorDetails = {'type': 'some_unknown_type', 'loc': ('field',), 'msg': 'Original message', 'input': None}
        result = format_error_message(error)
        assert result == 'Original message'


class TestFormatValidationError:
    """Tests for format_validation_error function."""

    def test_empty_file_error(self) -> None:
        """Test error message for empty YAML file (None input)."""

        class TestModel(BaseModel):
            dashboards: list[str] = Field(...)

        try:
            TestModel.model_validate(None)
        except ValidationError as e:
            result = format_validation_error(e, Path('config.yaml'))
            assert 'config.yaml' in result
            assert 'empty or invalid' in result.lower()

    def test_missing_dashboards_key_error(self) -> None:
        """Test error message for missing 'dashboards' key."""

        class TestModel(BaseModel):
            dashboards: list[str] = Field(...)

        try:
            TestModel.model_validate({'panels': []})
        except ValidationError as e:
            result = format_validation_error(e, Path('my-dashboard.yaml'))
            assert 'my-dashboard.yaml' in result
            assert 'dashboards' in result.lower()

    def test_single_validation_error(self) -> None:
        """Test formatting of a single validation error."""

        class NestedModel(BaseModel):
            name: str = Field(...)

        class TestModel(BaseModel):
            dashboards: list[NestedModel] = Field(...)

        try:
            TestModel.model_validate({'dashboards': [{'title': 'test'}]})
        except ValidationError as e:
            result = format_validation_error(e, Path('test.yaml'))
            assert '1 validation error' in result
            assert 'test.yaml' in result
            assert 'dashboards[0].name' in result

    def test_multiple_validation_errors(self) -> None:
        """Test formatting of multiple validation errors."""

        class NestedModel(BaseModel):
            name: str = Field(...)
            value: int = Field(...)

        class TestModel(BaseModel):
            dashboards: list[NestedModel] = Field(...)

        try:
            TestModel.model_validate({'dashboards': [{}]})
        except ValidationError as e:
            result = format_validation_error(e, Path('test.yaml'))
            assert '2 validation errors' in result
            assert 'name' in result
            assert 'value' in result

    def test_no_garbage_in_error_message(self) -> None:
        """Test that error messages don't contain pydantic internal metadata."""

        class TestModel(BaseModel):
            dashboards: list[str] = Field(...)

        try:
            TestModel.model_validate({'dashboards': 'not a list'})
        except ValidationError as e:
            result = format_validation_error(e, Path('test.yaml'))
            # Should not contain pydantic internal formatting
            assert 'input_type=' not in result
            assert 'input_value=' not in result

    def test_no_file_path(self) -> None:
        """Test formatting when no file path is provided."""

        class TestModel(BaseModel):
            name: str = Field(...)

        try:
            TestModel.model_validate({})
        except ValidationError as e:
            result = format_validation_error(e)
            assert 'name' in result
            # Should work without file context


class TestFormatYamlError:
    """Tests for format_yaml_error function."""

    def test_yaml_syntax_error_with_position(self) -> None:
        """Test formatting of YAML syntax error with line/column info."""
        invalid_yaml = 'key: {\n  value'
        try:
            yaml.safe_load(invalid_yaml)
        except yaml.YAMLError as e:
            result = format_yaml_error(e, Path('broken.yaml'))
            assert 'YAML syntax error in broken.yaml' in result
            assert 'line' in result
            assert 'column' in result

    def test_yaml_parser_error(self) -> None:
        """Test formatting of YAML parser error."""
        invalid_yaml = 'test: {\n'
        try:
            yaml.safe_load(invalid_yaml)
        except yaml.YAMLError as e:
            result = format_yaml_error(e, Path('invalid.yaml'))
            assert 'YAML syntax error in invalid.yaml' in result

    def test_yaml_scanner_error(self) -> None:
        """Test formatting of YAML scanner error (invalid characters)."""
        invalid_yaml = 'key: @invalid'
        try:
            yaml.safe_load(invalid_yaml)
        except yaml.YAMLError as e:
            result = format_yaml_error(e, Path('scanner-error.yaml'))
            assert 'YAML syntax error in scanner-error.yaml' in result

    def test_yaml_error_without_mark(self) -> None:
        """Test handling of YAML error without position information."""
        error = yaml.YAMLError('Generic error')
        result = format_yaml_error(error, Path('generic.yaml'))
        assert 'YAML syntax error in generic.yaml' in result
        assert 'Generic error' in result

    def test_yaml_error_no_file_path(self) -> None:
        """Test YAML error formatting without file path."""
        error = yaml.YAMLError('Generic error')
        result = format_yaml_error(error)
        assert 'YAML syntax error' in result
        assert 'YAML' in result  # Uses 'YAML' as default context

    def test_yaml_syntax_error_missing_brace(self) -> None:
        """Test formatting of YAML syntax error (missing brace)."""
        invalid_yaml = 'items:\n  - title: "Test"\n    grid: {x: 0\n'
        try:
            yaml.safe_load(invalid_yaml)
        except yaml.YAMLError as e:
            result = format_yaml_error(e, Path('syntax_error.yaml'))
            assert 'YAML syntax error in syntax_error.yaml' in result


class TestCompileYamlToJsonErrorHandling:
    """Integration tests for compile_yaml_to_json error handling."""

    def test_compile_empty_file(self, tmp_path: Path) -> None:
        """Test that empty YAML files produce friendly error messages."""
        from dashboard_compiler.cli import compile_yaml_to_json

        empty_file = tmp_path / 'empty.yaml'
        empty_file.write_text('')

        json_lines, _dashboards, error = compile_yaml_to_json(empty_file)
        assert json_lines == []
        assert error is not None
        assert 'empty.yaml' in error

    def test_compile_invalid_yaml_syntax(self, tmp_path: Path) -> None:
        """Test that YAML syntax errors produce friendly error messages."""
        from dashboard_compiler.cli import compile_yaml_to_json

        invalid_file = tmp_path / 'invalid.yaml'
        invalid_file.write_text('dashboards:\n  - name: Test\n    panels:\n      - title: Bad\n      grid: {x: 0\n')

        json_lines, _dashboards, error = compile_yaml_to_json(invalid_file)
        assert json_lines == []
        assert error is not None
        assert 'YAML syntax error in invalid.yaml' in error
        assert 'line' in error

    def test_compile_missing_dashboards_key(self, tmp_path: Path) -> None:
        """Test that missing 'dashboards' key produces friendly error message."""
        from dashboard_compiler.cli import compile_yaml_to_json

        missing_key_file = tmp_path / 'missing-key.yaml'
        missing_key_file.write_text('panels:\n  - title: Test\n')

        json_lines, _dashboards, error = compile_yaml_to_json(missing_key_file)
        assert json_lines == []
        assert error is not None
        assert 'missing-key.yaml' in error
        assert 'dashboards' in error.lower()

    def test_compile_missing_dashboard_name(self, tmp_path: Path) -> None:
        """Test that missing dashboard name produces friendly error message."""
        from dashboard_compiler.cli import compile_yaml_to_json

        missing_name_file = tmp_path / 'missing-name.yaml'
        missing_name_file.write_text('dashboards:\n  - description: Test\n    panels: []\n')

        json_lines, _dashboards, error = compile_yaml_to_json(missing_name_file)
        assert json_lines == []
        assert error is not None
        assert 'missing-name.yaml' in error
        assert 'name' in error

    def test_compile_file_not_found(self, tmp_path: Path) -> None:
        """Test that file not found produces friendly error message."""
        from dashboard_compiler.cli import compile_yaml_to_json

        nonexistent_file = tmp_path / 'nonexistent.yaml'

        json_lines, _dashboards, error = compile_yaml_to_json(nonexistent_file)
        assert json_lines == []
        assert error is not None
        assert 'not found' in error

    def test_compile_valid_dashboard(self, tmp_path: Path) -> None:
        """Test that valid dashboards compile without errors."""
        from dashboard_compiler.cli import compile_yaml_to_json

        valid_file = tmp_path / 'valid.yaml'
        valid_file.write_text("""---
dashboards:
  - name: Test Dashboard
    panels:
      - title: Test Panel
        size: {w: 24, h: 12}
        position: {x: 0, y: 0}
        markdown:
          content: Hello World
""")

        json_lines, dashboards, error = compile_yaml_to_json(valid_file)
        assert error is None
        assert len(json_lines) == 1
        assert len(dashboards) == 1
