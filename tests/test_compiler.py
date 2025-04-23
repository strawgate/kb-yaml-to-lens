import unittest
import json
import os
from dashboard_compiler.compiler import compile_dashboard

class TestDashboardCompiler(unittest.TestCase):

    def test_empty_dashboard(self):
        yaml_path = "configs/empty-dashboard-summary.yaml"
        json_path = "samples/empty dashboard.json"
        with open(json_path, 'r') as f:
            expected_json = json.load(f)
        
        compiled_json_string = compile_dashboard(yaml_path)
        compiled_json = json.loads(compiled_json_string)

        # Basic comparison - might need more sophisticated comparison for real tests
        self.assertEqual(compiled_json["attributes"]["title"], expected_json["attributes"]["title"])
        self.assertEqual(compiled_json["attributes"]["description"], expected_json["attributes"]["description"])
        self.assertEqual(len(compiled_json["attributes"]["panelsJSON"]), len(expected_json["attributes"]["panelsJSON"]))


    def test_markdown_only_dashboard(self):
        yaml_path = "configs/markdown-only-summary.yaml"
        json_path = "samples/markdown-only.json"
        with open(json_path, 'r') as f:
            expected_json = json.load(f)
        
        compiled_json_string = compile_dashboard(yaml_path)
        compiled_json = json.loads(compiled_json_string)

        self.assertEqual(compiled_json["attributes"]["title"], expected_json["attributes"]["title"])
        self.assertEqual(compiled_json["attributes"]["description"], expected_json["attributes"]["description"])
        self.assertEqual(len(compiled_json["attributes"]["panelsJSON"]), len(expected_json["attributes"]["panelsJSON"]))
        # TODO: Add more detailed comparison for panel content


    def test_pie_chart_only_dashboard(self):
        yaml_path = "configs/pie-chart-only-summary.yaml"
        json_path = "samples/pie-chart-only.json"
        with open(json_path, 'r') as f:
            expected_json = json.load(f)
        
        compiled_json_string = compile_dashboard(yaml_path)
        compiled_json = json.loads(compiled_json_string)

        self.assertEqual(compiled_json["attributes"]["title"], expected_json["attributes"]["title"])
        self.assertEqual(compiled_json["attributes"]["description"], expected_json["attributes"]["description"])
        self.assertEqual(len(compiled_json["attributes"]["panelsJSON"]), len(expected_json["attributes"]["panelsJSON"]))
        # TODO: Add more detailed comparison for panel content


    def test_vertical_bar_only_dashboard(self):
        yaml_path = "configs/vertical-bar-only-summary.yaml"
        json_path = "samples/vertical-bar-only.json"
        with open(json_path, 'r') as f:
            expected_json = json.load(f)
        
        compiled_json_string = compile_dashboard(yaml_path)
        compiled_json = json.loads(compiled_json_string)

        self.assertEqual(compiled_json["attributes"]["title"], expected_json["attributes"]["title"])
        self.assertEqual(compiled_json["attributes"]["description"], expected_json["attributes"]["description"])
        self.assertEqual(len(compiled_json["attributes"]["panelsJSON"]), len(expected_json["attributes"]["panelsJSON"]))
        # TODO: Add more detailed comparison for panel content