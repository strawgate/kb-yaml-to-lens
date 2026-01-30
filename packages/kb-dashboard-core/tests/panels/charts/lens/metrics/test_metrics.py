"""Test the compilation of Lens metrics from config models to view models."""

from typing import Any

from inline_snapshot import snapshot
from pydantic import BaseModel

from kb_dashboard_core.panels.charts.esql.columns.compile import compile_esql_metric
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLMetricTypes
from kb_dashboard_core.panels.charts.lens.metrics.compile import compile_lens_metric
from kb_dashboard_core.panels.charts.lens.metrics.config import LensMetricTypes


class LensMetricHolder(BaseModel):
    """A holder for metrics to be used in tests."""

    metric: LensMetricTypes


class ESQLMetricHolder(BaseModel):
    """A holder for ESQL metrics to be used in tests."""

    metric: ESQLMetricTypes


def compile_metric_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    """Compile Lens metric config and return dict for snapshot testing."""
    metric_holder = LensMetricHolder.model_validate({'metric': config})
    result = compile_lens_metric(metric=metric_holder.metric)
    assert result.primary_column is not None
    return result.primary_column.model_dump()


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
            'label': 'count(*)',
            'customLabel': False,
            'meta': {'type': 'number', 'esType': 'long'},
            'inMetricDimension': True,
        }
    )


async def test_compile_lens_formula_metric_simple() -> None:
    """Test the compilation of a simple formula metric."""
    result = compile_metric_snapshot({'formula': 'count() / 100', 'label': 'Count Percentage'})
    # Formula now correctly references the math column (X1) which contains the tinymathAST
    # The helper columns (X0 for count() aggregation, X1 for the math) are generated separately
    assert result['label'] == 'Count Percentage'
    assert result['customLabel'] is True
    assert result['dataType'] == 'number'
    assert result['operationType'] == 'formula'
    assert result['isBucketed'] is False
    assert result['scale'] == 'ratio'
    assert result['params']['formula'] == 'count() / 100'
    assert result['params']['isFormulaBroken'] is False
    # The references should now contain the math column ID (ends with X1)
    assert len(result['references']) == 1
    assert result['references'][0].endswith('X1')


async def test_compile_lens_formula_metric_with_fields() -> None:
    """Test the compilation of a formula metric using field aggregations."""
    result = compile_metric_snapshot(
        {
            'formula': "(max(field='response.time') - min(field='response.time')) / average(field='response.time')",
            'label': 'Response Time Variability',
        }
    )
    # Formula with 3 aggregations (max, min, average) generates X0, X1, X2 columns + X3 for math
    assert result['label'] == 'Response Time Variability'
    assert result['customLabel'] is True
    assert result['dataType'] == 'number'
    assert result['operationType'] == 'formula'
    assert result['isBucketed'] is False
    assert result['scale'] == 'ratio'
    assert result['params']['formula'] == "(max(field='response.time') - min(field='response.time')) / average(field='response.time')"
    assert result['params']['isFormulaBroken'] is False
    # The references should now contain the math column ID (ends with X3 for 3 aggregations)
    assert len(result['references']) == 1
    assert result['references'][0].endswith('X3')


async def test_compile_lens_formula_metric_with_format() -> None:
    """Test the compilation of a formula metric with number format."""
    result = compile_metric_snapshot({'formula': 'count(kql="status:error") / count() * 100', 'format': {'type': 'percent'}})
    # Formula with 2 count() calls generates X0, X1 columns + X2 for math
    assert result['label'] == 'Formula'
    assert result['dataType'] == 'number'
    assert result['operationType'] == 'formula'
    assert result['isBucketed'] is False
    assert result['scale'] == 'ratio'
    assert result['params']['formula'] == 'count(kql="status:error") / count() * 100'
    assert result['params']['isFormulaBroken'] is False
    assert result['params']['format'] == {'id': 'percent', 'params': {'decimals': 2}}
    # The references should now contain the math column ID (ends with X2 for 2 aggregations)
    assert len(result['references']) == 1
    assert result['references'][0].endswith('X2')


def compile_formula_with_helpers(config: dict[str, Any]) -> dict[str, Any]:
    """Compile formula metric and return full result including helper columns."""
    metric_holder = LensMetricHolder.model_validate({'metric': config})
    result = compile_lens_metric(metric=metric_holder.metric)
    return {
        'primary_id': result.primary_id,
        'primary_column': result.primary_column.model_dump(),
        'helper_columns': {col_id: col.model_dump() for col_id, col in result.helper_columns.items()},
    }


class TestFormulaFullReferenceOperations:
    """Test formula compilation with fullReference operations like counter_rate."""

    async def test_counter_rate_with_max(self) -> None:
        """Test counter_rate(max(field)) generates correct helper columns."""
        result = compile_formula_with_helpers({'formula': 'counter_rate(max(postgresql.operations))'})

        # Should have 2 helper columns: X0 (max aggregation) and X1 (counter_rate fullReference)
        assert len(result['helper_columns']) == 2

        # Get helper column IDs
        helper_ids = sorted(result['helper_columns'].keys())
        agg_col_id = helper_ids[0]  # X0
        fullref_col_id = helper_ids[1]  # X1

        # X0 should be the max aggregation
        agg_col = result['helper_columns'][agg_col_id]
        assert agg_col == snapshot(
            {
                'label': 'Part of counter_rate(max(postgresql.operations))',
                'customLabel': True,
                'dataType': 'number',
                'operationType': 'max',
                'isBucketed': False,
                'scale': 'ratio',
                'sourceField': 'postgresql.operations',
                'params': {'emptyAsNull': False},
            }
        )

        # X1 should be the counter_rate fullReference referencing X0
        fullref_col = result['helper_columns'][fullref_col_id]
        assert fullref_col == snapshot(
            {
                'label': 'Part of counter_rate(max(postgresql.operations))',
                'customLabel': True,
                'dataType': 'number',
                'operationType': 'counter_rate',
                'isBucketed': False,
                'scale': 'ratio',
                'params': {'emptyAsNull': False},
                'references': [agg_col_id],
                'timeScale': 's',
            }
        )

        # Formula column should reference both helper columns
        primary = result['primary_column']
        assert primary['operationType'] == 'formula'
        assert primary['params']['formula'] == 'counter_rate(max(postgresql.operations))'
        assert len(primary['references']) == 2

    async def test_cumulative_sum_with_count(self) -> None:
        """Test cumulative_sum(count()) generates correct helper columns."""
        result = compile_formula_with_helpers({'formula': 'cumulative_sum(count())'})

        # Should have 2 helper columns: X0 (count aggregation) and X1 (cumulative_sum fullReference)
        assert len(result['helper_columns']) == 2

        helper_ids = sorted(result['helper_columns'].keys())
        agg_col_id = helper_ids[0]
        fullref_col_id = helper_ids[1]

        # X0 should be the count aggregation
        agg_col = result['helper_columns'][agg_col_id]
        assert agg_col['operationType'] == 'count'
        assert agg_col['sourceField'] == '___records___'

        # X1 should be the cumulative_sum fullReference
        fullref_col = result['helper_columns'][fullref_col_id]
        assert fullref_col['operationType'] == 'cumulative_sum'
        assert fullref_col['references'] == [agg_col_id]

    async def test_differences_with_sum(self) -> None:
        """Test differences(sum(bytes)) generates correct helper columns."""
        result = compile_formula_with_helpers({'formula': 'differences(sum(bytes))'})

        helper_ids = sorted(result['helper_columns'].keys())
        agg_col_id = helper_ids[0]
        fullref_col_id = helper_ids[1]

        # Verify aggregation column
        agg_col = result['helper_columns'][agg_col_id]
        assert agg_col['operationType'] == 'sum'
        assert agg_col['sourceField'] == 'bytes'

        # Verify fullReference column
        fullref_col = result['helper_columns'][fullref_col_id]
        assert fullref_col['operationType'] == 'differences'
        assert fullref_col['references'] == [agg_col_id]

    async def test_moving_average_with_average(self) -> None:
        """Test moving_average(average(response.time)) generates correct helper columns."""
        result = compile_formula_with_helpers({'formula': "moving_average(average(field='response.time'))"})

        helper_ids = sorted(result['helper_columns'].keys())
        agg_col_id = helper_ids[0]
        fullref_col_id = helper_ids[1]

        # Verify aggregation column
        agg_col = result['helper_columns'][agg_col_id]
        assert agg_col['operationType'] == 'average'
        assert agg_col['sourceField'] == 'response.time'

        # Verify fullReference column
        fullref_col = result['helper_columns'][fullref_col_id]
        assert fullref_col['operationType'] == 'moving_average'
        assert fullref_col['references'] == [agg_col_id]

    async def test_complex_formula_with_multiple_counter_rates(self) -> None:
        """Test formula with multiple counter_rate operations.

        counter_rate(max(in.bytes)) + counter_rate(max(out.bytes))
        Should generate:
        - X0: max(in.bytes)
        - X1: counter_rate referencing X0
        - X2: max(out.bytes)
        - X3: counter_rate referencing X2
        - X4: math column with add operation
        """
        result = compile_formula_with_helpers({'formula': 'counter_rate(max(in.bytes)) + counter_rate(max(out.bytes))'})

        # Should have 5 helper columns: 2 aggregations + 2 fullReferences + 1 math
        assert len(result['helper_columns']) == 5

        # Verify the formula column references the math column
        primary = result['primary_column']
        assert primary['operationType'] == 'formula'
        assert len(primary['references']) == 1
        math_col_id = primary['references'][0]
        assert math_col_id.endswith('X4')

        # Verify the math column contains the add operation
        math_col = result['helper_columns'][math_col_id]
        assert math_col['operationType'] == 'math'
        assert 'tinymathAst' in math_col['params']
        assert math_col['params']['tinymathAst']['name'] == 'add'

    async def test_simple_aggregation_still_works(self) -> None:
        """Verify that simple aggregations without fullReference still work."""
        result = compile_formula_with_helpers({'formula': "unique_count(field='user.id')"})

        # Should have 1 helper column: just the aggregation
        assert len(result['helper_columns']) == 1

        helper_id = next(iter(result['helper_columns'].keys()))
        agg_col = result['helper_columns'][helper_id]
        assert agg_col['operationType'] == 'unique_count'
        assert agg_col['sourceField'] == 'user.id'

        # Formula should reference the aggregation directly (no math column needed)
        primary = result['primary_column']
        assert primary['references'] == [helper_id]
