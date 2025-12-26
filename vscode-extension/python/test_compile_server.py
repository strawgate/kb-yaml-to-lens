#!/usr/bin/env python3
"""Unit tests for compile_server.py LSP handlers."""

import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

# Add parent directories to path for importing
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from compile_server import _compile_dashboard, _params_to_dict, compile_command, compile_custom, get_dashboards_custom
from lsprotocol import types


class TestParamsToDict(unittest.TestCase):
    """Test the _params_to_dict helper function."""

    def test_dict_passthrough(self) -> None:
        """Test that dict inputs are returned as-is."""
        params = {'path': '/test.yaml', 'dashboard_index': 0}
        result = _params_to_dict(params)
        self.assertEqual(result, params)

    def test_cattrs_object_conversion(self) -> None:
        """Test conversion of cattrs-structured objects to dict."""
        # Create a mock object with attributes
        mock_params = MagicMock()
        mock_params.path = '/test.yaml'
        mock_params.dashboard_index = 0

        # Mock cattrs.unstructure to return a dict
        with patch('compile_server.cattrs.unstructure') as mock_unstructure:
            mock_unstructure.return_value = {'path': '/test.yaml', 'dashboard_index': 0}

            result = _params_to_dict(mock_params)

            self.assertEqual(result, {'path': '/test.yaml', 'dashboard_index': 0})
            mock_unstructure.assert_called_once_with(mock_params)


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
  - type: markdown
    title: Test Panel
    grid:
      x: 0
      y: 0
      w: 12
      h: 10
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
  - type: markdown
    title: Panel
    grid: {x: 0, y: 0, w: 12, h: 10}
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


class TestCompileCommand(unittest.TestCase):
    """Test the compile_command handler (workspace/executeCommand pattern)."""

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

    def test_compile_command_with_path_only(self) -> None:
        """Test executeCommand with just path argument."""
        mock_ls = MagicMock()
        args = [str(self.temp_file)]

        result = compile_command(mock_ls, args)

        self.assertTrue(result['success'])
        self.assertIn('data', result)

    def test_compile_command_with_index(self) -> None:
        """Test executeCommand with path and dashboard index."""
        mock_ls = MagicMock()
        args = [str(self.temp_file), 1]

        result = compile_command(mock_ls, args)

        self.assertTrue(result['success'])
        self.assertEqual(result['data']['attributes']['title'], 'Second Dashboard')

    def test_compile_command_with_string_index(self) -> None:
        """Test executeCommand with dashboard index as string."""
        mock_ls = MagicMock()
        args = [str(self.temp_file), '1']

        result = compile_command(mock_ls, args)

        self.assertTrue(result['success'])
        self.assertEqual(result['data']['attributes']['title'], 'Second Dashboard')

    def test_compile_command_missing_args(self) -> None:
        """Test executeCommand with no arguments returns error."""
        mock_ls = MagicMock()
        args: list[Any] = []

        result = compile_command(mock_ls, args)

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('Missing path', result['error'])

    def test_compile_command_empty_args(self) -> None:
        """Test executeCommand with None args returns error."""
        mock_ls = MagicMock()

        result = compile_command(mock_ls, [])

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

    def test_compile_custom_with_mock_object(self) -> None:
        """Test custom request with cattrs-structured object."""
        mock_params = MagicMock()

        with patch('compile_server.cattrs.unstructure') as mock_unstructure:
            mock_unstructure.return_value = {'path': str(self.temp_file), 'dashboard_index': 0}

            result = compile_custom(mock_params)

            self.assertTrue(result['success'])
            mock_unstructure.assert_called_once()


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

    def test_get_dashboards_with_mock_object(self) -> None:
        """Test with cattrs-structured object."""
        yaml_content = """dashboards:
- name: Test
  panels: []
"""
        self.temp_file.write_text(yaml_content)

        mock_params = MagicMock()

        with patch('compile_server.cattrs.unstructure') as mock_unstructure:
            mock_unstructure.return_value = {'path': str(self.temp_file)}

            result = get_dashboards_custom(mock_params)

            self.assertTrue(result['success'])
            mock_unstructure.assert_called_once()


class TestDidSaveHandler(unittest.TestCase):
    """Test the did_save notification handler."""

    def test_did_save_sends_notification(self) -> None:
        """Test that did_save handler sends fileChanged notification."""
        from compile_server import did_save

        # Create mock language server
        mock_ls = MagicMock()
        mock_protocol = MagicMock()
        mock_ls.protocol = mock_protocol

        # Create params
        params = types.DidSaveTextDocumentParams(text_document=types.TextDocumentIdentifier(uri='file:///test/dashboard.yaml'))

        # Call handler
        did_save(mock_ls, params)

        # Verify notification was sent
        mock_protocol.notify.assert_called_once_with('dashboard/fileChanged', {'uri': 'file:///test/dashboard.yaml'})

    def test_did_save_with_different_uris(self) -> None:
        """Test did_save with various file URIs."""
        from compile_server import did_save

        test_uris = [
            'file:///workspace/test.yaml',
            'file:///home/user/dashboards/main.yaml',
            'file:///c:/Windows/dashboard.yaml',
        ]

        for uri in test_uris:
            mock_ls = MagicMock()
            mock_protocol = MagicMock()
            mock_ls.protocol = mock_protocol

            params = types.DidSaveTextDocumentParams(text_document=types.TextDocumentIdentifier(uri=uri))

            did_save(mock_ls, params)

            mock_protocol.notify.assert_called_once_with('dashboard/fileChanged', {'uri': uri})


if __name__ == '__main__':
    unittest.main()
