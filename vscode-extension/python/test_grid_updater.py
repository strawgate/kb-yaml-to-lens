#!/usr/bin/env python3
"""Unit tests for grid_updater.py."""

import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path for importing
sys.path.insert(0, str(Path(__file__).parent))
from grid_updater import update_panel_grid


class TestGridUpdater(unittest.TestCase):
    """Test grid coordinate updates in YAML dashboard files."""

    def setUp(self):
        """Create temporary test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = Path(self.temp_dir) / 'test_dashboard.yaml'

    def tearDown(self):
        """Clean up temporary files."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_update_panel_by_index(self):
        """Test updating a panel by index."""
        yaml_content = """dashboard:
  name: Test Dashboard
  panels:
    - title: Panel 1
      type: markdown
      grid: { x: 0, y: 0, w: 24, h: 15 }
      content: "Test 1"
    - title: Panel 2
      type: markdown
      grid: { x: 24, y: 0, w: 24, h: 15 }
      content: "Test 2"
"""
        self.temp_file.write_text(yaml_content)

        result = update_panel_grid(str(self.temp_file), 'panel_0', {'x': 10, 'y': 20, 'w': 30, 'h': 40})

        self.assertTrue(result['success'])

        # Read back and verify
        updated_content = self.temp_file.read_text()
        self.assertIn('x: 10', updated_content)
        self.assertIn('y: 20', updated_content)
        self.assertIn('w: 30', updated_content)
        self.assertIn('h: 40', updated_content)

    def test_update_panel_by_id(self):
        """Test updating a panel by explicit ID."""
        yaml_content = """dashboard:
  name: Test Dashboard
  panels:
    - id: my-panel
      title: Panel with ID
      type: markdown
      grid: { x: 0, y: 0, w: 12, h: 8 }
      content: "Test"
"""
        self.temp_file.write_text(yaml_content)

        result = update_panel_grid(str(self.temp_file), 'my-panel', {'x': 5, 'y': 10, 'w': 15, 'h': 20})

        self.assertTrue(result['success'])

        # Read back and verify
        updated_content = self.temp_file.read_text()
        self.assertIn('x: 5', updated_content)
        self.assertIn('y: 10', updated_content)

    def test_update_second_panel(self):
        """Test updating the second panel in a multi-panel dashboard."""
        yaml_content = """dashboard:
  name: Test Dashboard
  panels:
    - title: Panel 1
      grid: { x: 0, y: 0, w: 24, h: 15 }
      type: markdown
      content: "Test 1"
    - title: Panel 2
      grid: { x: 24, y: 0, w: 24, h: 15 }
      type: markdown
      content: "Test 2"
"""
        self.temp_file.write_text(yaml_content)

        result = update_panel_grid(str(self.temp_file), 'panel_1', {'x': 12, 'y': 16, 'w': 36, 'h': 20})

        self.assertTrue(result['success'])

        # Read back and verify both panels
        updated_content = self.temp_file.read_text()
        # First panel should be unchanged
        self.assertIn('{ x: 0, y: 0, w: 24, h: 15 }', updated_content)
        # Second panel should be updated
        self.assertIn('x: 12', updated_content)
        self.assertIn('y: 16', updated_content)

    def test_update_nonexistent_file(self):
        """Test that updating a nonexistent file returns error."""
        result = update_panel_grid('/nonexistent/file.yaml', 'panel_0', {'x': 0, 'y': 0, 'w': 10, 'h': 10})

        self.assertFalse(result['success'])
        self.assertIn('File not found', result['error'])

    def test_update_nonexistent_panel(self):
        """Test that updating a nonexistent panel returns error."""
        yaml_content = """dashboard:
  name: Test Dashboard
  panels:
    - title: Panel 1
      grid: { x: 0, y: 0, w: 24, h: 15 }
      type: markdown
      content: "Test"
"""
        self.temp_file.write_text(yaml_content)

        result = update_panel_grid(str(self.temp_file), 'nonexistent-panel', {'x': 0, 'y': 0, 'w': 10, 'h': 10})

        self.assertFalse(result['success'])
        self.assertIn('not found', result['error'])

    def test_preserve_yaml_formatting(self):
        """Test that YAML formatting is preserved after update."""
        yaml_content = """dashboard:
  name: Test Dashboard
  # This is a comment
  panels:
    - title: Panel 1
      type: markdown
      grid: { x: 0, y: 0, w: 24, h: 15 }
      markdown: "Test content"
"""
        self.temp_file.write_text(yaml_content)

        update_panel_grid(str(self.temp_file), 'panel_0', {'x': 5, 'y': 5, 'w': 20, 'h': 10})

        updated_content = self.temp_file.read_text()
        # Comment should be preserved
        self.assertIn('# This is a comment', updated_content)
        # Other content should be preserved
        self.assertIn('markdown: "Test content"', updated_content)

    def test_reject_invalid_panel_id(self):
        """Test that invalid panel IDs are rejected."""
        yaml_content = """dashboard:
  name: Test Dashboard
  panels:
    - title: Panel 1
      grid: { x: 0, y: 0, w: 24, h: 15 }
      type: markdown
      content: "Test"
"""
        self.temp_file.write_text(yaml_content)

        # Try various invalid panel IDs
        invalid_ids = [
            'panel/../../../etc/passwd',  # Path traversal
            'panel;rm -rf /',  # Command injection attempt
            'panel{test}',  # Special characters
            'panel\nmalicious',  # Newline injection
        ]

        for invalid_id in invalid_ids:
            result = update_panel_grid(str(self.temp_file), invalid_id, {'x': 0, 'y': 0, 'w': 10, 'h': 10})
            self.assertFalse(result['success'], f'Should reject invalid ID: {invalid_id}')
            self.assertIn('Invalid panel ID', result['error'])

    def test_reject_invalid_grid_coordinates(self):
        """Test that invalid grid coordinates are rejected."""
        yaml_content = """dashboard:
  name: Test Dashboard
  panels:
    - title: Panel 1
      grid: { x: 0, y: 0, w: 24, h: 15 }
      type: markdown
      content: "Test"
"""
        self.temp_file.write_text(yaml_content)

        # Test various invalid grid coordinates
        invalid_grids = [
            {'x': -1, 'y': 0, 'w': 10, 'h': 10},  # Negative x
            {'x': 0, 'y': -1, 'w': 10, 'h': 10},  # Negative y
            {'x': 0, 'y': 0, 'w': -10, 'h': 10},  # Negative width
            {'x': 0, 'y': 0, 'w': 10, 'h': -10},  # Negative height
            {'x': 0, 'y': 0, 'h': 10},  # Missing w
            {'x': 0, 'y': 0, 'w': 10},  # Missing h
        ]

        for invalid_grid in invalid_grids:
            result = update_panel_grid(str(self.temp_file), 'panel_0', invalid_grid)
            self.assertFalse(result['success'], f'Should reject invalid grid: {invalid_grid}')
            self.assertIn('Invalid grid', result['error'])


if __name__ == '__main__':
    unittest.main()
