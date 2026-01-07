"""Tests for CLI error message formatting functions."""

from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

from dashboard_compiler.cli import _format_validation_error, _format_yaml_error


class TestFormatValidationError:
    """Tests for _format_validation_error function."""

    def test_empty_file_error(self) -> None:
        """Test error message for empty YAML file (None input)."""

        class TestModel(BaseModel):
            dashboards: list[str] = Field(...)

        try:
            TestModel.model_validate(None)
        except ValidationError as e:
            result = _format_validation_error(e, Path('config.yaml'))
            assert 'config.yaml' in result
            assert 'empty or does not contain valid YAML' in result
            assert 'dashboards' in result

    def test_missing_dashboards_key_error(self) -> None:
        """Test error message for missing 'dashboards' key."""

        class TestModel(BaseModel):
            dashboards: list[str] = Field(...)

        try:
            TestModel.model_validate({'panels': []})
        except ValidationError as e:
            result = _format_validation_error(e, Path('my-dashboard.yaml'))
            assert 'my-dashboard.yaml' in result
            assert 'Missing required "dashboards" key' in result
            assert 'dashboards:' in result

    def test_single_validation_error(self) -> None:
        """Test formatting of a single validation error."""

        class NestedModel(BaseModel):
            name: str = Field(...)

        class TestModel(BaseModel):
            dashboards: list[NestedModel] = Field(...)

        try:
            TestModel.model_validate({'dashboards': [{'title': 'test'}]})
        except ValidationError as e:
            result = _format_validation_error(e, Path('test.yaml'))
            assert '1 validation error in test.yaml:' in result
            assert 'dashboards.0.name' in result
            assert 'Field required' in result

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
            result = _format_validation_error(e, Path('test.yaml'))
            assert '2 validation errors in test.yaml:' in result
            assert 'name' in result
            assert 'value' in result

    def test_no_garbage_in_error_message(self) -> None:
        """Test that error messages don't contain pydantic internal metadata."""

        class TestModel(BaseModel):
            dashboards: list[str] = Field(...)

        try:
            TestModel.model_validate({'dashboards': 'not a list'})
        except ValidationError as e:
            result = _format_validation_error(e, Path('test.yaml'))
            # Should not contain pydantic internal formatting
            assert 'input_type=' not in result
            assert 'input_value=' not in result


class TestFormatYamlError:
    """Tests for _format_yaml_error function."""

    def test_yaml_syntax_error_with_position(self) -> None:
        """Test formatting of YAML syntax error with line/column info."""
        invalid_yaml = 'key: {\n  value'
        try:
            yaml.safe_load(invalid_yaml)
        except yaml.YAMLError as e:
            result = _format_yaml_error(e, Path('broken.yaml'))
            assert 'YAML syntax error in broken.yaml' in result
            assert 'line' in result
            assert 'column' in result

    def test_yaml_parser_error(self) -> None:
        """Test formatting of YAML parser error."""
        invalid_yaml = 'test: {\n'
        try:
            yaml.safe_load(invalid_yaml)
        except yaml.YAMLError as e:
            result = _format_yaml_error(e, Path('invalid.yaml'))
            assert 'YAML syntax error in invalid.yaml' in result

    def test_yaml_scanner_error(self) -> None:
        """Test formatting of YAML scanner error (invalid characters)."""
        invalid_yaml = 'key: @invalid'
        try:
            yaml.safe_load(invalid_yaml)
        except yaml.YAMLError as e:
            result = _format_yaml_error(e, Path('scanner-error.yaml'))
            assert 'YAML syntax error in scanner-error.yaml' in result

    def test_yaml_error_without_mark(self) -> None:
        """Test handling of YAML error without position information."""
        # Create a mock error without problem_mark
        error = yaml.YAMLError('Generic error')
        result = _format_yaml_error(error, Path('generic.yaml'))
        assert 'YAML syntax error in generic.yaml' in result
        assert 'Generic error' in result

    def test_yaml_duplicate_key_error(self) -> None:
        """Test formatting of YAML duplicate key warning."""
        # Note: PyYAML doesn't raise an error for duplicate keys by default,
        # but we can test the structure
        invalid_yaml = 'items:\n  - title: "Test"\n    grid: {x: 0\n'
        try:
            yaml.safe_load(invalid_yaml)
        except yaml.YAMLError as e:
            result = _format_yaml_error(e, Path('duplicate.yaml'))
            assert 'YAML syntax error in duplicate.yaml' in result


class TestCompileYamlToJsonErrorHandling:
    """Integration tests for compile_yaml_to_json error handling."""

    def test_compile_empty_file(self, tmp_path: Path) -> None:
        """Test that empty YAML files produce friendly error messages."""
        from dashboard_compiler.cli import compile_yaml_to_json

        empty_file = tmp_path / 'empty.yaml'
        empty_file.write_text('')

        json_lines, error = compile_yaml_to_json(empty_file)
        assert json_lines == []
        assert error is not None
        assert 'empty.yaml' in error
        assert 'empty or does not contain valid YAML' in error

    def test_compile_invalid_yaml_syntax(self, tmp_path: Path) -> None:
        """Test that YAML syntax errors produce friendly error messages."""
        from dashboard_compiler.cli import compile_yaml_to_json

        invalid_file = tmp_path / 'invalid.yaml'
        invalid_file.write_text('dashboards:\n  - name: Test\n    panels:\n      - title: Bad\n      grid: {x: 0\n')

        json_lines, error = compile_yaml_to_json(invalid_file)
        assert json_lines == []
        assert error is not None
        assert 'YAML syntax error in invalid.yaml' in error
        assert 'line' in error

    def test_compile_missing_dashboards_key(self, tmp_path: Path) -> None:
        """Test that missing 'dashboards' key produces friendly error message."""
        from dashboard_compiler.cli import compile_yaml_to_json

        missing_key_file = tmp_path / 'missing-key.yaml'
        missing_key_file.write_text('panels:\n  - title: Test\n')

        json_lines, error = compile_yaml_to_json(missing_key_file)
        assert json_lines == []
        assert error is not None
        assert 'missing-key.yaml' in error
        assert 'dashboards' in error.lower()

    def test_compile_missing_dashboard_name(self, tmp_path: Path) -> None:
        """Test that missing dashboard name produces friendly error message."""
        from dashboard_compiler.cli import compile_yaml_to_json

        missing_name_file = tmp_path / 'missing-name.yaml'
        missing_name_file.write_text('dashboards:\n  - description: Test\n    panels: []\n')

        json_lines, error = compile_yaml_to_json(missing_name_file)
        assert json_lines == []
        assert error is not None
        assert 'missing-name.yaml' in error
        assert 'name' in error

    def test_compile_file_not_found(self, tmp_path: Path) -> None:
        """Test that file not found produces friendly error message."""
        from dashboard_compiler.cli import compile_yaml_to_json

        nonexistent_file = tmp_path / 'nonexistent.yaml'

        json_lines, error = compile_yaml_to_json(nonexistent_file)
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
        grid: {x: 0, y: 0, w: 24, h: 12}
        markdown:
          content: Hello World
""")

        json_lines, error = compile_yaml_to_json(valid_file)
        assert error is None
        assert len(json_lines) == 1
