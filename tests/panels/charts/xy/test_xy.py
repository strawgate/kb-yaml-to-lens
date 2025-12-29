"""Test the compilation of Lens metrics from config models to view models."""

from dirty_equals import IsStr, IsUUID
from inline_snapshot import snapshot

from dashboard_compiler.panels.charts.xy.compile import compile_esql_xy_chart, compile_lens_xy_chart
from dashboard_compiler.panels.charts.xy.config import (
    ESQLAreaChart,
    ESQLBarChart,
    ESQLLineChart,
    LensAreaChart,
    LensBarChart,
    LensLineChart,
)


async def test_bar_stacked_chart() -> None:
    """Test bar stacked chart."""
    lens_config = {
        'type': 'bar',
        'mode': 'stacked',
        'data_view': 'metrics-*',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }
    esql_config = {
        'type': 'bar',
        'mode': 'stacked',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'field': 'count(*)', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }

    lens_chart = LensBarChart(**lens_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
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
    layer_id, kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
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
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }
    esql_config = {
        'type': 'bar',
        'mode': 'unstacked',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'field': 'count(*)', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }

    lens_chart = LensBarChart(**lens_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
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
    layer_id, kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
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
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }
    esql_config = {
        'type': 'line',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'field': 'count(*)', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }

    lens_chart = LensLineChart(**lens_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
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
    layer_id, kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
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
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }
    esql_config = {
        'type': 'area',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'field': 'count(*)', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }

    lens_chart = LensAreaChart(**lens_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
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
    layer_id, kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
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


async def test_area_percentage_chart() -> None:
    """Test area percentage chart."""
    lens_config = {
        'type': 'area',
        'mode': 'percentage',
        'data_view': 'metrics-*',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }
    esql_config = {
        'type': 'area',
        'mode': 'percentage',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'field': 'count(*)', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }

    lens_chart = LensAreaChart(**lens_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
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
    layer_id, kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
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


async def test_line_chart_with_reference_lines() -> None:
    """Test line chart with reference lines."""
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'reference_lines': [
            {
                'label': 'SLA Threshold',
                'value': 500.0,
                'axis': 'left',
                'color': '#FF0000',
                'line_style': 'dashed',
                'line_width': 2,
            },
            {
                'label': 'Target',
                'value': 200.0,
                'axis': 'left',
                'color': '#00FF00',
                'line_style': 'solid',
            },
        ],
    }

    lens_chart = LensLineChart(**lens_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None

    # Verify the visualization state layers
    assert kbn_state_visualization.model_dump() == snapshot(
        {
            'preferredSeriesType': 'line',
            'layers': [
                {
                    'layerId': IsUUID,
                    'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
                    'layerType': 'data',
                    'seriesType': 'line',
                    'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
                    'position': 'top',
                    'showGridlines': False,
                    'colorMapping': {
                        'assignments': [],
                        'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                        'paletteId': 'eui_amsterdam_color_blind',
                        'colorMode': {'type': 'categorical'},
                    },
                },
                {
                    'layerId': IsUUID,
                    'accessors': [IsStr],
                    'layerType': 'referenceLine',
                    'yConfig': [
                        {
                            'forAccessor': IsStr,
                            'color': '#FF0000',
                            'lineStyle': 'dashed',
                            'lineWidth': 2.0,
                            'axisMode': {'name': 'left'},
                            'fill': None,
                            'icon': None,
                            'iconPosition': None,
                            'textVisibility': None,
                        }
                    ],
                },
                {
                    'layerId': IsUUID,
                    'accessors': [IsStr],
                    'layerType': 'referenceLine',
                    'yConfig': [
                        {
                            'forAccessor': IsStr,
                            'color': '#00FF00',
                            'lineStyle': 'solid',
                            'lineWidth': None,
                            'axisMode': {'name': 'left'},
                            'fill': None,
                            'icon': None,
                            'iconPosition': None,
                            'textVisibility': None,
                        }
                    ],
                },
            ],
            'legend': {'isVisible': True, 'position': 'right'},
            'valueLabels': 'hide',
        }
    )

    # Verify reference line columns
    ref_1_accessor = kbn_state_visualization.layers[1].accessors[0]
    ref_2_accessor = kbn_state_visualization.layers[2].accessors[0]

    assert kbn_columns[ref_1_accessor].model_dump() == snapshot(
        {
            'label': 'SLA Threshold',
            'dataType': 'number',
            'operationType': 'static_value',
            'isBucketed': False,
            'scale': 'ratio',
            'isStaticValue': True,
            'params': {'value': '500.0'},
            'references': [],
            'customLabel': True,
        }
    )

    assert kbn_columns[ref_2_accessor].model_dump() == snapshot(
        {
            'label': 'Target',
            'dataType': 'number',
            'operationType': 'static_value',
            'isBucketed': False,
            'scale': 'ratio',
            'isStaticValue': True,
            'params': {'value': '200.0'},
            'references': [],
            'customLabel': True,
        }
    )


async def test_reference_line_with_advanced_features() -> None:
    """Test reference line with advanced features like fill, icon, and XYReferenceLineValue object."""
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimensions': [{'field': '@timestamp', 'id': 'dim-id'}],
        'metrics': [{'aggregation': 'count', 'id': 'metric-id'}],
        'reference_lines': [
            {
                'label': 'Critical Threshold',
                'value': {'type': 'static', 'value': 1000.0},  # XYReferenceLineValue object form
                'axis': 'right',
                'color': '#E7664C',
                'line_style': 'dotted',
                'line_width': 3,
                'fill': 'above',
                'icon': 'alert',
                'icon_position': 'above',
            },
        ],
    }

    lens_chart = LensLineChart(**lens_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)

    # Verify layer structure matches Kibana's XYReferenceLineLayerConfig
    ref_layer = kbn_state_visualization.layers[1]
    assert ref_layer.layerType == 'referenceLine'
    assert len(ref_layer.accessors) == 1
    assert ref_layer.yConfig is not None
    assert len(ref_layer.yConfig) == 1

    # Verify YConfig structure matches Kibana's YConfig type
    y_config = ref_layer.yConfig[0]
    assert y_config.forAccessor == ref_layer.accessors[0]
    assert y_config.color == '#E7664C'
    assert y_config.lineStyle == 'dotted'
    assert y_config.lineWidth == 3.0
    assert y_config.fill == 'above'
    assert y_config.icon == 'alert'
    assert y_config.iconPosition == 'above'
    assert y_config.axisMode is not None
    assert y_config.axisMode.name == 'right'

    # Verify column structure matches Kibana's static value column type
    accessor_id = ref_layer.accessors[0]
    ref_column = kbn_columns[accessor_id]
    assert ref_column.label == 'Critical Threshold'
    assert ref_column.dataType == 'number'
    assert ref_column.operationType == 'static_value'
    assert ref_column.isBucketed is False
    assert ref_column.scale == 'ratio'
    assert ref_column.isStaticValue is True
    assert ref_column.params.value == '1000.0'
    assert ref_column.references == []
    assert ref_column.customLabel is True


async def test_reference_line_without_label() -> None:
    """Test reference line without explicit label uses default format."""
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimensions': [{'field': '@timestamp', 'id': 'dim-id'}],
        'metrics': [{'aggregation': 'count', 'id': 'metric-id'}],
        'reference_lines': [
            {
                'value': 750.0,
                'color': '#5470C6',
            },
        ],
    }

    lens_chart = LensLineChart(**lens_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)

    # Verify default label format
    ref_layer = kbn_state_visualization.layers[1]
    accessor_id = ref_layer.accessors[0]
    ref_column = kbn_columns[accessor_id]
    assert ref_column.label == 'Static value: 750.0'
    assert ref_column.params.value == '750.0'
