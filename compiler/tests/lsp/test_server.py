#!/usr/bin/env python3
"""Unit tests for dashboard_compiler.lsp.server LSP handlers."""
# ruff: noqa: PT009

import tempfile
import unittest
from pathlib import Path

from dashboard_compiler.lsp.server import (
    _compile_dashboard,
    _params_to_dict,
    compile_custom,
    get_dashboards_custom,
    get_grid_layout_custom,
)


class TestParamsToDict(unittest.TestCase):
    """Test the _params_to_dict helper function."""

    def test_dict_passthrough(self) -> None:
        """Test that dict inputs are returned as-is."""
        params = {'path': '/test.yaml', 'dashboard_index': 0}
        result = _params_to_dict(params)
        self.assertEqual(result, params)

    def test_namedtuple_conversion(self) -> None:
        """Test conversion of namedtuple objects (like pygls.protocol.Object) to dict."""
        from collections import namedtuple

        # Create a namedtuple like pygls.protocol.Object
        ParamsType = namedtuple('ParamsType', ['path', 'dashboard_index'])
        params = ParamsType(path='/test.yaml', dashboard_index=0)

        result = _params_to_dict(params)

        self.assertEqual(result, {'path': '/test.yaml', 'dashboard_index': 0})


class TestCompileDashboard(unittest.TestCase):
    """Test the _compile_dashboard helper function."""

    def setUp(self) -> None:
        """Create temporary test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = Path(self.temp_dir) / 'test_dashboard.yaml'

    def tearDown(self) -> None:
        """Clean up temporary files."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_compile_valid_dashboard(self) -> None:
        """Test compiling a valid dashboard YAML file."""
        yaml_content = """dashboards:
- name: Test Dashboard
  description: A test dashboard
  panels:
  - title: Test Panel
    grid:
      x: 0
      y: 0
      w: 12
      h: 10
    markdown:
      content: "# Test"
"""
        self.temp_file.write_text(yaml_content)

        result = _compile_dashboard(str(self.temp_file), 0)

        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIsInstance(result['data'], dict)

    def test_compile_missing_path(self) -> None:
        """Test that missing path returns error."""
        result = _compile_dashboard('', 0)

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('Missing path', result['error'])

    def test_compile_nonexistent_file(self) -> None:
        """Test that nonexistent file returns error."""
        result = _compile_dashboard('/nonexistent/file.yaml', 0)

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_compile_empty_dashboards(self) -> None:
        """Test that file with no dashboards returns error."""
        yaml_content = """dashboards: []
"""
        self.temp_file.write_text(yaml_content)

        result = _compile_dashboard(str(self.temp_file), 0)

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('No dashboards found', result['error'])

    def test_compile_dashboard_index_out_of_range(self) -> None:
        """Test that out-of-range dashboard index returns error."""
        yaml_content = """dashboards:
- name: Test Dashboard
  panels: []
"""
        self.temp_file.write_text(yaml_content)

        result = _compile_dashboard(str(self.temp_file), 5)

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('out of range', result['error'])

    def test_compile_negative_dashboard_index(self) -> None:
        """Test that negative dashboard index returns error."""
        yaml_content = """dashboards:
- name: Test Dashboard
  panels: []
"""
        self.temp_file.write_text(yaml_content)

        result = _compile_dashboard(str(self.temp_file), -1)

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('out of range', result['error'])

    def test_compile_second_dashboard(self) -> None:
        """Test compiling the second dashboard in a multi-dashboard file."""
        yaml_content = """dashboards:
- name: First Dashboard
  panels: []
- name: Second Dashboard
  description: The second one
  panels:
  - title: Panel
    grid: {x: 0, y: 0, w: 12, h: 10}
    markdown:
      content: "Test"
"""
        self.temp_file.write_text(yaml_content)

        result = _compile_dashboard(str(self.temp_file), 1)

        self.assertTrue(result['success'])
        self.assertIn('data', result)
        # Verify it's the second dashboard
        self.assertEqual(result['data']['attributes']['title'], 'Second Dashboard')

    def test_compile_invalid_yaml(self) -> None:
        """Test that invalid YAML returns error."""
        yaml_content = """dashboards:
- name: Test
  invalid: [unclosed bracket
"""
        self.temp_file.write_text(yaml_content)

        result = _compile_dashboard(str(self.temp_file), 0)

        self.assertFalse(result['success'])
        self.assertIn('error', result)


class TestCompileCustom(unittest.TestCase):
    """Test the compile_custom handler (custom request pattern)."""

    def setUp(self) -> None:
        """Create temporary test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = Path(self.temp_dir) / 'test_dashboard.yaml'
        yaml_content = """dashboards:
- name: Test Dashboard
  panels: []
- name: Second Dashboard
  panels: []
"""
        self.temp_file.write_text(yaml_content)

    def tearDown(self) -> None:
        """Clean up temporary files."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_compile_custom_with_dict_params(self) -> None:
        """Test custom request with dict parameters."""
        params = {'path': str(self.temp_file), 'dashboard_index': 0}

        result = compile_custom(params)

        self.assertTrue(result['success'])
        self.assertIn('data', result)

    def test_compile_custom_with_string_index(self) -> None:
        """Test custom request with string dashboard index."""
        params = {'path': str(self.temp_file), 'dashboard_index': '1'}

        result = compile_custom(params)

        self.assertTrue(result['success'])
        self.assertEqual(result['data']['attributes']['title'], 'Second Dashboard')

    def test_compile_custom_missing_path(self) -> None:
        """Test custom request with missing path parameter."""
        params = {'dashboard_index': 0}

        result = compile_custom(params)

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_compile_custom_default_index(self) -> None:
        """Test custom request defaults to index 0 when not provided."""
        params = {'path': str(self.temp_file)}

        result = compile_custom(params)

        self.assertTrue(result['success'])
        self.assertEqual(result['data']['attributes']['title'], 'Test Dashboard')

    def test_compile_custom_with_namedtuple(self) -> None:
        """Test custom request with namedtuple params (like pygls.protocol.Object)."""
        from collections import namedtuple

        ParamsType = namedtuple('ParamsType', ['path', 'dashboard_index'])
        params = ParamsType(path=str(self.temp_file), dashboard_index=0)

        result = compile_custom(params)

        self.assertTrue(result['success'])

    def test_compile_custom_invalid_string_index(self) -> None:
        """Invalid dashboard_index should return a structured error (not raise)."""
        params = {'path': str(self.temp_file), 'dashboard_index': 'abc'}

        result = compile_custom(params)

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('Invalid dashboard_index', result['error'])

    def test_compile_custom_none_index(self) -> None:
        """None dashboard_index should return a structured error (not raise)."""
        params = {'path': str(self.temp_file), 'dashboard_index': None}

        result = compile_custom(params)

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('Invalid dashboard_index', result['error'])


class TestGetDashboardsCustom(unittest.TestCase):
    """Test the get_dashboards_custom handler."""

    def setUp(self) -> None:
        """Create temporary test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = Path(self.temp_dir) / 'test_dashboard.yaml'

    def tearDown(self) -> None:
        """Clean up temporary files."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_get_dashboards_single(self) -> None:
        """Test getting list of dashboards from single dashboard file."""
        yaml_content = """dashboards:
- name: Test Dashboard
  description: A test dashboard
  panels: []
"""
        self.temp_file.write_text(yaml_content)

        params = {'path': str(self.temp_file)}
        result = get_dashboards_custom(params)

        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['data'][0]['index'], 0)
        self.assertEqual(result['data'][0]['title'], 'Test Dashboard')
        self.assertEqual(result['data'][0]['description'], 'A test dashboard')

    def test_get_dashboards_multiple(self) -> None:
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
        self.temp_file.write_text(yaml_content)

        params = {'path': str(self.temp_file)}
        result = get_dashboards_custom(params)

        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 3)
        self.assertEqual(result['data'][0]['title'], 'First Dashboard')
        self.assertEqual(result['data'][1]['title'], 'Second Dashboard')
        self.assertEqual(result['data'][2]['title'], 'Third Dashboard')

    def test_get_dashboards_no_description(self) -> None:
        """Test dashboard without description gets empty string."""
        yaml_content = """dashboards:
- name: No Description Dashboard
  panels: []
"""
        self.temp_file.write_text(yaml_content)

        params = {'path': str(self.temp_file)}
        result = get_dashboards_custom(params)

        self.assertTrue(result['success'])
        self.assertEqual(result['data'][0]['description'], '')

    def test_get_dashboards_no_name(self) -> None:
        """Test dashboard without name returns validation error."""
        yaml_content = """dashboards:
- panels: []
"""
        self.temp_file.write_text(yaml_content)

        params = {'path': str(self.temp_file)}
        result = get_dashboards_custom(params)

        # Dashboard requires name field, so this should fail validation
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_get_dashboards_missing_path(self) -> None:
        """Test that missing path returns error."""
        params = {}

        result = get_dashboards_custom(params)

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('Missing path', result['error'])

    def test_get_dashboards_nonexistent_file(self) -> None:
        """Test that nonexistent file returns error."""
        params = {'path': '/nonexistent/file.yaml'}

        result = get_dashboards_custom(params)

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_get_dashboards_with_namedtuple(self) -> None:
        """Test with namedtuple params (like pygls.protocol.Object)."""
        from collections import namedtuple

        yaml_content = """dashboards:
- name: Test
  panels: []
"""
        self.temp_file.write_text(yaml_content)

        ParamsType = namedtuple('ParamsType', ['path'])
        params = ParamsType(path=str(self.temp_file))

        result = get_dashboards_custom(params)

        self.assertTrue(result['success'])


class TestGetGridLayoutCustom(unittest.TestCase):
    """Test the get_grid_layout_custom handler."""

    def setUp(self) -> None:
        """Create temporary test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = Path(self.temp_dir) / 'test_dashboard.yaml'

    def tearDown(self) -> None:
        """Clean up temporary files."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_get_grid_layout_valid(self) -> None:
        """Test getting grid layout from a valid dashboard file."""
        yaml_content = """dashboards:
- name: Test Dashboard
  description: A test dashboard
  panels:
  - title: Test Panel
    grid:
      x: 0
      y: 0
      w: 24
      h: 12
    markdown:
      content: "# Test"
"""
        self.temp_file.write_text(yaml_content)

        params = {'path': str(self.temp_file), 'dashboard_index': 0}
        result = get_grid_layout_custom(params)

        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['title'], 'Test Dashboard')
        self.assertEqual(result['data']['description'], 'A test dashboard')
        self.assertEqual(len(result['data']['panels']), 1)
        self.assertEqual(result['data']['panels'][0]['title'], 'Test Panel')
        self.assertEqual(result['data']['panels'][0]['grid']['x'], 0)
        self.assertEqual(result['data']['panels'][0]['grid']['y'], 0)
        self.assertEqual(result['data']['panels'][0]['grid']['w'], 24)
        self.assertEqual(result['data']['panels'][0]['grid']['h'], 12)

    def test_get_grid_layout_multiple_panels(self) -> None:
        """Test getting grid layout with multiple panels."""
        yaml_content = """dashboards:
- name: Multi Panel Dashboard
  panels:
  - title: Panel 1
    grid: {x: 0, y: 0, w: 24, h: 10}
    markdown:
      content: "1"
  - title: Panel 2
    grid: {x: 24, y: 0, w: 24, h: 10}
    markdown:
      content: "2"
"""
        self.temp_file.write_text(yaml_content)

        params = {'path': str(self.temp_file)}
        result = get_grid_layout_custom(params)

        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']['panels']), 2)
        self.assertEqual(result['data']['panels'][0]['title'], 'Panel 1')
        self.assertEqual(result['data']['panels'][1]['title'], 'Panel 2')

    def test_get_grid_layout_missing_path(self) -> None:
        """Test that missing path returns error."""
        params = {}

        result = get_grid_layout_custom(params)

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('Missing path', result['error'])

    def test_get_grid_layout_empty_path(self) -> None:
        """Test that empty path returns error."""
        params = {'path': ''}

        result = get_grid_layout_custom(params)

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('Missing path', result['error'])

    def test_get_grid_layout_nonexistent_file(self) -> None:
        """Test that nonexistent file returns error."""
        params = {'path': '/nonexistent/file.yaml'}

        result = get_grid_layout_custom(params)

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_get_grid_layout_invalid_dashboard_index(self) -> None:
        """Test that out-of-range dashboard index returns error."""
        yaml_content = """dashboards:
- name: Test Dashboard
  panels:
  - title: Panel
    grid: {x: 0, y: 0, w: 24, h: 10}
    markdown:
      content: "Test"
"""
        self.temp_file.write_text(yaml_content)

        params = {'path': str(self.temp_file), 'dashboard_index': 5}
        result = get_grid_layout_custom(params)

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('out of range', result['error'])

    def test_get_grid_layout_negative_index(self) -> None:
        """Test that negative dashboard index returns error."""
        yaml_content = """dashboards:
- name: Test Dashboard
  panels:
  - title: Panel
    grid: {x: 0, y: 0, w: 24, h: 10}
    markdown:
      content: "Test"
"""
        self.temp_file.write_text(yaml_content)

        params = {'path': str(self.temp_file), 'dashboard_index': -1}
        result = get_grid_layout_custom(params)

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('out of range', result['error'])

    def test_get_grid_layout_second_dashboard(self) -> None:
        """Test getting grid layout from second dashboard in multi-dashboard file."""
        yaml_content = """dashboards:
- name: First Dashboard
  panels:
  - title: First Panel
    grid: {x: 0, y: 0, w: 24, h: 10}
    markdown:
      content: "1"
- name: Second Dashboard
  description: The second one
  panels:
  - title: Second Panel
    grid: {x: 0, y: 0, w: 48, h: 20}
    markdown:
      content: "2"
"""
        self.temp_file.write_text(yaml_content)

        params = {'path': str(self.temp_file), 'dashboard_index': 1}
        result = get_grid_layout_custom(params)

        self.assertTrue(result['success'])
        self.assertEqual(result['data']['title'], 'Second Dashboard')
        self.assertEqual(result['data']['description'], 'The second one')
        self.assertEqual(result['data']['panels'][0]['title'], 'Second Panel')

    def test_get_grid_layout_default_index(self) -> None:
        """Test that default index is 0 when not provided."""
        yaml_content = """dashboards:
- name: Default Dashboard
  panels:
  - title: Panel
    grid: {x: 0, y: 0, w: 24, h: 10}
    markdown:
      content: "Test"
"""
        self.temp_file.write_text(yaml_content)

        params = {'path': str(self.temp_file)}
        result = get_grid_layout_custom(params)

        self.assertTrue(result['success'])
        self.assertEqual(result['data']['title'], 'Default Dashboard')

    def test_get_grid_layout_with_namedtuple(self) -> None:
        """Test with namedtuple params (like pygls.protocol.Object)."""
        from collections import namedtuple

        yaml_content = """dashboards:
- name: Test
  panels:
  - title: Panel
    grid: {x: 0, y: 0, w: 24, h: 10}
    markdown:
      content: "Test"
"""
        self.temp_file.write_text(yaml_content)

        ParamsType = namedtuple('ParamsType', ['path', 'dashboard_index'])
        params = ParamsType(path=str(self.temp_file), dashboard_index=0)

        result = get_grid_layout_custom(params)

        self.assertTrue(result['success'])

    def test_get_grid_layout_string_index(self) -> None:
        """Test with string dashboard index (should be converted to int)."""
        yaml_content = """dashboards:
- name: First
  panels:
  - title: Panel
    grid: {x: 0, y: 0, w: 24, h: 10}
    markdown:
      content: "Test"
- name: Second
  panels:
  - title: Panel
    grid: {x: 0, y: 0, w: 24, h: 10}
    markdown:
      content: "Test"
"""
        self.temp_file.write_text(yaml_content)

        params = {'path': str(self.temp_file), 'dashboard_index': '1'}
        result = get_grid_layout_custom(params)

        self.assertTrue(result['success'])
        self.assertEqual(result['data']['title'], 'Second')

    def test_get_grid_layout_no_dashboards(self) -> None:
        """Test that file with no dashboards returns error."""
        yaml_content = """dashboards: []
"""
        self.temp_file.write_text(yaml_content)

        params = {'path': str(self.temp_file)}
        result = get_grid_layout_custom(params)

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('No dashboards found', result['error'])

    def test_get_grid_layout_invalid_string_index(self) -> None:
        """Invalid dashboard_index should return a structured error (not raise)."""
        yaml_content = """dashboards:
- name: Only
  panels:
  - title: Panel
    grid: {x: 0, y: 0, w: 24, h: 10}
    markdown:
      content: "Test"
"""
        self.temp_file.write_text(yaml_content)

        params = {'path': str(self.temp_file), 'dashboard_index': 'abc'}
        result = get_grid_layout_custom(params)

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('Invalid dashboard_index', result['error'])

    def test_get_grid_layout_none_index(self) -> None:
        """None dashboard_index should return a structured error (not raise)."""
        yaml_content = """dashboards:
- name: Only
  panels:
  - title: Panel
    grid: {x: 0, y: 0, w: 24, h: 10}
    markdown:
      content: "Test"
"""
        self.temp_file.write_text(yaml_content)

        params = {'path': str(self.temp_file), 'dashboard_index': None}
        result = get_grid_layout_custom(params)

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('Invalid dashboard_index', result['error'])


if __name__ == '__main__':
    unittest.main()
