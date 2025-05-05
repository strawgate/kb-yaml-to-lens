"""Test the compilation of markdown panels from config models to view models."""

import pytest
from deepdiff import DeepDiff

from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.markdown.compile import compile_markdown_panel_config
from dashboard_compiler.panels.markdown.config import MarkdownPanel
from tests.conftest import DEEP_DIFF_DEFAULTS
from tests.panels.markdown.test_markdown_data import (
    TEST_CASE_IDS,
    TEST_CASES,
)

# Define fields to exclude from DeepDiff comparison
EXCLUDE_REGEX_PATHS = [
    r"root\['panelIndex'\]",  # Exclude the panelIndex field
    r"root\['gridData'\]\['i'\]",  # Exclude the gridData.i field
]


@pytest.mark.parametrize(('config', 'desired_output', 'desired_references'), TEST_CASES, ids=TEST_CASE_IDS)
async def test_compile_markdown_panel(config: dict, desired_output: dict, desired_references: list) -> None:
    """Test the compilation of various MarkdownPanel configurations to their Kibana view model."""
    panel_grid = Grid(x=0, y=0, w=24, h=10)

    markdown_panel = MarkdownPanel(grid=panel_grid, **config)

    kbn_references, kbn_panel_config = compile_markdown_panel_config(markdown_panel=markdown_panel)

    kbn_panel_as_dict = kbn_panel_config.model_dump(by_alias=True)

    assert DeepDiff(desired_output, kbn_panel_as_dict, exclude_regex_paths=EXCLUDE_REGEX_PATHS, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore

    kbn_references_as_dicts = [ref.model_dump(by_alias=True) for ref in kbn_references]

    assert DeepDiff(desired_references, kbn_references_as_dicts, exclude_regex_paths=EXCLUDE_REGEX_PATHS, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore
