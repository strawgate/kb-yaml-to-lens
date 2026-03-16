"""Test the compilation of Lens waffle charts from config models to view models."""

import pytest
from dirty_equals import IsUUID
from inline_snapshot import snapshot
from pydantic import ValidationError

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


def test_waffle_invalid_legacy_titles_and_text_type_is_rejected() -> None:
    """Malformed titles_and_text should fail validation instead of being silently dropped."""
    with pytest.raises(ValidationError, match='titles_and_text'):
        LensWaffleChart.model_validate(
            {
                'type': 'waffle',
                'data_view': 'logs-*',
                'metric': {'aggregation': 'count'},
                'breakdown': {'type': 'values', 'field': 'service.name'},
                'titles_and_text': 'invalid',
            }
        )


def test_waffle_legacy_titles_and_text_maps_to_appearance_values() -> None:
    """Legacy titles_and_text value fields should map into appearance.values."""
    chart = LensWaffleChart.model_validate(
        {
            'type': 'waffle',
            'data_view': 'logs-*',
            'metric': {'aggregation': 'count'},
            'breakdown': {'type': 'values', 'field': 'service.name'},
            'titles_and_text': {'value_format': 'value', 'value_decimal_places': 4},
        }
    )
    assert chart.appearance is not None
    assert chart.appearance.values is not None
    assert chart.appearance.values.format == 'value'
    assert chart.appearance.values.decimal_places == 4


def test_waffle_appearance_values_override_legacy_titles_and_text() -> None:
    """Explicit appearance.values should win over legacy titles_and_text values."""
    chart = LensWaffleChart.model_validate(
        {
            'type': 'waffle',
            'data_view': 'logs-*',
            'metric': {'aggregation': 'count'},
            'breakdown': {'type': 'values', 'field': 'service.name'},
            'titles_and_text': {'value_format': 'hide', 'value_decimal_places': 1},
            'appearance': {'values': {'format': 'percent', 'decimal_places': 5}},
        }
    )
    assert chart.appearance is not None
    assert chart.appearance.values is not None
    assert chart.appearance.values.format == 'percent'
    assert chart.appearance.values.decimal_places == 5


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


def test_waffle_deprecated_dimension_does_not_override_explicit_breakdown() -> None:
    """Explicit breakdown should win over deprecated dimension for both chart modes."""
    lens_chart = LensWaffleChart.model_validate(
        {
            'type': 'waffle',
            'data_view': 'logs-*',
            'metric': {'aggregation': 'count'},
            'breakdown': {'type': 'values', 'field': 'service.name', 'id': 'new-breakdown'},
            'dimension': {'type': 'values', 'field': 'host.name', 'id': 'legacy-dimension'},
        }
    )
    assert lens_chart.breakdown.id == 'new-breakdown'

    esql_chart = ESQLWafflePanelConfig.model_validate(
        {
            'type': 'waffle',
            'query': 'FROM logs-* | STATS c = COUNT(*) BY service.name',
            'metric': {'field': 'c'},
            'breakdown': {'field': 'service.name', 'id': 'new-breakdown'},
            'dimension': {'field': 'host.name', 'id': 'legacy-dimension'},
        }
    )
    assert esql_chart.breakdown.id == 'new-breakdown'


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


def test_waffle_deprecated_titles_and_text_warns_and_maps() -> None:
    """Deprecated titles_and_text should warn and map to appearance.values."""
    with pytest.warns(DeprecationWarning, match='titles_and_text'):
        chart = LensWaffleChart.model_validate(
            {
                'type': 'waffle',
                'data_view': 'logs-*',
                'metric': {'aggregation': 'count'},
                'breakdown': {'type': 'values', 'field': 'service.name'},
                'titles_and_text': {'value_format': 'value', 'value_decimal_places': 4},
            }
        )

    assert chart.appearance is not None
    assert chart.appearance.values is not None
    assert chart.appearance.values.format == 'value'
    assert chart.appearance.values.decimal_places == 4


def test_waffle_deprecated_titles_and_text_warns_when_ignored() -> None:
    """Deprecated titles_and_text fields should warn when overridden by appearance.values."""
    with pytest.warns(DeprecationWarning, match="ignored because 'appearance.values.format' is already set"):
        chart = LensWaffleChart.model_validate(
            {
                'type': 'waffle',
                'data_view': 'logs-*',
                'metric': {'aggregation': 'count'},
                'breakdown': {'type': 'values', 'field': 'service.name'},
                'appearance': {'values': {'format': 'hide'}},
                'titles_and_text': {'value_format': 'value'},
            }
        )

    assert chart.appearance is not None
    assert chart.appearance.values is not None
    assert chart.appearance.values.format == 'hide'
