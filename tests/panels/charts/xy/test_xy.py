"""Test the compilation of Lens metrics from config models to view models."""

from dirty_equals import IsUUID
from inline_snapshot import snapshot

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
            'textVisibility': None,
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
                        'lineWidth': None,
                        'lineStyle': 'solid',
                        'fill': None,
                        'icon': None,
                        'iconPosition': None,
                        'textVisibility': None,
                        'axisMode': 'left',
                    },
                    {
                        'forAccessor': 'threshold-high',
                        'color': '#FF0000',
                        'lineWidth': None,
                        'lineStyle': 'dashed',
                        'fill': None,
                        'icon': None,
                        'iconPosition': None,
                        'textVisibility': None,
                        'axisMode': 'left',
                    },
                    {
                        'forAccessor': 'threshold-critical',
                        'color': '#FF00FF',
                        'lineWidth': 3.0,
                        'lineStyle': 'dotted',
                        'fill': None,
                        'icon': None,
                        'iconPosition': None,
                        'textVisibility': None,
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
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'legend': {'position': 'top'},
    }

    lens_chart = LensLineChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    assert kbn_state_visualization.legend == snapshot({'isVisible': True, 'position': 'top'})


async def test_xy_chart_with_legend_hidden() -> None:
    """Test XY chart with hidden legend."""
    lens_config = {
        'type': 'bar',
        'data_view': 'metrics-*',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'legend': {'visible': False},
    }

    lens_chart = LensBarChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    assert kbn_state_visualization.legend == snapshot({'isVisible': False, 'position': 'right'})


async def test_xy_chart_with_legend_bottom_position() -> None:
    """Test XY chart with legend at bottom."""
    lens_config = {
        'type': 'area',
        'data_view': 'metrics-*',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'legend': {'visible': True, 'position': 'bottom'},
    }

    lens_chart = LensAreaChart(**lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    assert kbn_state_visualization.legend == snapshot({'isVisible': True, 'position': 'bottom'})
