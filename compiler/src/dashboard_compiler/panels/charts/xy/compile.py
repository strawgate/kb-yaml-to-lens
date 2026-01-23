"""Compile Lens XY visualizations into their Kibana view models."""

from typing import Literal

from dashboard_compiler.panels.charts.base.compile import compile_color_mapping
from dashboard_compiler.panels.charts.base.config import LegendVisibleEnum
from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_dimensions, compile_esql_metrics
from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnLensColumnTypes,
    KbnLensDimensionColumnTypes,
    KbnLensMetricColumnTypes,
    KbnLensStaticValueColumn,
    KbnLensStaticValueColumnParams,
)
from dashboard_compiler.panels.charts.lens.dimensions.compile import compile_lens_dimensions
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.xy.config import (
    AreaChartAppearance,
    AxisConfig,
    AxisExtent,
    BarChartAppearance,
    ESQLAreaChart,
    ESQLBarChart,
    ESQLLineChart,
    ESQLXYChartTypes,
    LensAreaChart,
    LensBarChart,
    LensLineChart,
    LensReferenceLineLayer,
    LensXYChartTypes,
    LineChartAppearance,
    XYReferenceLine,
    XYReferenceLineValue,
)
from dashboard_compiler.panels.charts.xy.view import (
    AxisExtentConfig,
    AxisTitlesVisibilitySettings,
    KbnXYVisualizationState,
    XYDataLayerConfig,
    XYLegendConfig,
    XYReferenceLineLayerConfig,
    YConfig,
)


def _convert_axis_extent(extent: AxisExtent) -> AxisExtentConfig:
    """Convert config AxisExtent to view AxisExtentConfig.

    Transforms snake_case 'data_bounds' to camelCase 'dataBounds' for Kibana.

    Args:
        extent: The axis extent configuration from the user config.

    Returns:
        AxisExtentConfig for Kibana visualization state.
    """
    return AxisExtentConfig(
        mode='dataBounds' if extent.mode == 'data_bounds' else extent.mode,
        lowerBound=extent.min,
        upperBound=extent.max,
        enforce=extent.enforce,
        niceValues=extent.nice_values,
    )


def _extract_axis_config(
    axis_config: AxisConfig | None,
) -> tuple[str | None, Literal['linear', 'log', 'sqrt', 'time'] | None, AxisExtentConfig | None]:
    """Extract axis configuration (title, scale, extent) from an AxisConfig.

    Args:
        axis_config: The axis configuration object (or None).

    Returns:
        Tuple of (title, scale, extent) where each can be None.
    """
    if axis_config is None:
        return None, None, None

    title = axis_config.title
    scale = axis_config.scale
    extent = _convert_axis_extent(axis_config.extent) if axis_config.extent is not None else None

    return title, scale, extent


def compile_lens_reference_line_layer(
    layer: 'LensReferenceLineLayer',
) -> tuple[str, dict[str, KbnLensStaticValueColumn], list[XYReferenceLineLayerConfig]]:
    """Compile a LensReferenceLineLayer into a Kibana reference line layer and columns.

    Args:
        layer: The reference line layer configuration.

    Returns:
        tuple[str, dict[str, KbnLensStaticValueColumn], list[XYReferenceLineLayerConfig]]:
            - layer_id: The primary layer ID (used for data view reference and visualization layer)
            - columns: Dictionary of accessor ID -> static value column
            - ref_layers: List containing a single XYReferenceLineLayerConfig with all reference lines
    """
    primary_layer_id = layer.get_id()

    reference_line_columns: dict[str, KbnLensStaticValueColumn] = {}
    accessor_ids: list[str] = []
    y_configs: list[YConfig] = []

    for ref_line in layer.reference_lines:
        # Compile each reference line into an accessor and column
        accessor_id, ref_column, y_config = compile_reference_line(ref_line)
        reference_line_columns[accessor_id] = ref_column
        accessor_ids.append(accessor_id)
        y_configs.append(y_config)

    # Create a single XYReferenceLineLayerConfig with all accessors
    reference_line_layer = XYReferenceLineLayerConfig(
        layerId=primary_layer_id,
        accessors=accessor_ids,
        yConfig=y_configs,
        layerType='referenceLine',
    )

    return primary_layer_id, reference_line_columns, [reference_line_layer]


def compile_reference_line(ref_line: XYReferenceLine) -> tuple[str, KbnLensStaticValueColumn, YConfig]:
    """Compile a reference line into an accessor ID, static value column, and Y config.

    Args:
        ref_line: The reference line configuration.

    Returns:
        tuple[str, KbnLensStaticValueColumn, YConfig]: The accessor ID, static value column, and Y config.
    """
    # Extract the numeric value from the ref_line.value field
    if isinstance(ref_line.value, float):
        numeric_value = ref_line.value
    elif isinstance(ref_line.value, XYReferenceLineValue):
        numeric_value = ref_line.value.value
    else:
        # This should never happen due to Pydantic validation
        msg = f'Invalid value type: {type(ref_line.value)}'
        raise TypeError(msg)

    accessor_id = ref_line.get_id()

    # Create the static value column for the reference line
    static_value_column = KbnLensStaticValueColumn(
        label=ref_line.label if ref_line.label is not None else f'Static value: {numeric_value}',
        dataType='number',
        operationType='static_value',
        isBucketed=False,
        isStaticValue=True,
        scale='ratio',
        params=KbnLensStaticValueColumnParams(value=str(numeric_value)),
        references=[],
        customLabel=ref_line.label is not None,
    )

    # Build yConfig for styling
    y_config = YConfig(
        forAccessor=accessor_id,
        color=ref_line.color,
        lineWidth=ref_line.line_width,
        lineStyle=ref_line.line_style,
        fill=ref_line.fill,
        icon=ref_line.icon,
        iconPosition=ref_line.icon_position,
        axisMode=ref_line.axis,
    )

    return accessor_id, static_value_column, y_config


def _map_curve_type_to_kibana(curve_type: str | None) -> str | None:
    """Map user-friendly curve type values to Kibana's expected format.

    Kibana supports only 3 curve types as defined in:
    x-pack/plugins/lens/public/visualizations/xy/xy_config_panel/visual_options_popover/curve_styles.tsx

    - LINEAR: Straight line segments between points
    - CURVE_MONOTONE_X: Smooth curve that preserves monotonicity
    - CURVE_STEP_AFTER: Step function with horizontal segment after each point

    Args:
        curve_type: The curve type from config ('linear', 'monotone-x', or 'step-after').

    Returns:
        The Kibana-formatted curve type constant or None.
    """
    if curve_type is None:
        return None

    # Mapping from config values to Kibana constants
    # Only the 3 curve types supported by Kibana are included
    curve_type_mapping = {
        'linear': 'LINEAR',
        'monotone-x': 'CURVE_MONOTONE_X',
        'step-after': 'CURVE_STEP_AFTER',
    }

    return curve_type_mapping.get(curve_type, curve_type)


def _extract_chart_type_specific_appearance(
    chart: LensXYChartTypes | ESQLXYChartTypes,
) -> tuple[
    str | None,  # fitting_function
    bool | None,  # emphasize_fitting
    str | None,  # end_value
    str | None,  # curve_type
    float | None,  # fill_opacity
    float | None,  # min_bar_height
    bool | None,  # show_current_time_marker
    bool | None,  # hide_endzones
]:
    """Extract chart-type-specific appearance properties.

    Args:
        chart: The XY chart configuration.

    Returns:
        Tuple of (fitting_function, emphasize_fitting, end_value, curve_type, fill_opacity,
                 min_bar_height, show_current_time_marker, hide_endzones).
    """
    fitting_function = None
    emphasize_fitting = None
    end_value = None
    curve_type = None
    fill_opacity = None
    min_bar_height = None
    show_current_time_marker = None
    hide_endzones = None

    # Extract line/area chart appearance
    if chart.appearance is not None and isinstance(chart.appearance, (LineChartAppearance, AreaChartAppearance)):
        fitting_function = chart.appearance.missing_values
        emphasize_fitting = chart.appearance.show_as_dotted
        end_value = chart.appearance.end_values
        curve_type = _map_curve_type_to_kibana(chart.appearance.line_style)

        if isinstance(chart.appearance, AreaChartAppearance):
            fill_opacity = chart.appearance.fill_opacity

    # Extract bar chart appearance
    if chart.appearance is not None and isinstance(chart.appearance, BarChartAppearance):
        min_bar_height = chart.appearance.min_bar_height

    # Extract time series features from line/area charts
    if isinstance(chart, (LensLineChart, LensAreaChart, ESQLLineChart, ESQLAreaChart)):
        show_current_time_marker = chart.show_current_time_marker
        hide_endzones = chart.hide_endzones

    return (
        fitting_function,
        emphasize_fitting,
        end_value,
        curve_type,
        fill_opacity,
        min_bar_height,
        show_current_time_marker,
        hide_endzones,
    )


def _compile_legend_config(chart: LensXYChartTypes | ESQLXYChartTypes) -> XYLegendConfig:
    """Compile legend configuration from chart config.

    Args:
        chart: The XY chart configuration.

    Returns:
        XYLegendConfig: The compiled legend configuration.
    """
    legend_visible = None  # Default to None (omit field, let Kibana decide)
    legend_position = 'right'
    legend_show_single_series = None
    legend_size = None
    legend_should_truncate = None
    legend_max_lines = None

    if chart.legend is not None:
        if chart.legend.visible is not None:
            match chart.legend.visible:
                case LegendVisibleEnum.SHOW:
                    legend_visible = True
                case LegendVisibleEnum.HIDE:
                    legend_visible = False
                case LegendVisibleEnum.AUTO:
                    legend_visible = None  # Omit field, let Kibana decide based on series count
                case _:  # pyright: ignore[reportUnnecessaryComparison]
                    # This should never happen due to Pydantic enum validation, but we handle it defensively
                    msg = f'Unknown legend visibility value: {chart.legend.visible}'
                    raise ValueError(msg)  # pyright: ignore[reportUnreachable]
        if chart.legend.position is not None:
            legend_position = chart.legend.position
        if chart.legend.show_single_series is not None:
            legend_show_single_series = chart.legend.show_single_series
        if chart.legend.size is not None:
            legend_size = chart.legend.size
        if chart.legend.truncate_labels is not None:
            if chart.legend.truncate_labels == 0:
                legend_should_truncate = False
            else:
                legend_should_truncate = True
                legend_max_lines = chart.legend.truncate_labels

    return XYLegendConfig(
        isVisible=legend_visible,
        position=legend_position,
        showSingleSeries=legend_show_single_series,
        legendSize=legend_size,
        shouldTruncate=legend_should_truncate,
        maxLines=legend_max_lines,
    )


def compile_series_type(chart: LensXYChartTypes | ESQLXYChartTypes) -> str:
    """Determine the Kibana series type based on the chart configuration.

    Maps chart config types and modes to Kibana's specific seriesType strings.
    Kibana distinguishes between:
    - Basic types: 'line', 'bar_stacked', 'area' (default/stacked mode)
    - Unstacked variants: 'bar_unstacked', 'area_unstacked'
    - Percentage variants: 'bar_percentage_stacked', 'area_percentage_stacked'
    The exact string values must match Kibana's XY visualization registry.

    Args:
        chart: The XY chart configuration (Lens or ESQL).

    Returns:
        The Kibana series type string (e.g., 'line', 'bar_stacked', 'area').
    """
    if isinstance(chart, LensLineChart | ESQLLineChart):
        series_type = 'line'
    elif isinstance(chart, LensBarChart | ESQLBarChart):
        if chart.mode == 'unstacked':
            series_type = 'bar_unstacked'
        elif chart.mode == 'stacked':
            series_type = 'bar_stacked'
        elif chart.mode == 'percentage':
            series_type = 'bar_percentage_stacked'
        else:  # default to stacked
            series_type = 'bar_stacked'
    # This check is necessary even though it appears redundant to type checkers
    elif isinstance(chart, (LensAreaChart, ESQLAreaChart)):  # pyright: ignore[reportUnnecessaryIsInstance]
        if chart.mode == 'unstacked':
            series_type = 'area_unstacked'
        elif chart.mode == 'stacked':
            series_type = 'area'
        elif chart.mode == 'percentage':
            series_type = 'area_percentage_stacked'
        else:  # default to stacked
            series_type = 'area'
    else:
        # Defensive programming: ensure runtime type safety
        msg = f'Unsupported chart type: {type(chart).__name__}'  # pyright: ignore[reportUnreachable]
        raise TypeError(msg)

    return series_type


def compile_xy_chart_visualization_state(
    *,
    layer_id: str,
    chart: LensXYChartTypes | ESQLXYChartTypes,
    dimension_id: str | None,
    metric_ids: list[str],
    breakdown_id: str | None = None,
) -> KbnXYVisualizationState:
    """Compile an XY chart config object into a Kibana XY visualization state.

    Args:
        layer_id (str): The ID of the layer.
        chart (LensXYChartTypes | ESQLXYChartTypes): The XY chart config object.
        dimension_id (str | None): The ID of the X-axis dimension.
        metric_ids (list[str]): The IDs of the metrics.
        breakdown_id (str | None): The ID of the breakdown dimension if any.

    Returns:
        KbnXYVisualizationState: The compiled visualization state.
    """
    series_type: str = compile_series_type(chart=chart)

    kbn_color_mapping = compile_color_mapping(chart.color)

    # Build yConfig from metric appearance properties
    y_config: list[YConfig] | None = None
    y_config_list: list[YConfig] = []

    for metric_id, metric in zip(metric_ids, chart.metrics, strict=True):
        if metric.axis is not None or metric.color is not None:
            y_config_list.append(
                YConfig(
                    forAccessor=metric_id,
                    axisMode=metric.axis,
                    color=metric.color,
                )
            )

    y_config = y_config_list if len(y_config_list) > 0 else None

    # Build axis configuration from appearance settings
    x_title = None
    x_scale = None
    y_left_title = None
    y_right_title = None
    y_left_scale = None
    y_right_scale = None
    y_left_extent = None
    y_right_extent = None
    x_extent = None

    if chart.appearance is not None:
        x_title, x_scale, x_extent = _extract_axis_config(chart.appearance.x_axis)
        y_left_title, y_left_scale, y_left_extent = _extract_axis_config(chart.appearance.y_left_axis)
        y_right_title, y_right_scale, y_right_extent = _extract_axis_config(chart.appearance.y_right_axis)

    # Build axisTitlesVisibilitySettings if any titles are set
    axis_titles_visibility = None
    if x_title is not None or y_left_title is not None or y_right_title is not None:
        axis_titles_visibility = AxisTitlesVisibilitySettings(
            x=x_title is not None,
            yLeft=y_left_title is not None,
            yRight=y_right_title is not None,
        )

    kbn_layer_visualization = XYDataLayerConfig(
        layerId=layer_id,
        accessors=metric_ids,
        xAccessor=dimension_id,
        position='top',
        seriesType=series_type,
        showGridlines=False,
        layerType='data',
        colorMapping=kbn_color_mapping,
        splitAccessor=breakdown_id,
        yConfig=y_config,
        xScaleType=x_scale,
    )

    # Configure legend
    legend_config = _compile_legend_config(chart)

    # Extract chart-type-specific appearance properties
    (
        fitting_function,
        emphasize_fitting,
        end_value,
        curve_type,
        fill_opacity,
        min_bar_height,
        show_current_time_marker,
        hide_endzones,
    ) = _extract_chart_type_specific_appearance(chart)

    return KbnXYVisualizationState(
        preferredSeriesType=series_type,
        layers=[kbn_layer_visualization],
        legend=legend_config,
        valueLabels='hide',
        xTitle=x_title,
        yTitle=y_left_title,  # Legacy field for backward compatibility - Kibana requires both yTitle and yLeftTitle
        yLeftTitle=y_left_title,
        yRightTitle=y_right_title,
        yLeftScale=y_left_scale,
        yRightScale=y_right_scale,
        xExtent=x_extent,
        yLeftExtent=y_left_extent,
        yRightExtent=y_right_extent,
        axisTitlesVisibilitySettings=axis_titles_visibility,
        fittingFunction=fitting_function,
        emphasizeFitting=emphasize_fitting,
        endValue=end_value,
        curveType=curve_type,
        fillOpacity=fill_opacity,
        minBarHeight=min_bar_height,
        showCurrentTimeMarker=show_current_time_marker,
        hideEndzones=hide_endzones,
    )


def compile_lens_xy_chart(
    lens_xy_chart: LensXYChartTypes,
) -> tuple[str, dict[str, KbnLensColumnTypes], KbnXYVisualizationState]:
    """Compile a LensXYChart config object into a Kibana XY visualization state.

    Args:
        lens_xy_chart (LensXYChartTypes): The LensXYChart config object.

    Returns:
        tuple[str, dict[str, KbnLensColumnTypes], KbnXYVisualizationState]: The layer ID, columns, and visualization state.
    """
    # Compile metrics to get accessor IDs for visualization state
    metric_ids: list[str] = []
    kbn_metric_columns: dict[str, KbnLensMetricColumnTypes] = {}
    for metric in lens_xy_chart.metrics:
        result = compile_lens_metric(metric=metric)
        metric_id = result.primary_id
        kbn_metric = result.primary_column
        metric_ids.append(metric_id)
        kbn_metric_columns[metric_id] = kbn_metric
        kbn_metric_columns.update(result.helper_columns)

    # Compile dimensions
    kbn_dimension_columns: dict[str, KbnLensDimensionColumnTypes] = {}
    dimension_id = None
    if lens_xy_chart.dimension is not None:
        kbn_dimension_columns = compile_lens_dimensions(
            dimensions=[lens_xy_chart.dimension],
            kbn_metric_column_by_id=kbn_metric_columns,
        )
        dimension_id = next(iter(kbn_dimension_columns.keys()))

    breakdown_id = None
    if lens_xy_chart.breakdown is not None:
        kbn_breakdown_columns = compile_lens_dimensions(dimensions=[lens_xy_chart.breakdown], kbn_metric_column_by_id=kbn_metric_columns)
        breakdown_id = next(iter(kbn_breakdown_columns.keys()))

        kbn_dimension_columns[breakdown_id] = kbn_breakdown_columns[breakdown_id]

    kbn_columns = {**kbn_dimension_columns, **kbn_metric_columns}

    layer_id = lens_xy_chart.get_id()

    return (
        layer_id,
        kbn_columns,
        compile_xy_chart_visualization_state(
            layer_id=layer_id,
            chart=lens_xy_chart,
            dimension_id=dimension_id,
            metric_ids=metric_ids,
            breakdown_id=breakdown_id,
        ),
    )


def compile_esql_xy_chart(
    esql_xy_chart: ESQLXYChartTypes,
) -> tuple[str, list[KbnESQLColumnTypes], KbnXYVisualizationState]:
    """Compile an ESQLXYChart config object into a Kibana XY visualization state.

    Args:
        esql_xy_chart (ESQLXYChartTypes): The ESQLXYChart config object.

    Returns:
        tuple[str, list[KbnESQLColumnTypes], KbnXYVisualizationState]: The layer ID, columns, and visualization state.
    """
    # Compile metrics to get columnIds for visualization state
    metrics = compile_esql_metrics(esql_xy_chart.metrics)
    metric_ids = [metric.columnId for metric in metrics]

    # Compile dimensions
    dimensions = []
    dimension_id = None
    if esql_xy_chart.dimension is not None:
        dimensions = compile_esql_dimensions(dimensions=[esql_xy_chart.dimension])
        dimension_id = dimensions[0].columnId

    breakdown_id = None
    if esql_xy_chart.breakdown is not None:
        breakdown = compile_esql_dimensions(dimensions=[esql_xy_chart.breakdown])
        breakdown_id = breakdown[0].columnId
        dimensions.extend(breakdown)

    kbn_columns = [*metrics, *dimensions]

    layer_id = esql_xy_chart.get_id()

    return (
        layer_id,
        kbn_columns,
        compile_xy_chart_visualization_state(
            layer_id=layer_id,
            chart=esql_xy_chart,
            dimension_id=dimension_id,
            metric_ids=metric_ids,
            breakdown_id=breakdown_id,
        ),
    )
