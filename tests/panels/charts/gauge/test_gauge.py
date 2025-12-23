"""Test the compilation of Lens gauge charts from config models to view models using inline snapshots."""

from typing import Any

import pytest
from dirty_equals import IsUUID
from inline_snapshot import snapshot

from dashboard_compiler.panels.charts.gauge.compile import (
    compile_esql_gauge_chart,
    compile_lens_gauge_chart,
)
from dashboard_compiler.panels.charts.gauge.config import ESQLGaugeChart, LensGaugeChart


@pytest.fixture
def compile_gauge_chart_snapshot():
    """Fixture that returns a function to compile gauge charts and return dict for snapshot."""

    def _compile(config: dict[str, Any], chart_type: str = 'lens') -> dict[str, Any]:
        if chart_type == 'lens':
            lens_chart = LensGaugeChart.model_validate(config)
            layer_id, kbn_columns_by_id, kbn_state_visualization = compile_lens_gauge_chart(lens_gauge_chart=lens_chart)
        else:  # esql
            esql_chart = ESQLGaugeChart.model_validate(config)
            layer_id, kbn_columns, kbn_state_visualization = compile_esql_gauge_chart(esql_gauge_chart=esql_chart)

        assert kbn_state_visualization is not None
        assert len(kbn_state_visualization.layers) > 0
        kbn_state_visualization_layer = kbn_state_visualization.layers[0]
        return kbn_state_visualization_layer.model_dump()

    return _compile


def test_compile_gauge_chart_metric_only_lens(compile_gauge_chart_snapshot):
    """Test the compilation of a gauge chart with only a metric (Lens)."""
    config = {
        'type': 'gauge',
        'data_view': 'metrics-*',
        'metric': {
            'field': 'system.cpu.total.pct',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'aggregation': 'average',
        },
    }

    result = compile_gauge_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
        }
    )


def test_compile_gauge_chart_metric_only_esql(compile_gauge_chart_snapshot):
    """Test the compilation of a gauge chart with only a metric (ESQL)."""
    config = {
        'type': 'gauge',
        'metric': {
            'field': 'avg(system.cpu.total.pct)',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
        },
    }

    result = compile_gauge_chart_snapshot(config, 'esql')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
        }
    )


def test_compile_gauge_chart_with_min_max_lens(compile_gauge_chart_snapshot):
    """Test the compilation of a gauge chart with metric, min, and max (Lens)."""
    config = {
        'type': 'gauge',
        'data_view': 'metrics-*',
        'metric': {
            'field': 'system.cpu.total.pct',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'aggregation': 'average',
        },
        'minimum': {
            'field': 'system.cpu.total.pct',
            'id': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
            'aggregation': 'min',
        },
        'maximum': {
            'field': 'system.cpu.total.pct',
            'id': 'b2fd6994-20c3-5bc0-c138-b24e8185238c',
            'aggregation': 'max',
        },
    }

    result = compile_gauge_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'minAccessor': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
            'maxAccessor': 'b2fd6994-20c3-5bc0-c138-b24e8185238c',
        }
    )


def test_compile_gauge_chart_with_min_max_esql(compile_gauge_chart_snapshot):
    """Test the compilation of a gauge chart with metric, min, and max (ESQL)."""
    config = {
        'type': 'gauge',
        'metric': {
            'field': 'avg(system.cpu.total.pct)',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
        },
        'minimum': {
            'field': 'min(system.cpu.total.pct)',
            'id': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
        },
        'maximum': {
            'field': 'max(system.cpu.total.pct)',
            'id': 'b2fd6994-20c3-5bc0-c138-b24e8185238c',
        },
    }

    result = compile_gauge_chart_snapshot(config, 'esql')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'minAccessor': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
            'maxAccessor': 'b2fd6994-20c3-5bc0-c138-b24e8185238c',
        }
    )


def test_compile_gauge_chart_with_goal_lens(compile_gauge_chart_snapshot):
    """Test the compilation of a gauge chart with metric and goal (Lens)."""
    config = {
        'type': 'gauge',
        'data_view': 'metrics-*',
        'metric': {
            'field': 'system.cpu.total.pct',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'aggregation': 'average',
        },
        'goal': {
            'field': 'system.cpu.total.pct',
            'id': 'c3ge7aa5-30d4-6cd1-d249-c35f9296349d',
            'aggregation': 'max',
        },
    }

    result = compile_gauge_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'goalAccessor': 'c3ge7aa5-30d4-6cd1-d249-c35f9296349d',
        }
    )


def test_compile_gauge_chart_with_goal_esql(compile_gauge_chart_snapshot):
    """Test the compilation of a gauge chart with metric and goal (ESQL)."""
    config = {
        'type': 'gauge',
        'metric': {
            'field': 'avg(system.cpu.total.pct)',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
        },
        'goal': {
            'field': 'max(system.cpu.total.pct)',
            'id': 'c3ge7aa5-30d4-6cd1-d249-c35f9296349d',
        },
    }

    result = compile_gauge_chart_snapshot(config, 'esql')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'goalAccessor': 'c3ge7aa5-30d4-6cd1-d249-c35f9296349d',
        }
    )


def test_compile_gauge_chart_with_all_options_lens(compile_gauge_chart_snapshot):
    """Test the compilation of a gauge chart with all options (Lens)."""
    config = {
        'type': 'gauge',
        'data_view': 'metrics-*',
        'metric': {
            'field': 'system.cpu.total.pct',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'aggregation': 'average',
        },
        'minimum': {
            'field': 'system.cpu.total.pct',
            'id': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
            'aggregation': 'min',
        },
        'maximum': {
            'field': 'system.cpu.total.pct',
            'id': 'b2fd6994-20c3-5bc0-c138-b24e8185238c',
            'aggregation': 'max',
        },
        'goal': {
            'field': 'system.cpu.total.pct',
            'id': 'c3ge7aa5-30d4-6cd1-d249-c35f9296349d',
            'aggregation': 'max',
        },
        'shape': 'arc',
        'ticks_position': 'bands',
        'label_major': 'CPU Usage',
        'label_minor': 'Average',
        'color_mode': 'palette',
        'respect_ranges': True,
    }

    result = compile_gauge_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'minAccessor': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
            'maxAccessor': 'b2fd6994-20c3-5bc0-c138-b24e8185238c',
            'goalAccessor': 'c3ge7aa5-30d4-6cd1-d249-c35f9296349d',
            'shape': 'arc',
            'ticksPosition': 'bands',
            'labelMajor': 'CPU Usage',
            'labelMinor': 'Average',
            'colorMode': 'palette',
            'respectRanges': True,
        }
    )


def test_compile_gauge_chart_with_all_options_esql(compile_gauge_chart_snapshot):
    """Test the compilation of a gauge chart with all options (ESQL)."""
    config = {
        'type': 'gauge',
        'metric': {
            'field': 'avg(system.cpu.total.pct)',
            'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
        },
        'minimum': {
            'field': 'min(system.cpu.total.pct)',
            'id': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
        },
        'maximum': {
            'field': 'max(system.cpu.total.pct)',
            'id': 'b2fd6994-20c3-5bc0-c138-b24e8185238c',
        },
        'goal': {
            'field': 'max(system.cpu.total.pct)',
            'id': 'c3ge7aa5-30d4-6cd1-d249-c35f9296349d',
        },
        'shape': 'circle',
        'ticks_position': 'auto',
        'label_major': 'CPU Usage',
        'label_minor': 'Average',
        'color_mode': 'none',
        'respect_ranges': False,
    }

    result = compile_gauge_chart_snapshot(config, 'esql')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            'minAccessor': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
            'maxAccessor': 'b2fd6994-20c3-5bc0-c138-b24e8185238c',
            'goalAccessor': 'c3ge7aa5-30d4-6cd1-d249-c35f9296349d',
            'shape': 'circle',
            'ticksPosition': 'auto',
            'labelMajor': 'CPU Usage',
            'labelMinor': 'Average',
            'colorMode': 'none',
            'respectRanges': False,
        }
    )
