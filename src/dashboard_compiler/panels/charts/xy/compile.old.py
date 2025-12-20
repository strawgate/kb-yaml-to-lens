from typing import Any

from dashboard_compiler.panels.charts.columns.compile import compile_dimensions
from dashboard_compiler.panels.charts.metrics.compile import compile_lens_metrics
from dashboard_compiler.panels.lens.charts.xy.config import LensXYChart, XYChart
from dashboard_compiler.panels.lens.charts.xy.view import (
    KbnXYVisualizationState,
    SeriesTypeEnum,
    XYDataLayerConfig,
)
from dashboard_compiler.shared.config import stable_id_generator

ORIENTATION_MAP = {
    'horizontal': 0,
    'vertical': 90,
    'rotated': 45,
}


def bar_chart_to_series_type(mode: str | None = None) -> SeriesTypeEnum:
    """Convert Lens bar chart type and mode to Kibana SeriesType.

    Args:
        mode (str | None): The mode of the bar chart (e.g., 'unstacked', 'percentage', 'stacked').

    Returns:
        SeriesTypeEnum: The corresponding Kibana SeriesType.
    """
    if mode == 'unstacked':
        return SeriesTypeEnum.bar
    if mode == 'percentage':
        return SeriesTypeEnum.bar_percentage_stacked
    if mode in {None, 'stacked'}:
        return SeriesTypeEnum.bar_stacked

    msg = f'Unsupported bar chart mode: {mode}'
    raise NotImplementedError(msg)


def area_chart_to_series_type(mode: str | None = None) -> SeriesTypeEnum:
    """Convert Lens area chart type and mode to Kibana SeriesType.

    Args:
        mode (str | None): The mode of the area chart (e.g., 'unstacked', 'percentage', 'stacked').

    Returns:
        SeriesTypeEnum: The corresponding Kibana SeriesType.
    """
    if mode == 'unstacked':
        return SeriesTypeEnum.area
    if mode == 'percentage':
        return SeriesTypeEnum.area_percentage_stacked
    if mode in {None, 'stacked'}:
        return SeriesTypeEnum.area_stacked

    msg = f'Unsupported area chart with mode: {mode}'
    raise NotImplementedError(msg)


def chart_to_series_type(chart_type: str, mode: str | None = None) -> SeriesTypeEnum:
    """Convert Lens chart type and mode to Kibana SeriesType.

    Args:
        chart_type (str): The type of the chart (e.g., 'line', 'bar', 'area').
        mode (str | None): The mode of the chart (e.g., 'unstacked', 'percentage', 'stacked').

    Returns:
        SeriesTypeEnum: The corresponding Kibana SeriesType.
    """
    if chart_type == 'line':
        return SeriesTypeEnum.line

    if chart_type == 'bar':
        return bar_chart_to_series_type(mode=mode)
    if chart_type == 'area':
        return area_chart_to_series_type(mode=mode)

    msg = f'Unsupported chart type: {chart_type} with mode: {mode}'
    raise NotImplementedError(msg)


def axis_titles_visibility_from_chart(chart: XYChart) -> dict[str, Any] | None:
    """Extract axis titles visibility settings from the chart configuration.

    Args:
        chart (XYChart): The chart configuration object.

    Returns:
        dict[str, Any] | None: A dictionary with axis visibility settings or None if no titles are set.
    """
    visibility = {}

    if chart.axis.bottom and chart.axis.bottom.title:
        visibility['x'] = chart.axis.bottom.title

    if chart.axis.left and chart.axis.left.title:
        visibility['yLeft'] = chart.axis.left.title

    if chart.axis.right and chart.axis.right.title:
        visibility['yRight'] = chart.axis.right.title

    return visibility if visibility else None


def tick_labels_visibility_from_chart(chart: XYChart) -> dict[str, Any] | None:
    """Extract tick labels visibility settings from the chart configuration.

    Args:
        chart (XYChart): The chart configuration object.

    Returns:
        dict[str, Any] | None: A dictionary with tick labels visibility settings or None if no labels are set.
    """
    visibility = {}

    if chart.axis.bottom and chart.axis.bottom.tick_labels:
        visibility['x'] = chart.axis.bottom.tick_labels

    if chart.axis.left and chart.axis.left.tick_labels:
        visibility['yLeft'] = chart.axis.left.tick_labels

    if chart.axis.right and chart.axis.right.tick_labels:
        visibility['yRight'] = chart.axis.right.tick_labels

    return visibility if visibility else None


def gridlines_visibility_from_chart(chart: XYChart) -> dict[str, Any] | None:
    """Extract gridlines visibility settings from the chart configuration.

    Args:
        chart (XYChart): The chart configuration object.

    Returns:
        dict[str, Any] | None: A dictionary with gridlines visibility settings or None if no gridlines are set.
    """
    visibility = {}

    if chart.axis.bottom and chart.axis.bottom.gridlines:
        visibility['x'] = chart.axis.bottom.gridlines

    if chart.axis.left and chart.axis.left.gridlines:
        visibility['yLeft'] = chart.axis.left.gridlines

    if chart.axis.right and chart.axis.right.gridlines:
        visibility['yRight'] = chart.axis.right.gridlines

    return visibility if visibility else None


def labels_orientation_from_chart(chart: XYChart) -> dict[str, Any] | None:
    """Extract label orientations from the chart configuration.

    Args:
        chart (XYChart): The chart configuration object.

    Returns:
        dict[str, Any] | None: A dictionary with label orientations or None if no orientations are set.
    """
    orientations = {}
    if chart.axis.bottom and chart.axis.bottom.orientation:
        orientations['x'] = ORIENTATION_MAP.get(chart.axis.bottom.orientation, 0)
    if chart.axis.left and chart.axis.left.orientation:
        orientations['yLeft'] = ORIENTATION_MAP.get(chart.axis.left.orientation, 90)
    if chart.axis.right and chart.axis.right.orientation:
        orientations['yRight'] = ORIENTATION_MAP.get(chart.axis.right.orientation, 0)
    return orientations if orientations else None


def bottom_axis_from_chart(chart: XYChart) -> dict[str, Any] | None:
    """Extract x-axis extent from the chart configuration.

    Args:
        chart (XYChart): The chart configuration object.

    Returns:
        dict[str, Any] | None: A dictionary with x-axis extent or None if no extent is set.
    """
    if chart.axis.bottom:
        return {
            'min': chart.axis.bottom.min,
            'max': chart.axis.bottom.max,
        }
    return None


def left_axis_from_chart(chart: XYChart) -> dict[str, Any] | None:
    """Extract y-axis extent from the chart configuration for the specified axis.

    Args:
        chart (XYChart): The chart configuration object.

    Returns:
        dict[str, Any] | None: A dictionary with y-axis extent or None if no extent is set.
    """
    if chart.axis.left:
        return {
            'min': chart.axis.left.min,
            'max': chart.axis.left.max,
        }

    return None


def right_axis_from_chart(chart: XYChart) -> dict[str, Any] | None:
    """Extract right y-axis extent from the chart configuration.

    Args:
        chart (XYChart): The chart configuration object.

    Returns:
        dict[str, Any] | None: A dictionary with right y-axis extent or None if no extent is set.
    """
    if chart.axis.right:
        return {
            'min': chart.axis.right.min,
            'max': chart.axis.right.max,
        }
    return None


def legend_from_chart(chart: XYChart) -> dict[str, Any] | None:
    """Extract legend settings from the chart configuration.

    Args:
        chart (XYChart): The chart configuration object.

    Returns:
        dict[str, Any] | None: A dictionary with legend settings or None if no legend is set.
    """
    if chart.legend:
        return {
            'isVisible': chart.legend.is_visible,
            'position': chart.legend.position,
        }
    return None

    # Compile yConfig for metrics
    # y_configs: list[YConfig] = []
    # for metric in chart.metrics:
    #     metric_id = metrics_by_name.get(metric.label)  # Get the generated ID for the metric
    #     if metric_id:
    #         # Determine axis mode based on whether a right axis is defined and if the metric should use it
    #         axis_mode_name = "left"
    #         if chart.axis.right and metric.label in [m.label for m in chart.axis.right.metrics]:  # Assuming metrics in right axis config
    #             axis_mode_name = "right"

    #         y_configs.append(YConfig(forAccessor=metric_id, axisMode=YAxisMode(name=axis_mode_name)))


def compile_lens_xy_chart(
    chart: LensXYChart,
    dimension_ids: list[str],
    metric_ids: list[str],
    metrics_by_name: dict[str, str],
) -> KbnXYVisualizationState:
    """Compile a Lens XY chart into a Kibana visualization state.

    Args:
        chart (LensXYChart): The Lens XY chart configuration.
        dimension_ids (list[str]): List of dimension IDs.
        metric_ids (list[str]): List of metric IDs.
        metrics_by_name (dict[str, str]): Mapping of metric names to their generated IDs.

    Returns:
        KbnXYVisualizationState: The compiled Kibana visualization state.
    """
    layer_id = chart.id or stable_id_generator([chart.type, chart.mode or '', *dimension_ids, *metric_ids])

    metrics_by_id, metrics_by_name = compile_lens_metrics(chart.metrics)
    split_by_by_id = compile_dimensions(chart.split_by, metrics_by_name)

    kbn_series_type: SeriesTypeEnum = chart_to_series_type(chart.type, chart.mode)

    axis_titles_visibility = axis_titles_visibility_from_chart(chart)
    tick_labels_visibility = tick_labels_visibility_from_chart(chart)
    gridlines_visibility = gridlines_visibility_from_chart(chart)

    label_orientations = labels_orientation_from_chart(chart)

    bottom_axis = bottom_axis_from_chart(chart)
    left_axis = left_axis_from_chart(chart)
    right_axis = right_axis_from_chart(chart)

    legend = legend_from_chart(chart)

    value_labels = chart.appearance.value_labels if chart.appearance else None
    fitting_function = chart.appearance.fitting_function if chart.appearance else None
    emphasize_fitting = chart.appearance.emphasize_fitting if chart.appearance else False  # Default to False

    xy_data_layer = XYDataLayerConfig(  # Corrected model name
        layerId=layer_id,
        accessors=metric_ids,  # Metrics are accessors (Y-axis)
        xAccessor=dimension_ids[0] if dimension_ids else None,  # Assuming first dimension is x-axis
        position='top',  # Default based on sample
        seriesType=kbn_series_type,
        showGridlines=chart.axis.bottom.gridlines
        if chart.axis.bottom
        else True,  # Assuming bottom axis gridlines control layer gridlines, default to True
        layerType='data',  # Data layer
        colorMapping=None,  # Add color mapping compilation if needed
        splitAccessor=dimension_ids[1] if len(dimension_ids) > 1 else None,
    )

    kbn_state_visualization = KbnXYVisualizationState(
        preferredSeriesType=kbn_series_type,
        legend=legend,
        valueLabels=value_labels,
        fittingFunction=fitting_function,
        emphasizeFitting=emphasize_fitting,
        endValue=None,  # Not in config model, default to None
        xExtent=bottom_axis,  # Mapped from config
        yLeftExtent=left_axis,  # Mapped from config
        yRightExtent=right_axis,  # Mapped from config
        layers=[
            XYDataLayerConfig(  # Corrected model name
                layerId=layer_id,
                accessors=metric_ids,  # Metrics are accessors (Y-axis)
                xAccessor=dimension_ids[0] if dimension_ids else None,  # Assuming first dimension is x-axis
                position='top',  # Default based on sample
                seriesType=kbn_series_type,
                showGridlines=chart.axis.bottom.gridlines
                if chart.axis.bottom
                else True,  # Assuming bottom axis gridlines control layer gridlines, default to True
                layerType='data',  # Data layer
                colorMapping=None,  # Add color mapping compilation if needed
                splitAccessor=dimension_ids[1] if len(dimension_ids) > 1 else None,  # Assuming second dimension is split
                # yConfig=y_configs,  # Added yConfig
            ),
        ],
        xTitle=chart.axis.bottom.title if chart.axis.bottom else None,
        yTitle=chart.axis.left.title if chart.axis.left else None,
        yRightTitle=chart.axis.right.title if chart.axis.right else None,
        yLeftScale={'type': chart.axis.left.scale} if chart.axis.left and chart.axis.left.scale else None,  # Default to linear
        yRightScale={'type': chart.axis.right.scale} if chart.axis.right and chart.axis.right.scale else None,  # Default to linear
        axisTitlesVisibilitySettings=axis_titles_visibility,
        tickLabelsVisibilitySettings=tick_labels_visibility,
        labelsOrientation=label_orientations,
        gridlinesVisibilitySettings=gridlines_visibility,
        showCurrentTimeMarker=chart.axis.bottom.show_current_time_marker if chart.axis.bottom else False,  # Default to False
        curveType={'type': chart.appearance.curve_type} if chart.appearance and chart.appearance.curve_type else None,
        fillOpacity=chart.appearance.fill_opacity if chart.appearance else None,
        minBarHeight=chart.appearance.min_bar_height if chart.appearance else None,
        hideEndzones=chart.appearance.hide_endzones if chart.appearance else None,
    )

    return kbn_state_visualization
