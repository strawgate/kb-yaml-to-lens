import uuid
import pytest
import json
import pytest_freezer
import re
from deepdiff import DeepDiff
from syrupy.filters import props
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.json import JSONSnapshotExtension
from syrupy.matchers import path_type # Import matcher utility
from dashboard_compiler.compiler import compile_dashboard, compile_dashboard_to_testable_dict
from dashboard_compiler.models.dashboard import Dashboard

# Regex for ISO 8601 timestamp with milliseconds and Z timezone
ISO_TIMESTAMP_REGEX = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$"
# Regex for standard UUID format
UUID_REGEX = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"

# Define matchers for dynamic fields, including nested panel IDs
matchers = (
    #path_type("id", replacer=lambda *_: "MATCHER_1"),
    #path_type(types=(datetime.datetime,), replacer=lambda *_: "MATCHER_2"),
)

EXCLUDE_PATHS = [
    "root['created_by']",
    "root['updated_at']",
    "root['created_at']",
    "root['id']",
    "root['version']",
    "root['updated_by']",
    "root['attributes']['panelsJSON'][0]['gridData']['i']",
    "root['attributes']['panelsJSON'][0]['panelIndex']"
]

@pytest.mark.parametrize(
        "json_path, yaml_path",
        [
            ("samples/simple/empty-dashboard.json", "configs/simple/empty-dashboard-summary.yaml"),
            ("samples/simple/markdown-only.json", "configs/simple/markdown-only-summary.yaml"),
            ("samples/simple/pie-chart-only.json", "configs/simple/pie-chart-only-summary.yaml"),
            ("samples/simple/vertical-bar-only.json", "configs/simple/vertical-bar-only-summary.yaml"),
            ("samples/complex/1password-audit-events-full-dashboard.json", "configs/complex/audit-events-summary.yaml"),
            ("samples/complex/1password-item-usages-full-dashboard.json", "configs/complex/item-usages-summary.yaml"),
            ("samples/complex/1password-signin-attempts-full-dashboard.json", "configs/complex/signin-attempts-summary.yaml"),
        ], ids=[
            "empty-dashboard",
            "markdown-only-dashboard",
            "pie-chart-only-dashboard",
            "vertical-bar-only-dashboard",
            "audit-events-dashboard",
            "item-usages-dashboard",
            "signin-attempts-dashboard",
        ]
)
def test_dashboard(json_path, yaml_path, snapshot_json: SnapshotAssertion):
    """Tests compiling an empty dashboard configuration."""
    #yaml_path = "configs/simple/empty-dashboard-summary.yaml"
    dashboard_as_yaml = open(yaml_path, 'r').read()
    dashboard = Dashboard.loads(dashboard_as_yaml)
    dashboard_as_dict = dashboard.to_dict(panels_as_json=False)
    dashboard_as_dict_panels_json = dashboard.to_dict(panels_as_json=False)

    assert dashboard_as_dict == snapshot_json

    #json_path = "samples/simple/empty-dashboard.json"
    reference_as_json = open(json_path, 'r').read()
    reference_as_dict_panels_json = json.loads(reference_as_json)
    panels_json = reference_as_dict_panels_json["attributes"]["panelsJSON"]

    if isinstance(panels_json, str):
        reference_as_dict_panels_json["attributes"]["panelsJSON"] = json.loads(panels_json)

    diff = DeepDiff(exclude_paths=EXCLUDE_PATHS, ignore_order=True,threshold_to_diff_deeper=0, t1=reference_as_dict_panels_json, t2=dashboard_as_dict_panels_json)
    assert diff == snapshot_json(name="diff")


# def test_markdown_only_dashboard(snapshot_json):
#     """Tests compiling a dashboard with only a markdown panel."""
#     yaml_path = "configs/simple/markdown-only-summary.yaml"
#     compiled_dict = compile_dashboard_to_testable_dict(yaml_path)
#     assert compiled_dict == snapshot_json

# def test_pie_chart_only_dashboard(snapshot_json):
#     """Tests compiling a dashboard with only a pie chart panel."""
#     yaml_path = "configs/simple/pie-chart-only-summary.yaml"
#     compiled_dict = compile_dashboard_to_testable_dict(yaml_path)
#     assert compiled_dict == snapshot_json

# def test_vertical_bar_only_dashboard(snapshot_json):
#     """Tests compiling a dashboard with only a vertical bar panel."""
#     yaml_path = "configs/simple/vertical-bar-only-summary.yaml"
#     compiled_dict = compile_dashboard_to_testable_dict(yaml_path)
#     assert compiled_dict == snapshot_json

# # --- Complex Configurations ---

# def test_audit_events_dashboard(snapshot_json):
#     """Tests compiling the audit events dashboard configuration."""
#     yaml_path = "configs/complex/audit-events-summary.yaml"
#     compiled_dict = compile_dashboard_to_testable_dict(yaml_path)
#     assert compiled_dict == snapshot_json

# def test_item_usages_dashboard(snapshot_json):
#     """Tests compiling the item usages dashboard configuration."""
#     yaml_path = "configs/complex/item-usages-summary.yaml"
#     compiled_dict = compile_dashboard_to_testable_dict(yaml_path)
#     assert compiled_dict == snapshot_json

# def test_signin_attempts_dashboard(snapshot_json):
#     """Tests compiling the signin attempts dashboard configuration."""
#     yaml_path = "configs/complex/signin-attempts-summary.yaml"
#     compiled_dict = compile_dashboard_to_testable_dict(yaml_path)
#     assert compiled_dict == snapshot_json