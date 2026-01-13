"""Test the compilation of Lens mosaic charts from config models to view models."""

from dirty_equals import IsUUID
from inline_snapshot import snapshot

from dashboard_compiler.panels.charts.config import ESQLMosaicPanelConfig
from dashboard_compiler.panels.charts.mosaic.compile import compile_esql_mosaic_chart, compile_lens_mosaic_chart
from dashboard_compiler.panels.charts.mosaic.config import LensMosaicChart


async def test_basic_mosaic_chart() -> None:
    """Test basic mosaic chart."""
    lens_config = {
        'type': 'mosaic',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'dimension': {'type': 'values', 'field': 'http.request.method', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'mosaic',
        'query': 'FROM logs-* | STATS count = COUNT(*) BY http.request.method',
        'metric': {'field': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'dimension': {'field': 'http.request.method', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensMosaicChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_mosaic_chart(lens_mosaic_chart=lens_chart)
    assert kbn_state_visualization is not None
    assert kbn_state_visualization.shape == 'mosaic'
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
            'primaryGroups': ['6e73286b-85cf-4343-9676-b7ee2ed0a3df'],
            'metrics': ['8f020607-379e-4b54-bc9e-e5550e84f5d5'],
            'allowMultipleMetrics': False,
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'legendPosition': 'right',
            'nestedLegend': False,
        }
    )

    esql_chart = ESQLMosaicPanelConfig.model_validate(esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_mosaic_chart(esql_mosaic_chart=esql_chart)
    assert kbn_state_visualization is not None
    assert kbn_state_visualization.shape == 'mosaic'
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
            'primaryGroups': ['6e73286b-85cf-4343-9676-b7ee2ed0a3df'],
            'metrics': ['8f020607-379e-4b54-bc9e-e5550e84f5d5'],
            'allowMultipleMetrics': False,
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'legendPosition': 'right',
            'nestedLegend': False,
        }
    )


async def test_mosaic_chart_with_breakdown() -> None:
    """Test mosaic chart with breakdown dimension."""
    lens_config = {
        'type': 'mosaic',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'dimension': {'type': 'values', 'field': 'http.request.method', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'breakdown': {'type': 'values', 'field': 'service.name', 'id': '7f84397c-95f0-5454-bd88-c8ff3fe1b4eg'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensMosaicChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_mosaic_chart(lens_mosaic_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
            'primaryGroups': ['6e73286b-85cf-4343-9676-b7ee2ed0a3df'],
            'secondaryGroups': ['7f84397c-95f0-5454-bd88-c8ff3fe1b4eg'],
            'metrics': ['8f020607-379e-4b54-bc9e-e5550e84f5d5'],
            'allowMultipleMetrics': False,
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'legendPosition': 'right',
            'nestedLegend': False,
        }
    )


async def test_mosaic_chart_with_legend_options() -> None:
    """Test mosaic chart with legend configuration."""
    lens_config = {
        'type': 'mosaic',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'dimension': {'type': 'values', 'field': 'service.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'legend': {'visible': 'show', 'width': 'medium', 'nested': True},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensMosaicChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_mosaic_chart(lens_mosaic_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
            'primaryGroups': ['6e73286b-85cf-4343-9676-b7ee2ed0a3df'],
            'metrics': ['8f020607-379e-4b54-bc9e-e5550e84f5d5'],
            'allowMultipleMetrics': False,
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'show',
            'legendPosition': 'right',
            'nestedLegend': True,
            'legendSize': 'medium',
        }
    )


async def test_mosaic_chart_with_value_display() -> None:
    """Test mosaic chart with value display options."""
    lens_config = {
        'type': 'mosaic',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'dimension': {'type': 'values', 'field': 'service.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'titles_and_text': {'value_format': 'value'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensMosaicChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_mosaic_chart(lens_mosaic_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
            'primaryGroups': ['6e73286b-85cf-4343-9676-b7ee2ed0a3df'],
            'metrics': ['8f020607-379e-4b54-bc9e-e5550e84f5d5'],
            'allowMultipleMetrics': False,
            'numberDisplay': 'value',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'legendPosition': 'right',
            'nestedLegend': False,
        }
    )


async def test_mosaic_chart_with_hidden_values() -> None:
    """Test mosaic chart with hidden values."""
    lens_config = {
        'type': 'mosaic',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'dimension': {'type': 'values', 'field': 'service.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'titles_and_text': {'value_format': 'hidden'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensMosaicChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_mosaic_chart(lens_mosaic_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.numberDisplay == 'hidden'


async def test_mosaic_chart_with_collapse_functions() -> None:
    """Test mosaic chart with collapse functions."""
    lens_config = {
        'type': 'mosaic',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'dimension': {'type': 'values', 'field': 'service.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df', 'collapse': 'sum'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensMosaicChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_mosaic_chart(lens_mosaic_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.model_dump() == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
            'primaryGroups': ['6e73286b-85cf-4343-9676-b7ee2ed0a3df'],
            'metrics': ['8f020607-379e-4b54-bc9e-e5550e84f5d5'],
            'allowMultipleMetrics': False,
            'collapseFns': {'6e73286b-85cf-4343-9676-b7ee2ed0a3df': 'sum'},
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'legendPosition': 'right',
            'nestedLegend': False,
        }
    )


async def test_mosaic_chart_with_custom_colors() -> None:
    """Test mosaic chart with custom color assignments."""
    lens_config = {
        'type': 'mosaic',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'dimension': {'type': 'values', 'field': 'service.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'color': {
            'palette': 'eui_amsterdam_color_blind',
            'assignments': [
                {'values': ['api-gateway'], 'color': '#00BF6F'},
                {'values': ['database'], 'color': '#006BB4'},
            ],
        },
    }

    lens_chart = LensMosaicChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_mosaic_chart(lens_mosaic_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.colorMapping is not None
    assert layer.colorMapping.paletteId == 'eui_amsterdam_color_blind'
    assert len(layer.colorMapping.assignments) == 2


async def test_mosaic_chart_with_legend_position() -> None:
    """Test mosaic chart with legend position configuration."""
    lens_config = {
        'type': 'mosaic',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'dimension': {'type': 'values', 'field': 'service.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'legend': {'visible': 'show', 'position': 'bottom'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensMosaicChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_mosaic_chart(lens_mosaic_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.legendPosition == 'bottom'
    assert layer.legendDisplay == 'show'


async def test_esql_mosaic_chart_with_breakdown() -> None:
    """Test ES|QL mosaic chart with breakdown dimension."""
    esql_config = {
        'type': 'mosaic',
        'query': 'FROM logs-* | STATS count = COUNT(*) BY http.request.method, service.name',
        'metric': {'field': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'dimension': {'field': 'http.request.method', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'breakdown': {'field': 'service.name', 'id': '7f84397c-95f0-5454-bd88-c8ff3fe1b4eg'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    esql_chart = ESQLMosaicPanelConfig.model_validate(esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_mosaic_chart(esql_mosaic_chart=esql_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.primaryGroups == ['6e73286b-85cf-4343-9676-b7ee2ed0a3df']
    assert layer.secondaryGroups == ['7f84397c-95f0-5454-bd88-c8ff3fe1b4eg']
    assert layer.metrics == ['8f020607-379e-4b54-bc9e-e5550e84f5d5']
