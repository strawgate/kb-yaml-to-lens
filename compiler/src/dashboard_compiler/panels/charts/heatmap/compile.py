"""Compilation logic for heatmap chart visualizations."""

from typing import TYPE_CHECKING

from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_dimension, compile_esql_metric
from dashboard_compiler.panels.charts.heatmap.view import (
    KbnHeatmapGridConfig,
    KbnHeatmapLegendConfig,
    KbnHeatmapVisualizationState,
)
from dashboard_compiler.panels.charts.lens.dimensions.compile import compile_lens_dimension
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.shared.config import get_layer_id
from dashboard_compiler.shared.defaults import default_false, default_true

if TYPE_CHECKING:
    from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
    from dashboard_compiler.panels.charts.heatmap.config import ESQLHeatmapChart, LensHeatmapChart
    from dashboard_compiler.panels.charts.lens.columns.view import KbnLensColumnTypes, KbnLensMetricColumnTypes


def compile_heatmap_chart_visualization_state(
    layer_id: str,
    x_accessor_id: str,
    value_accessor_id: str,
    chart: 'LensHeatmapChart | ESQLHeatmapChart',
    y_accessor_id: str | None = None,
) -> KbnHeatmapVisualizationState:
    """Compile a heatmap chart config object into a Kibana Lens Heatmap visualization state.

    Args:
        layer_id (str): The ID of the layer.
        x_accessor_id (str): The ID of the X-axis dimension.
        value_accessor_id (str): The ID of the value metric.
        chart (LensHeatmapChart | ESQLHeatmapChart): The heatmap chart config object.
        y_accessor_id (str | None): The ID of the Y-axis dimension.

    Returns:
        KbnHeatmapVisualizationState: The compiled visualization state.

    """
    # Compile grid configuration (always present, use defaults if not provided)
    if chart.grid_config is not None:
        gc = chart.grid_config
        grid_config = KbnHeatmapGridConfig(
            isCellLabelVisible=default_false(gc.is_cell_label_visible),
            isXAxisLabelVisible=default_false(gc.is_x_axis_label_visible),
            isXAxisTitleVisible=default_false(gc.is_x_axis_title_visible),
            isYAxisLabelVisible=default_false(gc.is_y_axis_label_visible),
            isYAxisTitleVisible=default_false(gc.is_y_axis_title_visible),
        )
    else:
        grid_config = KbnHeatmapGridConfig()

    # Compile legend configuration (always present, use defaults if not provided)
    if chart.legend is not None:
        legend = KbnHeatmapLegendConfig(
            isVisible=default_true(chart.legend.is_visible),
            position=chart.legend.position if chart.legend.position is not None else 'right',
        )
    else:
        legend = KbnHeatmapLegendConfig()

    return KbnHeatmapVisualizationState(
        layerId=layer_id,
        xAccessor=x_accessor_id,
        yAccessor=y_accessor_id,
        valueAccessor=value_accessor_id,
        gridConfig=grid_config,
        legend=legend,
    )


def compile_lens_heatmap_chart(
    lens_heatmap_chart: 'LensHeatmapChart',
) -> 'tuple[str, dict[str, KbnLensColumnTypes], KbnHeatmapVisualizationState]':
    """Compile a LensHeatmapChart config object into a Kibana Lens Heatmap visualization state.

    Args:
        lens_heatmap_chart (LensHeatmapChart): The LensHeatmapChart object to compile.

    Returns:
        tuple[str, dict[str, KbnLensColumnTypes], KbnHeatmapVisualizationState]: A tuple containing:
            - layer_id (str): The ID of the layer.
            - kbn_columns (dict[str, KbnLensColumnTypes]): A dictionary of columns for the layer.
            - kbn_state_visualization (KbnHeatmapVisualizationState): The compiled visualization state.

    """
    kbn_columns_by_id: 'dict[str, KbnLensColumnTypes]' = {}  # noqa: UP037

    # Compile value metric first (dimensions may reference it)
    value_id, value_column = compile_lens_metric(lens_heatmap_chart.value)
    kbn_metric_columns_by_id: 'dict[str, KbnLensMetricColumnTypes]' = {value_id: value_column}  # noqa: UP037

    # Compile X-axis dimension (required)
    x_id, x_column = compile_lens_dimension(
        lens_heatmap_chart.x_axis,
        kbn_metric_column_by_id=kbn_metric_columns_by_id,
    )
    kbn_columns_by_id[x_id] = x_column

    # Compile Y-axis dimension (optional)
    y_id: str | None = None
    if lens_heatmap_chart.y_axis is not None:
        y_id, y_column = compile_lens_dimension(
            lens_heatmap_chart.y_axis,
            kbn_metric_column_by_id=kbn_metric_columns_by_id,
        )
        kbn_columns_by_id[y_id] = y_column

    # Add value metric to columns
    kbn_columns_by_id[value_id] = value_column

    layer_id = get_layer_id(lens_heatmap_chart)

    return (
        layer_id,
        kbn_columns_by_id,
        compile_heatmap_chart_visualization_state(
            layer_id=layer_id,
            x_accessor_id=x_id,
            value_accessor_id=value_id,
            chart=lens_heatmap_chart,
            y_accessor_id=y_id,
        ),
    )


def compile_esql_heatmap_chart(
    esql_heatmap_chart: 'ESQLHeatmapChart',
) -> 'tuple[str, list[KbnESQLColumnTypes], KbnHeatmapVisualizationState]':
    """Compile an ESQL HeatmapChart config object into a Kibana Lens Heatmap visualization state.

    Args:
        esql_heatmap_chart (ESQLHeatmapChart): The ESQLHeatmapChart object to compile.

    Returns:
        tuple[str, list[KbnESQLColumnTypes], KbnHeatmapVisualizationState]: A tuple containing:
            - layer_id (str): The ID of the layer.
            - kbn_columns (list[KbnESQLColumnTypes]): A list of columns for the layer.
            - kbn_state_visualization (KbnHeatmapVisualizationState): The compiled visualization state.

    """
    layer_id = get_layer_id(esql_heatmap_chart)

    kbn_columns: 'list[KbnESQLColumnTypes]' = []  # noqa: UP037

    # Compile X-axis dimension (required)
    x_column = compile_esql_dimension(esql_heatmap_chart.x_axis)
    x_id = x_column.columnId
    kbn_columns.append(x_column)

    # Compile Y-axis dimension (optional)
    y_id: str | None = None
    if esql_heatmap_chart.y_axis is not None:
        y_column = compile_esql_dimension(esql_heatmap_chart.y_axis)
        y_id = y_column.columnId
        kbn_columns.append(y_column)

    # Compile value metric (required)
    value_column = compile_esql_metric(esql_heatmap_chart.value)
    value_id = value_column.columnId
    kbn_columns.append(value_column)

    return (
        layer_id,
        kbn_columns,
        compile_heatmap_chart_visualization_state(
            layer_id=layer_id,
            x_accessor_id=x_id,
            value_accessor_id=value_id,
            chart=esql_heatmap_chart,
            y_accessor_id=y_id,
        ),
    )
