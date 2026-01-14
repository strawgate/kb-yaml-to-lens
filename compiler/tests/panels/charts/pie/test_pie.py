"""Test the compilation of Lens metrics from config models to view models.

Fixture Examples:
    https://github.com/strawgate/kb-yaml-to-lens-fixtures
    - ES|QL: output/<version>/pie-chart-esql.json
    - Data View: output/<version>/pie-chart-dataview.json
"""

from typing import TYPE_CHECKING

from dirty_equals import IsStr, IsUUID
from inline_snapshot import snapshot

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.panels.charts.config import ESQLPiePanelConfig
from dashboard_compiler.panels.charts.pie.compile import compile_esql_pie_chart, compile_lens_pie_chart
from dashboard_compiler.panels.charts.pie.config import LensPieChart

if TYPE_CHECKING:
    from dashboard_compiler.dashboard.view import KbnDashboard


async def test_basic_pie_chart() -> None:
    """Test basic pie chart."""
    lens_config = {
        'type': 'pie',
        'data_view': 'metrics-*',
        'metrics': [{'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'dimensions': [{'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'pie',
        'query': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'metrics': [{'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'dimensions': [{'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
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
        'dimensions': [{'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'appearance': {'donut': 'medium'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'pie',
        'query': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'metrics': [{'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'dimensions': [{'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
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
        'dimensions': [{'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'titles_and_text': {'slice_labels': 'inside', 'slice_values': 'integer'},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'pie',
        'query': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'metrics': [{'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'dimensions': [{'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
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
        'dimensions': [{'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'legend': {'visible': 'show', 'width': 'large', 'truncate_labels': 0},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'pie',
        'query': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'metrics': [{'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'dimensions': [{'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
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
        'dimensions': [
            {'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
            {'type': 'values', 'field': 'region', 'id': '7f84397c-95f0-5454-bd88-c8ff3fe1b4eg'},
        ],
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'pie',
        'query': 'FROM metrics-* | STATS count(*) by aerospike.namespace, region',
        'metrics': [{'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'dimensions': [
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
        'dimensions': [{'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'pie',
        'query': 'FROM metrics-* | STATS count(*), sum(bytes) by aerospike.namespace',
        'metrics': [
            {'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'},
            {'field': 'sum(bytes)', 'id': '9g131718-490f-5c65-cd0f-f6661g95g6f7'},
        ],
        'dimensions': [{'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
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
        'dimensions': [
            {'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df', 'collapse': 'sum'},
        ],
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'pie',
        'query': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'metrics': [{'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'dimensions': [
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
        'dimensions': [
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


async def test_pie_chart_with_show_single_series() -> None:
    """Test pie chart with show_single_series enabled."""
    lens_config = {
        'type': 'pie',
        'data_view': 'metrics-*',
        'metrics': [{'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'dimensions': [
            {'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        ],
        'color': {'palette': 'eui_amsterdam_color_blind'},
        'legend': {'show_single_series': True},
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
            'showSingleSeries': True,
        }
    )


async def test_pie_chart_with_show_single_series_false() -> None:
    """Test pie chart with show_single_series disabled."""
    lens_config = {
        'type': 'pie',
        'data_view': 'metrics-*',
        'metrics': [{'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'dimensions': [
            {'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
        ],
        'color': {'palette': 'eui_amsterdam_color_blind'},
        'legend': {'show_single_series': False},
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
            'showSingleSeries': False,
        }
    )


async def test_pie_chart_with_show_single_series_omitted() -> None:
    """Test pie chart with show_single_series omitted."""
    lens_config = {
        'type': 'pie',
        'data_view': 'metrics-*',
        'metrics': [{'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'dimensions': [
            {'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'},
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
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'nestedLegend': False,
        }
    )


async def test_pie_chart_with_value_decimal_places() -> None:
    """Test pie chart with value_decimal_places specified at layer level."""
    lens_config = {
        'type': 'pie',
        'data_view': 'metrics-*',
        'metrics': [{'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'dimensions': [{'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'titles_and_text': {'value_decimal_places': 5},
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'pie',
        'query': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'metrics': [{'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'dimensions': [{'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'titles_and_text': {'value_decimal_places': 5},
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
            'percentDecimals': 5,
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
            'percentDecimals': 5,
        }
    )


async def test_pie_chart_without_value_decimal_places() -> None:
    """Test that pie chart omits percentDecimals when not specified."""
    lens_config = {
        'type': 'pie',
        'data_view': 'metrics-*',
        'metrics': [{'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'dimensions': [{'type': 'values', 'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }
    esql_config = {
        'type': 'pie',
        'query': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'metrics': [{'field': 'count(*)', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}],
        'dimensions': [{'field': 'aerospike.namespace.name', 'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df'}],
        'color': {'palette': 'eui_amsterdam_color_blind'},
    }

    lens_chart = LensPieChart.model_validate(lens_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_lens_pie_chart(lens_pie_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    dumped = layer.model_dump()
    assert 'percentDecimals' not in dumped

    esql_chart = ESQLPiePanelConfig.model_validate(esql_config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_pie_chart(esql_pie_chart=esql_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    dumped = layer.model_dump()
    assert 'percentDecimals' not in dumped


def test_pie_chart_dashboard_references_bubble_up() -> None:
    """Test that pie chart data view references bubble up to dashboard level correctly.

    Pie charts reference a data view (index-pattern), so this reference should appear
    at the dashboard's top-level references array with proper panel namespacing.
    """
    dashboard = Dashboard(
        name='Test Pie Chart Dashboard',
        panels=[
            {
                'title': 'Pie Chart',
                'id': 'pie-panel-1',
                'grid': {'x': 0, 'y': 0, 'w': 24, 'h': 15},
                'lens': {
                    'type': 'pie',
                    'data_view': 'metrics-*',
                    'metrics': [{'aggregation': 'count', 'id': 'count-metric'}],
                    'dimensions': [{'type': 'values', 'field': 'host.name', 'id': 'host-dimension'}],
                },
            }
        ],
    )

    kbn_dashboard: KbnDashboard = render(dashboard=dashboard)
    references = [ref.model_dump() for ref in kbn_dashboard.references]

    assert references == snapshot(
        [
            {
                'id': 'metrics-*',
                'name': IsStr(regex=r'pie-panel-1:indexpattern-datasource-layer-[a-f0-9-]+'),
                'type': 'index-pattern',
            }
        ]
    )
