from pydantic import ValidationError
import pytest
from dashboard_compiler.models.panels import Grid
from dashboard_compiler.models.panels.search import SearchPanel
from tests.conftest import parse_yaml_string
from tests.models.panels.conftest import SAMPLE_GRID_DATA, SAMPLE_GRID_YAML

# --- Sample Data ---

SEARCH_PANEL_DATA = {
    "title": "Search Test Panel",
    "type": "search",
    "grid": SAMPLE_GRID_DATA,
    "saved_search_id": "1password-signin-attempts",
}

SEARCH_PANEL_YAML = f"""
title: Search Test Panel
type: search
{SAMPLE_GRID_YAML}
saved_search_id: 1password-signin-attempts
"""


class TestSearchPanel:
    """Tests for the SearchPanel model."""

    async def test_missing_fields(self):
        """Tests that SearchPanel raises an error when required fields are missing."""
        with pytest.raises(ValidationError, match="saved_search_id\n  Field required"):
            SearchPanel(title="Search Test Panel", type="search", grid=SAMPLE_GRID_DATA)

        with pytest.raises(ValidationError, match="title\n  Field required"):
            SearchPanel(type="search", grid=SAMPLE_GRID_DATA, saved_search_id="some_id")

        try:
            SearchPanel(title="Search Test Panel", type="search", grid=SAMPLE_GRID_DATA, saved_search_id="some_id")
        except ValidationError as e:
            pytest.fail(f"Unexpected ValidationError raised: {e}")

    class TestSerDes:
        @pytest.fixture(params=[SEARCH_PANEL_DATA, parse_yaml_string(SEARCH_PANEL_YAML)])
        async def search_panel_definition(self, request):
            return request.param

        async def test_search_panel_init(self, search_panel_definition):
            """Tests successful instantiation of the SearchPanel model from code and YAML."""
            panel = SearchPanel(**search_panel_definition)

            assert panel.title == "Search Test Panel"
            assert panel.type == "search"
            assert panel.saved_search_id == "1password-signin-attempts"

            assert isinstance(panel.grid, Grid)

        async def test_search_panel_serialization(self, search_panel_definition, snapshot_json):
            """Tests the SearchPanel.to_json() method."""
            panel = SearchPanel(**search_panel_definition)
            json_output = panel.model_dump()

            assert False #json_output["embeddableConfig"] != {"enhancements": {}}

            assert json_output == snapshot_json
