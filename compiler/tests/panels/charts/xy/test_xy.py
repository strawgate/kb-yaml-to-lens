"""Test the compilation of Lens metrics from config models to view models."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import pytest
from dirty_equals import IsStr, IsUUID
from inline_snapshot import snapshot
from pydantic import ValidationError

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.panels.charts.xy.compile import (
    compile_esql_xy_chart,
    compile_lens_reference_line_layer,
    compile_lens_xy_chart,
    compile_reference_line,
)
from dashboard_compiler.panels.charts.xy.config import (
    ESQLAreaChart,
    ESQLBarChart,
    ESQLLineChart,
    LensAreaChart,
    LensBarChart,
    LensLineChart,
    LensReferenceLineLayer,
    XYReferenceLine,
    XYReferenceLineValue,
)
from dashboard_compiler.panels.charts.xy.view import XYDataLayerConfig, XYLegendConfig

if TYPE_CHECKING:
    from dashboard_compiler.dashboard.view import KbnDashboard


async def test_bar_stacked_chart() -> None:
    """Test bar stacked chart."""
    lens_config = {
        'type': 'bar',
        'mode': 'stacked',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'type': 'values', 'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }
    esql_config = {
        'type': 'bar',
        'mode': 'stacked',
        'dimension': {'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'field': 'count(*)', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }

    lens_chart = LensBarChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
            'layerType': 'data',
            'seriesType': 'bar_stacked',
            'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
            'position': 'top',
            'showGridlines': False,
            'splitAccessor': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )

    esql_chart = ESQLBarChart(**esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
            'layerType': 'data',
            'seriesType': 'bar_stacked',
            'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
            'position': 'top',
            'showGridlines': False,
            'splitAccessor': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )


async def test_bar_unstacked_chart() -> None:
    """Test bar unstacked chart."""
    lens_config = {
        'type': 'bar',
        'mode': 'unstacked',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'type': 'values', 'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }
    esql_config = {
        'type': 'bar',
        'mode': 'unstacked',
        'dimension': {'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'field': 'count(*)', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }

    lens_chart = LensBarChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
            'layerType': 'data',
            'seriesType': 'bar_unstacked',
            'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
            'position': 'top',
            'showGridlines': False,
            'splitAccessor': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )

    esql_chart = ESQLBarChart(**esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
            'layerType': 'data',
            'seriesType': 'bar_unstacked',
            'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
            'position': 'top',
            'showGridlines': False,
            'splitAccessor': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )


async def test_line_chart() -> None:
    """Test line chart."""
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'type': 'values', 'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }
    esql_config = {
        'type': 'line',
        'dimension': {'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'field': 'count(*)', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }

    lens_chart = LensLineChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
            'layerType': 'data',
            'seriesType': 'line',
            'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
            'position': 'top',
            'showGridlines': False,
            'splitAccessor': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )

    esql_chart = ESQLLineChart(**esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
            'layerType': 'data',
            'seriesType': 'line',
            'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
            'position': 'top',
            'showGridlines': False,
            'splitAccessor': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )


async def test_area_chart() -> None:
    """Test area chart."""
    lens_config = {
        'type': 'area',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'type': 'values', 'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }
    esql_config = {
        'type': 'area',
        'dimension': {'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'field': 'count(*)', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }

    lens_chart = LensAreaChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
            'layerType': 'data',
            'seriesType': 'area',
            'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
            'position': 'top',
            'showGridlines': False,
            'splitAccessor': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )

    esql_chart = ESQLAreaChart(**esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
            'layerType': 'data',
            'seriesType': 'area',
            'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
            'position': 'top',
            'showGridlines': False,
            'splitAccessor': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )


async def test_bar_percentage_chart() -> None:
    """Test bar percentage chart."""
    lens_config = {
        'type': 'bar',
        'mode': 'percentage',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp'},
        'metrics': [{'aggregation': 'count'}],
    }
    esql_config = {
        'type': 'bar',
        'mode': 'percentage',
        'dimension': {'field': '@timestamp'},
        'metrics': [{'field': 'count(*)'}],
    }

    lens_chart = LensBarChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': [IsUUID],
            'layerType': 'data',
            'seriesType': 'bar_percentage_stacked',
            'xAccessor': IsUUID,
            'position': 'top',
            'showGridlines': False,
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )

    esql_chart = ESQLBarChart(**esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': [IsUUID],
            'layerType': 'data',
            'seriesType': 'bar_percentage_stacked',
            'xAccessor': IsUUID,
            'position': 'top',
            'showGridlines': False,
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )


async def test_area_percentage_chart() -> None:
    """Test area percentage chart."""
    lens_config = {
        'type': 'area',
        'mode': 'percentage',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'type': 'values', 'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }
    esql_config = {
        'type': 'area',
        'mode': 'percentage',
        'dimension': {'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'field': 'count(*)', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }

    lens_chart = LensAreaChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
            'layerType': 'data',
            'seriesType': 'area_percentage_stacked',
            'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
            'position': 'top',
            'showGridlines': False,
            'splitAccessor': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )

    esql_chart = ESQLAreaChart(**esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
            'layerType': 'data',
            'seriesType': 'area_percentage_stacked',
            'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
            'position': 'top',
            'showGridlines': False,
            'splitAccessor': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )


async def test_area_unstacked_chart() -> None:
    """Test area unstacked chart."""
    lens_config = {
        'type': 'area',
        'mode': 'unstacked',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp'},
        'metrics': [{'aggregation': 'count'}],
    }
    esql_config = {
        'type': 'area',
        'mode': 'unstacked',
        'dimension': {'field': '@timestamp'},
        'metrics': [{'field': 'count(*)'}],
    }

    lens_chart = LensAreaChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': [IsUUID],
            'layerType': 'data',
            'seriesType': 'area_unstacked',
            'xAccessor': IsUUID,
            'position': 'top',
            'showGridlines': False,
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )

    esql_chart = ESQLAreaChart(**esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': [IsUUID],
            'layerType': 'data',
            'seriesType': 'area_unstacked',
            'xAccessor': IsUUID,
            'position': 'top',
            'showGridlines': False,
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )


async def test_reference_line_single() -> None:
    """Test compilation of a single reference line."""
    ref_line = XYReferenceLine(
        id='ref-line-1',
        label='SLA Threshold',
        value=500.0,
        color='#FF0000',
        line_width=2,
        line_style='dashed',
        fill='above',
        icon='alert',
        icon_position='auto',
        axis='left',
    )

    accessor_id, ref_column, y_config = compile_reference_line(ref_line)

    # Test the accessor ID
    assert accessor_id == 'ref-line-1'

    # Test the Y config structure
    assert y_config.model_dump() == snapshot(
        {
            'forAccessor': 'ref-line-1',
            'color': '#FF0000',
            'lineWidth': 2.0,
            'lineStyle': 'dashed',
            'fill': 'above',
            'icon': 'alert',
            'iconPosition': 'auto',
            'axisMode': 'left',
        }
    )

    # Test the static value column structure
    assert ref_column.model_dump() == snapshot(
        {
            'label': 'SLA Threshold',
            'dataType': 'number',
            'operationType': 'static_value',
            'isBucketed': False,
            'isStaticValue': True,
            'scale': 'ratio',
            'params': {'value': '500.0'},
            'references': [],
            'customLabel': True,
        }
    )


async def test_reference_line_with_value_object() -> None:
    """Test reference line with XYReferenceLineValue instead of float."""
    ref_line = XYReferenceLine(
        label='Baseline',
        value=XYReferenceLineValue(value=100.0),
    )

    _accessor_id, ref_column, _y_config = compile_reference_line(ref_line)

    # Should compile to same static value column structure
    assert ref_column.params.value == '100.0'
    assert ref_column.label == 'Baseline'


async def test_reference_line_minimal() -> None:
    """Test reference line with minimal configuration."""
    ref_line = XYReferenceLine(value=250.0)

    _accessor_id, ref_column, y_config = compile_reference_line(ref_line)

    # Test defaults
    assert ref_column.label == 'Static value: 250.0'
    assert ref_column.customLabel is False
    assert y_config.axisMode == 'left'  # default axis


async def test_reference_line_layer_multiple_lines() -> None:
    """Test compilation of a reference line layer with multiple lines."""
    layer_config = LensReferenceLineLayer(
        data_view='logs-*',
        reference_lines=[
            XYReferenceLine(
                id='threshold-low',
                label='Low Threshold',
                value=100.0,
                color='#00FF00',
                line_style='solid',
            ),
            XYReferenceLine(
                id='threshold-high',
                label='High Threshold',
                value=500.0,
                color='#FF0000',
                line_style='dashed',
            ),
            XYReferenceLine(
                id='threshold-critical',
                label='Critical',
                value=1000.0,
                color='#FF00FF',
                line_style='dotted',
                line_width=3,
            ),
        ],
    )

    layer_id, columns, ref_layers = compile_lens_reference_line_layer(layer_config)

    # Validate the complete output structure using snapshots
    assert (layer_id, len(ref_layers), ref_layers[0].model_dump()) == snapshot(
        (
            IsUUID,
            1,
            {
                'layerId': IsUUID,
                'accessors': ['threshold-low', 'threshold-high', 'threshold-critical'],
                'yConfig': [
                    {
                        'forAccessor': 'threshold-low',
                        'color': '#00FF00',
                        'lineStyle': 'solid',
                        'axisMode': 'left',
                    },
                    {
                        'forAccessor': 'threshold-high',
                        'color': '#FF0000',
                        'lineStyle': 'dashed',
                        'axisMode': 'left',
                    },
                    {
                        'forAccessor': 'threshold-critical',
                        'color': '#FF00FF',
                        'lineWidth': 3.0,
                        'lineStyle': 'dotted',
                        'axisMode': 'left',
                    },
                ],
                'layerType': 'referenceLine',
            },
        )
    )

    # Validate columns structure using snapshot
    assert {k: v.model_dump() for k, v in columns.items()} == snapshot(
        {
            'threshold-low': {
                'label': 'Low Threshold',
                'dataType': 'number',
                'operationType': 'static_value',
                'isBucketed': False,
                'isStaticValue': True,
                'scale': 'ratio',
                'params': {'value': '100.0'},
                'references': [],
                'customLabel': True,
            },
            'threshold-high': {
                'label': 'High Threshold',
                'dataType': 'number',
                'operationType': 'static_value',
                'isBucketed': False,
                'isStaticValue': True,
                'scale': 'ratio',
                'params': {'value': '500.0'},
                'references': [],
                'customLabel': True,
            },
            'threshold-critical': {
                'label': 'Critical',
                'dataType': 'number',
                'operationType': 'static_value',
                'isBucketed': False,
                'isStaticValue': True,
                'scale': 'ratio',
                'params': {'value': '1000.0'},
                'references': [],
                'customLabel': True,
            },
        }
    )


async def test_reference_line_layer_without_ids() -> None:
    """Test that multiple reference lines without IDs get unique accessor IDs."""
    layer_config = LensReferenceLineLayer(
        data_view='logs-*',
        reference_lines=[
            XYReferenceLine(value=100.0, label='Threshold 1'),
            XYReferenceLine(value=200.0, label='Threshold 2'),
            XYReferenceLine(value=300.0, label='Threshold 3'),
        ],
    )

    layer_id, columns, ref_layers = compile_lens_reference_line_layer(layer_config)

    # Validate basic structure
    accessor_ids = list(columns.keys())
    assert isinstance(layer_id, str)
    assert len(ref_layers) == 1
    assert len(columns) == 3
    # All accessor IDs should be unique (no collisions)
    assert len(accessor_ids) == len(set(accessor_ids))
    # Accessor IDs should not be the layer_id (they should be generated)
    assert all(accessor_id != layer_id for accessor_id in accessor_ids)
    # Column values should be correct
    assert sorted([col.params.value for col in columns.values()]) == ['100.0', '200.0', '300.0']
    # The single layer has all 3 accessors
    assert len(ref_layers[0].accessors) == 3
    assert ref_layers[0].yConfig is not None
    assert len(ref_layers[0].yConfig) == 3


async def test_reference_line_layer_empty() -> None:
    """Test compilation of a reference line layer with no lines."""
    layer_config = LensReferenceLineLayer(
        data_view='logs-*',
        reference_lines=[],
    )

    layer_id, columns, ref_layers = compile_lens_reference_line_layer(layer_config)

    # Validate empty layer structure
    assert isinstance(layer_id, str)
    assert len(columns) == 0
    assert len(ref_layers) == 1
    assert len(ref_layers[0].accessors) == 0
    assert ref_layers[0].yConfig is not None
    assert len(ref_layers[0].yConfig) == 0


async def test_xy_chart_with_legend_position() -> None:
    """Test XY chart with custom legend position."""
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'legend': {'position': 'top'},
    }

    lens_chart = LensLineChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    assert kbn_state_visualization.legend == snapshot(
        XYLegendConfig(isVisible=None, position='top', showSingleSeries=None, legendSize=None, shouldTruncate=None, maxLines=None)
    )


async def test_xy_chart_with_legend_hidden() -> None:
    """Test XY chart with hidden legend."""
    lens_config = {
        'type': 'bar',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'legend': {'visible': 'hide'},
    }

    lens_chart = LensBarChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    assert kbn_state_visualization.legend == snapshot(
        XYLegendConfig(isVisible=False, position='right', showSingleSeries=None, legendSize=None, shouldTruncate=None, maxLines=None)
    )


async def test_xy_chart_with_legend_auto() -> None:
    """Test XY chart with legend visibility set to auto.

    When visibility is 'auto', isVisible should be None (omitted from output),
    allowing Kibana to automatically determine legend visibility based on series count.
    """
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'legend': {'visible': 'auto'},
    }

    lens_chart = LensLineChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    assert kbn_state_visualization.legend == snapshot(
        XYLegendConfig(isVisible=None, position='right', showSingleSeries=None, legendSize=None, shouldTruncate=None, maxLines=None)
    )


async def test_xy_chart_with_legend_bottom_position() -> None:
    """Test XY chart with legend at bottom."""
    lens_config = {
        'type': 'area',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'legend': {'visible': 'show', 'position': 'bottom'},
    }

    lens_chart = LensAreaChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    assert kbn_state_visualization.legend == snapshot(
        XYLegendConfig(isVisible=True, position='bottom', showSingleSeries=None, legendSize=None, shouldTruncate=None, maxLines=None)
    )


async def test_xy_chart_with_legend_size() -> None:
    """Test XY chart with custom legend size."""
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'legend': {'size': 'large'},
    }

    lens_chart = LensLineChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    assert kbn_state_visualization.legend == snapshot(
        XYLegendConfig(isVisible=None, position='right', showSingleSeries=None, legendSize='large', shouldTruncate=None, maxLines=None)
    )


async def test_xy_chart_with_legend_truncate() -> None:
    """Test XY chart with legend label truncation."""
    lens_config = {
        'type': 'bar',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'legend': {'truncate_labels': 2},
    }

    lens_chart = LensBarChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    assert kbn_state_visualization.legend == snapshot(
        XYLegendConfig(isVisible=None, position='right', showSingleSeries=None, legendSize=None, shouldTruncate=True, maxLines=2)
    )


async def test_xy_chart_with_legend_no_truncate() -> None:
    """Test XY chart with legend label truncation disabled."""
    lens_config = {
        'type': 'area',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'legend': {'truncate_labels': 0},
    }

    lens_chart = LensAreaChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    assert kbn_state_visualization.legend == snapshot(
        XYLegendConfig(isVisible=None, position='right', showSingleSeries=None, legendSize=None, shouldTruncate=False, maxLines=None)
    )


async def test_xy_chart_with_show_single_series() -> None:
    """Test XY chart with show_single_series enabled."""
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'legend': {'show_single_series': True},
    }

    lens_chart = LensLineChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    assert kbn_state_visualization.legend == snapshot(
        XYLegendConfig(isVisible=None, position='right', showSingleSeries=True, legendSize=None, shouldTruncate=None, maxLines=None)
    )


async def test_dual_axis_chart() -> None:
    """Test dual Y-axis chart with per-metric configuration.

    Uses the metric-based configuration structure where visual properties
    are defined directly on metric definitions.
    """
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [
            {'aggregation': 'count', 'id': 'metric1', 'axis': 'left', 'color': '#2196F3'},
            {'aggregation': 'average', 'field': 'error_rate', 'id': 'metric2', 'axis': 'right', 'color': '#FF5252'},
        ],
        'appearance': {
            'y_left_axis': {'title': 'Count', 'scale': 'linear'},
            'y_right_axis': {'title': 'Error Rate (%)', 'scale': 'linear'},
        },
    }
    lens_chart = LensLineChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None

    # Test layer configuration
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': ['metric1', 'metric2'],
            'layerType': 'data',
            'seriesType': 'line',
            'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
            'position': 'top',
            'showGridlines': False,
            'yConfig': [
                {'forAccessor': 'metric1', 'axisMode': 'left', 'color': '#2196F3'},
                {'forAccessor': 'metric2', 'axisMode': 'right', 'color': '#FF5252'},
            ],
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )

    # Test axis configuration
    assert kbn_state_visualization.yTitle == 'Count'  # Legacy field for backward compatibility
    assert kbn_state_visualization.yLeftTitle == 'Count'
    assert kbn_state_visualization.yRightTitle == 'Error Rate (%)'
    assert kbn_state_visualization.yLeftScale == 'linear'
    assert kbn_state_visualization.yRightScale == 'linear'

    # Test axis title visibility settings
    assert kbn_state_visualization.axisTitlesVisibilitySettings is not None
    assert kbn_state_visualization.axisTitlesVisibilitySettings.yLeft is True
    assert kbn_state_visualization.axisTitlesVisibilitySettings.yRight is True
    assert kbn_state_visualization.axisTitlesVisibilitySettings.x is False


async def test_styled_series_chart() -> None:
    """Test chart with styled series using metric-based configuration.

    Uses the metric-based configuration where visual properties like color
    are defined directly on metric definitions.
    """
    lens_config = {
        'type': 'area',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'},
        'metrics': [
            {'aggregation': 'sum', 'field': 'bytes_in', 'id': 'metric1', 'color': '#4CAF50'},
            {'aggregation': 'sum', 'field': 'bytes_out', 'id': 'metric2', 'color': '#FF9800'},
        ],
    }

    lens_chart = LensAreaChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'accessors': ['metric1', 'metric2'],
            'layerType': 'data',
            'seriesType': 'area',
            'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
            'position': 'top',
            'showGridlines': False,
            'yConfig': [
                {'forAccessor': 'metric1', 'color': '#4CAF50'},
                {'forAccessor': 'metric2', 'color': '#FF9800'},
            ],
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )


async def test_axis_extent_configuration() -> None:
    """Test axis extent/bounds configuration for custom axis ranges."""
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
        'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
        'appearance': {
            'x_axis': {'title': 'Time', 'extent': {'mode': 'custom', 'min': 0, 'max': 100, 'enforce': True}},
            'y_left_axis': {'title': 'Count', 'extent': {'mode': 'data_bounds'}},
        },
    }
    lens_chart = LensLineChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)

    # Verify extent compilation for x-axis (custom bounds)
    assert kbn_state_visualization.xExtent is not None
    assert kbn_state_visualization.xExtent.mode == 'custom'
    assert kbn_state_visualization.xExtent.lowerBound == 0
    assert kbn_state_visualization.xExtent.upperBound == 100
    assert kbn_state_visualization.xExtent.enforce is True

    # Verify extent compilation for y-axis (data bounds)
    assert kbn_state_visualization.yLeftExtent is not None
    assert kbn_state_visualization.yLeftExtent.mode == 'dataBounds'

    # Verify axis titles (including legacy yTitle field)
    assert kbn_state_visualization.yTitle == 'Count'  # Legacy field for backward compatibility
    assert kbn_state_visualization.yLeftTitle == 'Count'

    # Verify axis title visibility settings
    assert kbn_state_visualization.axisTitlesVisibilitySettings is not None
    assert kbn_state_visualization.axisTitlesVisibilitySettings.x is True
    assert kbn_state_visualization.axisTitlesVisibilitySettings.yLeft is True
    assert kbn_state_visualization.axisTitlesVisibilitySettings.yRight is False


async def test_line_chart_with_fitting_function() -> None:
    """Test line chart with fitting function configuration."""
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
        'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
        'appearance': {
            'missing_values': 'Linear',
            'show_as_dotted': True,
            'end_values': 'Zero',
        },
    }

    lens_chart = LensLineChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None

    # Verify fitting function is compiled
    assert kbn_state_visualization.fittingFunction == 'Linear'
    assert kbn_state_visualization.emphasizeFitting is True
    assert kbn_state_visualization.endValue == 'Zero'


@pytest.mark.parametrize('fitting_func', ['None', 'Linear', 'Carry', 'Lookahead', 'Average', 'Nearest'])
async def test_line_chart_with_all_fitting_functions(fitting_func: str) -> None:
    """Test line chart with all available fitting function options."""
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
        'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
        'appearance': {
            'missing_values': fitting_func,
        },
    }

    lens_chart = LensLineChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    assert kbn_state_visualization.fittingFunction == fitting_func


async def test_area_chart_with_fitting_and_fill_opacity() -> None:
    """Test area chart with fitting function and fill opacity."""
    lens_config = {
        'type': 'area',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
        'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
        'appearance': {
            'missing_values': 'Carry',
            'show_as_dotted': False,
            'fill_opacity': 0.5,
        },
    }

    lens_chart = LensAreaChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None

    # Verify fitting function and fill opacity
    assert kbn_state_visualization.fittingFunction == 'Carry'
    assert kbn_state_visualization.emphasizeFitting is False
    assert kbn_state_visualization.fillOpacity == 0.5


async def test_line_chart_with_time_series_features() -> None:
    """Test line chart with time series features (current time marker and hide endzones)."""
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
        'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
        'show_current_time_marker': True,
        'hide_endzones': True,
    }

    lens_chart = LensLineChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None

    # Verify time series features
    assert kbn_state_visualization.showCurrentTimeMarker is True
    assert kbn_state_visualization.hideEndzones is True


async def test_area_chart_with_time_series_features() -> None:
    """Test area chart with time series features."""
    lens_config = {
        'type': 'area',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
        'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
        'show_current_time_marker': False,
        'hide_endzones': False,
    }

    lens_chart = LensAreaChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None

    # Verify time series features
    assert kbn_state_visualization.showCurrentTimeMarker is False
    assert kbn_state_visualization.hideEndzones is False


async def test_line_chart_with_all_advanced_features() -> None:
    """Test line chart with all advanced features combined."""
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
        'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
        'appearance': {
            'missing_values': 'Average',
            'show_as_dotted': True,
            'end_values': 'Nearest',
            'line_style': 'monotone-x',
        },
        'show_current_time_marker': True,
        'hide_endzones': True,
    }

    lens_chart = LensLineChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None

    # Verify all features are compiled
    assert kbn_state_visualization.fittingFunction == 'Average'
    assert kbn_state_visualization.emphasizeFitting is True
    assert kbn_state_visualization.endValue == 'Nearest'
    assert kbn_state_visualization.curveType == 'CURVE_MONOTONE_X'  # Mapped from 'monotone-x' to Kibana format
    assert kbn_state_visualization.showCurrentTimeMarker is True
    assert kbn_state_visualization.hideEndzones is True


@pytest.mark.parametrize(
    ('config_value', 'expected_kibana_value'),
    [
        ('linear', 'LINEAR'),
        ('monotone-x', 'CURVE_MONOTONE_X'),
        ('step-after', 'CURVE_STEP_AFTER'),
    ],
)
async def test_line_style_mapping(config_value: str, expected_kibana_value: str) -> None:
    """Test that line styles are correctly mapped from config to Kibana format.

    Only tests the 3 line styles supported by Kibana.
    """
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
        'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
        'appearance': {
            'line_style': config_value,
        },
    }

    lens_chart = LensLineChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)

    assert kbn_state_visualization.curveType == expected_kibana_value


async def test_esql_line_chart_with_advanced_features() -> None:
    """Test ESQL line chart with advanced features."""
    esql_config = {
        'type': 'line',
        'dimension': {'field': '@timestamp', 'id': 'dim1'},
        'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
        'appearance': {
            'missing_values': 'Lookahead',
            'show_as_dotted': False,
        },
        'show_current_time_marker': True,
        'hide_endzones': False,
    }

    esql_chart = ESQLLineChart.model_validate(esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
    assert kbn_state_visualization is not None

    # Verify features are compiled for ESQL charts
    assert kbn_state_visualization.fittingFunction == 'Lookahead'
    assert kbn_state_visualization.emphasizeFitting is False
    assert kbn_state_visualization.showCurrentTimeMarker is True
    assert kbn_state_visualization.hideEndzones is False


async def test_esql_area_chart_with_fitting_and_fill_opacity() -> None:
    """Test ESQL area chart with fitting function and fill opacity."""
    esql_config = {
        'type': 'area',
        'dimension': {'field': '@timestamp', 'id': 'dim1'},
        'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
        'appearance': {
            'missing_values': 'Carry',
            'show_as_dotted': True,
            'fill_opacity': 0.7,
        },
        'show_current_time_marker': False,
        'hide_endzones': True,
    }

    esql_chart = ESQLAreaChart.model_validate(esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
    assert kbn_state_visualization is not None

    # Verify features are compiled for ESQL area charts
    assert kbn_state_visualization.fittingFunction == 'Carry'
    assert kbn_state_visualization.emphasizeFitting is True
    assert kbn_state_visualization.fillOpacity == 0.7
    assert kbn_state_visualization.showCurrentTimeMarker is False
    assert kbn_state_visualization.hideEndzones is True


async def test_bar_chart_with_min_bar_height() -> None:
    """Test bar chart with min_bar_height configuration."""
    lens_config = {
        'type': 'bar',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
        'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
        'appearance': {
            'min_bar_height': 5.0,
        },
    }

    lens_chart = LensBarChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None

    # Verify min_bar_height is compiled
    assert kbn_state_visualization.minBarHeight == 5.0


async def test_bar_chart_with_min_bar_height_and_axis_config() -> None:
    """Test bar chart with min_bar_height and axis configuration."""
    lens_config = {
        'type': 'bar',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
        'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
        'appearance': {
            'min_bar_height': 3.5,
            'y_left_axis': {
                'title': 'Count',
                'scale': 'linear',
            },
        },
    }

    lens_chart = LensBarChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None

    # Verify min_bar_height and axis config are compiled
    assert kbn_state_visualization.minBarHeight == 3.5
    assert kbn_state_visualization.yLeftTitle == 'Count'
    assert kbn_state_visualization.yLeftScale == 'linear'


@pytest.mark.parametrize(
    ('chart_cls', 'config'),
    [
        (
            LensBarChart,
            {
                'type': 'bar',
                'data_view': 'metrics-*',
                'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
                'metrics': [],
            },
        ),
        (
            LensLineChart,
            {
                'type': 'line',
                'data_view': 'metrics-*',
                'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
                'metrics': [],
            },
        ),
        (
            LensAreaChart,
            {
                'type': 'area',
                'data_view': 'metrics-*',
                'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
                'metrics': [],
            },
        ),
        (
            ESQLBarChart,
            {
                'type': 'bar',
                'dimension': {'field': '@timestamp', 'id': 'dim1'},
                'metrics': [],
            },
        ),
        (
            ESQLLineChart,
            {
                'type': 'line',
                'dimension': {'field': '@timestamp', 'id': 'dim1'},
                'metrics': [],
            },
        ),
        (
            ESQLAreaChart,
            {
                'type': 'area',
                'dimension': {'field': '@timestamp', 'id': 'dim1'},
                'metrics': [],
            },
        ),
    ],
    ids=[
        'lens-bar',
        'lens-line',
        'lens-area',
        'esql-bar',
        'esql-line',
        'esql-area',
    ],
)
async def test_chart_validation_requires_metrics(chart_cls: type[Any], config: dict[str, Any]) -> None:
    """Test that chart validation fails when metrics list is empty."""
    with pytest.raises(ValidationError, match=r'List should have at least 1 item'):
        chart_cls.model_validate(config)


@pytest.mark.parametrize(
    ('chart_cls', 'compile_fn', 'compile_kwarg', 'config'),
    [
        (
            LensBarChart,
            compile_lens_xy_chart,
            'lens_xy_chart',
            {
                'type': 'bar',
                'data_view': 'metrics-*',
                'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
            },
        ),
        (
            ESQLLineChart,
            compile_esql_xy_chart,
            'esql_xy_chart',
            {
                'type': 'line',
                'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
            },
        ),
    ],
    ids=['lens-bar', 'esql-line'],
)
async def test_chart_without_dimension(
    chart_cls: type[Any],
    compile_fn: Callable[..., tuple[Any, Any, Any]],
    compile_kwarg: str,
    config: dict[str, Any],
) -> None:
    """Test charts with no dimension (dimension=None)."""
    chart = chart_cls(**config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_fn(**{compile_kwarg: chart})
    assert kbn_state_visualization is not None
    layer_dict = kbn_state_visualization.layers[0].model_dump()
    assert layer_dict['xAccessor'] is None
    assert len(layer_dict['accessors']) == 1


async def test_metric_with_axis_only() -> None:
    """Test metric with only axis configuration (no color)."""
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
        'metrics': [
            {'aggregation': 'count', 'id': 'metric1', 'axis': 'left'},
            {'aggregation': 'average', 'field': 'response_time', 'id': 'metric2', 'axis': 'right'},
        ],
    }

    lens_chart = LensLineChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None

    # Verify yConfig contains only axis settings
    layer = kbn_state_visualization.layers[0]
    assert isinstance(layer, XYDataLayerConfig)
    assert layer.yConfig is not None
    assert len(layer.yConfig) == 2
    assert layer.yConfig[0].model_dump() == snapshot({'forAccessor': 'metric1', 'axisMode': 'left'})
    assert layer.yConfig[1].model_dump() == snapshot({'forAccessor': 'metric2', 'axisMode': 'right'})


async def test_metric_with_color_only() -> None:
    """Test metric with only color configuration (no axis)."""
    lens_config = {
        'type': 'bar',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
        'metrics': [
            {'aggregation': 'count', 'id': 'metric1', 'color': '#FF0000'},
            {'aggregation': 'sum', 'field': 'bytes', 'id': 'metric2', 'color': '#00FF00'},
        ],
    }

    lens_chart = LensBarChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None

    # Verify yConfig contains only color settings
    layer = kbn_state_visualization.layers[0]
    assert isinstance(layer, XYDataLayerConfig)
    assert layer.yConfig is not None
    assert len(layer.yConfig) == 2
    assert layer.yConfig[0].model_dump() == snapshot({'forAccessor': 'metric1', 'color': '#FF0000'})
    assert layer.yConfig[1].model_dump() == snapshot({'forAccessor': 'metric2', 'color': '#00FF00'})


async def test_metric_with_no_appearance() -> None:
    """Test metric with no appearance configuration (no axis or color)."""
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
        'metrics': [
            {'aggregation': 'count', 'id': 'metric1'},
            {'aggregation': 'average', 'field': 'response_time', 'id': 'metric2'},
        ],
    }

    lens_chart = LensLineChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None

    # Verify no yConfig is created when metrics have no appearance properties
    layer = kbn_state_visualization.layers[0]
    assert isinstance(layer, XYDataLayerConfig)
    assert layer.yConfig is None


async def test_mixed_metrics_some_with_appearance() -> None:
    """Test chart with mix of metrics with and without appearance properties."""
    lens_config = {
        'type': 'area',
        'data_view': 'metrics-*',
        'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
        'metrics': [
            {'aggregation': 'count', 'id': 'metric1', 'color': '#FF0000'},
            {'aggregation': 'average', 'field': 'response_time', 'id': 'metric2'},
            {'aggregation': 'sum', 'field': 'bytes', 'id': 'metric3', 'axis': 'right', 'color': '#0000FF'},
        ],
    }

    lens_chart = LensAreaChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None

    # Verify yConfig only includes metrics with appearance properties
    layer = kbn_state_visualization.layers[0]
    assert isinstance(layer, XYDataLayerConfig)
    assert layer.yConfig is not None
    assert len(layer.yConfig) == 2  # Only metric1 and metric3
    assert layer.yConfig[0].model_dump() == snapshot({'forAccessor': 'metric1', 'color': '#FF0000'})
    assert layer.yConfig[1].model_dump() == snapshot({'forAccessor': 'metric3', 'axisMode': 'right', 'color': '#0000FF'})


def test_xy_chart_dashboard_references_bubble_up() -> None:
    """Test that XY chart data view references bubble up to dashboard level correctly.

    XY charts (line, bar, area) reference a data view (index-pattern), so this reference
    should appear at the dashboard's top-level references array with proper panel namespacing.
    """
    dashboard = Dashboard(
        name='Test XY Chart Dashboard',
        panels=[
            {
                'title': 'Line Chart',
                'id': 'xy-panel-1',
                'grid': {'x': 0, 'y': 0, 'w': 24, 'h': 15},
                'lens': {
                    'type': 'line',
                    'data_view': 'logs-*',
                    'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
                    'metrics': [{'aggregation': 'count', 'id': 'count-metric'}],
                },
            }
        ],
    )

    kbn_dashboard: KbnDashboard = render(dashboard=dashboard)
    references = [ref.model_dump() for ref in kbn_dashboard.references]

    assert references == snapshot(
        [
            {
                'id': 'logs-*',
                'name': IsStr(regex=r'xy-panel-1:indexpattern-datasource-layer-[a-f0-9-]+'),
                'type': 'index-pattern',
            }
        ]
    )
