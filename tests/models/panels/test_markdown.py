from pydantic import ValidationError
import pytest
from dashboard_compiler.models.panels import MarkdownPanel
from tests.conftest import parse_yaml_string
from tests.models.panels.conftest import SAMPLE_GRID_DATA, SAMPLE_GRID_YAML


PANEL_FROM_YAML = parse_yaml_string(f"""
title: Markdown Test Panel
type: markdown
{SAMPLE_GRID_YAML}
content: |
  # Header
  this is the header
  # Body
  this is the body
  # Footer
  this is the footer""")

PANEL_FROM_DICT = {
    "title": "Markdown Test Panel",
    "type": "markdown",
    "grid": SAMPLE_GRID_DATA,
    "content": "# Header\nthis is the header\n# Body\nthis is the body\n# Footer\nthis is the footer",
}


class TestMarkdownPanel:
    """Tests for the MarkdownPanel model."""

    async def test_yaml_and_dict_equivalence(self):
        """Tests that the YAML and dictionary definitions of the MarkdownPanel are equivalent."""
        yaml_sourced_panel = PANEL_FROM_YAML
        dict_sourced_panel = PANEL_FROM_DICT

        assert yaml_sourced_panel == dict_sourced_panel, "YAML and dictionary definitions should be equivalent"

    @pytest.fixture()
    async def markdown_panel_definition(self, sample_grid_data):
        return {
            "title": "Markdown Test Panel",
            "type": "markdown",
            "grid": sample_grid_data,
            "content": "# Header\nthis is the header\n# Body\nthis is the body\n# Footer\nthis is the footer",
        }

    async def test_missing_fields(self, sample_grid_data):
        """Tests that MarkdownPanel raises an error when required fields are missing."""
        with pytest.raises(ValidationError, match="content\n  Field required"):
            MarkdownPanel(title="Markdown Test Panel", type="markdown", grid=sample_grid_data)

        with pytest.raises(ValidationError, match="title\n  Field required"):
            MarkdownPanel(content="# Header", type="markdown", grid=sample_grid_data)

        try:
            MarkdownPanel(title="Markdown Test Panel", content="# Header", grid=sample_grid_data)
        except ValidationError as e:
            pytest.fail(f"Unexpected ValidationError raised: {e}")

    async def test_font_size(self):
        """Tests that the MarkdownPanel model accepts font_size as an optional field."""
        panel = MarkdownPanel(
            title="Markdown Test Panel",
            type="markdown",
            grid=SAMPLE_GRID_DATA,
            content="# Header\nthis is the header\n# Body\nthis is the body\n# Footer\nthis is the footer",
            font_size=16,
        )

        assert panel.font_size == 16, "Font size should be set to 16"

        serialized_panel = panel.model_dump()

        assert serialized_panel["embeddableConfig"]["savedVis"]["params"]["fontSize"] == 16, (
            "Serialized font size should match the input value"
        )

    async def test_open_links_in_new_tab(self):
        """Tests that the MarkdownPanel model accepts open_links_in_new_tab as an optional field."""

        panel = MarkdownPanel(
            title="Markdown Test Panel",
            type="markdown",
            grid=SAMPLE_GRID_DATA,
            content="# Header\nthis is the header\n# Body\nthis is the body\n# Footer\nthis is the footer",
            open_links_in_new_tab=True,
        )

        assert panel.open_links_in_new_tab is True, "open_links_in_new_tab should be set to True"

        serialized_panel = panel.model_dump()

        assert serialized_panel["embeddableConfig"]["savedVis"]["params"]["openLinksInNewTab"] is True, (
            "Serialized open_links_in_new_tab should match the input value"
        )

    class TestSerDes:
        """Tests for instantiation, serialization, and deserialization of the MarkdownPanel model."""

        @pytest.fixture(params=[PANEL_FROM_YAML, PANEL_FROM_DICT])
        async def panel_definition(self, request):
            return request.param

        async def test_markdown_panel_init(self, panel_definition, sample_grid_data):
            panel = MarkdownPanel(**panel_definition)

            assert panel.title == "Markdown Test Panel"
            assert panel.type == "markdown"
            assert panel.content == "# Header\nthis is the header\n# Body\nthis is the body\n# Footer\nthis is the footer"

            assert panel.grid.h == sample_grid_data["h"]
            assert panel.grid.w == sample_grid_data["w"]
            assert panel.grid.x == sample_grid_data["x"]
            assert panel.grid.y == sample_grid_data["y"]

        async def test_markdown_panel_serialization(self, panel_definition, snapshot_json):
            """Tests the MarkdownPanel.model_dump() method."""
            panel = MarkdownPanel(**panel_definition)
            output = panel.model_dump()

            assert output == snapshot_json
