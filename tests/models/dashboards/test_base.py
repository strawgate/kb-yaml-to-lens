from dashboard_compiler.models.dashboard import Dashboard
from dashboard_compiler.models.panels import (
    MarkdownPanel
) 

SAMPLE_GRID_DATA = {"x": 0, "y": 0, "w": 12, "h": 5}

MARKDOWN_PANEL_DATA = {
    "title": "Test Markdown",
    "grid": SAMPLE_GRID_DATA,
    "content": "## Hello",
}

DASHBOARD_EMPTY_DATA = {
    "title": "Empty Dashboard Test",
    "description": "An empty dashboard.",
    "panels": [],
}

DASHBOARD_WITH_PANEL_DATA = {
    "title": "Dashboard With Panel",
    "description": "A dashboard containing one panel.",
    "panels": [MarkdownPanel(**MARKDOWN_PANEL_DATA)],
}


def test_dashboard_instantiation_empty():
    """Tests successful instantiation of an empty Dashboard model."""
    dashboard = Dashboard(**DASHBOARD_EMPTY_DATA)
    assert dashboard.title == "Empty Dashboard Test"
    assert dashboard.description == "An empty dashboard."
    assert dashboard.panels == []


def test_dashboard_instantiation_with_panel():
    """Tests successful instantiation of a Dashboard model with a panel."""
    dashboard = Dashboard(**DASHBOARD_WITH_PANEL_DATA)
    assert dashboard.title == "Dashboard With Panel"
    assert len(dashboard.panels) == 1
    assert isinstance(dashboard.panels[0], MarkdownPanel)
    assert dashboard.panels[0].title == "Test Markdown"


def test_dashboard_to_dict_empty(snapshot_json):
    """Tests the Dashboard.to_dict() method for an empty dashboard."""
    dashboard = Dashboard(**DASHBOARD_EMPTY_DATA)
    dashboard_as_dict = dashboard.to_dict()

    assert dashboard_as_dict["type"] == "dashboard"
    assert dashboard_as_dict.get("attributes") is not None
    assert dashboard_as_dict["attributes"]["title"] == "Empty Dashboard Test"
    assert dashboard_as_dict["attributes"]["description"] == "An empty dashboard."

    assert dashboard_as_dict["attributes"]["panelsJSON"] == "[]"  # Empty panelsJSON should be an empty string

    assert dashboard_as_dict == snapshot_json


def test_dashboard_to_dict_with_panel(snapshot_json):
    """Tests the Dashboard.to_dict() method with a panel."""
    dashboard = Dashboard(**DASHBOARD_WITH_PANEL_DATA)
    dashboard_as_dict = dashboard.to_dict(panels_as_json=False)

    assert dashboard_as_dict["type"] == "dashboard"
    assert dashboard_as_dict.get("attributes") is not None
    assert dashboard_as_dict["attributes"]["title"] == "Dashboard With Panel"
    assert dashboard_as_dict["attributes"]["description"] == "A dashboard containing one panel."
    assert type(dashboard_as_dict["attributes"]["panelsJSON"]) is list
    assert len(dashboard_as_dict["attributes"]["panelsJSON"]) == 1

    first_panel = dashboard_as_dict["attributes"]["panelsJSON"][0]

    assert first_panel["type"] == "visualization"
    assert first_panel["embeddableConfig"]["savedVis"]["title"] == "Test Markdown"
    assert first_panel["embeddableConfig"]["savedVis"]["params"]["markdown"] == "## Hello"

    assert first_panel["gridData"]["w"] == 12
    assert first_panel["gridData"]["h"] == 5
    assert first_panel["gridData"]["x"] == 0
    assert first_panel["gridData"]["y"] == 0

    assert dashboard_as_dict == snapshot_json
