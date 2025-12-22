"""Test the compilation of Lens metrics from config models to view models using inline snapshots."""

import re
from typing import Any

import pytest
from inline_snapshot import snapshot

from dashboard_compiler.panels.charts.metric.compile import (
    compile_esql_metric_chart,
    compile_lens_metric_chart,
)
from dashboard_compiler.panels.charts.metric.config import ESQLMetricChart, LensMetricChart


def normalize_layer_id(result: dict[str, Any]) -> None:
    """Validate layerId format and replace with placeholder for snapshot comparison."""
    layer_id = result['layerId']
    assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', layer_id)
    result['layerId'] = 'DYNAMIC_LAYER_ID'


@pytest.fixture
def compile_metric_chart_snapshot():
    """Fixture that returns a function to compile metric charts and return dict for snapshot."""

    def _compile(config: dict[str, Any], chart_type: str = 'lens') -> dict[str, Any]:
        if chart_type == 'lens':
            lens_chart = LensMetricChart.model_validate(config)
            layer_id, kbn_columns_by_id, kbn_state_visualization = compile_lens_metric_chart(lens_metric_chart=lens_chart)
        else:  # esql
            esql_chart = ESQLMetricChart.model_validate(config)
            layer_id, kbn_columns, kbn_state_visualization = compile_esql_metric_chart(esql_metric_chart=esql_chart)

        assert kbn_state_visualization is not None
        assert len(kbn_state_visualization.layers) > 0
        kbn_state_visualization_layer = kbn_state_visualization.layers[0]
        return kbn_state_visualization_layer.model_dump()

    return _compile


def test_compile_metric_chart_primary_only_lens(compile_metric_chart_snapshot):
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
    normalize_layer_id(result)

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': 'DYNAMIC_LAYER_ID',
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
        }
    )


def test_compile_metric_chart_primary_only_esql(compile_metric_chart_snapshot):
    """Test the compilation of a metric chart with only a primary metric (ESQL)."""
    config = {
        'type': 'metric',
        'primary': {
            'field': 'count(aerospike.namespace)',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
        },
    }

    result = compile_metric_chart_snapshot(config, 'esql')
    normalize_layer_id(result)

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': 'DYNAMIC_LAYER_ID',
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
        }
    )


def test_compile_metric_chart_primary_and_secondary_lens(compile_metric_chart_snapshot):
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
    normalize_layer_id(result)

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': 'DYNAMIC_LAYER_ID',
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'secondaryMetricAccessor': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
        }
    )


def test_compile_metric_chart_primary_and_secondary_esql(compile_metric_chart_snapshot):
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
    normalize_layer_id(result)

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': 'DYNAMIC_LAYER_ID',
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'secondaryMetricAccessor': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
        }
    )


def test_compile_metric_chart_primary_secondary_breakdown_lens(compile_metric_chart_snapshot):
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
    normalize_layer_id(result)

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': 'DYNAMIC_LAYER_ID',
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'secondaryMetricAccessor': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
            'breakdownByAccessor': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
        }
    )


def test_compile_metric_chart_primary_secondary_breakdown_esql(compile_metric_chart_snapshot):
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
    normalize_layer_id(result)

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': 'DYNAMIC_LAYER_ID',
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'secondaryMetricAccessor': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
            'breakdownByAccessor': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
        }
    )
