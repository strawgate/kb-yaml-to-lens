"""Test the compilation of Lens waffle charts from config models to view models."""

from dirty_equals import IsUUID
from inline_snapshot import snapshot

from kb_dashboard_core.panels.charts.config import ESQLWafflePanelConfig
from kb_dashboard_core.panels.charts.waffle.compile import compile_esql_waffle_chart, compile_lens_waffle_chart
from kb_dashboard_core.panels.charts.waffle.config import LensWaffleChart


async def test_basic_waffle_chart() -> None:
    """Test basic waffle chart."""
    lens_config = {
        'type': 'waffle',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'breakdown': {'type': 'values', 'field': 'http.request.method', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'waffle',
        'query': 'FROM logs-* | STATS count = COUNT(*) BY http.request.method',
        'metric': {'field': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'breakdown': {'field': 'http.request.method', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensWaffleChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_waffle_chart(lens_waffle_chart=lens_chart)
    assert kbn_state_visualization is not None
    assert kbn_state_visualization.shape == 'waffle'
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

    esql_chart = ESQLWafflePanelConfig.model_validate(esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_waffle_chart(esql_waffle_chart=esql_chart)
    assert kbn_state_visualization is not None
    assert kbn_state_visualization.shape == 'waffle'
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


async def test_waffle_chart_breakdown_goes_to_primary_groups() -> None:
    """Test waffle chart breakdown is compiled into primaryGroups."""
    lens_config = {
        'type': 'waffle',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'breakdown': {'type': 'values', 'field': 'http.request.method', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensWaffleChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_waffle_chart(lens_waffle_chart=lens_chart)
    layer = kbn_state_visualization.layers[0]
    assert layer.primaryGroups == ['6e73286b-85cf-4343-9676-b7ee2ed0a3df']
    assert layer.secondaryGroups is None


async def test_waffle_chart_with_legend_options() -> None:
    """Test waffle chart with legend configuration."""
    lens_config = {
        'type': 'waffle',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'breakdown': {'type': 'values', 'field': 'service.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'legend': {'visible': 'show', 'width': 'extra_large', 'nested': True},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensWaffleChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_waffle_chart(lens_waffle_chart=lens_chart)
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
            'legendSize': 'xlarge',
        }
    )


async def test_waffle_chart_with_value_display() -> None:
    """Test waffle chart with value display options."""
    lens_config = {
        'type': 'waffle',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'breakdown': {'type': 'values', 'field': 'service.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'appearance': {'values': {'format': 'value'}},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensWaffleChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_waffle_chart(lens_waffle_chart=lens_chart)
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


async def test_waffle_chart_with_hidden_values() -> None:
    """Test waffle chart with hidden values."""
    lens_config = {
        'type': 'waffle',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'breakdown': {'type': 'values', 'field': 'service.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'appearance': {'values': {'format': 'hide'}},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensWaffleChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_waffle_chart(lens_waffle_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.numberDisplay == 'hidden'


async def test_waffle_chart_with_collapse_functions() -> None:
    """Test waffle chart with collapse functions."""
    lens_config = {
        'type': 'waffle',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'breakdown': {'type': 'values', 'field': 'service.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df', 'collapse': 'sum'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensWaffleChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_waffle_chart(lens_waffle_chart=lens_chart)
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


async def test_waffle_chart_with_custom_colors() -> None:
    """Test waffle chart with custom color assignments."""
    lens_config = {
        'type': 'waffle',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'breakdown': {'type': 'values', 'field': 'service.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'color': {
            'palette': 'eui_amsterdam_color_blind',
            'assignments': [
                {'values': ['api-gateway'], 'color': '#00BF6F'},
                {'values': ['database'], 'color': '#006BB4'},
            ],
        },
    }

    lens_chart = LensWaffleChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_waffle_chart(lens_waffle_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.colorMapping is not None
    assert layer.colorMapping.paletteId == 'eui_amsterdam_color_blind'
    assert len(layer.colorMapping.assignments) == 2


async def test_waffle_chart_with_legend_position() -> None:
    """Test waffle chart with legend position configuration."""
    lens_config = {
        'type': 'waffle',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'breakdown': {'type': 'values', 'field': 'service.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'legend': {'visible': 'show', 'position': 'bottom'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensWaffleChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_waffle_chart(lens_waffle_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.legendPosition == 'bottom'
    assert layer.legendDisplay == 'show'


async def test_waffle_chart_legend_auto_maps_to_default() -> None:
    """Partition chart legend auto should compile to Kibana default."""
    lens_config = {
        'type': 'waffle',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': 'metric-id'},
        'breakdown': {'type': 'values', 'field': 'service.name', 'id': 'breakdown-id'},
        'legend': {'visible': 'auto'},
    }
    esql_config = {
        'type': 'waffle',
        'query': 'FROM logs-* | STATS c = COUNT(*) BY service.name',
        'metric': {'field': 'c', 'id': 'metric-id'},
        'breakdown': {'field': 'service.name', 'id': 'breakdown-id'},
        'legend': {'visible': 'auto'},
    }

    lens_chart = LensWaffleChart.model_validate(lens_config)
    _layer_id, _kbn_columns, lens_visualization = compile_lens_waffle_chart(lens_waffle_chart=lens_chart)
    assert lens_visualization.layers[0].legendDisplay == 'default'

    esql_chart = ESQLWafflePanelConfig.model_validate(esql_config)
    _layer_id, _kbn_columns, esql_visualization = compile_esql_waffle_chart(esql_waffle_chart=esql_chart)
    assert esql_visualization.layers[0].legendDisplay == 'default'


async def test_esql_waffle_chart_breakdown_goes_to_primary_groups() -> None:
    """Test ES|QL waffle chart breakdown is compiled into primaryGroups."""
    esql_config = {
        'type': 'waffle',
        'query': 'FROM logs-* | STATS count = COUNT(*) BY http.request.method',
        'metric': {'field': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'breakdown': {'field': 'http.request.method', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    esql_chart = ESQLWafflePanelConfig.model_validate(esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_waffle_chart(esql_waffle_chart=esql_chart)
    layer = kbn_state_visualization.layers[0]
    assert layer.primaryGroups == ['6e73286b-85cf-4343-9676-b7ee2ed0a3df']
    assert layer.secondaryGroups is None


async def test_waffle_chart_without_breakdown_compiles_for_lens_and_esql() -> None:
    """Waffle charts should support metric-only mode with no breakdown."""
    lens_config = {
        'type': 'waffle',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': 'metric-id'},
    }
    esql_config = {
        'type': 'waffle',
        'query': 'FROM logs-* | STATS c = COUNT(*)',
        'metric': {'field': 'c', 'id': 'metric-id'},
    }

    lens_chart = LensWaffleChart.model_validate(lens_config)
    _layer_id, _kbn_columns, lens_visualization = compile_lens_waffle_chart(lens_waffle_chart=lens_chart)
    lens_layer = lens_visualization.layers[0]
    assert lens_layer.primaryGroups == []
    assert lens_layer.collapseFns is None
    assert lens_layer.metrics == ['metric-id']

    esql_chart = ESQLWafflePanelConfig.model_validate(esql_config)
    _layer_id, _kbn_columns, esql_visualization = compile_esql_waffle_chart(esql_waffle_chart=esql_chart)
    esql_layer = esql_visualization.layers[0]
    assert esql_layer.primaryGroups == []
    assert esql_layer.collapseFns is None
    assert esql_layer.metrics == ['metric-id']


async def test_waffle_chart_with_value_decimal_places() -> None:
    """Test waffle chart with value_decimal_places specified at layer level."""
    lens_config = {
        'type': 'waffle',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'breakdown': {'type': 'values', 'field': 'http.request.method', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'appearance': {'values': {'decimal_places': 5}},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'waffle',
        'query': 'FROM logs-* | STATS count = COUNT(*) BY http.request.method',
        'metric': {'field': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'breakdown': {'field': 'http.request.method', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'appearance': {'values': {'decimal_places': 5}},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensWaffleChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_waffle_chart(lens_waffle_chart=lens_chart)
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
            'legendDisplay': 'default',
            'legendPosition': 'right',
            'nestedLegend': False,
            'percentDecimals': 5,
        }
    )

    esql_chart = ESQLWafflePanelConfig.model_validate(esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_waffle_chart(esql_waffle_chart=esql_chart)
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
            'legendDisplay': 'default',
            'legendPosition': 'right',
            'nestedLegend': False,
            'percentDecimals': 5,
        }
    )


async def test_waffle_chart_without_value_decimal_places() -> None:
    """Test that waffle chart omits percentDecimals when not specified."""
    lens_config = {
        'type': 'waffle',
        'data_view': 'logs-*',
        'metric': {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
        'breakdown': {'type': 'values', 'field': 'http.request.method', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensWaffleChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_waffle_chart(lens_waffle_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    dumped = layer.model_dump()
    assert 'percentDecimals' not in dumped
