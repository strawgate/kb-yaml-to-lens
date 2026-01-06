"""Test the compilation of Lens metrics from config models to view models using inline snapshots."""

from typing import Any

from dirty_equals import IsUUID
from inline_snapshot import snapshot

from dashboard_compiler.panels.charts.metric.compile import (
    compile_esql_metric_chart,
    compile_lens_metric_chart,
)
from dashboard_compiler.panels.charts.metric.config import ESQLMetricChart, LensMetricChart


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
