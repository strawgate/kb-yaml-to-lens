"""Test the compilation of Lens metrics from config models to view models."""

from typing import TYPE_CHECKING

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel

from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_metric
from dashboard_compiler.panels.charts.esql.columns.config import ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes

if TYPE_CHECKING:
    from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLFieldMetricColumn
    from dashboard_compiler.panels.charts.lens.columns.view import KbnLensColumnTypes


class LensMetricHolder(BaseModel):
    """A holder for metrics to be used in tests."""

    metric: LensMetricTypes


async def test_compile_lens_metric_count() -> None:
    """Test the compilation of a count metric."""
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


async def test_compile_lens_metric_sum() -> None:
    """Test the compilation of a sum metric."""
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


async def test_compile_lens_metric_sum_number_format() -> None:
    """Test the compilation of a sum metric with number format."""
    config = {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'number'}}
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
            'params': {'format': {'id': 'number', 'params': {'decimals': 2}}, 'emptyAsNull': True},
        }
    )


async def test_compile_lens_metric_sum_percent_format() -> None:
    """Test the compilation of a sum metric with percent format."""
    config = {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'percent'}}
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
            'params': {'format': {'id': 'percent', 'params': {'decimals': 2}}, 'emptyAsNull': True},
        }
    )


async def test_compile_lens_metric_sum_bytes_format() -> None:
    """Test the compilation of a sum metric with bytes format."""
    config = {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'bytes'}}
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
            'params': {'format': {'id': 'bytes', 'params': {'decimals': 2}}, 'emptyAsNull': True},
        }
    )


async def test_compile_lens_metric_sum_bits_format() -> None:
    """Test the compilation of a sum metric with bits format."""
    config = {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'bits'}}
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
            'params': {'format': {'id': 'bits', 'params': {'decimals': 0}}, 'emptyAsNull': True},
        }
    )


async def test_compile_lens_metric_sum_duration_format() -> None:
    """Test the compilation of a sum metric with duration format."""
    config = {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'duration'}}
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
            'params': {'format': {'id': 'duration', 'params': {'decimals': 0}}, 'emptyAsNull': True},
        }
    )


async def test_compile_lens_metric_sum_custom_format() -> None:
    """Test the compilation of a sum metric with custom format."""
    config = {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'custom', 'pattern': '0,0.[0000]'}}
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
            'params': {'format': {'id': 'custom', 'params': {'decimals': 0, 'pattern': '0,0.[0000]'}}, 'emptyAsNull': True},
        }
    )


async def test_compile_lens_metric_sum_number_format_with_suffix() -> None:
    """Test the compilation of a sum metric with number format and suffix."""
    config = {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'number', 'suffix': 'KB'}}
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
            'params': {'format': {'id': 'number', 'params': {'decimals': 2, 'suffix': 'KB'}}, 'emptyAsNull': True},
        }
    )


async def test_compile_lens_metric_sum_number_format_with_compact() -> None:
    """Test the compilation of a sum metric with number format and compact."""
    config = {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'number', 'compact': True}}
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
            'params': {'format': {'id': 'number', 'params': {'decimals': 2, 'compact': True}}, 'emptyAsNull': True},
        }
    )


async def test_compile_lens_metric_last_value() -> None:
    """Test the compilation of a last value metric."""
    config = {'aggregation': 'last_value', 'field': 'aerospike.namespace.query.count'}
    metric_holder = LensMetricHolder.model_validate({'metric': config})

    column_id: str
    kbn_column: KbnLensColumnTypes
    column_id, kbn_column = compile_lens_metric(metric=metric_holder.metric)

    assert kbn_column is not None
    kbn_column_as_dict = kbn_column.model_dump()

    assert kbn_column_as_dict == snapshot(
        {
            'label': 'Last value of aerospike.namespace.query.count',
            'dataType': 'number',
            'operationType': 'last_value',
            'isBucketed': False,
            'scale': 'ratio',
            'sourceField': 'aerospike.namespace.query.count',
            'filter': {'query': '"aerospike.namespace.query.count": *', 'language': 'kuery'},
            'params': {'sortField': '@timestamp'},
        }
    )


async def test_compile_lens_metric_min() -> None:
    """Test the compilation of a min metric."""
    config = {'aggregation': 'min', 'field': 'aerospike.node.connection.open'}
    metric_holder = LensMetricHolder.model_validate({'metric': config})

    column_id: str
    kbn_column: KbnLensColumnTypes
    column_id, kbn_column = compile_lens_metric(metric=metric_holder.metric)

    assert kbn_column is not None
    kbn_column_as_dict = kbn_column.model_dump()

    assert kbn_column_as_dict == snapshot(
        {
            'label': 'Minimum of aerospike.node.connection.open',
            'dataType': 'number',
            'operationType': 'min',
            'sourceField': 'aerospike.node.connection.open',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {'emptyAsNull': True},
        }
    )


async def test_compile_lens_metric_max() -> None:
    """Test the compilation of a max metric."""
    config = {'aggregation': 'max', 'field': 'aerospike.node.connection.open'}
    metric_holder = LensMetricHolder.model_validate({'metric': config})

    column_id: str
    kbn_column: KbnLensColumnTypes
    column_id, kbn_column = compile_lens_metric(metric=metric_holder.metric)

    assert kbn_column is not None
    kbn_column_as_dict = kbn_column.model_dump()

    assert kbn_column_as_dict == snapshot(
        {
            'label': 'Maximum of aerospike.node.connection.open',
            'dataType': 'number',
            'operationType': 'max',
            'sourceField': 'aerospike.node.connection.open',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {'emptyAsNull': True},
        }
    )


async def test_compile_lens_metric_percentile_rank() -> None:
    """Test the compilation of a percentile rank metric."""
    config = {'aggregation': 'percentile_rank', 'field': 'aerospike.node.connection.open', 'rank': 5}
    metric_holder = LensMetricHolder.model_validate({'metric': config})

    column_id: str
    kbn_column: KbnLensColumnTypes
    column_id, kbn_column = compile_lens_metric(metric=metric_holder.metric)

    assert kbn_column is not None
    kbn_column_as_dict = kbn_column.model_dump()

    assert kbn_column_as_dict == snapshot(
        {
            'label': 'Percentile rank (5) of aerospike.node.connection.open',
            'dataType': 'number',
            'operationType': 'percentile_rank',
            'sourceField': 'aerospike.node.connection.open',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {'value': 5},
        }
    )


async def test_compile_lens_metric_percentile_95() -> None:
    """Test the compilation of a 95th percentile metric."""
    config = {'aggregation': 'percentile', 'field': 'aerospike.node.connection.open', 'percentile': 95}
    metric_holder = LensMetricHolder.model_validate({'metric': config})

    column_id: str
    kbn_column: KbnLensColumnTypes
    column_id, kbn_column = compile_lens_metric(metric=metric_holder.metric)

    assert kbn_column is not None
    kbn_column_as_dict = kbn_column.model_dump()

    assert kbn_column_as_dict == snapshot(
        {
            'label': '95th percentile of aerospike.node.connection.open',
            'dataType': 'number',
            'operationType': 'percentile',
            'sourceField': 'aerospike.node.connection.open',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {'percentile': 95},
        }
    )


class ESQLMetricHolder(BaseModel):
    """A holder for ESQL metrics to be used in tests."""

    metric: ESQLMetricTypes


async def test_compile_esql_metric_count() -> None:
    """Test the compilation of a count ESQL metric."""
    config = {'id': 'ac345678-90ab-cdef-1234-567890abcdef', 'field': 'count(*)'}
    metric_holder = ESQLMetricHolder.model_validate({'metric': config})

    kbn_column: KbnESQLFieldMetricColumn = compile_esql_metric(metric=metric_holder.metric)

    assert kbn_column is not None
    kbn_column_as_dict = kbn_column.model_dump()

    assert kbn_column_as_dict == snapshot({'fieldName': 'count(*)', 'columnId': 'ac345678-90ab-cdef-1234-567890abcdef'})
