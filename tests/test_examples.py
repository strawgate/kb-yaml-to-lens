import os
import pytest
import json
from deepdiff import DeepDiff
from syrupy.assertion import SnapshotAssertion
from dashboard_compiler.models.dashboard.base import Dashboard

SCENARIOS_DIR = os.path.join(os.path.dirname(__file__), "scenarios")

CONFIG_FILE = "config.yaml"
KIBANA_EXPORT = "from-kibana.json"

EXCLUDE_PATHS = [
    "root['created_by']",
    "root['updated_at']",
    "root['created_at']",
    "root['id']",
    "root['version']",
    "root['updated_by']",
    "root['attributes']['panelsJSON'][0]['gridData']['i']",
    "root['attributes']['panelsJSON'][0]['panelIndex']",
]


@pytest.mark.parametrize(
    "scenario",
    [
        "1password-audit-events",
        "1password-item-usages",
        "1password-signin-attempts",
        "empty",
        "one-markdown",
        "one-pie-chart",
        "one-vertical-bar",
    ]
)
def test_dashboard(scenario, snapshot_json: SnapshotAssertion):
    """Tests compiling an empty dashboard configuration."""
    
    # Load the scenario-specific dashboard configuration and exported reference
    scenario_dir = os.path.join(SCENARIOS_DIR, scenario) 

    config_path = os.path.join(scenario_dir, CONFIG_FILE)
    exported_path = os.path.join(scenario_dir, KIBANA_EXPORT)

    # Load the config and render a dashboard from it
    dashboard = Dashboard.load(config_path)
    rendered_dashboard = dashboard.model_dump()

    # Compare the rendered dashboard with our snapshot
    assert rendered_dashboard == snapshot_json

    # Load the exported reference dashboard
    reference_dashboard = json.load(open(exported_path, "r"))

    # Sometimes parseJson is a stringified blob
    panels_json = reference_dashboard["attributes"]["panelsJSON"]
    if type(panels_json) is str:
        reference_dashboard["attributes"]["panelsJSON"] = json.loads(panels_json)

    # Compare the rendered dashboard with the exported reference
    diff = DeepDiff(
        exclude_paths=EXCLUDE_PATHS,
        ignore_order=True,
        threshold_to_diff_deeper=0,
        t1=reference_dashboard,
        t2=rendered_dashboard,
        verbose_level=2,
    )

    # This diff represents the differences between our rendered dashboard and the exported reference
    # this isn't necessarily a failure, but we snapshot it to detect changes in the future and as a todo list
    # of things we may need to add support for
    assert diff == snapshot_json(name="diff")
