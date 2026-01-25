"""Test the compilation of heatmap charts from config models to view models using inline snapshots.

Fixture Examples:
    https://github.com/strawgate/kb-yaml-to-lens-fixtures
    - ES|QL: output/<version>/heatmap-esql.json
    - Data View: output/<version>/heatmap-dataview.json
"""

from typing import TYPE_CHECKING, Any

from dirty_equals import IsStr, IsUUID
from inline_snapshot import snapshot

from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.dashboard_compiler import render
from kb_dashboard_core.panels.charts.heatmap.compile import (
    compile_esql_heatmap_chart,
    compile_lens_heatmap_chart,
)
from kb_dashboard_core.panels.charts.heatmap.config import ESQLHeatmapChart, LensHeatmapChart

if TYPE_CHECKING:
    from kb_dashboard_core.dashboard.view import KbnDashboard


def compile_heatmap_chart_snapshot(config: dict[str, Any], chart_type: str = 'lens') -> dict[str, Any]:
    """Compile heatmap chart config and return dict for snapshot testing."""
    if chart_type == 'lens':
        lens_chart = LensHeatmapChart.model_validate(config)
        _layer_id, _kbn_columns_by_id, kbn_state_visualization = compile_lens_heatmap_chart(lens_heatmap_chart=lens_chart)
    elif chart_type == 'esql':
        esql_chart = ESQLHeatmapChart.model_validate(config)
        _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_heatmap_chart(esql_heatmap_chart=esql_chart)
    else:
        msg = f"Invalid chart_type: {chart_type}. Expected 'lens' or 'esql'."
        raise ValueError(msg)

    assert kbn_state_visualization is not None
    return kbn_state_visualization.model_dump(mode='json', exclude_none=False)


def test_compile_heatmap_chart_1d_lens() -> None:
    """Test the compilation of a 1D heatmap chart (no Y-axis) (Lens)."""
    config = {
        'type': 'heatmap',
        'data_view': 'metrics-*',
        'x_axis': {
            'type': 'values',
            'field': 'host.name',
            'id': 'x_accessor',
        },
        'value': {
            'aggregation': 'sum',
            'field': 'system.cpu.total.pct',
            'id': 'value_accessor',
        },
    }

    result = compile_heatmap_chart_snapshot(config, 'lens')

    assert result == snapshot(
        {
            'gridConfig': {
                'isCellLabelVisible': False,
                'isXAxisLabelVisible': False,
                'isXAxisTitleVisible': False,
                'isYAxisLabelVisible': False,
                'isYAxisTitleVisible': False,
                'type': 'heatmap_grid',
            },
            'layerId': IsUUID,
            'layerType': 'data',
            'legend': {
                'isVisible': True,
                'position': 'right',
                'type': 'heatmap_legend',
            },
            'shape': 'heatmap',
            'valueAccessor': 'value_accessor',
            'xAccessor': 'x_accessor',
        }
    )


def test_compile_heatmap_chart_2d_lens() -> None:
    """Test the compilation of a 2D heatmap chart (with Y-axis) (Lens)."""
    config = {
        'type': 'heatmap',
        'data_view': 'metrics-*',
        'x_axis': {
            'type': 'values',
            'field': 'host.name',
            'id': 'x_accessor',
        },
        'y_axis': {
            'type': 'values',
            'field': 'service.name',
            'id': 'y_accessor',
        },
        'value': {
            'aggregation': 'average',
            'field': 'system.cpu.total.pct',
            'id': 'value_accessor',
        },
    }

    result = compile_heatmap_chart_snapshot(config, 'lens')

    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'shape': 'heatmap',
            'xAccessor': 'x_accessor',
            'yAccessor': 'y_accessor',
            'valueAccessor': 'value_accessor',
            'gridConfig': {
                'type': 'heatmap_grid',
                'isCellLabelVisible': False,
                'isXAxisLabelVisible': False,
                'isXAxisTitleVisible': False,
                'isYAxisLabelVisible': False,
                'isYAxisTitleVisible': False,
            },
            'legend': {
                'type': 'heatmap_legend',
                'isVisible': True,
                'position': 'right',
            },
        }
    )


def test_compile_heatmap_chart_1d_esql() -> None:
    """Test the compilation of a 1D heatmap chart (no Y-axis) (ESQL)."""
    config = {
        'type': 'heatmap',
        'x_axis': {
            'field': 'host_name',
            'id': 'x_accessor',
        },
        'value': {
            'field': 'avg_cpu',
            'id': 'value_accessor',
        },
    }

    result = compile_heatmap_chart_snapshot(config, 'esql')

    assert result == snapshot(
        {
            'gridConfig': {
                'isCellLabelVisible': False,
                'isXAxisLabelVisible': False,
                'isXAxisTitleVisible': False,
                'isYAxisLabelVisible': False,
                'isYAxisTitleVisible': False,
                'type': 'heatmap_grid',
            },
            'layerId': IsUUID,
            'layerType': 'data',
            'legend': {
                'isVisible': True,
                'position': 'right',
                'type': 'heatmap_legend',
            },
            'shape': 'heatmap',
            'valueAccessor': 'value_accessor',
            'xAccessor': 'x_accessor',
        }
    )


def test_compile_heatmap_chart_2d_esql() -> None:
    """Test the compilation of a 2D heatmap chart (with Y-axis) (ESQL)."""
    config = {
        'type': 'heatmap',
        'x_axis': {
            'field': 'host_name',
            'id': 'x_accessor',
        },
        'y_axis': {
            'field': 'service_name',
            'id': 'y_accessor',
        },
        'value': {
            'field': 'avg_cpu',
            'id': 'value_accessor',
        },
    }

    result = compile_heatmap_chart_snapshot(config, 'esql')

    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'shape': 'heatmap',
            'xAccessor': 'x_accessor',
            'yAccessor': 'y_accessor',
            'valueAccessor': 'value_accessor',
            'gridConfig': {
                'type': 'heatmap_grid',
                'isCellLabelVisible': False,
                'isXAxisLabelVisible': False,
                'isXAxisTitleVisible': False,
                'isYAxisLabelVisible': False,
                'isYAxisTitleVisible': False,
            },
            'legend': {
                'type': 'heatmap_legend',
                'isVisible': True,
                'position': 'right',
            },
        }
    )


def test_compile_heatmap_chart_with_grid_config_lens() -> None:
    """Test the compilation of a heatmap chart with grid configuration (Lens)."""
    config = {
        'type': 'heatmap',
        'data_view': 'metrics-*',
        'x_axis': {
            'type': 'values',
            'field': 'host.name',
            'id': 'x_accessor',
        },
        'value': {
            'aggregation': 'average',
            'field': 'system.cpu.total.pct',
            'id': 'value_accessor',
        },
        'grid_config': {
            'cells': {
                'show_labels': True,
            },
            'x_axis': {
                'show_labels': True,
                'show_title': True,
            },
            'y_axis': {
                'show_labels': False,
                'show_title': False,
            },
        },
    }

    result = compile_heatmap_chart_snapshot(config, 'lens')

    assert result == snapshot(
        {
            'gridConfig': {
                'isCellLabelVisible': True,
                'isXAxisLabelVisible': True,
                'isXAxisTitleVisible': True,
                'isYAxisLabelVisible': False,
                'isYAxisTitleVisible': False,
                'type': 'heatmap_grid',
            },
            'layerId': IsUUID,
            'layerType': 'data',
            'legend': {
                'isVisible': True,
                'position': 'right',
                'type': 'heatmap_legend',
            },
            'shape': 'heatmap',
            'valueAccessor': 'value_accessor',
            'xAccessor': 'x_accessor',
        }
    )


def test_compile_heatmap_chart_with_grid_config_esql() -> None:
    """Test the compilation of a heatmap chart with grid configuration (ESQL)."""
    config = {
        'type': 'heatmap',
        'x_axis': {
            'field': 'host_name',
            'id': 'x_accessor',
        },
        'value': {
            'field': 'avg_cpu',
            'id': 'value_accessor',
        },
        'grid_config': {
            'cells': {
                'show_labels': True,
            },
            'x_axis': {
                'show_labels': True,
                'show_title': True,
            },
            'y_axis': {
                'show_labels': True,
                'show_title': True,
            },
        },
    }

    result = compile_heatmap_chart_snapshot(config, 'esql')

    assert result == snapshot(
        {
            'gridConfig': {
                'isCellLabelVisible': True,
                'isXAxisLabelVisible': True,
                'isXAxisTitleVisible': True,
                'isYAxisLabelVisible': True,
                'isYAxisTitleVisible': True,
                'type': 'heatmap_grid',
            },
            'layerId': IsUUID,
            'layerType': 'data',
            'legend': {
                'isVisible': True,
                'position': 'right',
                'type': 'heatmap_legend',
            },
            'shape': 'heatmap',
            'valueAccessor': 'value_accessor',
            'xAccessor': 'x_accessor',
        }
    )


def test_compile_heatmap_chart_with_legend_config_lens() -> None:
    """Test the compilation of a heatmap chart with legend configuration (Lens)."""
    config = {
        'type': 'heatmap',
        'data_view': 'metrics-*',
        'x_axis': {
            'type': 'values',
            'field': 'host.name',
            'id': 'x_accessor',
        },
        'value': {
            'aggregation': 'average',
            'field': 'system.cpu.total.pct',
            'id': 'value_accessor',
        },
        'legend': {
            'visible': 'hide',
            'position': 'bottom',
        },
    }

    result = compile_heatmap_chart_snapshot(config, 'lens')

    assert result == snapshot(
        {
            'gridConfig': {
                'isCellLabelVisible': False,
                'isXAxisLabelVisible': False,
                'isXAxisTitleVisible': False,
                'isYAxisLabelVisible': False,
                'isYAxisTitleVisible': False,
                'type': 'heatmap_grid',
            },
            'layerId': IsUUID,
            'layerType': 'data',
            'legend': {
                'isVisible': False,
                'position': 'bottom',
                'type': 'heatmap_legend',
            },
            'shape': 'heatmap',
            'valueAccessor': 'value_accessor',
            'xAccessor': 'x_accessor',
        }
    )


def test_compile_heatmap_chart_with_legend_positions() -> None:
    """Test the compilation of heatmap charts with different legend position options."""
    positions = ['top', 'right', 'bottom', 'left']

    for position in positions:
        config = {
            'type': 'heatmap',
            'data_view': 'metrics-*',
            'x_axis': {
                'type': 'values',
                'field': 'host.name',
                'id': 'x_accessor',
            },
            'value': {
                'aggregation': 'average',
                'field': 'system.cpu.total.pct',
                'id': 'value_accessor',
            },
            'legend': {
                'position': position,
            },
        }

        result = compile_heatmap_chart_snapshot(config, 'lens')

        assert result['legend']['position'] == position
        assert result['legend']['isVisible'] is True
        assert result['shape'] == 'heatmap'


def test_compile_heatmap_chart_with_all_grid_options_lens() -> None:
    """Test the compilation of a heatmap chart with all grid configuration options (Lens)."""
    config = {
        'type': 'heatmap',
        'data_view': 'metrics-*',
        'x_axis': {
            'type': 'values',
            'field': 'host.name',
            'id': 'x_accessor',
        },
        'y_axis': {
            'type': 'values',
            'field': 'service.name',
            'id': 'y_accessor',
        },
        'value': {
            'aggregation': 'average',
            'field': 'system.cpu.total.pct',
            'id': 'value_accessor',
        },
        'grid_config': {
            'cells': {
                'show_labels': True,
            },
            'x_axis': {
                'show_labels': True,
                'show_title': True,
            },
            'y_axis': {
                'show_labels': True,
                'show_title': True,
            },
        },
        'legend': {
            'visible': 'show',
            'position': 'left',
        },
    }

    result = compile_heatmap_chart_snapshot(config, 'lens')

    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'shape': 'heatmap',
            'xAccessor': 'x_accessor',
            'yAccessor': 'y_accessor',
            'valueAccessor': 'value_accessor',
            'gridConfig': {
                'type': 'heatmap_grid',
                'isCellLabelVisible': True,
                'isXAxisLabelVisible': True,
                'isXAxisTitleVisible': True,
                'isYAxisLabelVisible': True,
                'isYAxisTitleVisible': True,
            },
            'legend': {
                'type': 'heatmap_legend',
                'isVisible': True,
                'position': 'left',
            },
        }
    )


def test_compile_heatmap_chart_with_all_grid_options_esql() -> None:
    """Test the compilation of a heatmap chart with all grid configuration options (ESQL)."""
    config = {
        'type': 'heatmap',
        'x_axis': {
            'field': 'host_name',
            'id': 'x_accessor',
        },
        'y_axis': {
            'field': 'service_name',
            'id': 'y_accessor',
        },
        'value': {
            'field': 'avg_cpu',
            'id': 'value_accessor',
        },
        'grid_config': {
            'cells': {
                'show_labels': True,
            },
            'x_axis': {
                'show_labels': True,
                'show_title': True,
            },
            'y_axis': {
                'show_labels': True,
                'show_title': True,
            },
        },
        'legend': {
            'visible': 'hide',
            'position': 'top',
        },
    }

    result = compile_heatmap_chart_snapshot(config, 'esql')

    assert result == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'shape': 'heatmap',
            'xAccessor': 'x_accessor',
            'yAccessor': 'y_accessor',
            'valueAccessor': 'value_accessor',
            'gridConfig': {
                'type': 'heatmap_grid',
                'isCellLabelVisible': True,
                'isXAxisLabelVisible': True,
                'isXAxisTitleVisible': True,
                'isYAxisLabelVisible': True,
                'isYAxisTitleVisible': True,
            },
            'legend': {
                'type': 'heatmap_legend',
                'isVisible': False,
                'position': 'top',
            },
        }
    )


def test_compile_heatmap_chart_partial_grid_config() -> None:
    """Test the compilation of a heatmap chart with partial grid configuration."""
    config = {
        'type': 'heatmap',
        'data_view': 'metrics-*',
        'x_axis': {
            'type': 'values',
            'field': 'host.name',
            'id': 'x_accessor',
        },
        'value': {
            'aggregation': 'average',
            'field': 'system.cpu.total.pct',
            'id': 'value_accessor',
        },
        'grid_config': {
            'cells': {
                'show_labels': True,
            },
        },
    }

    result = compile_heatmap_chart_snapshot(config, 'lens')

    # Should fill in defaults for unspecified fields
    assert result['gridConfig']['isCellLabelVisible'] is True
    assert result['gridConfig']['isXAxisLabelVisible'] is False
    assert result['gridConfig']['isXAxisTitleVisible'] is False
    assert result['gridConfig']['isYAxisLabelVisible'] is False
    assert result['gridConfig']['isYAxisTitleVisible'] is False


def test_compile_heatmap_chart_partial_legend_config() -> None:
    """Test the compilation of a heatmap chart with partial legend configuration."""
    config = {
        'type': 'heatmap',
        'data_view': 'metrics-*',
        'x_axis': {
            'type': 'values',
            'field': 'host.name',
            'id': 'x_accessor',
        },
        'value': {
            'aggregation': 'average',
            'field': 'system.cpu.total.pct',
            'id': 'value_accessor',
        },
        'legend': {
            'visible': 'hide',
        },
    }

    result = compile_heatmap_chart_snapshot(config, 'lens')

    # Should fill in default position when only visibility is specified
    assert result['legend']['isVisible'] is False
    assert result['legend']['position'] == 'right'


def test_heatmap_chart_dashboard_references_bubble_up() -> None:
    """Test that heatmap chart data view references bubble up to dashboard level correctly.

    Heatmap charts reference a data view (index-pattern), so this reference should appear
    at the dashboard's top-level references array with proper panel namespacing.
    """
    dashboard = Dashboard(
        name='Test Heatmap Chart Dashboard',
        panels=[
            {
                'title': 'Heatmap',
                'id': 'heatmap-panel-1',
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 15},
                'lens': {
                    'type': 'heatmap',
                    'data_view': 'logs-*',
                    'x_axis': {
                        'type': 'values',
                        'field': 'host.name',
                        'id': 'x_accessor',
                    },
                    'value': {
                        'aggregation': 'count',
                        'id': 'value_accessor',
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
                'id': 'logs-*',
                'name': IsStr(regex=r'heatmap-panel-1:indexpattern-datasource-layer-[a-f0-9-]+'),
                'type': 'index-pattern',
            }
        ]
    )
