#!/usr/bin/env python3
"""Unit tests for dashboard_compiler.lsp.server LSP handlers."""

from collections import namedtuple
from pathlib import Path

import pytest

from dashboard_compiler.lsp.server import (
    _compile_dashboard,
    _params_to_dict,
    compile_custom,
    get_dashboards_custom,
    get_grid_layout_custom,
)

# Test data: Valid dashboard YAML content
VALID_SINGLE_DASHBOARD = """dashboards:
- name: Test Dashboard
  description: A test dashboard
  panels:
  - title: Test Panel
    size:
      w: 12
      h: 10
    position:
      x: 0
      y: 0
    markdown:
      content: "# Test"
"""

VALID_TWO_DASHBOARDS = """dashboards:
- name: First Dashboard
  description: First one
  panels: []
- name: Second Dashboard
  description: The second one
  panels:
  - title: Panel
    size: {w: 12, h: 10}
    position: {x: 0, y: 0}
    markdown:
      content: "Test"
"""

EMPTY_DASHBOARDS = """dashboards: []
"""

INVALID_YAML = """dashboards:
- name: Test
  invalid: [unclosed bracket
"""

NO_NAME_DASHBOARD = """dashboards:
- panels: []
"""


class TestParamsToDict:
    """Test the _params_to_dict helper function."""

    def test_dict_passthrough(self) -> None:
        """Test that dict inputs are returned as-is."""
        params = {'path': '/test.yaml', 'dashboard_index': 0}
        result = _params_to_dict(params)
        assert result == params

    def test_namedtuple_conversion(self) -> None:
        """Test conversion of namedtuple objects (like pygls.protocol.Object) to dict."""
        ParamsType = namedtuple('ParamsType', ['path', 'dashboard_index'])
        params = ParamsType(path='/test.yaml', dashboard_index=0)

        result = _params_to_dict(params)

        assert result == {'path': '/test.yaml', 'dashboard_index': 0}

    def test_unsupported_type_raises_typeerror(self) -> None:
        """Test that unsupported types raise TypeError."""
        with pytest.raises(TypeError, match='Unable to convert params of type int to dict'):
            _params_to_dict(42)


class TestCompileDashboard:
    """Test the _compile_dashboard helper function."""

    def test_compile_valid_dashboard(self, temp_yaml_file: Path) -> None:
        """Test compiling a valid dashboard YAML file."""
        temp_yaml_file.write_text(VALID_SINGLE_DASHBOARD)

        result = _compile_dashboard(str(temp_yaml_file), 0)

        assert result['success'] is True
        assert 'data' in result
        assert isinstance(result['data'], dict)

    def test_compile_missing_path(self) -> None:
        """Test that missing path returns error."""
        result = _compile_dashboard('', 0)

        assert result['success'] is False
        assert 'error' in result
        assert 'Missing path' in result['error']

    def test_compile_nonexistent_file(self) -> None:
        """Test that nonexistent file returns error."""
        result = _compile_dashboard('/nonexistent/file.yaml', 0)

        assert result['success'] is False
        assert 'error' in result

    def test_compile_empty_dashboards(self, temp_yaml_file: Path) -> None:
        """Test that file with no dashboards returns error."""
        temp_yaml_file.write_text(EMPTY_DASHBOARDS)

        result = _compile_dashboard(str(temp_yaml_file), 0)

        assert result['success'] is False
        assert 'error' in result
        assert 'No dashboards found' in result['error']

    def test_compile_dashboard_index_out_of_range(self, temp_yaml_file: Path) -> None:
        """Test that out-of-range dashboard index returns error."""
        temp_yaml_file.write_text(VALID_SINGLE_DASHBOARD)

        result = _compile_dashboard(str(temp_yaml_file), 5)

        assert result['success'] is False
        assert 'error' in result
        assert 'out of range' in result['error']

    def test_compile_negative_dashboard_index(self, temp_yaml_file: Path) -> None:
        """Test that negative dashboard index returns error."""
        temp_yaml_file.write_text(VALID_SINGLE_DASHBOARD)

        result = _compile_dashboard(str(temp_yaml_file), -1)

        assert result['success'] is False
        assert 'error' in result
        assert 'out of range' in result['error']

    def test_compile_second_dashboard(self, temp_yaml_file: Path) -> None:
        """Test compiling the second dashboard in a multi-dashboard file."""
        temp_yaml_file.write_text(VALID_TWO_DASHBOARDS)

        result = _compile_dashboard(str(temp_yaml_file), 1)

        assert result['success'] is True
        assert 'data' in result
        assert result['data']['attributes']['title'] == 'Second Dashboard'

    def test_compile_invalid_yaml(self, temp_yaml_file: Path) -> None:
        """Test that invalid YAML returns error."""
        temp_yaml_file.write_text(INVALID_YAML)

        result = _compile_dashboard(str(temp_yaml_file), 0)

        assert result['success'] is False
        assert 'error' in result


class TestCompileCustom:
    """Test the compile_custom handler (custom request pattern)."""

    def test_compile_custom_with_dict_params(self, temp_yaml_file: Path) -> None:
        """Test custom request with dict parameters."""
        temp_yaml_file.write_text(VALID_TWO_DASHBOARDS)
        params = {'path': str(temp_yaml_file), 'dashboard_index': 0}

        result = compile_custom(params)

        assert result['success'] is True
        assert 'data' in result

    def test_compile_custom_with_string_index(self, temp_yaml_file: Path) -> None:
        """Test custom request with string dashboard index."""
        temp_yaml_file.write_text(VALID_TWO_DASHBOARDS)
        params = {'path': str(temp_yaml_file), 'dashboard_index': '1'}

        result = compile_custom(params)

        assert result['success'] is True
        assert result['data']['attributes']['title'] == 'Second Dashboard'

    def test_compile_custom_missing_path(self) -> None:
        """Test custom request with missing path parameter."""
        params = {'dashboard_index': 0}

        result = compile_custom(params)

        assert result['success'] is False
        assert 'error' in result

    def test_compile_custom_default_index(self, temp_yaml_file: Path) -> None:
        """Test custom request defaults to index 0 when not provided."""
        temp_yaml_file.write_text(VALID_TWO_DASHBOARDS)
        params = {'path': str(temp_yaml_file)}

        result = compile_custom(params)

        assert result['success'] is True
        assert result['data']['attributes']['title'] == 'First Dashboard'

    def test_compile_custom_with_namedtuple(self, temp_yaml_file: Path) -> None:
        """Test custom request with namedtuple params (like pygls.protocol.Object)."""
        temp_yaml_file.write_text(VALID_TWO_DASHBOARDS)
        ParamsType = namedtuple('ParamsType', ['path', 'dashboard_index'])
        params = ParamsType(path=str(temp_yaml_file), dashboard_index=0)

        result = compile_custom(params)

        assert result['success'] is True

    def test_compile_custom_invalid_string_index(self, temp_yaml_file: Path) -> None:
        """Invalid dashboard_index should return a structured error (not raise)."""
        temp_yaml_file.write_text(VALID_TWO_DASHBOARDS)
        params = {'path': str(temp_yaml_file), 'dashboard_index': 'abc'}

        result = compile_custom(params)

        assert result['success'] is False
        assert 'error' in result
        assert 'Invalid dashboard_index' in result['error']

    def test_compile_custom_none_index(self, temp_yaml_file: Path) -> None:
        """None dashboard_index should return a structured error (not raise)."""
        temp_yaml_file.write_text(VALID_TWO_DASHBOARDS)
        params = {'path': str(temp_yaml_file), 'dashboard_index': None}

        result = compile_custom(params)

        assert result['success'] is False
        assert 'error' in result
        assert 'Invalid dashboard_index' in result['error']


class TestGetDashboardsCustom:
    """Test the get_dashboards_custom handler."""

    def test_get_dashboards_single(self, temp_yaml_file: Path) -> None:
        """Test getting list of dashboards from single dashboard file."""
        temp_yaml_file.write_text(VALID_SINGLE_DASHBOARD)
        params = {'path': str(temp_yaml_file)}

        result = get_dashboards_custom(params)

        assert result['success'] is True
        assert 'data' in result
        assert len(result['data']) == 1
        assert result['data'][0]['index'] == 0
        assert result['data'][0]['title'] == 'Test Dashboard'
        assert result['data'][0]['description'] == 'A test dashboard'

    def test_get_dashboards_multiple(self, temp_yaml_file: Path) -> None:
        """Test getting list of multiple dashboards."""
        yaml_content = """dashboards:
- name: First Dashboard
  description: First one
  panels: []
- name: Second Dashboard
  description: Second one
  panels: []
- name: Third Dashboard
  panels: []
"""
        temp_yaml_file.write_text(yaml_content)
        params = {'path': str(temp_yaml_file)}

        result = get_dashboards_custom(params)

        assert result['success'] is True
        assert len(result['data']) == 3
        assert result['data'][0]['title'] == 'First Dashboard'
        assert result['data'][1]['title'] == 'Second Dashboard'
        assert result['data'][2]['title'] == 'Third Dashboard'

    def test_get_dashboards_no_description(self, temp_yaml_file: Path) -> None:
        """Test dashboard without description gets empty string."""
        yaml_content = """dashboards:
- name: No Description Dashboard
  panels: []
"""
        temp_yaml_file.write_text(yaml_content)
        params = {'path': str(temp_yaml_file)}

        result = get_dashboards_custom(params)

        assert result['success'] is True
        assert result['data'][0]['description'] == ''

    def test_get_dashboards_no_name(self, temp_yaml_file: Path) -> None:
        """Test dashboard without name returns validation error."""
        temp_yaml_file.write_text(NO_NAME_DASHBOARD)
        params = {'path': str(temp_yaml_file)}

        result = get_dashboards_custom(params)

        assert result['success'] is False
        assert 'error' in result

    def test_get_dashboards_missing_path(self) -> None:
        """Test that missing path returns error."""
        params: dict[str, str] = {}

        result = get_dashboards_custom(params)

        assert result['success'] is False
        assert 'error' in result
        assert 'Missing path' in result['error']

    def test_get_dashboards_nonexistent_file(self) -> None:
        """Test that nonexistent file returns error."""
        params = {'path': '/nonexistent/file.yaml'}

        result = get_dashboards_custom(params)

        assert result['success'] is False
        assert 'error' in result

    def test_get_dashboards_with_namedtuple(self, temp_yaml_file: Path) -> None:
        """Test with namedtuple params (like pygls.protocol.Object)."""
        yaml_content = """dashboards:
- name: Test
  panels: []
"""
        temp_yaml_file.write_text(yaml_content)
        ParamsType = namedtuple('ParamsType', ['path'])
        params = ParamsType(path=str(temp_yaml_file))

        result = get_dashboards_custom(params)

        assert result['success'] is True


class TestGetGridLayoutCustom:
    """Test the get_grid_layout_custom handler."""

    def test_get_grid_layout_valid(self, temp_yaml_file: Path) -> None:
        """Test getting grid layout from a valid dashboard file."""
        yaml_content = """dashboards:
- name: Test Dashboard
  description: A test dashboard
  panels:
  - title: Test Panel
    size:
      w: 24
      h: 12
    position:
      x: 0
      y: 0
    markdown:
      content: "# Test"
"""
        temp_yaml_file.write_text(yaml_content)
        params = {'path': str(temp_yaml_file), 'dashboard_index': 0}

        result = get_grid_layout_custom(params)

        assert result['success'] is True
        assert 'data' in result
        assert result['data']['title'] == 'Test Dashboard'
        assert result['data']['description'] == 'A test dashboard'
        assert len(result['data']['panels']) == 1
        assert result['data']['panels'][0]['title'] == 'Test Panel'
        assert result['data']['panels'][0]['grid']['x'] == 0
        assert result['data']['panels'][0]['grid']['y'] == 0
        assert result['data']['panels'][0]['grid']['w'] == 24
        assert result['data']['panels'][0]['grid']['h'] == 12

    def test_get_grid_layout_multiple_panels(self, temp_yaml_file: Path) -> None:
        """Test getting grid layout with multiple panels."""
        yaml_content = """dashboards:
- name: Multi Panel Dashboard
  panels:
  - title: Panel 1
    size: {w: 24, h: 10}
    position: {x: 0, y: 0}
    markdown:
      content: "1"
  - title: Panel 2
    size: {w: 24, h: 10}
    position: {x: 24, y: 0}
    markdown:
      content: "2"
"""
        temp_yaml_file.write_text(yaml_content)
        params = {'path': str(temp_yaml_file)}

        result = get_grid_layout_custom(params)

        assert result['success'] is True
        assert len(result['data']['panels']) == 2
        assert result['data']['panels'][0]['title'] == 'Panel 1'
        assert result['data']['panels'][1]['title'] == 'Panel 2'

    def test_get_grid_layout_missing_path(self) -> None:
        """Test that missing path returns error."""
        params: dict[str, str] = {}

        result = get_grid_layout_custom(params)

        assert result['success'] is False
        assert 'error' in result
        assert 'Missing path' in result['error']

    def test_get_grid_layout_empty_path(self) -> None:
        """Test that empty path returns error."""
        params = {'path': ''}

        result = get_grid_layout_custom(params)

        assert result['success'] is False
        assert 'error' in result
        assert 'Missing path' in result['error']

    def test_get_grid_layout_nonexistent_file(self) -> None:
        """Test that nonexistent file returns error."""
        params = {'path': '/nonexistent/file.yaml'}

        result = get_grid_layout_custom(params)

        assert result['success'] is False
        assert 'error' in result

    def test_get_grid_layout_invalid_dashboard_index(self, temp_yaml_file: Path) -> None:
        """Test that out-of-range dashboard index returns error."""
        yaml_content = """dashboards:
- name: Test Dashboard
  panels:
  - title: Panel
    size: {w: 24, h: 10}
    position: {x: 0, y: 0}
    markdown:
      content: "Test"
"""
        temp_yaml_file.write_text(yaml_content)
        params = {'path': str(temp_yaml_file), 'dashboard_index': 5}

        result = get_grid_layout_custom(params)

        assert result['success'] is False
        assert 'error' in result
        assert 'out of range' in result['error']

    def test_get_grid_layout_negative_index(self, temp_yaml_file: Path) -> None:
        """Test that negative dashboard index returns error."""
        yaml_content = """dashboards:
- name: Test Dashboard
  panels:
  - title: Panel
    size: {w: 24, h: 10}
    position: {x: 0, y: 0}
    markdown:
      content: "Test"
"""
        temp_yaml_file.write_text(yaml_content)
        params = {'path': str(temp_yaml_file), 'dashboard_index': -1}

        result = get_grid_layout_custom(params)

        assert result['success'] is False
        assert 'error' in result
        assert 'out of range' in result['error']

    def test_get_grid_layout_second_dashboard(self, temp_yaml_file: Path) -> None:
        """Test getting grid layout from second dashboard in multi-dashboard file."""
        yaml_content = """dashboards:
- name: First Dashboard
  panels:
  - title: First Panel
    size: {w: 24, h: 10}
    position: {x: 0, y: 0}
    markdown:
      content: "1"
- name: Second Dashboard
  description: The second one
  panels:
  - title: Second Panel
    size: {w: 48, h: 20}
    position: {x: 0, y: 0}
    markdown:
      content: "2"
"""
        temp_yaml_file.write_text(yaml_content)
        params = {'path': str(temp_yaml_file), 'dashboard_index': 1}

        result = get_grid_layout_custom(params)

        assert result['success'] is True
        assert result['data']['title'] == 'Second Dashboard'
        assert result['data']['description'] == 'The second one'
        assert result['data']['panels'][0]['title'] == 'Second Panel'

    def test_get_grid_layout_default_index(self, temp_yaml_file: Path) -> None:
        """Test that default index is 0 when not provided."""
        yaml_content = """dashboards:
- name: Default Dashboard
  panels:
  - title: Panel
    size: {w: 24, h: 10}
    position: {x: 0, y: 0}
    markdown:
      content: "Test"
"""
        temp_yaml_file.write_text(yaml_content)
        params = {'path': str(temp_yaml_file)}

        result = get_grid_layout_custom(params)

        assert result['success'] is True
        assert result['data']['title'] == 'Default Dashboard'

    def test_get_grid_layout_with_namedtuple(self, temp_yaml_file: Path) -> None:
        """Test with namedtuple params (like pygls.protocol.Object)."""
        yaml_content = """dashboards:
- name: Test
  panels:
  - title: Panel
    size: {w: 24, h: 10}
    position: {x: 0, y: 0}
    markdown:
      content: "Test"
"""
        temp_yaml_file.write_text(yaml_content)
        ParamsType = namedtuple('ParamsType', ['path', 'dashboard_index'])
        params = ParamsType(path=str(temp_yaml_file), dashboard_index=0)

        result = get_grid_layout_custom(params)

        assert result['success'] is True

    def test_get_grid_layout_string_index(self, temp_yaml_file: Path) -> None:
        """Test with string dashboard index (should be converted to int)."""
        yaml_content = """dashboards:
- name: First
  panels:
  - title: Panel
    size: {w: 24, h: 10}
    position: {x: 0, y: 0}
    markdown:
      content: "Test"
- name: Second
  panels:
  - title: Panel
    size: {w: 24, h: 10}
    position: {x: 0, y: 0}
    markdown:
      content: "Test"
"""
        temp_yaml_file.write_text(yaml_content)
        params = {'path': str(temp_yaml_file), 'dashboard_index': '1'}

        result = get_grid_layout_custom(params)

        assert result['success'] is True
        assert result['data']['title'] == 'Second'

    def test_get_grid_layout_no_dashboards(self, temp_yaml_file: Path) -> None:
        """Test that file with no dashboards returns error."""
        temp_yaml_file.write_text(EMPTY_DASHBOARDS)
        params = {'path': str(temp_yaml_file)}

        result = get_grid_layout_custom(params)

        assert result['success'] is False
        assert 'error' in result
        assert 'No dashboards found' in result['error']

    def test_get_grid_layout_invalid_string_index(self, temp_yaml_file: Path) -> None:
        """Invalid dashboard_index should return a structured error (not raise)."""
        yaml_content = """dashboards:
- name: Only
  panels:
  - title: Panel
    size: {w: 24, h: 10}
    position: {x: 0, y: 0}
    markdown:
      content: "Test"
"""
        temp_yaml_file.write_text(yaml_content)
        params = {'path': str(temp_yaml_file), 'dashboard_index': 'abc'}

        result = get_grid_layout_custom(params)

        assert result['success'] is False
        assert 'error' in result
        assert 'Invalid dashboard_index' in result['error']

    def test_get_grid_layout_none_index(self, temp_yaml_file: Path) -> None:
        """None dashboard_index should return a structured error (not raise)."""
        yaml_content = """dashboards:
- name: Only
  panels:
  - title: Panel
    size: {w: 24, h: 10}
    position: {x: 0, y: 0}
    markdown:
      content: "Test"
"""
        temp_yaml_file.write_text(yaml_content)
        params = {'path': str(temp_yaml_file), 'dashboard_index': None}

        result = get_grid_layout_custom(params)

        assert result['success'] is False
        assert 'error' in result
        assert 'Invalid dashboard_index' in result['error']
