"""Test the compilation of gauge charts from config models to view models using inline snapshots."""

from typing import Any

from dirty_equals import IsUUID
from inline_snapshot import snapshot

from dashboard_compiler.panels.charts.gauge.compile import (
    compile_esql_gauge_chart,
    compile_lens_gauge_chart,
)
from dashboard_compiler.panels.charts.gauge.config import ESQLGaugeChart, LensGaugeChart


def compile_gauge_chart_snapshot(config: dict[str, Any], chart_type: str = 'lens') -> dict[str, Any]:
    """Compile gauge chart config and return dict for snapshot testing."""
    if chart_type == 'lens':
        lens_chart = LensGaugeChart.model_validate(config)
        _layer_id, _kbn_columns_by_id, kbn_state_visualization = compile_lens_gauge_chart(lens_gauge_chart=lens_chart)
    else:  # esql
        esql_chart = ESQLGaugeChart.model_validate(config)
        _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_gauge_chart(esql_gauge_chart=esql_chart)

    assert kbn_state_visualization is not None
    assert len(kbn_state_visualization.layers) > 0
    kbn_state_visualization_layer = kbn_state_visualization.layers[0]
    return kbn_state_visualization_layer.model_dump()


def test_compile_gauge_chart_metric_only_lens():
    """Test the compilation of a gauge chart with only a metric (Lens)."""
    config = {
        'type': 'gauge',
        'data_view': 'metrics-*',
        'metric': {
            'field': 'system.cpu.total.pct',
            'id': 'metric_accessor',
            'aggregation': 'average',
        },
    }

    result = compile_gauge_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': 'metric_accessor',
            'labelMajorMode': 'auto',
        }
    )


def test_compile_gauge_chart_metric_only_esql():
    """Test the compilation of a gauge chart with only a metric (ESQL)."""
    config = {
        'type': 'gauge',
        'metric': {
            'field': 'avg_cpu',
            'id': 'metric_accessor',
        },
    }

    result = compile_gauge_chart_snapshot(config, 'esql')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': 'metric_accessor',
            'labelMajorMode': 'auto',
        }
    )


def test_compile_gauge_chart_with_shape_lens():
    """Test the compilation of a gauge chart with shape configuration (Lens)."""
    config = {
        'type': 'gauge',
        'data_view': 'metrics-*',
        'metric': {
            'field': 'system.cpu.total.pct',
            'id': 'metric_accessor',
            'aggregation': 'average',
        },
        'shape': 'arc',
    }

    result = compile_gauge_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': 'metric_accessor',
            'shape': 'arc',
            'labelMajorMode': 'auto',
        }
    )


def test_compile_gauge_chart_with_min_max_goal_lens():
    """Test the compilation of a gauge chart with min/max/goal (Lens)."""
    config = {
        'type': 'gauge',
        'data_view': 'metrics-*',
        'metric': {
            'field': 'system.cpu.total.pct',
            'id': 'metric_accessor',
            'aggregation': 'average',
        },
        'minimum': {
            'field': 'system.cpu.total.pct',
            'id': 'min_accessor',
            'aggregation': 'min',
        },
        'maximum': {
            'field': 'system.cpu.total.pct',
            'id': 'max_accessor',
            'aggregation': 'max',
        },
        'goal': {
            'field': 'system.cpu.target',
            'id': 'goal_accessor',
            'aggregation': 'average',
        },
    }

    result = compile_gauge_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': 'metric_accessor',
            'minAccessor': 'min_accessor',
            'maxAccessor': 'max_accessor',
            'goalAccessor': 'goal_accessor',
            'labelMajorMode': 'auto',
        }
    )


def test_compile_gauge_chart_with_min_max_goal_esql():
    """Test the compilation of a gauge chart with min/max/goal (ESQL)."""
    config = {
        'type': 'gauge',
        'metric': {
            'field': 'avg_cpu',
            'id': 'metric_accessor',
        },
        'minimum': {
            'field': 'min_cpu',
            'id': 'min_accessor',
        },
        'maximum': {
            'field': 'max_cpu',
            'id': 'max_accessor',
        },
        'goal': {
            'field': 'goal_cpu',
            'id': 'goal_accessor',
        },
    }

    result = compile_gauge_chart_snapshot(config, 'esql')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': 'metric_accessor',
            'minAccessor': 'min_accessor',
            'maxAccessor': 'max_accessor',
            'goalAccessor': 'goal_accessor',
            'labelMajorMode': 'auto',
        }
    )


def test_compile_gauge_chart_with_all_options_lens():
    """Test the compilation of a gauge chart with all configuration options (Lens)."""
    config = {
        'type': 'gauge',
        'data_view': 'metrics-*',
        'metric': {
            'field': 'system.cpu.total.pct',
            'id': 'metric_accessor',
            'aggregation': 'average',
        },
        'shape': 'arc',
        'ticks_position': 'auto',
        'label_major': 'CPU Usage',
        'label_minor': 'Percentage',
        'color_mode': 'palette',
    }

    result = compile_gauge_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': 'metric_accessor',
            'shape': 'arc',
            'ticksPosition': 'auto',
            'labelMajor': 'CPU Usage',
            'labelMinor': 'Percentage',
            'labelMajorMode': 'custom',
            'colorMode': 'palette',
        }
    )


def test_compile_gauge_chart_with_all_shapes():
    """Test the compilation of gauge charts with different shape options."""
    shapes = ['horizontalBullet', 'verticalBullet', 'arc', 'circle']

    for shape in shapes:
        config = {
            'type': 'gauge',
            'data_view': 'metrics-*',
            'metric': {
                'field': 'system.cpu.total.pct',
                'id': 'metric_accessor',
                'aggregation': 'average',
            },
            'shape': shape,
        }

        result = compile_gauge_chart_snapshot(config, 'lens')

        # Verify the shape is correctly set
        assert result['shape'] == shape
        assert result['layerType'] == 'data'
        assert result['metricAccessor'] == 'metric_accessor'


def test_compile_gauge_chart_with_ticks_positions():
    """Test the compilation of gauge charts with different ticks position options."""
    ticks_positions = ['auto', 'bands', 'hidden']

    for ticks_position in ticks_positions:
        config = {
            'type': 'gauge',
            'data_view': 'metrics-*',
            'metric': {
                'field': 'system.cpu.total.pct',
                'id': 'metric_accessor',
                'aggregation': 'average',
            },
            'ticks_position': ticks_position,
        }

        result = compile_gauge_chart_snapshot(config, 'lens')

        # Verify the ticks_position is correctly set
        assert result['ticksPosition'] == ticks_position
        assert result['layerType'] == 'data'
        assert result['metricAccessor'] == 'metric_accessor'
