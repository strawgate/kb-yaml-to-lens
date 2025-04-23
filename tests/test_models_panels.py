import pytest
import json
from dashboard_compiler.models.base import Grid
from dashboard_compiler.models.panels import (
    Panel, # Added base Panel import
    MarkdownPanel,
    SearchPanel,
    MapPanel,
    MapLayer,
    MapLayerStyle,
)

# --- Sample Data ---

def validate_grid_data(grid_data, reference_grid_data, include_index=True):
    """Validates grid data structure."""
    assert grid_data["x"] == reference_grid_data["x"]
    assert grid_data["y"] == reference_grid_data["y"]
    assert grid_data["w"] == reference_grid_data["w"]
    assert grid_data["h"] == reference_grid_data["h"]
    # Ensure extra fields ('i') are ignored without error

    if include_index:
        assert "i" in grid_data

SAMPLE_GRID_DATA = {"x": 0, "y": 0, "w": 24, "h": 15}


SAMPLE_GRID = Grid(**SAMPLE_GRID_DATA)

# Base Panel Data (moved from test_models_base.py)
SAMPLE_PANEL_DATA = {
    "title": "Sample Panel Title",
    "type": "visualization", # Using a common type for base test
    "grid": SAMPLE_GRID
}


# MarkdownPanel Data (derived from samples/simple/markdown-only.json)
MARKDOWN_CONTENT = "# This is a basic markdown test"
MARKDOWN_PANEL_DATA = {
    "title": "Markdown Test Panel",
    "type": "markdown", # Correct type for MarkdownPanel
    "grid": SAMPLE_GRID,
    "content": MARKDOWN_CONTENT,
}

# SearchPanel Data (mocked based on model, ID from complex sample reference)
SEARCH_PANEL_DATA = {
    "title": "Search Test Panel",
    "type": "search",
    "grid": SAMPLE_GRID,
    "saved_search_id": "1password-signin-attempts", # From complex sample reference
}

# MapPanel Data (derived/simplified from complex sample)
MAP_LAYER_STYLE_DATA = {"type": "VECTOR", "size": 6, "color": "#54B399"}
MAP_LAYER_DATA_1 = { # Base Map Layer (simplified)
    "type": "EMS_VECTOR_TILE",
    "label": None,
    "style": None, # Base maps often have minimal style defined directly
}
MAP_LAYER_DATA_2 = { # Data Layer (simplified)
    "type": "GEOJSON_VECTOR",
    "label": "Source Locations",
    "index_pattern": "logs-*", # Assuming resolved pattern name
    "query": "data_stream.dataset:1password.signin_attempts",
    "geo_field": "source.geo.location",
    "style": MapLayerStyle(**MAP_LAYER_STYLE_DATA),
    "tooltip_fields": ["host.name", "event.action"], # Example tooltip fields
}
MAP_PANEL_DATA = {
    "title": "Map Test Panel",
    "type": "map",
    "grid": SAMPLE_GRID,
    "layers": [MapLayer(**MAP_LAYER_DATA_1), MapLayer(**MAP_LAYER_DATA_2)],
}


# --- Unit Tests ---

# Base Panel Tests (moved from test_models_base.py)
def test_panel_model_instantiation():
    """Tests successful instantiation of the base Panel model."""
    panel = Panel(**SAMPLE_PANEL_DATA)
    assert panel.title == "Sample Panel Title"
    assert panel.type == "visualization"
    assert isinstance(panel.grid, Grid)
    assert panel.grid.x == 0
    assert panel.grid.w == 24

def test_panel_to_dict_placeholder():
    """Tests the base Panel.to_dict() method placeholder."""
    panel = Panel(**SAMPLE_PANEL_DATA)
    rendered_panel = panel.to_dict()

    assert rendered_panel["type"] == "visualization"
    assert "gridData" in rendered_panel
    validate_grid_data(rendered_panel["gridData"], SAMPLE_GRID_DATA, include_index=False)

# Markdown Panel Tests
def test_markdown_panel_instantiation():
    """Tests successful instantiation of the MarkdownPanel model."""
    # Corrected data to use MARKDOWN_PANEL_DATA
    panel = MarkdownPanel(**MARKDOWN_PANEL_DATA)
    assert panel.title == "Markdown Test Panel"
    assert panel.type == "markdown" # Check specific type
    assert panel.content == MARKDOWN_CONTENT
    assert isinstance(panel.grid, Grid)

def test_markdown_panel_to_dict():
    """Tests the MarkdownPanel.to_dict() method."""
    # Corrected data to use MARKDOWN_PANEL_DATA
    panel = MarkdownPanel(**MARKDOWN_PANEL_DATA)
    json_output = panel.to_dict()

    assert json_output["type"] == "visualization" # Outer type for JSON
    validate_grid_data(json_output["gridData"], SAMPLE_GRID_DATA)
    assert "panelIndex" in json_output # Placeholder check
    embed_config = json_output["embeddableConfig"]
    assert embed_config["savedVis"]["type"] == "markdown" # Inner type
    assert embed_config["savedVis"]["title"] == "Markdown Test Panel"
    assert embed_config["savedVis"]["params"]["markdown"] == MARKDOWN_CONTENT
    assert embed_config["savedVis"]["params"]["fontSize"] == 12 # Default check

# Search Panel Tests
def test_search_panel_instantiation():
    """Tests successful instantiation of the SearchPanel model."""
    panel = SearchPanel(**SEARCH_PANEL_DATA)
    assert panel.title == "Search Test Panel"
    assert panel.type == "search"
    assert panel.saved_search_id == "1password-signin-attempts"
    assert isinstance(panel.grid, Grid)

def test_search_panel_to_dict():
    """Tests the SearchPanel.to_dict() method placeholder."""
    panel = SearchPanel(**SEARCH_PANEL_DATA)
    json_output = panel.to_dict()

    assert json_output["type"] == "search"
    validate_grid_data(json_output["gridData"], SAMPLE_GRID_DATA)
    assert "panelIndex" in json_output # Placeholder check
    # Check basic structure based on current placeholder implementation
    assert "embeddableConfig" in json_output
    assert "enhancements" in json_output["embeddableConfig"]
    assert "version" in json_output # Placeholder check

# Map Related Tests
def test_map_layer_style_instantiation():
    """Tests successful instantiation of MapLayerStyle."""
    style = MapLayerStyle(**MAP_LAYER_STYLE_DATA)
    assert style.type == "VECTOR"
    assert style.size == 6
    assert style.color == "#54B399"

def test_map_layer_instantiation():
    """Tests successful instantiation of MapLayer."""
    layer = MapLayer(**MAP_LAYER_DATA_2)
    assert layer.type == "GEOJSON_VECTOR"
    assert layer.label == "Source Locations"
    assert layer.index_pattern == "logs-*"
    assert layer.query == "data_stream.dataset:1password.signin_attempts"
    assert layer.geo_field == "source.geo.location"
    assert isinstance(layer.style, MapLayerStyle)
    assert layer.style.size == 6
    assert layer.tooltip_fields == ["host.name", "event.action"]

def test_map_layer_to_dict():
    """Tests the MapLayer.to_dict() method."""
    layer = MapLayer(**MAP_LAYER_DATA_2)
    json_output = layer.to_dict()

    assert json_output["type"] == "GEOJSON_VECTOR"
    assert json_output["label"] == "Source Locations"
    assert json_output["query"]["query"] == "data_stream.dataset:1password.signin_attempts"
    assert json_output["sourceDescriptor"]["type"] == "ES_SEARCH" # Assumed based on index_pattern
    assert json_output["sourceDescriptor"]["geoField"] == "source.geo.location"
    assert json_output["sourceDescriptor"]["indexPatternRefName"] == "placeholder" # Current placeholder
    assert json_output["index_pattern"] == "logs-*" # Included based on current logic
    assert json_output["style"]["type"] == "VECTOR"
    assert json_output["style"]["size"] == 6
    assert json_output["style"]["color"] == "#54B399"
    assert len(json_output["sourceDescriptor"]["tooltipProperties"]) == 2
    assert json_output["sourceDescriptor"]["tooltipProperties"][0]["field"] == "host.name"
    assert json_output["sourceDescriptor"]["tooltipProperties"][1]["field"] == "event.action"

def test_map_panel_instantiation():
    """Tests successful instantiation of MapPanel."""
    panel = MapPanel(**MAP_PANEL_DATA)
    assert panel.title == "Map Test Panel"
    assert panel.type == "map"
    assert isinstance(panel.grid, Grid)
    assert len(panel.layers) == 2
    assert isinstance(panel.layers[0], MapLayer)
    assert isinstance(panel.layers[1], MapLayer)
    assert panel.layers[1].label == "Source Locations"

def test_map_panel_to_dict():
    """Tests the MapPanel.to_dict() method."""
    panel = MapPanel(**MAP_PANEL_DATA)
    json_output = panel.to_dict()

    assert json_output["type"] == "map"
    validate_grid_data(json_output["gridData"], SAMPLE_GRID_DATA)
    assert "panelIndex" in json_output # Placeholder check
    embed_config = json_output["embeddableConfig"]
    assert embed_config["attributes"]["title"] == "Map Test Panel"
    assert "layerListJSON" in embed_config["attributes"]

    # Verify layerListJSON content
    layer_list = json.loads(embed_config["attributes"]["layerListJSON"])
    assert isinstance(layer_list, list)
    assert len(layer_list) == 2
    # Check some details of the second layer from its to_dict output
    assert layer_list[1]["type"] == "GEOJSON_VECTOR"
    assert layer_list[1]["label"] == "Source Locations"
    assert layer_list[1]["style"]["size"] == 6
    assert layer_list[0]["type"] == "EMS_VECTOR_TILE" # Check first layer type