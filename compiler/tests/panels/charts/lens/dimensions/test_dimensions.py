"""Test the compilation of Lens dimensions from config models to view models."""

from dirty_equals import IsUUID
from inline_snapshot import snapshot
from pydantic import TypeAdapter

from dashboard_compiler.panels.charts.lens.dimensions.compile import compile_lens_dimension
from dashboard_compiler.panels.charts.lens.dimensions.config import (
    LensDateHistogramDimension,
    LensDimensionTypes,
    LensFiltersDimension,
    LensIntervalsDimension,
    LensTopValuesDimension,
)
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes


async def test_date_histogram_dimension() -> None:
    """Test date histogram dimension."""
    metric_config = {'aggregation': 'count', 'id': '87416118-6032-41a2-aaf9-173fc0e525eb'}
    dimension_config = {'type': 'date_histogram', 'field': '@timestamp'}

    metric = TypeAdapter(LensMetricTypes).validate_python(metric_config)
    metric_id, kbn_metric_column = compile_lens_metric(metric)
    metric_result = kbn_metric_column.model_dump()

    kbn_metric_column_by_id = {metric_id: kbn_metric_column}
    dimension = TypeAdapter(LensDimensionTypes).validate_python(dimension_config)
    _, kbn_dimension_column = compile_lens_dimension(
        dimension=dimension,
        kbn_metric_column_by_id=kbn_metric_column_by_id,
    )
    dimension_result = kbn_dimension_column.model_dump()

    assert metric_result == snapshot(
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
    assert dimension_result == snapshot(
        {
            'label': '@timestamp',
            'dataType': 'date',
            'operationType': 'date_histogram',
            'isBucketed': True,
            'scale': 'interval',
            'params': {'interval': 'auto', 'includeEmptyRows': True, 'dropPartials': False},
            'sourceField': '@timestamp',
        }
    )


async def test_terms_dimension_with_sorting() -> None:
    """Test terms dimension with sorting."""
    metric_config = {'aggregation': 'count', 'id': '87416118-6032-41a2-aaf9-173fc0e525eb'}
    dimension_config = {
        'type': 'values',
        'field': 'agent.type',
        'sort': {'by': 'Count of records', 'direction': 'desc'},
    }

    metric = TypeAdapter(LensMetricTypes).validate_python(metric_config)
    metric_id, kbn_metric_column = compile_lens_metric(metric)
    metric_result = kbn_metric_column.model_dump()

    kbn_metric_column_by_id = {metric_id: kbn_metric_column}
    dimension = TypeAdapter(LensDimensionTypes).validate_python(dimension_config)
    _, kbn_dimension_column = compile_lens_dimension(
        dimension=dimension,
        kbn_metric_column_by_id=kbn_metric_column_by_id,
    )
    dimension_result = kbn_dimension_column.model_dump()

    assert metric_result == snapshot(
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
    assert dimension_result == snapshot(
        {
            'label': 'Top 3 values of agent.type',
            'dataType': 'string',
            'operationType': 'terms',
            'isBucketed': True,
            'scale': 'ordinal',
            'params': {
                'orderBy': {'type': 'column', 'columnId': IsUUID},
                'orderDirection': 'desc',
                'otherBucket': True,
                'missingBucket': False,
                'parentFormat': {'id': 'terms'},
                'include': [],
                'exclude': [],
                'includeIsRegex': False,
                'excludeIsRegex': False,
            },
            'sourceField': 'agent.type',
        }
    )


async def test_filters_dimension() -> None:
    """Test filters dimension."""
    metric_config = {'aggregation': 'count', 'id': '87416118-6032-41a2-aaf9-173fc0e525eb'}
    dimension_config = {
        'type': 'filters',
        'filters': [
            {'query': {'kql': 'agent.version: 8.*'}},
            {'query': {'kql': 'agent.version: 7.*'}},
        ],
    }

    metric = TypeAdapter(LensMetricTypes).validate_python(metric_config)
    metric_id, kbn_metric_column = compile_lens_metric(metric)
    metric_result = kbn_metric_column.model_dump()

    kbn_metric_column_by_id = {metric_id: kbn_metric_column}
    dimension = TypeAdapter(LensDimensionTypes).validate_python(dimension_config)
    _, kbn_dimension_column = compile_lens_dimension(
        dimension=dimension,
        kbn_metric_column_by_id=kbn_metric_column_by_id,
    )
    dimension_result = kbn_dimension_column.model_dump()

    assert metric_result == snapshot(
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
    assert dimension_result == snapshot(
        {
            'label': 'Filters',
            'dataType': 'string',
            'operationType': 'filters',
            'isBucketed': True,
            'scale': 'ordinal',
            'params': {
                'filters': [
                    {'label': '', 'input': {'query': 'agent.version: 8.*', 'language': 'kuery'}},
                    {'label': '', 'input': {'query': 'agent.version: 7.*', 'language': 'kuery'}},
                ]
            },
        }
    )


async def test_intervals_dimension() -> None:
    """Test intervals dimension."""
    metric_config = {'aggregation': 'count', 'id': '87416118-6032-41a2-aaf9-173fc0e525eb'}
    dimension_config = {
        'type': 'intervals',
        'field': 'apache.uptime',
    }

    metric = TypeAdapter(LensMetricTypes).validate_python(metric_config)
    metric_id, kbn_metric_column = compile_lens_metric(metric)
    metric_result = kbn_metric_column.model_dump()

    kbn_metric_column_by_id = {metric_id: kbn_metric_column}
    dimension = TypeAdapter(LensDimensionTypes).validate_python(dimension_config)
    _, kbn_dimension_column = compile_lens_dimension(
        dimension=dimension,
        kbn_metric_column_by_id=kbn_metric_column_by_id,
    )
    dimension_result = kbn_dimension_column.model_dump()

    assert metric_result == snapshot(
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
    assert dimension_result == snapshot(
        {
            'label': 'apache.uptime',
            'dataType': 'number',
            'operationType': 'range',
            'isBucketed': True,
            'scale': 'interval',
            'params': {'includeEmptyRows': True, 'type': 'histogram', 'ranges': [{'from': 0, 'to': 1000, 'label': ''}], 'maxBars': 'auto'},
            'sourceField': 'apache.uptime',
        }
    )


async def test_intervals_dimension_with_custom_granularity() -> None:
    """Test intervals dimension with custom granularity."""
    metric_config = {'aggregation': 'count', 'id': '87416118-6032-41a2-aaf9-173fc0e525eb'}
    dimension_config = {
        'type': 'intervals',
        'field': 'apache.uptime',
        'granularity': 2,
    }

    metric = TypeAdapter(LensMetricTypes).validate_python(metric_config)
    metric_id, kbn_metric_column = compile_lens_metric(metric)
    metric_result = kbn_metric_column.model_dump()

    kbn_metric_column_by_id = {metric_id: kbn_metric_column}
    dimension = TypeAdapter(LensDimensionTypes).validate_python(dimension_config)
    _, kbn_dimension_column = compile_lens_dimension(
        dimension=dimension,
        kbn_metric_column_by_id=kbn_metric_column_by_id,
    )
    dimension_result = kbn_dimension_column.model_dump()

    assert metric_result == snapshot(
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
    assert dimension_result == snapshot(
        {
            'label': 'apache.uptime',
            'dataType': 'number',
            'operationType': 'range',
            'isBucketed': True,
            'scale': 'interval',
            'params': {'includeEmptyRows': True, 'type': 'histogram', 'ranges': [{'from': 0, 'to': 1000, 'label': ''}], 'maxBars': 167.5},
            'sourceField': 'apache.uptime',
        }
    )


async def test_intervals_dimension_with_custom_intervals() -> None:
    """Test intervals dimension with custom intervals."""
    metric_config = {'aggregation': 'count', 'id': '87416118-6032-41a2-aaf9-173fc0e525eb'}
    dimension_config = {
        'type': 'intervals',
        'field': 'apache.uptime',
        'intervals': [
            {'to': 0},
            {'from': 0, 'to': 1000},
            {'from': 1000, 'to': 2000, 'label': 'Custom Label'},
            {'from': 2000},
        ],
    }

    metric = TypeAdapter(LensMetricTypes).validate_python(metric_config)
    metric_id, kbn_metric_column = compile_lens_metric(metric)
    metric_result = kbn_metric_column.model_dump()

    kbn_metric_column_by_id = {metric_id: kbn_metric_column}
    dimension = TypeAdapter(LensDimensionTypes).validate_python(dimension_config)
    _, kbn_dimension_column = compile_lens_dimension(
        dimension=dimension,
        kbn_metric_column_by_id=kbn_metric_column_by_id,
    )
    dimension_result = kbn_dimension_column.model_dump()

    assert metric_result == snapshot(
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
    assert dimension_result == snapshot(
        {
            'label': 'apache.uptime',
            'dataType': 'string',
            'operationType': 'range',
            'isBucketed': True,
            'scale': 'ordinal',
            'params': {
                'type': 'range',
                'ranges': [
                    {'from': None, 'to': 0, 'label': ''},
                    {'from': 0, 'to': 1000, 'label': ''},
                    {'from': 1000, 'to': 2000, 'label': 'Custom Label'},
                    {'from': 2000, 'to': None, 'label': ''},
                ],
                'maxBars': 499.5,
                'parentFormat': {'id': 'range', 'params': {'template': 'arrow_right', 'replaceInfinity': True}},
            },
            'sourceField': 'apache.uptime',
        }
    )


async def test_dimension_type_field_has_default() -> None:
    """Test that dimension type field can be omitted and will use the default value."""
    # Test that type defaults are applied correctly when constructing directly
    date_hist = LensDateHistogramDimension(field='@timestamp')
    assert date_hist.type == 'date_histogram'

    top_values = LensTopValuesDimension(field='status')
    assert top_values.type == 'values'

    filters = LensFiltersDimension(filters=[])
    assert filters.type == 'filters'

    intervals = LensIntervalsDimension(field='price')
    assert intervals.type == 'intervals'


async def test_terms_dimension_with_formula_metric_uses_alphabetical_ordering() -> None:
    """Test that terms dimension uses alphabetical ordering when first metric is a formula.

    Formula columns are computed post-aggregation and cannot be used for
    Elasticsearch aggregation ordering. This test ensures we fall back to
    alphabetical ordering in this case.
    """
    metric_config = {
        'formula': '1 - average(system.cpu.idle.pct)',
        'label': 'CPU %',
        'id': 'cpu-util',
    }
    dimension_config = {
        'type': 'values',
        'field': 'host.name',
        'size': 100,
    }

    metric = TypeAdapter(LensMetricTypes).validate_python(metric_config)
    metric_id, kbn_metric_column = compile_lens_metric(metric)

    kbn_metric_column_by_id = {metric_id: kbn_metric_column}
    dimension = TypeAdapter(LensDimensionTypes).validate_python(dimension_config)
    _, kbn_dimension_column = compile_lens_dimension(
        dimension=dimension,
        kbn_metric_column_by_id=kbn_metric_column_by_id,
    )
    dimension_result = kbn_dimension_column.model_dump()

    # Should use alphabetical ordering, not order by the formula column
    assert dimension_result['params']['orderBy'] == snapshot({'type': 'alphabetical', 'fallback': True})
    assert dimension_result['params']['orderDirection'] == 'desc'


async def test_terms_dimension_with_non_formula_metric_orders_by_metric() -> None:
    """Test that terms dimension orders by metric when first metric is not a formula.

    Non-formula metrics (like count, average, sum, etc.) can be used for
    Elasticsearch aggregation ordering.
    """
    metric_config = {'aggregation': 'average', 'field': 'system.cpu.user.pct', 'label': 'Avg CPU', 'id': 'avg-cpu'}
    dimension_config = {
        'type': 'values',
        'field': 'host.name',
        'size': 10,
    }

    metric = TypeAdapter(LensMetricTypes).validate_python(metric_config)
    metric_id, kbn_metric_column = compile_lens_metric(metric)

    kbn_metric_column_by_id = {metric_id: kbn_metric_column}
    dimension = TypeAdapter(LensDimensionTypes).validate_python(dimension_config)
    _, kbn_dimension_column = compile_lens_dimension(
        dimension=dimension,
        kbn_metric_column_by_id=kbn_metric_column_by_id,
    )
    dimension_result = kbn_dimension_column.model_dump()

    # Should order by the metric column (not alphabetical)
    assert dimension_result['params']['orderBy']['type'] == 'column'
    assert dimension_result['params']['orderBy']['columnId'] == metric_id
    assert dimension_result['params']['orderDirection'] == 'desc'


async def test_terms_dimension_without_metrics_uses_alphabetical_ordering() -> None:
    """Test that terms dimension uses alphabetical ordering when there are no metrics."""
    dimension_config = {
        'type': 'values',
        'field': 'host.name',
        'size': 5,
    }

    kbn_metric_column_by_id = {}
    dimension = TypeAdapter(LensDimensionTypes).validate_python(dimension_config)
    _, kbn_dimension_column = compile_lens_dimension(
        dimension=dimension,
        kbn_metric_column_by_id=kbn_metric_column_by_id,
    )
    dimension_result = kbn_dimension_column.model_dump()

    # Should use alphabetical ordering when no metrics available
    assert dimension_result['params']['orderBy'] == snapshot({'type': 'alphabetical', 'fallback': True})
    assert dimension_result['params']['orderDirection'] == 'desc'
