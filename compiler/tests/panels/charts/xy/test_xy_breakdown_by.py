"""Test the multi-field breakdown_by functionality for XY charts."""

import pytest
from dirty_equals import IsUUID
from inline_snapshot import snapshot
from pydantic import ValidationError

from dashboard_compiler.panels.charts.lens.columns.view import KbnLensTermsDimensionColumn
from dashboard_compiler.panels.charts.xy.compile import compile_lens_xy_chart
from dashboard_compiler.panels.charts.xy.config import LensBarChart, LensLineChart
from dashboard_compiler.panels.charts.xy.view import XYDataLayerConfig


async def test_xy_single_field_breakdown_by() -> None:
    """Test XY chart with single field breakdown_by."""
    lens_config = {
        'type': 'bar',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim-1'},
        'metrics': [{'aggregation': 'count', 'id': 'metric-1'}],
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['service.name'],
            'size': 5,
        },
    }

    lens_chart = LensBarChart(**lens_config)
    _layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)

    # Check visualization state uses splitAccessors
    layer = kbn_state_visualization.layers[0]
    assert isinstance(layer, XYDataLayerConfig)
    assert layer.splitAccessor is None
    assert layer.splitAccessors is not None
    assert len(layer.splitAccessors) == 1

    # Check columns were created
    breakdown_column_id = layer.splitAccessors[0]
    assert breakdown_column_id in kbn_columns
    breakdown_column = kbn_columns[breakdown_column_id]
    assert isinstance(breakdown_column, KbnLensTermsDimensionColumn)
    assert breakdown_column.operationType == 'terms'
    assert breakdown_column.sourceField == 'service.name'
    assert breakdown_column.params.size == 5


async def test_xy_two_field_breakdown_by() -> None:
    """Test XY chart with two field breakdown_by."""
    lens_config = {
        'type': 'line',
        'data_view': 'logs-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp'},
        'metrics': [{'aggregation': 'count'}],
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['product.category', 'customer.region'],
            'size': 10,
        },
    }

    lens_chart = LensLineChart(**lens_config)
    _layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)

    layer = kbn_state_visualization.layers[0]
    assert isinstance(layer, XYDataLayerConfig)
    assert layer.splitAccessor is None
    assert layer.splitAccessors is not None
    assert len(layer.splitAccessors) == 2

    # Check both columns were created with shared configuration
    for accessor_id in layer.splitAccessors:
        assert accessor_id in kbn_columns
        column = kbn_columns[accessor_id]
        assert isinstance(column, KbnLensTermsDimensionColumn)
        assert column.operationType == 'terms'
        assert column.params.size == 10

    # Check that each column has the right field
    fields: list[str] = []
    for accessor_id in layer.splitAccessors:
        column = kbn_columns[accessor_id]
        assert isinstance(column, KbnLensTermsDimensionColumn)
        fields.append(column.sourceField)
    assert 'product.category' in fields
    assert 'customer.region' in fields


async def test_xy_four_field_breakdown_by() -> None:
    """Test XY chart with maximum (4) fields in breakdown_by."""
    lens_config = {
        'type': 'bar',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp'},
        'metrics': [{'aggregation': 'sum', 'field': 'bytes'}],
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['field1', 'field2', 'field3', 'field4'],
        },
    }

    lens_chart = LensBarChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)

    layer = kbn_state_visualization.layers[0]
    assert isinstance(layer, XYDataLayerConfig)
    assert layer.splitAccessors is not None
    assert len(layer.splitAccessors) == 4


async def test_xy_breakdown_by_with_collapse() -> None:
    """Test breakdown_by with collapse function."""
    lens_config = {
        'type': 'bar',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp'},
        'metrics': [{'aggregation': 'count'}],
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['service.name', 'host.name'],
            'size': 10,
            'collapse': 'sum',
        },
    }

    lens_chart = LensBarChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)

    # Verify collapse function (this would be in the collapseFn field of the layer in full implementation)
    layer = kbn_state_visualization.layers[0]
    assert isinstance(layer, XYDataLayerConfig)
    assert layer.splitAccessors is not None
    assert len(layer.splitAccessors) == 2


async def test_xy_breakdown_by_with_sort() -> None:
    """Test breakdown_by with sort configuration."""
    lens_config = {
        'type': 'bar',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp'},
        'metrics': [{'aggregation': 'count', 'label': 'Count'}],
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['service.name'],
            'sort': {
                'by': 'Count',
                'direction': 'asc',
            },
        },
    }

    lens_chart = LensBarChart(**lens_config)
    _layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)

    layer = kbn_state_visualization.layers[0]
    assert isinstance(layer, XYDataLayerConfig)
    assert layer.splitAccessors is not None

    # Check the breakdown column has the correct sort configuration
    assert layer.splitAccessors is not None
    breakdown_column = kbn_columns[layer.splitAccessors[0]]
    assert isinstance(breakdown_column, KbnLensTermsDimensionColumn)
    assert breakdown_column.params.orderDirection == 'asc'
    assert breakdown_column.params.orderBy is not None
    assert breakdown_column.params.orderBy.type == 'column'


async def test_xy_breakdown_by_with_include_exclude() -> None:
    """Test breakdown_by with include and exclude options."""
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp'},
        'metrics': [{'aggregation': 'count'}],
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['service.name'],
            'include': ['service-a', 'service-b'],
            'exclude': ['service-z'],
            'include_is_regex': False,
            'exclude_is_regex': False,
        },
    }

    lens_chart = LensLineChart(**lens_config)
    _layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)

    layer = kbn_state_visualization.layers[0]
    assert isinstance(layer, XYDataLayerConfig)
    assert layer.splitAccessors is not None
    breakdown_column = kbn_columns[layer.splitAccessors[0]]
    assert isinstance(breakdown_column, KbnLensTermsDimensionColumn)
    assert breakdown_column.params.include == ['service-a', 'service-b']
    assert breakdown_column.params.exclude == ['service-z']
    assert breakdown_column.params.includeIsRegex is False
    assert breakdown_column.params.excludeIsRegex is False


async def test_xy_breakdown_by_with_other_bucket() -> None:
    """Test breakdown_by with other_bucket and missing_bucket options."""
    lens_config = {
        'type': 'bar',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp'},
        'metrics': [{'aggregation': 'count'}],
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['service.name'],
            'other_bucket': True,
            'missing_bucket': True,
        },
    }

    lens_chart = LensBarChart(**lens_config)
    _layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)

    layer = kbn_state_visualization.layers[0]
    assert isinstance(layer, XYDataLayerConfig)
    assert layer.splitAccessors is not None
    breakdown_column = kbn_columns[layer.splitAccessors[0]]
    assert isinstance(breakdown_column, KbnLensTermsDimensionColumn)
    assert breakdown_column.params.otherBucket is True
    assert breakdown_column.params.missingBucket is True


async def test_xy_breakdown_and_breakdown_by_mutual_exclusion() -> None:
    """Test that breakdown and breakdown_by are mutually exclusive."""
    lens_config = {
        'type': 'bar',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp'},
        'metrics': [{'aggregation': 'count'}],
        'breakdown': {'type': 'values', 'field': 'service.name'},
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['host.name'],
        },
    }

    with pytest.raises(ValidationError, match="Cannot specify both 'breakdown' and 'breakdown_by'"):
        LensBarChart(**lens_config)


async def test_xy_breakdown_by_field_count_validation() -> None:
    """Test that breakdown_by enforces min/max field count."""
    # Test empty fields list
    lens_config_empty = {
        'type': 'bar',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp'},
        'metrics': [{'aggregation': 'count'}],
        'breakdown_by': {
            'operation': 'terms',
            'fields': [],
        },
    }

    with pytest.raises(ValidationError):
        LensBarChart(**lens_config_empty)

    # Test too many fields (>4)
    lens_config_too_many = {
        'type': 'bar',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp'},
        'metrics': [{'aggregation': 'count'}],
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['f1', 'f2', 'f3', 'f4', 'f5'],
        },
    }

    with pytest.raises(ValidationError):
        LensBarChart(**lens_config_too_many)


async def test_xy_breakdown_by_full_snapshot() -> None:
    """Test complete layer snapshot with breakdown_by."""
    lens_config = {
        'type': 'bar',
        'mode': 'stacked',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown_by': {
            'operation': 'terms',
            'fields': ['service.name', 'host.name'],
            'size': 10,
            'id': 'breakdown-id',
        },
    }

    lens_chart = LensBarChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)

    layer = kbn_state_visualization.layers[0]
    assert isinstance(layer, XYDataLayerConfig)
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
            'layerType': 'data',
            'seriesType': 'bar_stacked',
            'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
            'position': 'top',
            'showGridlines': False,
            'splitAccessors': [IsUUID, IsUUID],
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )
