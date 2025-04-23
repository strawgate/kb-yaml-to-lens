from pydantic import ValidationError
import pytest
from dashboard_compiler.models.panels import Grid
from dashboard_compiler.models.panels.lens.base import (
    LensPanel,
)
from tests.conftest import parse_yaml_string
from tests.models.panels.conftest import SAMPLE_GRID_DATA, SAMPLE_GRID_YAML
# --- Sample Data ---

LENS_PIE_DATA = {
    "title": "Pie Chart Test Panel",
    "type": "lens",
    "visualization": "pie",
    "grid": SAMPLE_GRID_DATA,
    "index_pattern": "metrics-*",
    "query": "",
    "dimensions": [
        {
            "field": "aerospike.namespace",
            "type": "terms",
            "label": "Top 5 values of aerospike.namespace",
            "size": 5,
            "order_by_metric": "Count of records",
            "order_direction": "desc",
        }
    ],
    "metrics": [{"type": "count", "label": "Count of records"}],
    "filters": [],
    "columns": [],
    "palette": None,
}

LENS_PIE_YAML = f"""
title: Pie Chart Test Panel
type: lens
visualization: pie
{SAMPLE_GRID_YAML}
index_pattern: metrics-*
query: ""
dimensions:
  - field: aerospike.namespace
    type: terms
    label: "Top 5 values of aerospike.namespace"
    size: 5
    order_by_metric: "Count of records"
    order_direction: desc
metrics:
  - type: count
    label: "Count of records"
"""

LENS_BAR_DATA = {
    "title": "Vertical Bar Test Panel",
    "type": "lens",
    "visualization": "bar_stacked",
    "grid": SAMPLE_GRID_DATA,
    "index_pattern": "metrics-*",
    "query": "",
    "dimensions": [{"field": "@timestamp", "type": "date_histogram", "label": "@timestamp", "interval": "auto"}],
    "metrics": [{"type": "count", "label": "Count of records"}],
    "filters": [],
    "columns": [],
    "palette": None,
}

LENS_BAR_YAML = f"""
title: Vertical Bar Test Panel
type: lens
visualization: bar_stacked
{SAMPLE_GRID_YAML}
index_pattern: metrics-*
query: ""
dimensions:
  - field: "@timestamp"
    type: date_histogram
    label: "@timestamp"
    interval: auto
metrics:
  - type: count
    label: "Count of records"
"""

# --- Unit Tests ---


class TestLensPanel:
    """Tests for the LensPanel model."""

    @pytest.fixture(params=[LENS_PIE_DATA, parse_yaml_string(LENS_PIE_YAML)])
    async def lens_pie_panel_definition(self, request):
        return request.param

    @pytest.fixture(params=[LENS_BAR_DATA, parse_yaml_string(LENS_BAR_YAML)])
    async def lens_bar_panel_definition(self, request):
        return request.param

    async def test_lens_pie_panel_init(self, lens_pie_panel_definition):
        """Tests successful instantiation of a Lens Pie Panel model from code and YAML."""
        panel = LensPanel(**lens_pie_panel_definition)
        assert panel.title == "Pie Chart Test Panel"
        assert panel.type == "lens"
        assert panel.visualization == "pie"
        assert isinstance(panel.grid, Grid)
        assert panel.index_pattern == "metrics-*"
        assert panel.query == ""
        assert len(panel.dimensions) == 1
        assert panel.dimensions[0].field == "aerospike.namespace"
        assert len(panel.metrics) == 1
        assert panel.metrics[0].type == "count"
        assert len(panel.filters) == 0
        assert len(panel.columns) == 0
        assert panel.palette is None

    async def test_lens_bar_panel_init(self, lens_bar_panel_definition):
        """Tests successful instantiation of a Lens Vertical Bar Panel model from code and YAML."""
        panel = LensPanel(**lens_bar_panel_definition)
        assert panel.title == "Vertical Bar Test Panel"
        assert panel.type == "lens"
        assert panel.visualization == "bar_stacked"
        assert isinstance(panel.grid, Grid)
        assert panel.index_pattern == "metrics-*"
        assert panel.query == ""
        assert len(panel.dimensions) == 1
        assert panel.dimensions[0].field == "@timestamp"
        assert len(panel.metrics) == 1
        assert panel.metrics[0].type == "count"
        assert len(panel.filters) == 0
        assert len(panel.columns) == 0
        assert panel.palette is None

    async def test_missing_fields(self):
        """Tests that LensPanel raises an error when required fields are missing."""
        with pytest.raises(ValidationError, match="visualization\n  Field required"):
            LensPanel(title="Test", type="lens", grid=SAMPLE_GRID_DATA, index_pattern="logs-*")

        with pytest.raises(ValidationError, match="index_pattern\n  Field required"):
            LensPanel(title="Test", type="lens", grid=SAMPLE_GRID_DATA, visualization="pie")

        try:
            LensPanel(title="Test", type="lens", grid=SAMPLE_GRID_DATA, visualization="pie", index_pattern="logs-*")
        except ValidationError as e:
            pytest.fail(f"Unexpected ValidationError raised: {e}")

    @pytest.fixture(params=[LENS_PIE_DATA, parse_yaml_string(LENS_PIE_YAML), LENS_BAR_DATA, parse_yaml_string(LENS_BAR_YAML)])
    async def lens_panel_definition_all(self, request):
        return request.param

    async def test_lens_panel_serialization(self, lens_panel_definition_all, snapshot_json):
        """Tests the LensPanel.to_json() method."""
        panel = LensPanel(**lens_panel_definition_all)
        json_output = panel.to_json()
        assert json_output == snapshot_json
