"""Compilation logic for heatmap chart visualizations."""

from typing import TYPE_CHECKING

from kb_dashboard_core.panels.charts.base.compile import compile_color_range_mapping, map_legend_size
from kb_dashboard_core.panels.charts.base.config import LegendVisibleEnum
from kb_dashboard_core.panels.charts.esql.columns.compile import compile_esql_dimension, compile_esql_metric
from kb_dashboard_core.panels.charts.heatmap.view import (
    KbnHeatmapGridConfig,
    KbnHeatmapLegendConfig,
    KbnHeatmapVisualizationState,
)
from kb_dashboard_core.panels.charts.lens.dimensions.compile import compile_lens_dimension
from kb_dashboard_core.panels.charts.lens.metrics.compile import compile_lens_metric
from kb_dashboard_core.shared.defaults import default_false

if TYPE_CHECKING:
    from kb_dashboard_core.panels.charts.esql.columns.view import KbnESQLColumnTypes
    from kb_dashboard_core.panels.charts.heatmap.config import ESQLHeatmapChart, LensHeatmapChart
    from kb_dashboard_core.panels.charts.lens.columns.view import KbnLensColumnTypes, KbnLensMetricColumnTypes


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
    if chart.appearance is not None:
        appearance = chart.appearance
        cell_labels = default_false(appearance.values.visible) if appearance.values is not None else False
        x_axis_labels = (
            default_false(appearance.x_axis.labels.visible)
            if appearance.x_axis is not None and appearance.x_axis.labels is not None
            else False
        )
        x_axis_title = (
            default_false(appearance.x_axis.title.visible)
            if appearance.x_axis is not None and appearance.x_axis.title is not None
            else False
        )
        y_axis_labels = (
            default_false(appearance.y_axis.labels.visible)
            if appearance.y_axis is not None and appearance.y_axis.labels is not None
            else False
        )
        y_axis_title = (
            default_false(appearance.y_axis.title.visible)
            if appearance.y_axis is not None and appearance.y_axis.title is not None
            else False
        )
    else:
        cell_labels = False
        x_axis_labels = False
        x_axis_title = False
        y_axis_labels = False
        y_axis_title = False

    grid_config = KbnHeatmapGridConfig(
        isCellLabelVisible=cell_labels,
        isXAxisLabelVisible=x_axis_labels,
        isXAxisTitleVisible=x_axis_title,
        isYAxisLabelVisible=y_axis_labels,
        isYAxisTitleVisible=y_axis_title,
    )

    # Compile legend configuration (always present, use defaults if not provided)
    legend_size = None
    if chart.appearance is not None and chart.appearance.legend is not None:
        # Map enum values: 'show' -> True, 'hide' -> False, None -> True (Kibana default)
        legend_visible = chart.appearance.legend.visible != LegendVisibleEnum.HIDE if chart.appearance.legend.visible is not None else True
        legend_size = map_legend_size(chart.appearance.legend.width)

        legend = KbnHeatmapLegendConfig(
            isVisible=legend_visible,
            position=chart.appearance.legend.position if chart.appearance.legend.position is not None else 'right',
        )
    else:
        legend = KbnHeatmapLegendConfig()

    palette = compile_color_range_mapping(chart.color)

    return KbnHeatmapVisualizationState(
        layerId=layer_id,
        xAccessor=x_accessor_id,
        yAccessor=y_accessor_id,
        valueAccessor=value_accessor_id,
        gridConfig=grid_config,
        legend=legend,
        legendSize=legend_size,
        palette=palette,
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
    result = compile_lens_metric(lens_heatmap_chart.value)
    value_id = result.primary_id
    value_column = result.primary_column
    kbn_metric_columns_by_id: 'dict[str, KbnLensMetricColumnTypes]' = {value_id: value_column}  # noqa: UP037
    kbn_metric_columns_by_id.update(result.helper_columns)

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

    # Add all metric columns (including helper columns) to the datasource layer
    kbn_columns_by_id.update(kbn_metric_columns_by_id)

    layer_id = lens_heatmap_chart.get_id()

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
    layer_id = esql_heatmap_chart.get_id()

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
