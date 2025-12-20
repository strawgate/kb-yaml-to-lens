"""Test the compilation of links panels from config models to view models."""

import pytest
from deepdiff import DeepDiff
from pydantic import BaseModel

from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.links.compile import compile_links_panel_config
from dashboard_compiler.panels.links.config import LinksPanel
from tests.conftest import DEEP_DIFF_DEFAULTS
from tests.panels.links.test_links_data import (
    TEST_CASE_IDS,
    TEST_CASES,
)

# Define fields to exclude from DeepDiff comparison
EXCLUDE_REGEX_PATHS = [
    # r"root\['panelIndex'\]", # Exclude the panelIndex field
    # r"root\['gridData'\]\['i'\]", # Exclude the gridData.i field
    r"root\['attributes'\]\['links'\]\[\d+\]\['id'\]",  # Exclude link IDs
    # r"root\['embeddableConfig'\]\['attributes'\]\['links'\]\[\d+\]\['destinationRefName'\]", # Exclude destinationRefName for dashboard
    # r"root\[\d+\]\['name'\]", # Exclude reference names
]


class LinksPanelHolder(BaseModel):
    """A holder for LinksPanel configurations to be used in tests."""

    panel: LinksPanel


@pytest.mark.parametrize(('config', 'desired_output', 'desired_references'), TEST_CASES, ids=TEST_CASE_IDS)
async def test_compile_links_panel(config: dict, desired_output: dict, desired_references: list[dict]) -> None:
    """Test the compilation of various LinksPanel configurations to their Kibana view model."""
    panel_grid = Grid(x=0, y=0, w=24, h=10)

    links_panel = LinksPanel(grid=panel_grid, **config)

    kbn_references, kbn_panel_config = compile_links_panel_config(links_panel=links_panel)

    kbn_panel_as_dict = kbn_panel_config.model_dump(by_alias=True)

    assert DeepDiff(desired_output, kbn_panel_as_dict, exclude_regex_paths=EXCLUDE_REGEX_PATHS, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore

    kbn_references_as_dicts = [ref.model_dump(by_alias=True) for ref in kbn_references]

    assert DeepDiff(desired_references, kbn_references_as_dicts, exclude_regex_paths=EXCLUDE_REGEX_PATHS, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore
