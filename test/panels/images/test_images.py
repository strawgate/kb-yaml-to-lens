"""Test the compilation of image panels from config models to view models."""

import pytest
from deepdiff import DeepDiff

from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.images.compile import compile_image_panel_config
from dashboard_compiler.panels.images.config import ImagePanel
from test.conftest import DEEP_DIFF_DEFAULTS
from test.panels.images.test_images_data import (
    TEST_CASE_IDS,
    TEST_CASES,
)

# Define fields to exclude from DeepDiff comparison
EXCLUDE_REGEX_PATHS = [
    r"root\['panelIndex'\]",  # Exclude the panelIndex field
    r"root\['gridData'\]\['i'\]",  # Exclude the gridData.i field
]


@pytest.mark.parametrize(('config', 'desired_output'), TEST_CASES, ids=TEST_CASE_IDS)
async def test_compile_image_panel(config: dict, desired_output: dict) -> None:
    """Test the compilation of various ImagePanel configurations to their Kibana view model."""
    panel_grid = Grid(x=0, y=0, w=24, h=10)

    image_panel = ImagePanel(grid=panel_grid, **config)

    _, kbn_panel_config = compile_image_panel_config(image_panel=image_panel)

    kbn_panel_as_dict = kbn_panel_config.model_dump(by_alias=True)

    assert DeepDiff(desired_output, kbn_panel_as_dict, exclude_regex_paths=EXCLUDE_REGEX_PATHS, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore
