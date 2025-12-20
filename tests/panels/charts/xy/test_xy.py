"""Test the compilation of Lens metrics from config models to view models."""

import pytest
from deepdiff import DeepDiff
from pydantic import BaseModel

from dashboard_compiler.panels.charts.xy.compile import compile_esql_xy_chart, compile_lens_xy_chart
from dashboard_compiler.panels.charts.xy.config import ESQLXYChartTypes, LensXYChartTypes
from tests.conftest import DEEP_DIFF_DEFAULTS
from tests.panels.charts.xy.test_xy_data import (
    TEST_CASE_IDS,
    TEST_CASES,
)

# Define fields to exclude from DeepDiff comparison
EXCLUDE_REGEX_PATHS = [
    # Add regex paths for fields to exclude, e.g., IDs
    # r"root\['columns'\]\[\d+\]\['id'\]",  # Example: Exclude column IDs
    r"root\['layerId'\]",
    # Refer to links test exclude paths for more ideas
]


class LensXYChartHolder(BaseModel):
    """Holder for Lens XY chart."""

    chart: LensXYChartTypes


class ESQLXYChartHolder(BaseModel):
    """Holder for ESQL XY chart."""

    chart: ESQLXYChartTypes


@pytest.mark.parametrize(('in_lens_config', 'in_esql_config', 'out_layer'), TEST_CASES, ids=TEST_CASE_IDS)
async def test_compile_xy(in_lens_config: dict, in_esql_config: dict, out_layer: dict) -> None:
    """Test the compilation of various Lens xy configurations to their Kibana view model."""
    lens_chart = LensXYChartHolder.model_validate({'chart': in_lens_config})

    layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart.chart)

    assert kbn_state_visualization is not None

    kbn_state_visualization_layer = kbn_state_visualization.layers[0]

    kbn_state_visualization_layer_as_dict = kbn_state_visualization_layer.model_dump()

    assert DeepDiff(out_layer, kbn_state_visualization_layer_as_dict, exclude_regex_paths=EXCLUDE_REGEX_PATHS, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore

    esql_chart = ESQLXYChartHolder.model_validate({'chart': in_esql_config})

    layer_id, kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart.chart)

    assert kbn_state_visualization is not None

    kbn_state_visualization_layer = kbn_state_visualization.layers[0]

    kbn_state_visualization_layer_as_dict = kbn_state_visualization_layer.model_dump()

    assert DeepDiff(out_layer, kbn_state_visualization_layer_as_dict, exclude_regex_paths=EXCLUDE_REGEX_PATHS, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore
