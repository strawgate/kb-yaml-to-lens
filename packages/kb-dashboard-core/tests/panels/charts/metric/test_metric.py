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
from pydantic import ValidationError

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
            'applyColorTo': 'background',
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
            'applyColorTo': 'background',
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
            'applyColorTo': 'background',
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
            'applyColorTo': 'background',
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
            'applyColorTo': 'background',
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
            'applyColorTo': 'background',
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
            'applyColorTo': 'background',
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
            'applyColorTo': 'background',
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
@pytest.mark.parametrize('apply_to', ['value', 'background'])
def test_compile_metric_chart_apply_to(chart_type: str, apply_to: str) -> None:
    """Test metric apply_to compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {
                'aggregation': 'count',
                'id': 'primary-metric',
            },
            'apply_to': apply_to,
        }
    else:
        config = {
            'type': 'metric',
            'primary': {
                'field': 'count(*)',
                'id': 'primary-metric',
            },
            'apply_to': apply_to,
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['applyColorTo'] == apply_to


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_compile_metric_chart_apply_to_omitted(chart_type: str) -> None:
    """Test metric apply_to defaults to background for Lens and ES|QL charts."""
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
    assert result['applyColorTo'] == 'background'


def test_compile_metric_chart_with_maximum_and_secondary_lens() -> None:
    """Test the compilation of a metric chart with primary, secondary, and maximum metrics (Lens)."""
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'field': 'system.cpu.user.pct',
            'id': 'primary-metric-1',
            'aggregation': 'average',
        },
        'secondary': {
            'field': 'system.cpu.system.pct',
            'id': 'secondary-metric-1',
            'aggregation': 'average',
        },
        'maximum': {
            'value': 100,
            'id': 'maximum-metric-1',
        },
    }

    result = compile_metric_chart_snapshot(config, 'lens')

    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': 'primary-metric-1',
            'applyColorTo': 'background',
            'secondaryTrend': {'type': 'none'},
            'secondaryLabelPosition': 'before',
            'secondaryMetricAccessor': 'secondary-metric-1',
            'maxAccessor': 'maximum-metric-1',
        }
    )


def test_compile_metric_chart_column_order_with_maximum() -> None:
    """Test that kbn_columns_by_id contains maximum metric column when present (Lens)."""
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'field': 'system.cpu.user.pct',
            'id': 'primary-metric-1',
            'aggregation': 'average',
        },
        'maximum': {
            'value': 100,
            'id': 'maximum-metric-1',
        },
    }

    lens_chart = LensMetricChart.model_validate(config)
    _layer_id, kbn_columns_by_id, kbn_state = compile_lens_metric_chart(lens_metric_chart=lens_chart)

    result = kbn_state.model_dump()
    assert result['maxAccessor'] == 'maximum-metric-1'
    assert 'maximum-metric-1' in kbn_columns_by_id


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
            'titles_and_text': {'subtitle': 'Last 24 hours'},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'titles_and_text': {'subtitle': 'Last 24 hours'},
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
def test_compile_metric_chart_secondary_label_appearance(chart_type: str) -> None:
    """Test metric secondary label compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'secondary': {'aggregation': 'count', 'id': 'secondary-metric'},
            'appearance': {'secondary': {'label': {'text': 'vs. previous period'}}},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'secondary': {'field': 'prev_count', 'id': 'secondary-metric'},
            'appearance': {'secondary': {'label': {'text': 'vs. previous period'}}},
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['secondaryLabel'] == 'vs. previous period'


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_compile_metric_chart_secondary_label_position_after(chart_type: str) -> None:
    """Test secondary label position can be explicitly set to after."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'secondary': {'aggregation': 'count', 'id': 'secondary-metric'},
            'appearance': {'secondary': {'label': {'position': 'after'}}},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'secondary': {'field': 'prev_count', 'id': 'secondary-metric'},
            'appearance': {'secondary': {'label': {'position': 'after'}}},
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['secondaryLabelPosition'] == 'after'


def test_metric_deprecated_secondary_label_string_warns_and_maps() -> None:
    """Deprecated secondary.label string should warn and map to label.text."""
    with pytest.warns(DeprecationWarning, match="label'.*string"):
        chart = LensMetricChart.model_validate(
            {
                'type': 'metric',
                'data_view': 'metrics-*',
                'primary': {'aggregation': 'count'},
                'secondary': {'aggregation': 'count'},
                'appearance': {'secondary': {'label': 'legacy text'}},
            }
        )

    assert chart.appearance is not None
    assert chart.appearance.secondary is not None
    assert chart.appearance.secondary.label is not None
    assert chart.appearance.secondary.label.text == 'legacy text'


def test_metric_deprecated_label_position_warns_when_ignored() -> None:
    """Deprecated secondary.label_position should warn when nested position is present."""
    with pytest.warns(DeprecationWarning, match="ignored because 'appearance.secondary.label.position' is already set"):
        chart = LensMetricChart.model_validate(
            {
                'type': 'metric',
                'data_view': 'metrics-*',
                'primary': {'aggregation': 'count'},
                'secondary': {'aggregation': 'count'},
                'appearance': {'secondary': {'label_position': 'before', 'label': {'position': 'after'}}},
            }
        )

    assert chart.appearance is not None
    assert chart.appearance.secondary is not None
    assert chart.appearance.secondary.label is not None
    assert chart.appearance.secondary.label.position == 'after'


def test_metric_deprecated_label_position_only_maps_to_nested_label() -> None:
    """Deprecated secondary.label_position should map when label is omitted."""
    with pytest.warns(DeprecationWarning, match='label_position'):
        chart = LensMetricChart.model_validate(
            {
                'type': 'metric',
                'data_view': 'metrics-*',
                'primary': {'aggregation': 'count'},
                'secondary': {'aggregation': 'count'},
                'appearance': {'secondary': {'label_position': 'before'}},
            }
        )

    assert chart.appearance is not None
    assert chart.appearance.secondary is not None
    assert chart.appearance.secondary.label is not None
    assert chart.appearance.secondary.label.position == 'before'


def test_metric_deprecated_label_position_merges_with_label_text() -> None:
    """Deprecated secondary.label_position should merge into nested label when position missing."""
    with pytest.warns(DeprecationWarning, match='label_position'):
        chart = LensMetricChart.model_validate(
            {
                'type': 'metric',
                'data_view': 'metrics-*',
                'primary': {'aggregation': 'count'},
                'secondary': {'aggregation': 'count'},
                'appearance': {'secondary': {'label': {'text': 'legacy label'}, 'label_position': 'after'}},
            }
        )

    assert chart.appearance is not None
    assert chart.appearance.secondary is not None
    assert chart.appearance.secondary.label is not None
    assert chart.appearance.secondary.label.text == 'legacy label'
    assert chart.appearance.secondary.label.position == 'after'


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_compile_metric_chart_icon(chart_type: str) -> None:
    """Test metric icon compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'appearance': {'primary': {'icon': 'sortUp'}},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'appearance': {'primary': {'icon': 'sortUp'}},
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
def test_compile_metric_chart_breakdown_column_count(chart_type: str) -> None:
    """Test metric breakdown column_count compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'appearance': {'breakdown': {'column_count': 3}},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'appearance': {'breakdown': {'column_count': 3}},
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['maxCols'] == 3


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_compile_metric_chart_background_chart_bar_type(chart_type: str) -> None:
    """Test metric background_chart bar compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'appearance': {'primary': {'background_chart': {'type': 'bar'}}},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'appearance': {'primary': {'background_chart': {'type': 'bar'}}},
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['showBar'] is True


@pytest.mark.parametrize(
    ('background_type', 'expected_show_bar'),
    [('line', False), ('bar', True), ('none', None)],
)
@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_compile_metric_chart_background_chart_type_mapping(chart_type: str, background_type: str, expected_show_bar: bool | None) -> None:
    """Test background_chart.type mapping to Kibana showBar semantics."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'appearance': {'primary': {'background_chart': {'type': background_type}}},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'appearance': {'primary': {'background_chart': {'type': background_type}}},
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    if expected_show_bar is None:
        assert 'showBar' not in result
    else:
        assert result['showBar'] is expected_show_bar


def test_compile_metric_chart_line_background_adds_trendline_fields_lens() -> None:
    """Test line background charts emit trendline accessors in visualization state."""
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {'aggregation': 'count', 'id': 'primary-metric'},
        'secondary': {'aggregation': 'count', 'id': 'secondary-metric'},
        'appearance': {'primary': {'background_chart': {'type': 'line'}}},
    }

    result = compile_metric_chart_snapshot(config, 'lens')
    assert result['showBar'] is False
    assert result['trendlineLayerType'] == 'metricTrendline'
    assert result['trendlineLayerId']
    assert result['trendlineTimeAccessor']
    assert result['trendlineMetricAccessor'] == 'primary-metric'
    assert result['trendlineSecondaryMetricAccessor'] == 'secondary-metric'


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('direction', ['horizontal', 'vertical'])
def test_compile_metric_chart_background_chart_bar_direction(chart_type: str, direction: str) -> None:
    """Test metric background_chart direction compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'appearance': {'primary': {'background_chart': {'type': 'bar', 'direction': direction}}},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'appearance': {'primary': {'background_chart': {'type': 'bar', 'direction': direction}}},
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['progressDirection'] == direction


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('background_type', ['line', 'none'])
def test_metric_background_chart_direction_requires_bar(chart_type: str, background_type: str) -> None:
    """Test background_chart.direction is rejected unless type is bar."""
    if chart_type == 'lens':
        config: dict[str, Any] = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'appearance': {'primary': {'background_chart': {'type': background_type, 'direction': 'horizontal'}}},
        }
        with pytest.raises(ValidationError):
            LensMetricChart.model_validate(config)
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'appearance': {'primary': {'background_chart': {'type': background_type, 'direction': 'horizontal'}}},
        }
        with pytest.raises(ValidationError):
            ESQLMetricChart.model_validate(config)


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_metric_breakdown_column_count_minimum(chart_type: str) -> None:
    """Test breakdown.column_count enforces minimum value of 1."""
    if chart_type == 'lens':
        config: dict[str, Any] = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'appearance': {'breakdown': {'column_count': 0}},
        }
        with pytest.raises(ValidationError):
            LensMetricChart.model_validate(config)
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'appearance': {'breakdown': {'column_count': 0}},
        }
        with pytest.raises(ValidationError):
            ESQLMetricChart.model_validate(config)


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_metric_color_assignments_are_rejected(chart_type: str) -> None:
    """Metric charts should fail fast on unsupported color.assignments."""
    if chart_type == 'lens':
        config: dict[str, Any] = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'color': {'assignments': [{'value': 'critical', 'color': '#FF0000'}]},
        }
        with pytest.raises(ValidationError, match=r'color\.assignments'):
            LensMetricChart.model_validate(config)
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'color': {'assignments': [{'value': 'critical', 'color': '#FF0000'}]},
        }
        with pytest.raises(ValidationError, match=r'color\.assignments'):
            ESQLMetricChart.model_validate(config)


def test_metric_mixed_shifts_with_top_values_breakdown_is_rejected() -> None:
    """Metric charts should reject mixed time shifts with dynamic top-values breakdowns."""
    config: dict[str, Any] = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {'aggregation': 'count', 'id': 'primary-metric'},
        'secondary': {
            'id': 'secondary-shifted',
            'formula': "count(kql='event.outcome:failure', shift='1h')",
        },
        'breakdown': {
            'type': 'values',
            'field': 'service.name',
            'id': 'breakdown-service',
        },
    }

    with pytest.raises(ValidationError, match='different time shifts'):
        LensMetricChart.model_validate(config)


def test_metric_same_shift_with_top_values_breakdown_is_allowed() -> None:
    """Metric charts should allow dynamic top values when configured shifts match."""
    config: dict[str, Any] = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'id': 'primary-shifted',
            'formula': "count(shift='1h')",
        },
        'secondary': {
            'id': 'secondary-shifted',
            'formula': "count(kql='event.outcome:failure', shift='1h')",
        },
        'breakdown': {
            'type': 'values',
            'field': 'service.name',
            'id': 'breakdown-service',
        },
    }

    chart = LensMetricChart.model_validate(config)
    assert chart.primary is not None
    assert chart.secondary is not None


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('align', ['left', 'center', 'right'])
def test_compile_metric_chart_titles_and_text_alignment(chart_type: str, align: str) -> None:
    """Test metric titles_and_text.alignment compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'titles_and_text': {'alignment': align},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'titles_and_text': {'alignment': align},
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['titlesTextAlign'] == align


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('mode', ['default', 'fit', 'custom'])
def test_compile_metric_chart_value_font_mode(chart_type: str, mode: str) -> None:
    """Test metric appearance.primary.font_size compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'appearance': {'primary': {'font_size': mode}},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'appearance': {'primary': {'font_size': mode}},
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['valueFontMode'] == mode


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('align', ['left', 'right'])
def test_compile_metric_chart_primary_icon_position(chart_type: str, align: str) -> None:
    """Test metric appearance.primary.icon_position compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'appearance': {'primary': {'icon_position': align}},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'appearance': {'primary': {'icon_position': align}},
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['iconAlign'] == align


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('align', ['left', 'center', 'right'])
def test_compile_metric_chart_primary_alignment(chart_type: str, align: str) -> None:
    """Test metric appearance.primary.alignment compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'appearance': {'primary': {'alignment': align}},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'appearance': {'primary': {'alignment': align}},
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['primaryAlign'] == align


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('align', ['left', 'center', 'right'])
def test_compile_metric_chart_secondary_alignment(chart_type: str, align: str) -> None:
    """Test metric appearance.secondary.alignment compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'appearance': {'secondary': {'alignment': align}},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'appearance': {'secondary': {'alignment': align}},
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['secondaryAlign'] == align


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('weight', ['bold', 'normal', 'lighter'])
def test_compile_metric_chart_title_text_weight(chart_type: str, weight: str) -> None:
    """Test metric titles_and_text.weight compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'titles_and_text': {'weight': weight},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'titles_and_text': {'weight': weight},
        }

    result = compile_metric_chart_snapshot(config, chart_type)
    assert result['titleWeight'] == weight


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
@pytest.mark.parametrize('position', ['top', 'bottom'])
def test_compile_metric_chart_primary_value_position(chart_type: str, position: str) -> None:
    """Test metric appearance.primary.position compilation for Lens and ES|QL charts."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'appearance': {'primary': {'position': position}},
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'appearance': {'primary': {'position': position}},
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
            'apply_to': 'background',
            'appearance': {
                'primary': {
                    'icon': 'compute',
                    'background_chart': {'type': 'bar', 'direction': 'vertical'},
                    'font_size': 'fit',
                    'icon_position': 'right',
                    'position': 'bottom',
                    'alignment': 'center',
                },
                'secondary': {'alignment': 'right', 'label': {'text': 'Change'}},
                'breakdown': {'column_count': 5},
            },
            'titles_and_text': {
                'subtitle': 'Overview',
                'alignment': 'center',
                'weight': 'bold',
            },
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'secondary': {'field': 'prev_count', 'id': 'secondary-metric'},
            'maximum': {'field': 'max_val', 'id': 'max-metric'},
            'apply_to': 'background',
            'appearance': {
                'primary': {
                    'icon': 'compute',
                    'background_chart': {'type': 'bar', 'direction': 'vertical'},
                    'font_size': 'fit',
                    'icon_position': 'right',
                    'position': 'bottom',
                    'alignment': 'center',
                },
                'secondary': {'alignment': 'right', 'label': {'text': 'Change'}},
                'breakdown': {'column_count': 5},
            },
            'titles_and_text': {
                'subtitle': 'Overview',
                'alignment': 'center',
                'weight': 'bold',
            },
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
    assert result['applyColorTo'] == 'background'
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


def test_metric_line_background_adds_trendline_reference_and_layer() -> None:
    """Test line background charts include trendline datasource layer and reference."""
    dashboard = Dashboard(
        name='Line Trendline Metric Dashboard',
        panels=[
            {
                'title': 'Metric Line',
                'id': 'metric-panel-line',
                'position': {'x': 0, 'y': 0},
                'size': {'w': 12, 'h': 8},
                'lens': {
                    'type': 'metric',
                    'data_view': 'metrics-*',
                    'primary': {'aggregation': 'count', 'id': 'primary-metric'},
                    'secondary': {'aggregation': 'count', 'id': 'secondary-metric'},
                    'appearance': {'primary': {'background_chart': {'type': 'line'}}},
                },
            }
        ],
    )

    kbn_dashboard: KbnDashboard = render(dashboard=dashboard)
    references = [ref.model_dump() for ref in kbn_dashboard.references]
    assert len(references) == 2
    assert all(ref['type'] == 'index-pattern' and ref['id'] == 'metrics-*' for ref in references)
    assert all(ref['name'].startswith('metric-panel-line:indexpattern-datasource-layer-') for ref in references)

    panel_json = kbn_dashboard.attributes.panelsJSON[0].model_dump()
    layers = panel_json['embeddableConfig']['attributes']['state']['datasourceStates']['formBased']['layers']
    assert len(layers) == 2
    panel_layer_id = panel_json['embeddableConfig']['attributes']['state']['visualization']['layerId']
    trendline_layer = next(layer for layer in layers.values() if layer.get('linkToLayers') == [panel_layer_id])
    assert trendline_layer['indexPatternId'] == 'metrics-*'
    assert trendline_layer['ignoreGlobalFilters'] is False


def test_compile_metric_chart_with_maximum_lens() -> None:
    """Test the compilation of a metric chart with a maximum metric (Lens).

    The maximum metric enables progress bar display in Kibana, showing the primary
    metric value relative to a maximum.
    """
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'field': 'system.cpu.total.pct',
            'id': 'primary-cpu',
            'aggregation': 'average',
        },
        'maximum': {
            'value': 100,
            'id': 'max-cpu',
        },
    }

    result = compile_metric_chart_snapshot(config, 'lens')

    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': 'primary-cpu',
            'applyColorTo': 'background',
            'secondaryTrend': {'type': 'none'},
            'secondaryLabelPosition': 'before',
            'maxAccessor': 'max-cpu',
        }
    )


def test_compile_metric_chart_with_maximum_esql() -> None:
    """Test the compilation of a metric chart with a maximum metric (ES|QL).

    The maximum metric enables progress bar display in Kibana, showing the primary
    metric value relative to a maximum.
    """
    config = {
        'type': 'metric',
        'primary': {
            'field': 'avg_cpu',
            'id': 'primary-cpu',
        },
        'maximum': {
            'field': 'max_cpu',
            'id': 'max-cpu',
        },
    }

    result = compile_metric_chart_snapshot(config, 'esql')

    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': 'primary-cpu',
            'applyColorTo': 'background',
            'showBar': False,
            'maxAccessor': 'max-cpu',
        }
    )


def test_compile_metric_chart_with_maximum_columns_lens() -> None:
    """Test that the maximum metric is included in compiled columns (Lens)."""
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'field': 'system.cpu.total.pct',
            'id': 'primary-cpu',
            'aggregation': 'average',
        },
        'maximum': {
            'value': 100,
            'id': 'max-cpu',
        },
    }

    lens_chart = LensMetricChart.model_validate(config)
    _layer_id, kbn_columns_by_id, _kbn_state_visualization = compile_lens_metric_chart(lens_metric_chart=lens_chart)

    column_ids = list(kbn_columns_by_id.keys())
    assert 'primary-cpu' in column_ids
    assert 'max-cpu' in column_ids


def test_compile_metric_chart_with_maximum_columns_esql() -> None:
    """Test that the maximum metric is included in compiled columns (ES|QL)."""
    config = {
        'type': 'metric',
        'primary': {
            'field': 'avg_cpu',
            'id': 'primary-cpu',
        },
        'maximum': {
            'field': 'max_cpu',
            'id': 'max-cpu',
        },
    }

    esql_chart = ESQLMetricChart.model_validate(config)
    _layer_id, kbn_columns, _kbn_state_visualization = compile_esql_metric_chart(esql_metric_chart=esql_chart)

    column_ids = [col.columnId for col in kbn_columns]
    assert 'primary-cpu' in column_ids
    assert 'max-cpu' in column_ids


def test_compile_metric_chart_maximum_omitted_when_none() -> None:
    """Test that maxAccessor is omitted when maximum metric is not configured."""
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'aggregation': 'count',
            'id': 'primary-metric',
        },
    }

    result = compile_metric_chart_snapshot(config, 'lens')
    assert 'maxAccessor' not in result


def test_compile_metric_chart_with_all_metrics_lens() -> None:
    """Test compilation of a metric chart with primary, secondary, maximum, and breakdown (Lens)."""
    config = {
        'type': 'metric',
        'data_view': 'metrics-*',
        'primary': {
            'field': 'system.cpu.total.pct',
            'id': 'primary-cpu',
            'aggregation': 'average',
        },
        'secondary': {
            'field': 'system.cpu.total.pct',
            'id': 'secondary-cpu',
            'aggregation': 'min',
        },
        'maximum': {
            'value': 100,
            'id': 'max-cpu',
        },
        'breakdown': {
            'type': 'values',
            'field': 'host.name',
            'id': 'breakdown-host',
        },
    }

    result = compile_metric_chart_snapshot(config, 'lens')

    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': 'primary-cpu',
            'applyColorTo': 'background',
            'secondaryTrend': {'type': 'none'},
            'secondaryLabelPosition': 'before',
            'secondaryMetricAccessor': 'secondary-cpu',
            'maxAccessor': 'max-cpu',
            'breakdownByAccessor': 'breakdown-host',
        }
    )


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_compile_metric_chart_color_range_palette(chart_type: str) -> None:
    """Metrics should compile threshold color ranges into visualization.palette."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'color': {
                'range_type': 'number',
                'range_min': 0,
                'range_max': 100,
                'thresholds': [
                    {'up_to': 50, 'color': '#24c292'},
                    {'up_to': 80, 'color': '#fcd883'},
                    {'up_to': 100, 'color': '#f6726a'},
                ],
            },
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'color': {
                'range_type': 'number',
                'range_min': 0,
                'range_max': 100,
                'thresholds': [
                    {'up_to': 50, 'color': '#24c292'},
                    {'up_to': 80, 'color': '#fcd883'},
                    {'up_to': 100, 'color': '#f6726a'},
                ],
            },
        }

    result = compile_metric_chart_snapshot(config, chart_type)

    assert result['palette']['name'] == 'custom'
    assert result['palette']['type'] == 'palette'
    assert result['palette']['params']['rangeType'] == 'number'
    assert result['palette']['params']['rangeMin'] == 0.0
    assert result['palette']['params']['rangeMax'] == 100.0
    assert result['palette']['params']['continuity'] == 'above'
    assert result['palette']['params']['stops'] == [
        {'color': '#24c292', 'stop': 50.0},
        {'color': '#fcd883', 'stop': 80.0},
        {'color': '#f6726a', 'stop': 100.0},
    ]
    assert result['palette']['params']['colorStops'] == [
        {'color': '#24c292', 'stop': 0.0},
        {'color': '#fcd883', 'stop': 50.0},
        {'color': '#f6726a', 'stop': 80.0},
    ]


@pytest.mark.parametrize('chart_type', ['lens', 'esql'])
def test_compile_metric_chart_color_range_palette_extends_to_range_max(chart_type: str) -> None:
    """Metrics should append terminal stop at range_max when last threshold is lower."""
    if chart_type == 'lens':
        config = {
            'type': 'metric',
            'data_view': 'metrics-*',
            'primary': {'aggregation': 'count', 'id': 'primary-metric'},
            'color': {
                'range_type': 'number',
                'range_min': 0,
                'range_max': 100,
                'thresholds': [
                    {'up_to': 25, 'color': '#24c292'},
                    {'up_to': 50, 'color': '#fcd883'},
                    {'up_to': 75, 'color': '#f6726a'},
                ],
            },
        }
    else:
        config = {
            'type': 'metric',
            'primary': {'field': 'count(*)', 'id': 'primary-metric'},
            'color': {
                'range_type': 'number',
                'range_min': 0,
                'range_max': 100,
                'thresholds': [
                    {'up_to': 25, 'color': '#24c292'},
                    {'up_to': 50, 'color': '#fcd883'},
                    {'up_to': 75, 'color': '#f6726a'},
                ],
            },
        }

    result = compile_metric_chart_snapshot(config, chart_type)

    assert result['palette']['params']['rangeMax'] == 100.0
    assert result['palette']['params']['stops'] == [
        {'color': '#24c292', 'stop': 25.0},
        {'color': '#fcd883', 'stop': 50.0},
        {'color': '#f6726a', 'stop': 75.0},
        {'color': '#f6726a', 'stop': 100.0},
    ]
    assert result['palette']['params']['colorStops'] == [
        {'color': '#24c292', 'stop': 0.0},
        {'color': '#fcd883', 'stop': 25.0},
        {'color': '#f6726a', 'stop': 50.0},
        {'color': '#f6726a', 'stop': 75.0},
    ]
