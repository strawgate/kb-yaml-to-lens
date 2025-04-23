from pydantic import ValidationError
import pytest
from dashboard_compiler.models.panels import Grid
from dashboard_compiler.models.panels.map import MapPanel, MapLayer, MapLayerStyle
from tests.conftest import parse_yaml_string
from tests.models.panels.conftest import SAMPLE_GRID_DATA, SAMPLE_GRID_YAML

# --- Sample Data ---

MAP_LAYER_STYLE_DATA = {"type": "VECTOR", "size": 6, "color": "#54B399"}

MAP_LAYER_DATA_1 = {
    "type": "EMS_VECTOR_TILE",
    "label": None,
}
MAP_LAYER_DATA_2 = {
    "type": "GEOJSON_VECTOR",
    "label": "Source Locations",
    "index_pattern": "logs-*",
    "query": "data_stream.dataset:1password.signin_attempts",
    "geo_field": "source.geo.location",
    "style": MAP_LAYER_STYLE_DATA,  # Use dictionary for instantiation tests
    "tooltip_fields": ["host.name", "event.action"],
}

MAP_PANEL_DATA = {
    "title": "Map Test Panel",
    "type": "map",
    "grid": SAMPLE_GRID_DATA,
    "layers": [MAP_LAYER_DATA_1, MAP_LAYER_DATA_2],  # Use dictionaries for instantiation tests
}

MAP_PANEL_YAML = f"""
title: Map Test Panel
type: map
{SAMPLE_GRID_YAML}
layers:
  - type: EMS_VECTOR_TILE
  - type: GEOJSON_VECTOR
    label: Source Locations
    index_pattern: logs-*
    query: data_stream.dataset:1password.signin_attempts
    geo_field: source.geo.location
    style:
      type: VECTOR
      size: 6
      color: "#54B399"
    tooltip_fields:
      - host.name
      - event.action
"""

# --- Unit Tests ---


class TestMapLayerStyle:
    """Tests for the MapLayerStyle model."""

    @pytest.fixture()
    async def map_layer_style_definition(self):
        return MAP_LAYER_STYLE_DATA

    async def test_map_layer_style_init(self, map_layer_style_definition):
        """Tests successful instantiation of MapLayerStyle from code."""
        style = MapLayerStyle(**map_layer_style_definition)
        assert style.type == "VECTOR"
        assert style.size == 6
        assert style.color == "#54B399"

    async def test_missing_fields(self):
        """Tests that MapLayerStyle raises an error when required fields are missing."""
        with pytest.raises(ValidationError, match="type\n  Field required"):
            MapLayerStyle(size=6, color="#54B399")

        try:
            MapLayerStyle(type="VECTOR", size=6, color="#54B399")
        except ValidationError as e:
            pytest.fail(f"Unexpected ValidationError raised: {e}")

    async def test_map_layer_style_serialization(self, map_layer_style_definition, snapshot_json):
        """Tests the MapLayerStyle.to_json() method."""
        style = MapLayerStyle(**map_layer_style_definition)
        json_output = style.to_json()
        assert json_output == snapshot_json


class TestMapLayer:
    """Tests for the MapLayer model."""

    @pytest.fixture(params=[MAP_LAYER_DATA_2, parse_yaml_string(MAP_PANEL_YAML)["layers"][1]])
    async def map_layer_definition(self, request):
        return request.param

    async def test_map_layer_init(self, map_layer_definition):
        """Tests successful instantiation of MapLayer from code and YAML."""
        layer = MapLayer(**map_layer_definition)
        assert layer.type == "GEOJSON_VECTOR"
        assert layer.label == "Source Locations"
        assert layer.index_pattern == "logs-*"
        assert layer.query == "data_stream.dataset:1password.signin_attempts"
        assert layer.geo_field == "source.geo.location"
        assert isinstance(layer.style, MapLayerStyle)
        assert layer.style.size == 6
        assert layer.tooltip_fields == ["host.name", "event.action"]

    async def test_missing_fields(self):
        """Tests that MapLayer raises an error when required fields are missing."""
        with pytest.raises(ValidationError, match="type\n  Field required"):
            MapLayer(label="Test Layer")

        try:
            MapLayer(type="GEOJSON_VECTOR", label="Test Layer")
        except ValidationError as e:
            pytest.fail(f"Unexpected ValidationError raised: {e}")

    async def test_map_layer_serialization(self, map_layer_definition, snapshot_json):
        """Tests the MapLayer.to_json() method."""
        layer = MapLayer(**map_layer_definition)
        json_output = layer.to_json()
        assert json_output == snapshot_json


class TestMapPanel:
    """Tests for the MapPanel model."""

    @pytest.fixture(params=[MAP_PANEL_DATA, parse_yaml_string(MAP_PANEL_YAML)])
    async def map_panel_definition(self, request):
        return request.param

    async def test_map_panel_init(self, map_panel_definition):
        """Tests successful instantiation of MapPanel from code and YAML."""
        panel = MapPanel(**map_panel_definition)
        assert panel.title == "Map Test Panel"
        assert panel.type == "map"
        assert isinstance(panel.grid, Grid)
        assert len(panel.layers) == 2
        assert isinstance(panel.layers[0], MapLayer)
        assert isinstance(panel.layers[1], MapLayer)
        assert panel.layers[1].label == "Source Locations"

    async def test_missing_fields(self):
        """Tests that MapPanel raises an error when required fields are missing."""
        with pytest.raises(ValidationError, match="layers\n  Field required"):
            MapPanel(title="Map Test Panel", type="map", grid=SAMPLE_GRID_DATA)

        try:
            MapPanel(title="Map Test Panel", type="map", grid=SAMPLE_GRID_DATA, layers=[])
        except ValidationError as e:
            pytest.fail(f"Unexpected ValidationError raised: {e}")

    async def test_map_panel_serialization(self, map_panel_definition, snapshot_json):
        """Tests the MapPanel.to_json() method."""
        panel = MapPanel(**map_panel_definition)
        json_output = panel.to_json()
        assert json_output == snapshot_json
