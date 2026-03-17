"""Test the compilation of Lens treemap charts from config models to view models."""

from dirty_equals import IsUUID
from inline_snapshot import snapshot

from kb_dashboard_core.panels.charts.config import ESQLTreemapPanelConfig
from kb_dashboard_core.panels.charts.treemap.compile import compile_esql_treemap_chart, compile_lens_treemap_chart
from kb_dashboard_core.panels.charts.treemap.config import LensTreemapChart


async def test_basic_treemap_chart() -> None:
    """Test basic treemap chart."""
    lens_config = {
        'type': 'treemap',
        'data_view': 'metrics-*',
        'metrics': [{'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'breakdowns': [{'type': 'values', 'field': 'service.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'legend': {'width': 'extra_large'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'treemap',
        'query': 'FROM metrics-* | STATS count(*) by service.name',
        'metrics': [{'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'breakdowns': [{'field': 'service.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'legend': {'width': 'extra_large'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensTreemapChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_treemap_chart(lens_treemap_chart=lens_chart)
    assert kbn_state_visualization.shape == 'treemap'
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
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'legendPosition': 'right',
            'nestedLegend': False,
            'legendSize': 'xlarge',
        }
    )

    esql_chart = ESQLTreemapPanelConfig.model_validate(esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_treemap_chart(esql_treemap_chart=esql_chart)
    assert kbn_state_visualization.shape == 'treemap'
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
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'legendPosition': 'right',
            'nestedLegend': False,
            'legendSize': 'xlarge',
        }
    )


async def test_treemap_show_hide_label_mapping() -> None:
    """Test treemap slice_labels mapping to Kibana categoryDisplay values."""
    lens_show = LensTreemapChart.model_validate(
        {
            'type': 'treemap',
            'data_view': 'metrics-*',
            'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
            'breakdowns': [{'type': 'values', 'field': 'service.name', 'id': 'group1'}],
            'appearance': {'categories': {'position': 'show'}},
        }
    )
    _layer_id, _kbn_columns, show_state = compile_lens_treemap_chart(lens_treemap_chart=lens_show)
    assert show_state.layers[0].categoryDisplay == 'default'

    lens_hide = LensTreemapChart.model_validate(
        {
            'type': 'treemap',
            'data_view': 'metrics-*',
            'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
            'breakdowns': [{'type': 'values', 'field': 'service.name', 'id': 'group1'}],
            'appearance': {'categories': {'position': 'hide'}},
        }
    )
    _layer_id, _kbn_columns, hide_state = compile_lens_treemap_chart(lens_treemap_chart=lens_hide)
    assert hide_state.layers[0].categoryDisplay == 'hide'


async def test_treemap_with_two_breakdowns_uses_primary_groups_only() -> None:
    """Treemap should keep all grouping levels in primaryGroups for Kibana compatibility."""
    lens_chart = LensTreemapChart.model_validate(
        {
            'type': 'treemap',
            'data_view': 'metrics-*',
            'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
            'breakdowns': [
                {'type': 'values', 'field': 'service.name', 'id': 'group1'},
                {'type': 'values', 'field': 'service.environment', 'id': 'group2'},
            ],
        }
    )
    _layer_id, _kbn_columns, lens_state = compile_lens_treemap_chart(lens_treemap_chart=lens_chart)
    lens_layer = lens_state.layers[0]
    assert lens_layer.primaryGroups == ['group1', 'group2']
    assert lens_layer.secondaryGroups is None

    esql_chart = ESQLTreemapPanelConfig.model_validate(
        {
            'type': 'treemap',
            'query': 'FROM metrics-* | STATS c = count(*) by service.name, service.environment',
            'metrics': [{'field': 'c', 'id': 'metric1'}],
            'breakdowns': [
                {'field': 'service.name', 'id': 'group1'},
                {'field': 'service.environment', 'id': 'group2'},
            ],
        }
    )
    _layer_id, _kbn_columns, esql_state = compile_esql_treemap_chart(esql_treemap_chart=esql_chart)
    esql_layer = esql_state.layers[0]
    assert esql_layer.primaryGroups == ['group1', 'group2']
    assert esql_layer.secondaryGroups is None
