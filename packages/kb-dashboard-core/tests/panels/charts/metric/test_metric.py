"""Test the compilation of Lens metrics from config models to view models using inline snapshots.

Fixture Examples:
    https://github.com/strawgate/kb-yaml-to-lens-fixtures
    - ES|QL: output/<version>/metric-basic-esql.json
    - Data View: output/<version>/metric-basic-dataview.json
"""

from typing import TYPE_CHECKING, Any

import pytest
from dirty_equals import IsStr, IsUUID
from inline_snapshot import snapshot

from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.dashboard_compiler import render
from kb_dashboard_core.panels.charts.metric.compile import (
    compile_esql_metric_chart,
    compile_lens_metric_chart,
)
from kb_dashboard_core.panels.charts.metric.config import ESQLMetricChart, LensMetricChart

if TYPE_CHECKING:
    from kb_dashboard_core.dashboard.view import KbnDashboard


def compile_metric_chart_snapshot(config: dict[str, Any], chart_type: str = 'lens') -> dict[str, Any]:
    """Compile metric chart config and return dict for snapshot testing."""
    if chart_type == 'lens':
        lens_chart = LensMetricChart.model_validate(config)
        _layer_id, _kbn_columns_by_id, kbn_state_visualization = compile_lens_metric_chart(lens_metric_chart=lens_chart)
        assert kbn_state_visualization is not None
        return kbn_state_visualization.model_dump()

    # esql
    esql_chart = ESQLMetricChart.model_validate(config)
    _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_metric_chart(esql_metric_chart=esql_chart)
    assert kbn_state_visualization is not None
    return kbn_state_visualization.model_dump()


def test_compile_metric_chart_primary_only_lens() -> None:
    """Test the compilation of a metric chart with only a primary metric (Lens)."""
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'field': 'aerospike.namespace.name',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'aggregation': 'count',
        },
    }

    result = compile_metric_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'secondaryTrend': {'type': 'none'},
            'secondaryLabelPosition': 'before',
        }
    )


def test_compile_metric_chart_primary_only_esql() -> None:
    """Test the compilation of a metric chart with only a primary metric (ESQL)."""
    config = {
        'type': 'metric',
        'primary': {
            'field': 'count(aerospike.namespace)',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
        },
    }

    result = compile_metric_chart_snapshot(config, 'esql')

    # Verify the result matches the expected snapshot
    # Note: ES|QL metrics use flat structure without colorMapping
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'showBar': False,
        }
    )


def test_compile_metric_chart_primary_and_secondary_lens() -> None:
    """Test the compilation of a metric chart with primary and secondary metrics (Lens)."""
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'field': 'aerospike.namespace.name',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'aggregation': 'count',
        },
        'secondary': {
            'field': 'aerospike.node.name',
            'id': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
            'aggregation': 'unique_count',
        },
    }

    result = compile_metric_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'secondaryTrend': {'type': 'none'},
            'secondaryLabelPosition': 'before',
            'secondaryMetricAccessor': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
        }
    )


def test_compile_metric_chart_primary_and_secondary_esql() -> None:
    """Test the compilation of a metric chart with primary and secondary metrics (ESQL)."""
    config = {
        'type': 'metric',
        'primary': {
            'field': 'count(aerospike.namespace)',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
        },
        'secondary': {
            'field': 'count_distinct(aerospike.node.name)',
            'id': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
        },
    }

    result = compile_metric_chart_snapshot(config, 'esql')

    # Verify the result matches the expected snapshot
    # Note: ES|QL metrics use flat structure without colorMapping
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'showBar': False,
            'secondaryMetricAccessor': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
        }
    )


def test_compile_metric_chart_primary_secondary_breakdown_lens() -> None:
    """Test the compilation of a metric chart with primary, secondary metrics and breakdown (Lens)."""
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'field': 'aerospike.namespace.name',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'aggregation': 'count',
        },
        'secondary': {
            'field': 'aerospike.node.name',
            'id': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
            'aggregation': 'unique_count',
        },
        'breakdown': {
            'type': 'values',
            'field': 'agent.name',
            'id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
        },
    }

    result = compile_metric_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'secondaryTrend': {'type': 'none'},
            'secondaryLabelPosition': 'before',
            'secondaryMetricAccessor': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
            'breakdownByAccessor': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
        }
    )


def test_compile_metric_chart_primary_secondary_breakdown_esql() -> None:
    """Test the compilation of a metric chart with primary, secondary metrics and breakdown (ESQL)."""
    config = {
        'type': 'metric',
        'primary': {
            'field': 'count(aerospike.namespace)',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
        },
        'secondary': {
            'field': 'count_distinct(aerospike.node.name)',
            'id': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
        },
        'breakdown': {
            'field': 'agent.name',
            'id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
        },
    }

    result = compile_metric_chart_snapshot(config, 'esql')

    # Verify the result matches the expected snapshot
    # Note: ES|QL metrics use flat structure without colorMapping
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'showBar': False,
            'secondaryMetricAccessor': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
            'breakdownByAccessor': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
        }
    )


def test_compile_metric_chart_formula_simple() -> None:
    """Test the compilation of a metric chart with a simple formula (Lens)."""
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'formula': 'count() / 100',
            'label': 'Count Percentage',
            'id': 'formula-metric-1',
        },
    }

    result = compile_metric_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': 'formula-metric-1',
            'secondaryTrend': {'type': 'none'},
            'secondaryLabelPosition': 'before',
        }
    )


def test_compile_metric_chart_formula_with_fields() -> None:
    """Test the compilation of a metric chart with a formula using field aggregations (Lens)."""
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'formula': "(max(field='response.time') - min(field='response.time')) / average(field='response.time')",
            'label': 'Response Time Variability',
            'id': 'formula-metric-2',
        },
    }

    result = compile_metric_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': 'formula-metric-2',
            'secondaryTrend': {'type': 'none'},
            'secondaryLabelPosition': 'before',
        }
    )


def test_compile_metric_chart_column_order_without_breakdown() -> None:
    """Test that kbn_columns_by_id contains only metrics when no breakdown is present (Lens)."""
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'field': 'aerospike.namespace.name',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'aggregation': 'count',
        },
        'secondary': {
            'field': 'aerospike.node.name',
            'id': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
            'aggregation': 'unique_count',
        },
    }

    lens_chart = LensMetricChart.model_validate(config)
    _layer_id, kbn_columns_by_id, _kbn_state_visualization = compile_lens_metric_chart(lens_metric_chart=lens_chart)

    # Verify columnOrder contains only metric IDs
    column_ids = list(kbn_columns_by_id.keys())
    assert column_ids == ['156e3e91-7bb6-406f-8ae5-cb409747953b', 'a1ec5883-19b2-4ab9-b027-a13d6074128b']


def test_compile_metric_chart_column_order_with_breakdown() -> None:
    """Test that breakdown dimension appears before metrics in kbn_columns_by_id (Lens).

    Kibana requires breakdown dimensions to appear before metrics in the columnOrder
    array for proper Elasticsearch query generation.
    """
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'field': 'aerospike.namespace.name',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'aggregation': 'count',
        },
        'secondary': {
            'field': 'aerospike.node.name',
            'id': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
            'aggregation': 'unique_count',
        },
        'breakdown': {
            'type': 'values',
            'field': 'agent.name',
            'id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
        },
    }

    lens_chart = LensMetricChart.model_validate(config)
    _layer_id, kbn_columns_by_id, _kbn_state_visualization = compile_lens_metric_chart(lens_metric_chart=lens_chart)

    # Verify columnOrder has breakdown dimension BEFORE metrics
    column_ids = list(kbn_columns_by_id.keys())
    assert column_ids == [
        '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',  # breakdown dimension FIRST
        '156e3e91-7bb6-406f-8ae5-cb409747953b',  # primary metric
        'a1ec5883-19b2-4ab9-b027-a13d6074128b',  # secondary metric
    ]


def test_compile_metric_chart_column_order_with_breakdown_primary_only() -> None:
    """Test that breakdown dimension appears before primary metric in kbn_columns_by_id (Lens)."""
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'field': 'aerospike.namespace.name',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'aggregation': 'count',
        },
        'breakdown': {
            'type': 'values',
            'field': 'agent.name',
            'id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
        },
    }

    lens_chart = LensMetricChart.model_validate(config)
    _layer_id, kbn_columns_by_id, _kbn_state_visualization = compile_lens_metric_chart(lens_metric_chart=lens_chart)

    # Verify columnOrder has breakdown dimension BEFORE metric
    column_ids = list(kbn_columns_by_id.keys())
    assert column_ids == [
        '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',  # breakdown dimension FIRST
        '156e3e91-7bb6-406f-8ae5-cb409747953b',  # primary metric
    ]


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('color_mode', ['labels', 'background', 'none'])
def test_compile_metric_chart_color_mode(chart_type: str, color_mode: str) -> None:
    """Test metric color_mode compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {
                'aggregation': 'count',
                'id': 'primary-metric',
            },
            'color_mode': color_mode,
        }
    else:
        config = {
            'type': 'metric',
            'primary': {
                'field': 'count(*)',
                'id': 'primary-metric',
            },
            'color_mode': color_mode,
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['colorMode'] == color_mode


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_compile_metric_chart_color_mode_omitted(chart_type: str) -> None:
    """Test metric color_mode default omission for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {
                'aggregation': 'count',
                'id': 'primary-metric',
            },
        }
    else:
        config = {
            'type': 'metric',
            'primary': {
                'field': 'count(*)',
                'id': 'primary-metric',
            },
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert 'colorMode' not in result


def test_compile_metric_chart_maximum_lens() -> None:
    """Test the compilation of a metric chart with a maximum metric (Lens)."""
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'field': 'system.cpu.total.norm.pct',
            'id': 'primary-metric',
            'aggregation': 'average',
        },
        'maximum': {
            'value': 1,
            'id': 'max-metric',
        },
    }

    lens_chart = LensMetricChart.model_validate(config)
    _layer_id, kbn_columns_by_id, kbn_state = compile_lens_metric_chart(lens_metric_chart=lens_chart)

    result = kbn_state.model_dump()
    assert result['maxAccessor'] == 'max-metric'
    assert 'max-metric' in kbn_columns_by_id


def test_compile_metric_chart_maximum_esql() -> None:
    """Test the compilation of a metric chart with a maximum metric (ESQL)."""
    config = {
        'type': 'metric',
        'primary': {
            'field': 'avg_cpu',
            'id': 'primary-metric',
        },
        'maximum': {
            'field': 'max_cpu',
            'id': 'max-metric',
        },
    }

    esql_chart = ESQLMetricChart.model_validate(config)
    _layer_id, kbn_columns, kbn_state = compile_esql_metric_chart(esql_metric_chart=esql_chart)

    result = kbn_state.model_dump()
    assert result['maxAccessor'] == 'max-metric'
    column_ids = [col.columnId for col in kbn_columns]
    assert 'max-metric' in column_ids


def test_compile_metric_chart_maximum_column_order() -> None:
    """Test that maximum metric appears in kbn_columns_by_id alongside primary (Lens)."""
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'field': 'system.cpu.total.norm.pct',
            'id': 'primary-metric',
            'aggregation': 'average',
        },
        'maximum': {
            'value': 1,
            'id': 'max-metric',
        },
    }

    lens_chart = LensMetricChart.model_validate(config)
    _layer_id, kbn_columns_by_id, _state = compile_lens_metric_chart(lens_metric_chart=lens_chart)

    column_ids = list(kbn_columns_by_id.keys())
    assert 'primary-metric' in column_ids
    assert 'max-metric' in column_ids


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_compile_metric_chart_subtitle(chart_type: str) -> None:
    """Test metric subtitle compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'subtitle': 'Last 24 hours',
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'subtitle': 'Last 24 hours',
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['subtitle'] == 'Last 24 hours'


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_compile_metric_chart_subtitle_omitted(chart_type: str) -> None:
    """Test metric subtitle default omission for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert 'subtitle' not in result


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_compile_metric_chart_secondary_label(chart_type: str) -> None:
    """Test metric secondary_label compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'secondary': {'aggregation': 'count', 'id': 'secondary-metric'},
            'secondary_label': 'vs. previous period',
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'secondary': {'field': 'prev_count', 'id': 'secondary-metric'},
            'secondary_label': 'vs. previous period',
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['secondaryLabel'] == 'vs. previous period'


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_compile_metric_chart_icon(chart_type: str) -> None:
    """Test metric icon compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'icon': 'sortUp',
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'icon': 'sortUp',
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['icon'] == 'sortUp'


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_compile_metric_chart_icon_omitted(chart_type: str) -> None:
    """Test metric icon default omission for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert 'icon' not in result


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_compile_metric_chart_max_cols(chart_type: str) -> None:
    """Test metric max_cols compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'max_cols': 3,
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'max_cols': 3,
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['maxCols'] == 3


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_compile_metric_chart_show_bar(chart_type: str) -> None:
    """Test metric show_bar compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'show_bar': True,
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'show_bar': True,
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['showBar'] is True


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('direction', ['horizontal', 'vertical'])
def test_compile_metric_chart_progress_direction(chart_type: str, direction: str) -> None:
    """Test metric progress_direction compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'progress_direction': direction,
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'progress_direction': direction,
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['progressDirection'] == direction


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('align', ['left', 'center', 'right'])
def test_compile_metric_chart_titles_text_align(chart_type: str, align: str) -> None:
    """Test metric titles_text_align compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'titles_text_align': align,
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'titles_text_align': align,
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['titlesTextAlign'] == align


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('mode', ['default', 'fit', 'custom'])
def test_compile_metric_chart_value_font_mode(chart_type: str, mode: str) -> None:
    """Test metric value_font_mode compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'value_font_mode': mode,
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'value_font_mode': mode,
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['valueFontMode'] == mode


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('align', ['left', 'right'])
def test_compile_metric_chart_icon_align(chart_type: str, align: str) -> None:
    """Test metric icon_align compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'icon_align': align,
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'icon_align': align,
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['iconAlign'] == align


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('align', ['left', 'center', 'right'])
def test_compile_metric_chart_primary_align(chart_type: str, align: str) -> None:
    """Test metric primary_align compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'primary_align': align,
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'primary_align': align,
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['primaryAlign'] == align


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('align', ['left', 'center', 'right'])
def test_compile_metric_chart_secondary_align(chart_type: str, align: str) -> None:
    """Test metric secondary_align compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'secondary_align': align,
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'secondary_align': align,
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['secondaryAlign'] == align


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('weight', ['bold', 'normal', 'lighter'])
def test_compile_metric_chart_title_weight(chart_type: str, weight: str) -> None:
    """Test metric title_weight compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'title_weight': weight,
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'title_weight': weight,
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['titleWeight'] == weight


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('position', ['top', 'bottom'])
def test_compile_metric_chart_primary_position(chart_type: str, position: str) -> None:
    """Test metric primary_position compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'primary_position': position,
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'primary_position': position,
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['primaryPosition'] == position


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_compile_metric_chart_all_styling_options(chart_type: str) -> None:
    """Test metric chart with all styling options set simultaneously."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'secondary': {'aggregation': 'count', 'id': 'secondary-metric'},
            'maximum': {'value': 100, 'id': 'max-metric'},
            'subtitle': 'Overview',
            'secondary_label': 'Change',
            'icon': 'compute',
            'max_cols': 5,
            'show_bar': True,
            'progress_direction': 'vertical',
            'titles_text_align': 'center',
            'value_font_mode': 'fit',
            'icon_align': 'right',
            'primary_align': 'center',
            'secondary_align': 'right',
            'title_weight': 'bold',
            'primary_position': 'bottom',
            'color_mode': 'background',
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'secondary': {'field': 'prev_count', 'id': 'secondary-metric'},
            'maximum': {'field': 'max_val', 'id': 'max-metric'},
            'subtitle': 'Overview',
            'secondary_label': 'Change',
            'icon': 'compute',
            'max_cols': 5,
            'show_bar': True,
            'progress_direction': 'vertical',
            'titles_text_align': 'center',
            'value_font_mode': 'fit',
            'icon_align': 'right',
            'primary_align': 'center',
            'secondary_align': 'right',
            'title_weight': 'bold',
            'primary_position': 'bottom',
            'color_mode': 'background',
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['subtitle'] == 'Overview'
    assert result['secondaryLabel'] == 'Change'
    assert result['icon'] == 'compute'
    assert result['maxCols'] == 5
    assert result['showBar'] is True
    assert result['progressDirection'] == 'vertical'
    assert result['titlesTextAlign'] == 'center'
    assert result['valueFontMode'] == 'fit'
    assert result['iconAlign'] == 'right'
    assert result['primaryAlign'] == 'center'
    assert result['secondaryAlign'] == 'right'
    assert result['titleWeight'] == 'bold'
    assert result['primaryPosition'] == 'bottom'
    assert result['colorMode'] == 'background'
    assert result['maxAccessor'] == 'max-metric'


def test_metric_chart_dashboard_references_bubble_up() -> None:
    """Test that metric chart data view references bubble up to dashboard level correctly.

    Metric charts reference a data view (index-pattern), so this reference should appear
    at the dashboard's top-level references array with proper panel namespacing.
    """
    dashboard = Dashboard(
        name='Test Metric Chart Dashboard',
        panels=[
            {
                'title': 'Metric',
                'id': 'metric-panel-1',
                'position': {'x': 0, 'y': 0},
                'size': {'w': 12, 'h': 8},
                'lens': {
                    'type': 'metric',
                    'data_view': 'metrics-*',
                    'primary': {
                        'aggregation': 'count',
                        'id': 'primary-metric',
                    },
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
                'name': IsStr(regex=r'metric-panel-1:indexpattern-datasource-layer-[a-f0-9-]+'),
                'type': 'index-pattern',
            }
        ]
    )
