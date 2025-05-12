"""Test the compilation of Lens metrics from config models to view models."""

from typing import TYPE_CHECKING

import pytest
from deepdiff import DeepDiff
from pydantic import BaseModel

from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.lens.metrics.config import LensFormulaMetric
from tests.conftest import DEEP_DIFF_DEFAULTS
from tests.panels.charts.lens.formulas.test_lens_formulas_data import (
    TEST_CASE_IDS,
    TEST_CASES,
)

if TYPE_CHECKING:
    #    from dashboard_compiler.panels.charts.esql.columns.view import KbnLensFormulaMetric
    from dashboard_compiler.panels.charts.lens.columns.view import KbnLensColumnTypes

# Define fields to exclude from DeepDiff comparison
EXCLUDE_REGEX_PATHS = [
    # Add regex paths for fields to exclude, e.g., IDs
    r"root\['columns'\]\[\d+\]\['id'\]",  # Example: Exclude column IDs
    # Refer to links test exclude paths for more ideas
]


class LensFormulaMetricHolder(BaseModel):
    """A holder for metrics to be used in tests."""

    formula: LensFormulaMetric


@pytest.mark.parametrize(('config', 'desired_output'), TEST_CASES, ids=TEST_CASE_IDS)
async def test_compile_lens_formula(config: dict, desired_output: dict) -> None:
    """Test the compilation of various Lens metric configurations to their Kibana view model."""
    metric_holder = LensFormulaMetricHolder.model_validate(**config)

    column_id: str
    kbn_column: KbnLensColumnTypes
    column_id, kbn_column = compile_lens_metric(metric=metric_holder.formula)

    assert kbn_column is not None

    kbn_column_as_dict = kbn_column.model_dump()

    assert DeepDiff(desired_output, kbn_column_as_dict, exclude_regex_paths=EXCLUDE_REGEX_PATHS, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore
