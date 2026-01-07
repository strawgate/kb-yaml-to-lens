"""Test the compilation of Lens metrics from config models to view models."""

from dirty_equals import IsUUID
from inline_snapshot import snapshot

from dashboard_compiler.panels.charts.config import ESQLPiePanelConfig
from dashboard_compiler.panels.charts.pie.compile import compile_esql_pie_chart, compile_lens_pie_chart
from dashboard_compiler.panels.charts.pie.config import LensPieChart


async def test_basic_pie_chart() -> None:
    """Test basic pie chart."""
    lens_config = {
        'type': 'pie',
        'data_view': 'metrics-*',
        'metrics': [{'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'slice_by': [{'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'pie',
        'query': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'metrics': [{'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'slice_by': [{'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensPieChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_pie_chart(lens_pie_chart=lens_chart)
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
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'nestedLegend': False,
        }
    )

    esql_chart = ESQLPiePanelConfig.model_validate(esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_pie_chart(esql_pie_chart=esql_chart)
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
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'nestedLegend': False,
        }
    )


async def test_basic_donut_chart() -> None:
    """Test basic donut chart."""
    lens_config = {
        'type': 'pie',
        'data_view': 'metrics-*',
        'metrics': [{'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'slice_by': [{'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'appearance': {'donut': 'medium'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'pie',
        'query': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'metrics': [{'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'slice_by': [{'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'appearance': {'donut': 'medium'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensPieChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_pie_chart(lens_pie_chart=lens_chart)
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
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'nestedLegend': False,
        }
    )

    esql_chart = ESQLPiePanelConfig.model_validate(esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_pie_chart(esql_pie_chart=esql_chart)
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
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'nestedLegend': False,
        }
    )


async def test_pie_chart_with_inside_labels_and_integer_values() -> None:
    """Test pie chart with inside labels and integer values."""
    lens_config = {
        'type': 'pie',
        'data_view': 'metrics-*',
        'metrics': [{'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'slice_by': [{'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'titles_and_text': {'slice_labels': 'inside', 'slice_values': 'integer'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'pie',
        'query': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'metrics': [{'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'slice_by': [{'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'titles_and_text': {'slice_labels': 'inside', 'slice_values': 'integer'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensPieChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_pie_chart(lens_pie_chart=lens_chart)
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
            'numberDisplay': 'value',
            'categoryDisplay': 'inside',
            'legendDisplay': 'default',
            'nestedLegend': False,
        }
    )

    esql_chart = ESQLPiePanelConfig.model_validate(esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_pie_chart(esql_pie_chart=esql_chart)
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
            'numberDisplay': 'value',
            'categoryDisplay': 'inside',
            'legendDisplay': 'default',
            'nestedLegend': False,
        }
    )


async def test_pie_chart_with_large_legend_and_no_label_truncation() -> None:
    """Test pie chart with large legend and no label truncation."""
    lens_config = {
        'type': 'pie',
        'data_view': 'metrics-*',
        'metrics': [{'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'slice_by': [{'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'legend': {'visible': 'show', 'width': 'large', 'truncate_labels': 0},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'pie',
        'query': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'metrics': [{'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'slice_by': [{'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'legend': {'visible': 'show', 'width': 'large', 'truncate_labels': 0},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensPieChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_pie_chart(lens_pie_chart=lens_chart)
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
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'show',
            'nestedLegend': False,
            'legendSize': 'large',
            'truncateLegend': False,
        }
    )

    esql_chart = ESQLPiePanelConfig.model_validate(esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_pie_chart(esql_pie_chart=esql_chart)
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
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'show',
            'nestedLegend': False,
            'legendSize': 'large',
            'truncateLegend': False,
        }
    )


async def test_pie_chart_with_secondary_groups() -> None:
    """Test pie chart with secondary groups."""
    lens_config = {
        'type': 'pie',
        'data_view': 'metrics-*',
        'metrics': [{'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'slice_by': [
            {'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
            {'type': 'values', 'field': 'region', 'id': '7f84397c-95f0-5454-bd88-c8ff3fe1b4eg'},
        ],
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'pie',
        'query': 'FROM metrics-* | STATS count(*) by aerospike.namespace, region',
        'metrics': [{'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'slice_by': [
            {'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
            {'field': 'region', 'id': '7f84397c-95f0-5454-bd88-c8ff3fe1b4eg'},
        ],
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensPieChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_pie_chart(lens_pie_chart=lens_chart)
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
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'nestedLegend': False,
        }
    )

    esql_chart = ESQLPiePanelConfig.model_validate(esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_pie_chart(esql_pie_chart=esql_chart)
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
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'nestedLegend': False,
        }
    )


async def test_pie_chart_with_multiple_metrics() -> None:
    """Test pie chart with multiple metrics."""
    lens_config = {
        'type': 'pie',
        'data_view': 'metrics-*',
        'metrics': [
            {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
            {'aggregation': 'sum', 'field': 'bytes', 'id': '9g131718-490f-5c65-cd0f-f6661g95g6f7'},
        ],
        'slice_by': [{'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'pie',
        'query': 'FROM metrics-* | STATS count(*), sum(bytes) by aerospike.namespace',
        'metrics': [
            {'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
            {'field': 'sum(bytes)', 'id': '9g131718-490f-5c65-cd0f-f6661g95g6f7'},
        ],
        'slice_by': [{'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensPieChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_pie_chart(lens_pie_chart=lens_chart)
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
            'metrics': ['8f020607-379e-4b54-bc9e-e5550e84f5d5', '9g131718-490f-5c65-cd0f-f6661g95g6f7'],
            'allowMultipleMetrics': True,
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'nestedLegend': False,
            'emptySizeRatio': 0.0,
        }
    )

    esql_chart = ESQLPiePanelConfig.model_validate(esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_pie_chart(esql_pie_chart=esql_chart)
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
            'metrics': ['8f020607-379e-4b54-bc9e-e5550e84f5d5', '9g131718-490f-5c65-cd0f-f6661g95g6f7'],
            'allowMultipleMetrics': True,
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'nestedLegend': False,
            'emptySizeRatio': 0.0,
        }
    )


async def test_pie_chart_with_collapse_functions() -> None:
    """Test pie chart with collapse functions."""
    lens_config = {
        'type': 'pie',
        'data_view': 'metrics-*',
        'metrics': [{'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'slice_by': [
            {'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df', 'collapse': 'sum'},
        ],
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'pie',
        'query': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'metrics': [{'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'slice_by': [
            {'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df', 'collapse': 'sum'},
        ],
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensPieChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_pie_chart(lens_pie_chart=lens_chart)
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
            'collapseFns': {'6e73286b-85cf-4343-9676-b7ee2ed0a3df': 'sum'},
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'nestedLegend': False,
        }
    )

    esql_chart = ESQLPiePanelConfig.model_validate(esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_pie_chart(esql_pie_chart=esql_chart)
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
            'collapseFns': {'6e73286b-85cf-4343-9676-b7ee2ed0a3df': 'sum'},
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'nestedLegend': False,
        }
    )


async def test_pie_chart_with_nested_legend() -> None:
    """Test pie chart with nested legend enabled."""
    lens_config = {
        'type': 'pie',
        'data_view': 'metrics-*',
        'metrics': [{'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'slice_by': [
            {'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
            {'type': 'values', 'field': 'host.name', 'id': '7f456789-abcd-1234-5678-90abcdef1234'},
        ],
        'legend': {'nested': True},
    }

    lens_chart = LensPieChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_pie_chart(lens_pie_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    assert layer.nestedLegend is True
