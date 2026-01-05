"""Test the compilation of Lens metrics from config models to view models."""

from typing import Any

from inline_snapshot import snapshot
from pydantic import BaseModel

from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_metric
from dashboard_compiler.panels.charts.esql.columns.config import ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes


class LensMetricHolder(BaseModel):
    """A holder for metrics to be used in tests."""

    metric: LensMetricTypes


class ESQLMetricHolder(BaseModel):
    """A holder for ESQL metrics to be used in tests."""

    metric: ESQLMetricTypes


def compile_metric_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    """Compile Lens metric config and return dict for snapshot testing."""
    metric_holder = LensMetricHolder.model_validate({'metric': config})
    _column_id, kbn_column = compile_lens_metric(metric=metric_holder.metric)
    assert kbn_column is not None
    return kbn_column.model_dump()


def compile_esql_metric_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    """Compile ESQL metric config and return dict for snapshot testing."""
    metric_holder = ESQLMetricHolder.model_validate({'metric': config})
    kbn_column = compile_esql_metric(metric=metric_holder.metric)
    assert kbn_column is not None
    return kbn_column.model_dump()


async def test_compile_lens_metric_count() -> None:
    """Test the compilation of a count metric."""
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


async def test_compile_lens_metric_sum() -> None:
    """Test the compilation of a sum metric."""
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


async def test_compile_lens_metric_sum_number_format() -> None:
    """Test the compilation of a sum metric with number format."""
    result = compile_metric_snapshot({'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'number'}})
    assert result == snapshot(
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
    result = compile_metric_snapshot({'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'percent'}})
    assert result == snapshot(
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
    result = compile_metric_snapshot({'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'bytes'}})
    assert result == snapshot(
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
    result = compile_metric_snapshot({'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'bits'}})
    assert result == snapshot(
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
    result = compile_metric_snapshot({'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'duration'}})
    assert result == snapshot(
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
    result = compile_metric_snapshot(
        {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'custom', 'pattern': '0,0.[0000]'}}
    )
    assert result == snapshot(
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
    result = compile_metric_snapshot(
        {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'number', 'suffix': 'KB'}}
    )
    assert result == snapshot(
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
    result = compile_metric_snapshot(
        {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'number', 'compact': True}}
    )
    assert result == snapshot(
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
    result = compile_metric_snapshot({'aggregation': 'last_value', 'field': 'aerospike.namespace.query.count'})
    assert result == snapshot(
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
    result = compile_metric_snapshot({'aggregation': 'min', 'field': 'aerospike.node.connection.open'})
    assert result == snapshot(
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
    result = compile_metric_snapshot({'aggregation': 'max', 'field': 'aerospike.node.connection.open'})
    assert result == snapshot(
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
    result = compile_metric_snapshot({'aggregation': 'percentile_rank', 'field': 'aerospike.node.connection.open', 'rank': 5})
    assert result == snapshot(
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
    result = compile_metric_snapshot({'aggregation': 'percentile', 'field': 'aerospike.node.connection.open', 'percentile': 95})
    assert result == snapshot(
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


async def test_compile_esql_metric_count() -> None:
    """Test the compilation of a count ESQL metric."""
    result = compile_esql_metric_snapshot({'id': 'ac345678-90ab-cdef-1234-567890abcdef', 'field': 'count(*)'})
    assert result == snapshot(
        {
            'fieldName': 'count(*)',
            'columnId': 'ac345678-90ab-cdef-1234-567890abcdef',
            'inMetricDimension': True,
        }
    )


async def test_compile_lens_formula_metric_simple() -> None:
    """Test the compilation of a simple formula metric."""
    result = compile_metric_snapshot({'formula': 'count() / 100', 'label': 'Count Percentage'})
    assert result == snapshot(
        {
            'label': 'Count Percentage',
            'customLabel': True,
            'dataType': 'number',
            'operationType': 'formula',
            'isBucketed': False,
            'scale': 'ratio',
            'references': [],
            'params': {'formula': 'count() / 100', 'isFormulaBroken': False},
        }
    )


async def test_compile_lens_formula_metric_with_fields() -> None:
    """Test the compilation of a formula metric using field aggregations."""
    result = compile_metric_snapshot(
        {
            'formula': "(max(field='response.time') - min(field='response.time')) / average(field='response.time')",
            'label': 'Response Time Variability',
        }
    )
    assert result == snapshot(
        {
            'label': 'Response Time Variability',
            'customLabel': True,
            'dataType': 'number',
            'operationType': 'formula',
            'isBucketed': False,
            'scale': 'ratio',
            'references': [],
            'params': {
                'formula': "(max(field='response.time') - min(field='response.time')) / average(field='response.time')",
                'isFormulaBroken': False,
            },
        }
    )


async def test_compile_lens_formula_metric_with_format() -> None:
    """Test the compilation of a formula metric with number format."""
    result = compile_metric_snapshot({'formula': 'count(kql="status:error") / count() * 100', 'format': {'type': 'percent'}})
    assert result == snapshot(
        {
            'label': 'Formula',
            'dataType': 'number',
            'operationType': 'formula',
            'isBucketed': False,
            'scale': 'ratio',
            'references': [],
            'params': {
                'formula': 'count(kql="status:error") / count() * 100',
                'isFormulaBroken': False,
                'format': {'id': 'percent', 'params': {'decimals': 2}},
            },
        }
    )
