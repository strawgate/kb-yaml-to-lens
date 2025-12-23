"""Test the compilation of Lens dimensions from config models to view models."""

import re
from typing import Any

from inline_snapshot import snapshot
from pydantic import TypeAdapter

from dashboard_compiler.panels.charts.lens.dimensions.compile import compile_lens_dimension
from dashboard_compiler.panels.charts.lens.dimensions.config import LensDimensionTypes
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes


def _replace_column_ids(result: dict[str, Any]) -> dict[str, Any]:
    """Replace dynamic column IDs with placeholder for consistent snapshots."""
    # Replace top-level column IDs
    if 'columnId' in result and re.match(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        str(result['columnId']),
    ):
        result['columnId'] = 'DYNAMIC_COLUMN_ID'

    # Replace nested column IDs in params
    if (
        'params' in result
        and isinstance(result['params'], dict)
        and 'orderBy' in result['params']
        and isinstance(result['params']['orderBy'], dict)
        and 'columnId' in result['params']['orderBy']
    ):
        result['params']['orderBy']['columnId'] = 'DYNAMIC_COLUMN_ID'

    return result


async def test_date_histogram_dimension() -> None:
    """Test date histogram dimension."""
    metric_config = {'aggregation': 'count', 'id': '87416118-6032-41a2-aaf9-173fc0e525eb'}
    dimension_config = {'type': 'date_histogram', 'field': '@timestamp'}

    metric = TypeAdapter(LensMetricTypes).validate_python(metric_config)
    metric_id, kbn_metric_column = compile_lens_metric(metric)
    metric_result = _replace_column_ids(kbn_metric_column.model_dump())

    kbn_metric_column_by_id = {metric_id: kbn_metric_column}
    dimension = TypeAdapter(LensDimensionTypes).validate_python(dimension_config)
    _, kbn_dimension_column = compile_lens_dimension(
        dimension=dimension,
        kbn_metric_column_by_id=kbn_metric_column_by_id,
    )
    dimension_result = _replace_column_ids(kbn_dimension_column.model_dump())

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
    metric_result = _replace_column_ids(kbn_metric_column.model_dump())

    kbn_metric_column_by_id = {metric_id: kbn_metric_column}
    dimension = TypeAdapter(LensDimensionTypes).validate_python(dimension_config)
    _, kbn_dimension_column = compile_lens_dimension(
        dimension=dimension,
        kbn_metric_column_by_id=kbn_metric_column_by_id,
    )
    dimension_result = _replace_column_ids(kbn_dimension_column.model_dump())

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
                'orderBy': {'type': 'column', 'columnId': 'DYNAMIC_COLUMN_ID'},
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
    metric_result = _replace_column_ids(kbn_metric_column.model_dump())

    kbn_metric_column_by_id = {metric_id: kbn_metric_column}
    dimension = TypeAdapter(LensDimensionTypes).validate_python(dimension_config)
    _, kbn_dimension_column = compile_lens_dimension(
        dimension=dimension,
        kbn_metric_column_by_id=kbn_metric_column_by_id,
    )
    dimension_result = _replace_column_ids(kbn_dimension_column.model_dump())

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
    metric_result = _replace_column_ids(kbn_metric_column.model_dump())

    kbn_metric_column_by_id = {metric_id: kbn_metric_column}
    dimension = TypeAdapter(LensDimensionTypes).validate_python(dimension_config)
    _, kbn_dimension_column = compile_lens_dimension(
        dimension=dimension,
        kbn_metric_column_by_id=kbn_metric_column_by_id,
    )
    dimension_result = _replace_column_ids(kbn_dimension_column.model_dump())

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
    metric_result = _replace_column_ids(kbn_metric_column.model_dump())

    kbn_metric_column_by_id = {metric_id: kbn_metric_column}
    dimension = TypeAdapter(LensDimensionTypes).validate_python(dimension_config)
    _, kbn_dimension_column = compile_lens_dimension(
        dimension=dimension,
        kbn_metric_column_by_id=kbn_metric_column_by_id,
    )
    dimension_result = _replace_column_ids(kbn_dimension_column.model_dump())

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
    metric_result = _replace_column_ids(kbn_metric_column.model_dump())

    kbn_metric_column_by_id = {metric_id: kbn_metric_column}
    dimension = TypeAdapter(LensDimensionTypes).validate_python(dimension_config)
    _, kbn_dimension_column = compile_lens_dimension(
        dimension=dimension,
        kbn_metric_column_by_id=kbn_metric_column_by_id,
    )
    dimension_result = _replace_column_ids(kbn_dimension_column.model_dump())

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
