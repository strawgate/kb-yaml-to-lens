"""Test the compilation of tagcloud charts from config models to view models."""

import pytest
from deepdiff import DeepDiff

from dashboard_compiler.panels.charts.tagcloud.compile import compile_esql_tagcloud_chart, compile_lens_tagcloud_chart
from dashboard_compiler.panels.charts.tagcloud.config import ESQLTagcloudChart, LensTagcloudChart
from tests.conftest import DEEP_DIFF_DEFAULTS
from tests.panels.charts.tagcloud.test_tagcloud_data import (
    TEST_CASE_IDS,
    TEST_CASES,
)

# Define fields to exclude from DeepDiff comparison
EXCLUDE_REGEX_PATHS = [
    r"root\['layerId'\]",
]


@pytest.mark.parametrize(('in_lens_config', 'in_esql_config', 'out_lens_shape', 'out_layer'), TEST_CASES, ids=TEST_CASE_IDS)
async def test_compile_tagcloud(in_lens_config: dict, in_esql_config: dict, out_lens_shape: dict, out_layer: dict) -> None:  # noqa: ARG001
    """Test the compilation of various tagcloud configurations to their Kibana view model."""
    lens_chart = LensTagcloudChart.model_validate(in_lens_config)

    layer_id, kbn_columns, kbn_state_visualization = compile_lens_tagcloud_chart(chart=lens_chart)

    assert kbn_state_visualization is not None

    kbn_state_visualization_layer = kbn_state_visualization.layers[0]

    kbn_state_visualization_layer_as_dict = kbn_state_visualization_layer.model_dump()

    assert DeepDiff(out_layer, kbn_state_visualization_layer_as_dict, exclude_regex_paths=EXCLUDE_REGEX_PATHS, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore

    esql_chart = ESQLTagcloudChart.model_validate(in_esql_config)

    layer_id, kbn_columns, kbn_state_visualization = compile_esql_tagcloud_chart(chart=esql_chart)

    assert kbn_state_visualization is not None

    kbn_state_visualization_layer = kbn_state_visualization.layers[0]

    kbn_state_visualization_layer_as_dict = kbn_state_visualization_layer.model_dump()

    assert DeepDiff(out_layer, kbn_state_visualization_layer_as_dict, exclude_regex_paths=EXCLUDE_REGEX_PATHS, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore
