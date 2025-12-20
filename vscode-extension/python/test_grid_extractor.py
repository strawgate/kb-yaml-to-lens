#!/usr/bin/env python3
"""Unit tests for grid_extractor.py"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path for importing
sys.path.insert(0, str(Path(__file__).parent))
from grid_extractor import extract_grid_layout


class TestGridExtractor(unittest.TestCase):
    """Test grid extraction from YAML dashboard files."""

    def setUp(self):
        """Create temporary test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = Path(self.temp_dir) / "test_dashboard.yaml"

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_extract_simple_dashboard(self):
        """Test extracting grid info from a simple dashboard."""
        yaml_content = """dashboard:
  name: Test Dashboard
  description: A test dashboard
  panels:
    - title: Panel 1
      type: markdown
      grid: { x: 0, y: 0, w: 24, h: 15 }
      markdown: "Test content"
    - title: Panel 2
      type: lens
      grid: { x: 24, y: 0, w: 24, h: 15 }
"""
        self.temp_file.write_text(yaml_content)

        result = extract_grid_layout(str(self.temp_file))

        self.assertEqual(result["title"], "Test Dashboard")
        self.assertEqual(result["description"], "A test dashboard")
        self.assertEqual(len(result["panels"]), 2)

        # Check first panel
        panel1 = result["panels"][0]
        self.assertEqual(panel1["title"], "Panel 1")
        self.assertEqual(panel1["type"], "markdown")
        self.assertEqual(panel1["grid"]["x"], 0)
        self.assertEqual(panel1["grid"]["y"], 0)
        self.assertEqual(panel1["grid"]["w"], 24)
        self.assertEqual(panel1["grid"]["h"], 15)

    def test_extract_dashboard_with_panel_ids(self):
        """Test extracting grid info when panels have explicit IDs."""
        yaml_content = """dashboard:
  name: Test Dashboard
  panels:
    - id: my-panel-1
      title: Panel with ID
      type: metric
      grid: { x: 0, y: 0, w: 12, h: 8 }
"""
        self.temp_file.write_text(yaml_content)

        result = extract_grid_layout(str(self.temp_file))

        self.assertEqual(len(result["panels"]), 1)
        panel = result["panels"][0]
        self.assertEqual(panel["id"], "my-panel-1")

    def test_extract_dashboard_without_panel_ids(self):
        """Test that panels without IDs get auto-generated IDs."""
        yaml_content = """dashboard:
  name: Test Dashboard
  panels:
    - title: No ID Panel
      type: markdown
      grid: { x: 0, y: 0, w: 24, h: 15 }
      markdown: "Test"
"""
        self.temp_file.write_text(yaml_content)

        result = extract_grid_layout(str(self.temp_file))

        panel = result["panels"][0]
        self.assertEqual(panel["id"], "panel_0")

    def test_extract_dashboard_missing_title(self):
        """Test handling of panels without titles."""
        yaml_content = """dashboard:
  name: Test Dashboard
  panels:
    - type: markdown
      grid: { x: 0, y: 0, w: 24, h: 15 }
      markdown: "Test"
"""
        self.temp_file.write_text(yaml_content)

        result = extract_grid_layout(str(self.temp_file))

        panel = result["panels"][0]
        self.assertEqual(panel["title"], "Untitled Panel")

    def test_extract_nonexistent_file(self):
        """Test that extracting from a nonexistent file raises an error."""
        with self.assertRaises(Exception):
            extract_grid_layout("/nonexistent/file.yaml")

    def test_extract_invalid_yaml(self):
        """Test that invalid YAML raises an error."""
        self.temp_file.write_text("invalid: yaml: content: [[[")

        with self.assertRaises(Exception):
            extract_grid_layout(str(self.temp_file))


if __name__ == "__main__":
    unittest.main()
