"""Examples of different patterns to reduce boilerplate in inline-snapshot tests.

This file demonstrates 4 different approaches to the same test suite.
Compare the patterns to decide which works best for this codebase.
"""

from typing import TYPE_CHECKING, Any

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel

from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes

if TYPE_CHECKING:
    from dashboard_compiler.panels.charts.lens.columns.view import KbnLensColumnTypes


class LensMetricHolder(BaseModel):
    """A holder for metrics to be used in tests."""

    metric: LensMetricTypes


# ==============================================================================
# PATTERN 1: Helper Function (Most DRY)
# ==============================================================================
# Pros: Minimal duplication, test cases are just data
# Cons: Stack traces are less clear, harder to run individual test interactively


def _assert_metric_compiles_to_snapshot(config: dict[str, Any], expected_snapshot: dict[str, Any]) -> None:
    """Helper to compile a metric config and assert it matches the snapshot."""
    metric_holder = LensMetricHolder.model_validate({'metric': config})
    column_id, kbn_column = compile_lens_metric(metric=metric_holder.metric)

    assert kbn_column is not None
    kbn_column_as_dict = kbn_column.model_dump()
    assert kbn_column_as_dict == expected_snapshot


async def test_pattern1_count() -> None:
    """Test count metric using helper function pattern."""
    _assert_metric_compiles_to_snapshot(
        config={'aggregation': 'count'},
        expected_snapshot=snapshot(
            {
                'label': 'Count of records',
                'dataType': 'number',
                'operationType': 'count',
                'isBucketed': False,
                'scale': 'ratio',
                'sourceField': '___records___',
                'params': {'emptyAsNull': True},
            }
        ),
    )


async def test_pattern1_sum() -> None:
    """Test sum metric using helper function pattern."""
    _assert_metric_compiles_to_snapshot(
        config={'aggregation': 'sum', 'field': 'aerospike.node.connection.open'},
        expected_snapshot=snapshot(
            {
                'label': 'Sum of aerospike.node.connection.open',
                'dataType': 'number',
                'operationType': 'sum',
                'sourceField': 'aerospike.node.connection.open',
                'isBucketed': False,
                'scale': 'ratio',
                'params': {'emptyAsNull': True},
            }
        ),
    )


# ==============================================================================
# PATTERN 2: Parametrize with inline-snapshot (Compact but snapshots in one place)
# ==============================================================================
# Pros: Very compact, all test cases in one place
# Cons: All snapshots in single test function, harder to update individual cases


@pytest.mark.parametrize(
    ('test_id', 'config'),
    [
        ('count', {'aggregation': 'count'}),
        ('sum', {'aggregation': 'sum', 'field': 'aerospike.node.connection.open'}),
        ('min', {'aggregation': 'min', 'field': 'aerospike.node.connection.open'}),
    ],
)
async def test_pattern2_metrics(test_id: str, config: dict[str, Any]) -> None:
    """Test metrics using parametrize pattern."""
    metric_holder = LensMetricHolder.model_validate({'metric': config})
    column_id, kbn_column = compile_lens_metric(metric=metric_holder.metric)

    assert kbn_column is not None
    kbn_column_as_dict = kbn_column.model_dump()

    # inline-snapshot supports parametrized tests - each parameter gets its own snapshot
    assert kbn_column_as_dict == snapshot(
        {
            'count': {
                'label': 'Count of records',
                'dataType': 'number',
                'operationType': 'count',
                'isBucketed': False,
                'scale': 'ratio',
                'sourceField': '___records___',
                'params': {'emptyAsNull': True},
            },
            'sum': {
                'label': 'Sum of aerospike.node.connection.open',
                'dataType': 'number',
                'operationType': 'sum',
                'sourceField': 'aerospike.node.connection.open',
                'isBucketed': False,
                'scale': 'ratio',
                'params': {'emptyAsNull': True},
            },
            'min': {
                'label': 'Minimum of aerospike.node.connection.open',
                'dataType': 'number',
                'operationType': 'min',
                'sourceField': 'aerospike.node.connection.open',
                'isBucketed': False,
                'scale': 'ratio',
                'params': {'emptyAsNull': True},
            },
        }[test_id]
    )


# ==============================================================================
# PATTERN 3: Fixture for Common Setup (Middle ground)
# ==============================================================================
# Pros: Clear test structure, shared setup via fixture
# Cons: Still some duplication, fixture indirection


@pytest.fixture
def compile_metric_snapshot():
    """Fixture that returns a function to compile metrics and return dict for snapshot."""

    def _compile(config: dict[str, Any]) -> dict[str, Any]:
        metric_holder = LensMetricHolder.model_validate({'metric': config})
        column_id, kbn_column = compile_lens_metric(metric=metric_holder.metric)
        assert kbn_column is not None
        return kbn_column.model_dump()

    return _compile


async def test_pattern3_count(compile_metric_snapshot) -> None:
    """Test count metric using fixture pattern."""
    result = compile_metric_snapshot({'aggregation': 'count'})
    assert result == snapshot(
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


async def test_pattern3_sum(compile_metric_snapshot) -> None:
    """Test sum metric using fixture pattern."""
    result = compile_metric_snapshot({'aggregation': 'sum', 'field': 'aerospike.node.connection.open'})
    assert result == snapshot(
        {
            'label': 'Sum of aerospike.node.connection.open',
            'dataType': 'number',
            'operationType': 'sum',
            'sourceField': 'aerospike.node.connection.open',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {'emptyAsNull': True},
        }
    )


# ==============================================================================
# PATTERN 4: Current approach (Most explicit, most verbose)
# ==============================================================================
# Pros: Very clear, easy to debug, each test is independent
# Cons: Lots of boilerplate repetition


async def test_pattern4_count() -> None:
    """Test the compilation of a count metric - current approach."""
    config = {'aggregation': 'count'}
    metric_holder = LensMetricHolder.model_validate({'metric': config})

    column_id: str
    kbn_column: KbnLensColumnTypes
    column_id, kbn_column = compile_lens_metric(metric=metric_holder.metric)

    assert kbn_column is not None
    kbn_column_as_dict = kbn_column.model_dump()

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


async def test_pattern4_sum() -> None:
    """Test the compilation of a sum metric - current approach."""
    config = {'aggregation': 'sum', 'field': 'aerospike.node.connection.open'}
    metric_holder = LensMetricHolder.model_validate({'metric': config})

    column_id: str
    kbn_column: KbnLensColumnTypes
    column_id, kbn_column = compile_lens_metric(metric=metric_holder.metric)

    assert kbn_column is not None
    kbn_column_as_dict = kbn_column.model_dump()

    assert kbn_column_as_dict == snapshot(
        {
            'label': 'Sum of aerospike.node.connection.open',
            'dataType': 'number',
            'operationType': 'sum',
            'sourceField': 'aerospike.node.connection.open',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {'emptyAsNull': True},
        }
    )
