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
    _metric_id, primary_column, _helper_columns = compile_lens_metric(metric=metric_holder.metric)
    assert primary_column is not None
    return primary_column.model_dump()


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


async def test_compile_lens_metric_formula_simple_arithmetic() -> None:
    """Test formula metric: (count(filter) / count()) * 100."""
    metric_holder = LensMetricHolder.model_validate(
        {
            'metric': {
                'formula': {
                    'multiply': {
                        'left': {
                            'divide': {
                                'left': {'count': {'filter': {'kql': 'status:error'}}},
                                'right': {'count': {}},
                            }
                        },
                        'right': 100,
                    }
                },
                'label': 'Error Rate %',
            }
        }
    )

    _metric_id, primary_column, helper_columns = compile_lens_metric(metric=metric_holder.metric)

    # Check we got all the expected columns
    assert len(helper_columns) == 3  # math column + 2 aggregation columns

    # Primary column should be formula type
    assert primary_column.operationType == 'formula'
    assert primary_column.label == 'Error Rate %'
    primary_dict = primary_column.model_dump()

    # Check formula string (has outer parens from multiply operation)
    assert primary_dict['params']['formula'] == "((count(kql='status:error') / count()) * 100)"
    assert primary_dict['operationType'] == 'formula'
    assert primary_dict['dataType'] == 'number'
    assert primary_dict['customLabel'] is True
    assert len(primary_dict['references']) == 1

    # Check helper columns structure
    math_id = primary_dict['references'][0]
    assert isinstance(math_id, str)
    assert math_id in helper_columns

    # Math column should have tinymathAst
    math_column = helper_columns[math_id]
    assert math_column.operationType == 'math'
    math_dict = math_column.model_dump()
    assert 'tinymathAst' in math_dict['params']

    # Should have 2 aggregation columns (both count)
    agg_columns = {k: v for k, v in helper_columns.items() if k != math_id}
    assert len(agg_columns) == 2

    # Check one has filter, one doesn't
    agg_dicts = [col.model_dump() for col in agg_columns.values()]
    filters_present = [bool(d.get('filter')) for d in agg_dicts]
    assert True in filters_present
    assert False in filters_present


async def test_compile_lens_metric_formula_with_field_aggregations() -> None:
    """Test formula metric with field-based aggregations: (max - min) / avg."""
    metric_holder = LensMetricHolder.model_validate(
        {
            'metric': {
                'formula': {
                    'divide': {
                        'left': {
                            'subtract': {
                                'left': {'max': {'field': 'response.time'}},
                                'right': {'min': {'field': 'response.time'}},
                            }
                        },
                        'right': {'average': {'field': 'response.time'}},
                    }
                },
            }
        }
    )

    _metric_id, primary_column, helper_columns = compile_lens_metric(metric=metric_holder.metric)

    # Should have math + 3 aggregations (max, min, average)
    assert len(helper_columns) == 4

    # Primary column
    assert primary_column.operationType == 'formula'
    primary_dict = primary_column.model_dump()
    # Formula includes field= parameter
    expected_formula = "((max(field='response.time') - min(field='response.time')) / average(field='response.time'))"
    assert primary_dict['params']['formula'] == expected_formula

    # All aggregation columns should reference the same field
    math_id = primary_dict['references'][0]
    agg_columns = {k: v for k, v in helper_columns.items() if k != math_id}
    agg_fields = {col.sourceField for col in agg_columns.values() if hasattr(col, 'sourceField')}  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
    assert agg_fields == {'response.time'}

    # Should have max, min, and average operations
    agg_ops = {col.operationType for col in agg_columns.values()}
    assert agg_ops == {'max', 'min', 'average'}


async def test_compile_lens_metric_formula_unique_count() -> None:
    """Test formula metric with unique_count aggregation."""
    metric_holder = LensMetricHolder.model_validate(
        {
            'metric': {
                'formula': {
                    'multiply': {
                        'left': {'unique_count': {'field': 'user.id'}},
                        'right': 2,
                    }
                },
            }
        }
    )

    _metric_id, primary_column, helper_columns = compile_lens_metric(metric=metric_holder.metric)

    # Math column + 1 unique_count aggregation
    assert len(helper_columns) == 2

    primary_dict = primary_column.model_dump()
    assert primary_dict['params']['formula'] == "(unique_count(field='user.id') * 2)"

    # Find the unique_count column
    math_id = primary_dict['references'][0]
    agg_columns = {k: v for k, v in helper_columns.items() if k != math_id}
    assert len(agg_columns) == 1

    unique_count_col = next(iter(agg_columns.values()))
    assert unique_count_col.operationType == 'unique_count'
    assert unique_count_col.sourceField == 'user.id'


async def test_compile_lens_metric_formula_with_aggregation_filter() -> None:
    """Test formula metric with filtered aggregations."""
    metric_holder = LensMetricHolder.model_validate(
        {
            'metric': {
                'formula': {
                    'add': {
                        'left': {'sum': {'field': 'bytes', 'filter': {'kql': 'status:200'}}},
                        'right': {'sum': {'field': 'bytes', 'filter': {'kql': 'status:404'}}},
                    }
                },
            }
        }
    )

    _metric_id, primary_column, helper_columns = compile_lens_metric(metric=metric_holder.metric)

    # Math + 2 sum aggregations with different filters
    assert len(helper_columns) == 3

    primary_dict = primary_column.model_dump()
    # Formula uses field= and kql= parameters
    assert "sum(field='bytes', kql='status:200')" in primary_dict['params']['formula']
    assert "sum(field='bytes', kql='status:404')" in primary_dict['params']['formula']

    # Both aggregations should have filters
    math_id = primary_dict['references'][0]
    agg_columns = {k: v for k, v in helper_columns.items() if k != math_id}

    for col in agg_columns.values():
        col_dict = col.model_dump()
        assert col_dict['operationType'] == 'sum'
        assert col_dict['sourceField'] == 'bytes'
        assert col_dict.get('filter') is not None
        assert col_dict['filter']['language'] == 'kuery'


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
