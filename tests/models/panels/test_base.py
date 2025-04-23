from pydantic import ValidationError
import pytest
from dashboard_compiler.models.panels import Panel, Grid
from tests.conftest import parse_yaml_string
from tests.models.panels.conftest import SAMPLE_GRID_DATA

SAMPLE_PANEL_DATA = {
    "title": "Sample Panel Title",
    "type": "visualization",
    "grid": SAMPLE_GRID_DATA,
}

SAMPLE_PANEL_YAML = """
title: Sample Panel Title
type: visualization
grid:
  x: 0
  y: 0
  w: 24
  h: 15
"""


class TestGrid:
    """Tests for the Grid model."""

    async def test_grid_model_instantiation(self):
        """Tests successful instantiation of the Grid model."""
        grid = Grid(**SAMPLE_GRID_DATA)
        assert grid.x == 0
        assert grid.y == 0
        assert grid.w == 24
        assert grid.h == 15

    async def test_missing_fields(self):
        """Tests that Grid raises an error when required fields are missing."""
        with pytest.raises(ValidationError, match="x\n  Field required"):
            Grid(y=0, w=24, h=15)

        with pytest.raises(ValidationError, match="y\n  Field required"):
            Grid(x=0, w=24, h=15)

        with pytest.raises(ValidationError, match="w\n  Field required"):
            Grid(x=0, y=0, h=15)

        with pytest.raises(ValidationError, match="h\n  Field required"):
            Grid(x=0, y=0, w=24)

        try:
            Grid(x=0, y=0, w=24, h=15)

        except ValidationError as e:
            pytest.fail(f"Unexpected ValidationError raised: {e}")


class TestPanel:
    """Tests for the base Panel model."""

    @pytest.fixture(params=[SAMPLE_PANEL_DATA, parse_yaml_string(SAMPLE_PANEL_YAML)])
    async def panel_definition(self, request):
        return request.param

    async def test_panel_model_init(self, panel_definition):
        """Tests successful instantiation of the base Panel model from code and YAML."""
        panel = Panel(**panel_definition)
        assert panel.title == "Sample Panel Title"
        assert panel.type == "visualization"

        assert type(panel.grid) is Grid

        assert panel.grid.x == SAMPLE_GRID_DATA["x"]
        assert panel.grid.y == SAMPLE_GRID_DATA["y"]
        assert panel.grid.w == SAMPLE_GRID_DATA["w"]
        assert panel.grid.h == SAMPLE_GRID_DATA["h"]

    async def test_missing_fields(self):
        """Tests that Panel raises an error when required fields are missing."""
        with pytest.raises(ValidationError, match="title\n  Field required"):
            Panel(type="visualization", grid=SAMPLE_GRID_DATA)

        with pytest.raises(ValidationError, match="type\n  Field required"):
            Panel(title="Sample Panel Title", grid=SAMPLE_GRID_DATA)

        with pytest.raises(ValidationError, match="grid\n  Field required"):
            Panel(title="Sample Panel Title", type="visualization")

        try:
            Panel(title="Sample Panel Title", type="visualization", grid=SAMPLE_GRID_DATA)

        except ValidationError as e:
            pytest.fail(f"Unexpected ValidationError raised: {e}")

    async def test_panel_serialization(self, panel_definition, snapshot_json):
        """Tests the base Panel.to_json() method placeholder."""
        panel = Panel(**panel_definition)

        json_output = panel.model_dump()

        assert json_output == snapshot_json
