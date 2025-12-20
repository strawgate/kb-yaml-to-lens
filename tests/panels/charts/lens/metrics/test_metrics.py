"""Test the compilation of Lens metrics from config models to view models."""

from typing import TYPE_CHECKING

import pytest
from deepdiff import DeepDiff
from inline_snapshot import snapshot
from pydantic import BaseModel

from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_metric
from dashboard_compiler.panels.charts.esql.columns.config import ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes
from tests.conftest import DEEP_DIFF_DEFAULTS
from tests.panels.charts.lens.metrics.test_esql_metrics_data import (
    TEST_CASE_IDS_ESQL,
    TEST_CASES_ESQL,
)
from tests.panels.charts.lens.metrics.test_lens_metrics_data import (
    TEST_CASE_IDS_LENS,
    TEST_CASES_LENS,
)

if TYPE_CHECKING:
    from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLFieldMetricColumn
    from dashboard_compiler.panels.charts.lens.columns.view import KbnLensColumnTypes

# Define fields to exclude from DeepDiff comparison
EXCLUDE_REGEX_PATHS = [
    # Add regex paths for fields to exclude, e.g., IDs
    r"root\['columns'\]\[\d+\]\['id'\]",  # Example: Exclude column IDs
    # Refer to links test exclude paths for more ideas
]


class LensMetricHolder(BaseModel):
    """A holder for metrics to be used in tests."""

    metric: LensMetricTypes


async def test_compile_lens_metric_count_with_inline_snapshot() -> None:
    """Test the compilation of a count metric using inline-snapshot (POC)."""
    config = {'aggregation': 'count'}
    metric_holder = LensMetricHolder.model_validate({'metric': config})

    column_id: str
    kbn_column: KbnLensColumnTypes
    column_id, kbn_column = compile_lens_metric(metric=metric_holder.metric)

    assert kbn_column is not None

    kbn_column_as_dict = kbn_column.model_dump()

    # Using inline-snapshot instead of separate data file
    assert kbn_column_as_dict == snapshot(
        {
            'label': 'Count of records',
            'dataType': 'number',
            'operationType': 'count',
            'isBucketed': False,
            'scale': 'ratio',
            'sourceField': '___records___',
            'params': {'emptyAsNull': True},
        }
    )


@pytest.mark.parametrize(('config', 'desired_output'), TEST_CASES_LENS, ids=TEST_CASE_IDS_LENS)
async def test_compile_lens_metric(config: dict, desired_output: dict) -> None:
    """Test the compilation of various Lens metric configurations to their Kibana view model."""
    metric_holder = LensMetricHolder.model_validate({'metric': config})

    column_id: str
    kbn_column: KbnLensColumnTypes
    column_id, kbn_column = compile_lens_metric(metric=metric_holder.metric)

    assert kbn_column is not None

    kbn_column_as_dict = kbn_column.model_dump()

    assert DeepDiff(desired_output, kbn_column_as_dict, exclude_regex_paths=EXCLUDE_REGEX_PATHS, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore


class ESQLMetricHolder(BaseModel):
    """A holder for ESQL metrics to be used in tests."""

    metric: ESQLMetricTypes


@pytest.mark.parametrize(('config', 'desired_output'), TEST_CASES_ESQL, ids=TEST_CASE_IDS_ESQL)
async def test_compile_esql_metric(config: dict, desired_output: dict) -> None:
    """Test the compilation of various ESQL metric configurations to their Kibana view model."""
    metric_holder = ESQLMetricHolder.model_validate({'metric': config})

    kbn_column: KbnESQLFieldMetricColumn = compile_esql_metric(metric=metric_holder.metric)

    assert kbn_column is not None

    kbn_column_as_dict = kbn_column.model_dump()

    assert DeepDiff(desired_output, kbn_column_as_dict, exclude_regex_paths=EXCLUDE_REGEX_PATHS, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore
