"""Test the multi-field breakdown_by functionality for Metric charts."""

import pytest
from pydantic import ValidationError

from dashboard_compiler.panels.charts.lens.columns.view import KbnLensTermsDimensionColumn
from dashboard_compiler.panels.charts.metric.compile import compile_lens_metric_chart
from dashboard_compiler.panels.charts.metric.config import LensMetricChart


async def test_metric_single_field_breakdown_by() -> None:
    """Test Metric chart with single field breakdown_by."""
    lens_config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {'aggregation': 'count'},
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['service.name'],
            'size': 5,
        },
    }

    lens_chart = LensMetricChart(**lens_config)
    _layer_id, kbn_columns, kbn_state_visualization = compile_lens_metric_chart(lens_metric_chart=lens_chart)

    # Check that breakdown dimension was created
    assert kbn_state_visualization.breakdownByAccessor is not None
    breakdown_id = kbn_state_visualization.breakdownByAccessor
    assert breakdown_id in kbn_columns

    # Check the breakdown column
    breakdown_column = kbn_columns[breakdown_id]
    assert isinstance(breakdown_column, KbnLensTermsDimensionColumn)
    assert breakdown_column.operationType == 'terms'
    assert breakdown_column.sourceField == 'service.name'
    assert breakdown_column.params.size == 5


async def test_metric_multi_field_breakdown_by_uses_only_first() -> None:
    """Test that Metric chart only uses the first field from breakdown_by.

    Note: Kibana's Metric charts only support a single breakdown field,
    so we only use the first field even when multiple are specified.
    """
    lens_config = {
        'type': 'metric',
        'data_view': 'logs-*',
        'primary': {'aggregation': 'count'},
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['product.category', 'customer.region', 'extra.field'],
            'size': 10,
        },
    }

    lens_chart = LensMetricChart(**lens_config)
    _layer_id, kbn_columns, kbn_state_visualization = compile_lens_metric_chart(lens_metric_chart=lens_chart)

    # Should have breakdown accessor
    assert kbn_state_visualization.breakdownByAccessor is not None
    breakdown_id = kbn_state_visualization.breakdownByAccessor

    # Should only create ONE column (for the first field)
    breakdown_column = kbn_columns[breakdown_id]
    assert isinstance(breakdown_column, KbnLensTermsDimensionColumn)
    assert breakdown_column.operationType == 'terms'
    assert breakdown_column.sourceField == 'product.category'  # First field only
    assert breakdown_column.params.size == 10


async def test_metric_breakdown_by_with_options() -> None:
    """Test breakdown_by with various options."""
    lens_config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {'aggregation': 'sum', 'field': 'bytes', 'label': 'Total Bytes'},
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['service.name'],
            'size': 20,
            'sort': {
                'by': 'Total Bytes',
                'direction': 'desc',
            },
            'other_bucket': True,
            'missing_bucket': False,
        },
    }

    lens_chart = LensMetricChart(**lens_config)
    _layer_id, kbn_columns, kbn_state_visualization = compile_lens_metric_chart(lens_metric_chart=lens_chart)

    breakdown_column = kbn_columns[kbn_state_visualization.breakdownByAccessor]
    assert isinstance(breakdown_column, KbnLensTermsDimensionColumn)
    assert breakdown_column.params.size == 20
    assert breakdown_column.params.orderDirection == 'desc'
    assert breakdown_column.params.orderBy is not None
    assert breakdown_column.params.orderBy.type == 'column'
    assert breakdown_column.params.otherBucket is True
    assert breakdown_column.params.missingBucket is False


async def test_metric_breakdown_by_with_include_exclude() -> None:
    """Test breakdown_by with include and exclude patterns."""
    lens_config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {'aggregation': 'count'},
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['status'],
            'include': ['success', 'pending'],
            'exclude': ['error'],
            'include_is_regex': False,
            'exclude_is_regex': True,
        },
    }

    lens_chart = LensMetricChart(**lens_config)
    _layer_id, kbn_columns, kbn_state_visualization = compile_lens_metric_chart(lens_metric_chart=lens_chart)

    breakdown_column = kbn_columns[kbn_state_visualization.breakdownByAccessor]
    assert isinstance(breakdown_column, KbnLensTermsDimensionColumn)
    assert breakdown_column.params.include == ['success', 'pending']
    assert breakdown_column.params.exclude == ['error']
    assert breakdown_column.params.includeIsRegex is False
    assert breakdown_column.params.excludeIsRegex is True


async def test_metric_breakdown_and_breakdown_by_mutual_exclusion() -> None:
    """Test that breakdown and breakdown_by are mutually exclusive."""
    lens_config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {'aggregation': 'count'},
        'breakdown': {'type': 'values', 'field': 'service.name'},
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['host.name'],
        },
    }

    with pytest.raises(ValidationError, match="Cannot specify both 'breakdown' and 'breakdown_by'"):
        LensMetricChart(**lens_config)


async def test_metric_breakdown_by_field_count_validation() -> None:
    """Test that breakdown_by enforces min/max field count."""
    # Test empty fields list
    lens_config_empty = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {'aggregation': 'count'},
        'breakdown_by': {
            'operation': 'terms',
            'fields': [],
        },
    }

    with pytest.raises(ValidationError):
        LensMetricChart(**lens_config_empty)

    # Test too many fields (>4)
    lens_config_too_many = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {'aggregation': 'count'},
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['f1', 'f2', 'f3', 'f4', 'f5'],
        },
    }

    with pytest.raises(ValidationError):
        LensMetricChart(**lens_config_too_many)


async def test_metric_breakdown_by_column_order() -> None:
    """Test that breakdown column comes before metrics in column order.

    Kibana requires dimensions to be ordered before metrics in the columnOrder array.
    """
    lens_config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {'aggregation': 'count', 'id': 'primary-metric'},
        'secondary': {'aggregation': 'average', 'field': 'duration', 'id': 'secondary-metric'},
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['service.name'],
            'id': 'breakdown-dim',
        },
    }

    lens_chart = LensMetricChart(**lens_config)
    _layer_id, kbn_columns, kbn_state_visualization = compile_lens_metric_chart(lens_metric_chart=lens_chart)

    # Get the column IDs in order
    column_ids = list(kbn_columns.keys())

    # Find the breakdown column index
    breakdown_id = kbn_state_visualization.breakdownByAccessor
    breakdown_index = column_ids.index(breakdown_id)

    # Find the metric column indices
    primary_index = column_ids.index(kbn_state_visualization.metricAccessor)
    secondary_index = column_ids.index(kbn_state_visualization.secondaryMetricAccessor)

    # Breakdown should come before metrics
    assert breakdown_index < primary_index
    assert breakdown_index < secondary_index


async def test_metric_breakdown_by_full_snapshot() -> None:
    """Test complete visualization state snapshot with breakdown_by."""
    lens_config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {'aggregation': 'count', 'id': 'metric-primary'},
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['service.name', 'host.name'],  # Only first will be used
            'size': 10,
        },
    }

    lens_chart = LensMetricChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_metric_chart(lens_metric_chart=lens_chart)

    result = kbn_state_visualization.model_dump()
    assert 'layerId' in result
    assert 'metricAccessor' in result
    assert result['metricAccessor'] == 'metric-primary'
    assert 'breakdownByAccessor' in result
    assert result['secondaryTrend'] == {'type': 'none'}
    assert result['secondaryLabelPosition'] == 'before'


async def test_metric_with_primary_secondary_and_breakdown_by() -> None:
    """Test Metric chart with primary, secondary metrics and breakdown_by."""
    lens_config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {'aggregation': 'count'},
        'secondary': {'aggregation': 'average', 'field': 'response_time'},
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['service.name'],
            'size': 15,
        },
    }

    lens_chart = LensMetricChart(**lens_config)
    _layer_id, kbn_columns, kbn_state_visualization = compile_lens_metric_chart(lens_metric_chart=lens_chart)

    # Check all three components are present
    assert kbn_state_visualization.metricAccessor is not None
    assert kbn_state_visualization.secondaryMetricAccessor is not None
    assert kbn_state_visualization.breakdownByAccessor is not None

    # Verify breakdown column
    breakdown_column = kbn_columns[kbn_state_visualization.breakdownByAccessor]
    assert isinstance(breakdown_column, KbnLensTermsDimensionColumn)
    assert breakdown_column.params.size == 15
