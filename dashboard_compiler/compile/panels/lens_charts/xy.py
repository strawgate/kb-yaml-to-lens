from dashboard_compiler.compile.utils import stable_id_generator
from dashboard_compiler.models.config.panels.lens_charts.xy import LensXYChart
from dashboard_compiler.models.views.panels.lens_chart.xy import (
    KbnXYVisualizationState,
    SeriesType,
    XYDataLayerConfig,
)


def safe_getattr(obj, attr, default=None):
    return getattr(obj, attr, default) if obj is not None else default


def return_none_if_empty_dict(initial_titles: dict):
    """
    Returns None if all values in the dictionary are None, otherwise returns the dictionary with non-None values.
    """
    if all(value is None for value in initial_titles.values()):
        return None
    else:
        return {k: v for k, v in initial_titles.items() if v is not None}


def compile_lens_xy_chart(
    chart: LensXYChart, dimension_ids: list[str], metric_ids: list[str], metrics_by_name: dict[str, str]
) -> KbnXYVisualizationState:  # Added metrics_by_name
    layer_id = chart.id or stable_id_generator([chart.type, chart.mode or "", *dimension_ids, *metric_ids])

    # Determine Kibana seriesType based on chart type and mode
    kbn_series_type: SeriesType  # Use SeriesType model
    if chart.type == "line":
        kbn_series_type = "line"  # Assuming SeriesType has a type fiel
    elif chart.type == "bar":
        if chart.mode == "unstacked":
            kbn_series_type = "bar"
        elif chart.mode == "percentage":
            kbn_series_type = "bar_percentage_stacked"
        else:  # stacked or None
            kbn_series_type = "bar_stacked"
    elif chart.type == "area":
        if chart.mode == "unstacked":
            kbn_series_type = "area"
        elif chart.mode == "percentage":
            kbn_series_type = "area_percentage_stacked"
        else:  # stacked or None
            kbn_series_type = "area_stacked"
    else:
        raise ValueError(f"Unsupported XY chart type: {chart.type}")

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

    # Map axis formatting
    axis_titles_visibility = return_none_if_empty_dict(
        {
            "x": chart.axis.bottom.title if chart.axis.bottom else None,
            "yLeft": chart.axis.left.title if chart.axis.left else None,
            "yRight": chart.axis.right.title if chart.axis.right else None,
        }
    )

    tick_labels_visibility = return_none_if_empty_dict(
        {
            "x": chart.axis.bottom.tick_labels if chart.axis.bottom else None,
            "yLeft": chart.axis.left.tick_labels if chart.axis.left else None,
            "yRight": chart.axis.right.tick_labels if chart.axis.right else None,
        }
    )

    gridlines_visibility = return_none_if_empty_dict(
        {
            "x": chart.axis.bottom.gridlines if chart.axis.bottom else None,
            "yLeft": chart.axis.left.gridlines if chart.axis.left else None,
            "yRight": chart.axis.right.gridlines if chart.axis.right else None,
        }
    )

    # Map orientation (assuming 0 for horizontal, 90 for vertical, 45 for rotated - adjust if needed)
    orientation_map = {"horizontal": 0, "vertical": 90, "rotated": 45}

    label_orientations = (
        return_none_if_empty_dict(
            {
                "x": chart.axis.bottom.orientation if chart.axis.bottom else None,
                "yLeft": chart.axis.left.orientation if chart.axis.left else None,
                "yRight": chart.axis.right.orientation if chart.axis.right else None,
            }
        )
        or {}
    )

    label_orientations = return_none_if_empty_dict({k: orientation_map.get(v, 0) for k, v in label_orientations.items()})

    # labels_orientation = LabelsOrientationConfig(
    #     x=orientation_map.get(chart.axis.bottom.orientation, 0) if chart.axis.bottom else 0,
    #     yLeft=orientation_map.get(chart.axis.left.orientation, 90) if chart.axis.left else 90,
    #     yRight=orientation_map.get(chart.axis.right.orientation, 0) if chart.axis.right else 0,
    # )

    # Map axis extents
    x_extent = return_none_if_empty_dict(
        {
            "min": chart.axis.bottom.min,
            "max": chart.axis.bottom.max,
        }
        if chart.axis.bottom
        else {}
    )

    y_left_extent = return_none_if_empty_dict({"min": chart.axis.left.min, "max": chart.axis.left.max} if chart.axis.left else {})
    y_right_extent = return_none_if_empty_dict({"min": chart.axis.right.min, "max": chart.axis.right.max} if chart.axis.right else {})

    kbn_state_visualization = KbnXYVisualizationState(
        preferredSeriesType=kbn_series_type,
        legend={  # Map legend formatting
            "isVisible": chart.legend.is_visible if chart.legend else True,  # Default to True
            "position": chart.legend.position if chart.legend else "right",  # Default to right
        },
        valueLabels=chart.appearance.value_labels if chart.appearance else "hide",  # Default to hide
        fittingFunction={"type": chart.appearance.fitting_function} if chart.appearance and chart.appearance.fitting_function else None,
        emphasizeFitting=chart.appearance.emphasize_fitting if chart.appearance else False,  # Default to False
        endValue=None,  # Not in config model, default to None
        xExtent=x_extent,  # Mapped from config
        yLeftExtent=y_left_extent,  # Mapped from config
        yRightExtent=y_right_extent,  # Mapped from config
        layers=[
            XYDataLayerConfig(  # Corrected model name
                layerId=layer_id,
                accessors=metric_ids,  # Metrics are accessors (Y-axis)
                xAccessor=dimension_ids[0] if dimension_ids else None,  # Assuming first dimension is x-axis
                position="top",  # Default based on sample
                seriesType=kbn_series_type,
                showGridlines=chart.axis.bottom.gridlines
                if chart.axis.bottom
                else True,  # Assuming bottom axis gridlines control layer gridlines, default to True
                layerType="data",  # Data layer
                colorMapping=None,  # Add color mapping compilation if needed
                splitAccessor=dimension_ids[1] if len(dimension_ids) > 1 else None,  # Assuming second dimension is split
                # yConfig=y_configs,  # Added yConfig
            )
        ],
        xTitle=chart.axis.bottom.title if chart.axis.bottom else None,
        yTitle=chart.axis.left.title if chart.axis.left else None,
        yRightTitle=chart.axis.right.title if chart.axis.right else None,
        yLeftScale={"type": chart.axis.left.scale} if chart.axis.left and chart.axis.left.scale else None,  # Default to linear
        yRightScale={"type": chart.axis.right.scale} if chart.axis.right and chart.axis.right.scale else None,  # Default to linear
        axisTitlesVisibilitySettings=axis_titles_visibility,
        tickLabelsVisibilitySettings=tick_labels_visibility,
        labelsOrientation=label_orientations,
        gridlinesVisibilitySettings=gridlines_visibility,
        showCurrentTimeMarker=chart.axis.bottom.show_current_time_marker if chart.axis.bottom else False,  # Default to False
        curveType={"type": chart.appearance.curve_type} if chart.appearance and chart.appearance.curve_type else None,
        fillOpacity=chart.appearance.fill_opacity if chart.appearance else None,
        minBarHeight=chart.appearance.min_bar_height if chart.appearance else None,
        hideEndzones=chart.appearance.hide_endzones if chart.appearance else None,
    )

    return kbn_state_visualization
