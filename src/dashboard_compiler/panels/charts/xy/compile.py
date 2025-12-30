"""Compile Lens XY visualizations into their Kibana view models."""

from typing import Literal

from dashboard_compiler.panels.charts.base.compile import compile_color_mapping
from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_dimensions, compile_esql_metric
from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnLensColumnTypes,
    KbnLensMetricColumnTypes,
    KbnLensStaticValueColumn,
    KbnLensStaticValueColumnParams,
)
from dashboard_compiler.panels.charts.lens.dimensions.compile import compile_lens_dimensions
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.xy.config import (
    AxisConfig,
    AxisExtent,
    ESQLAreaChart,
    ESQLBarChart,
    ESQLLineChart,
    ESQLXYChartTypes,
    LensAreaChart,
    LensBarChart,
    LensLineChart,
    LensReferenceLineLayer,
    LensXYChartTypes,
    XYReferenceLine,
    XYReferenceLineValue,
)
from dashboard_compiler.panels.charts.xy.view import (
    AxisExtentConfig,
    AxisTitlesVisibilitySettings,
    KbnXYVisualizationState,
    XYDataLayerConfig,
    XYReferenceLineLayerConfig,
    YConfig,
)
from dashboard_compiler.shared.config import random_id_generator


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
    # Generate a primary layer ID for the data view reference and visualization layer
    primary_layer_id = random_id_generator()

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
    # Generate accessor ID
    accessor_id = ref_line.id if ref_line.id is not None else random_id_generator()

    # Extract the numeric value from the ref_line.value field
    if isinstance(ref_line.value, float):
        numeric_value = ref_line.value
    elif isinstance(ref_line.value, XYReferenceLineValue):
        numeric_value = ref_line.value.value
    else:
        # This should never happen due to Pydantic validation
        msg = f'Invalid value type: {type(ref_line.value)}'
        raise TypeError(msg)

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

    return series_type


def compile_xy_chart_visualization_state(
    *,
    layer_id: str,
    chart: LensXYChartTypes | ESQLXYChartTypes,
    dimension_ids: list[str],
    metric_ids: list[str],
    breakdown_id: str | None = None,
) -> KbnXYVisualizationState:
    """Compile an XY chart config object into a Kibana XY visualization state.

    Args:
        layer_id (str): The ID of the layer.
        chart (LensXYChartTypes | ESQLXYChartTypes): The XY chart config object.
        dimension_ids (list[str]): The IDs of the dimensions.
        metric_ids (list[str]): The IDs of the metrics.
        breakdown_id (str | None): The ID of the breakdown dimension if any.

    Returns:
        KbnXYVisualizationState: The compiled visualization state.
    """
    series_type: str = compile_series_type(chart=chart)

    kbn_color_mapping = compile_color_mapping(chart.color)

    # Build yConfig from series configuration if provided
    y_config: list[YConfig] | None = None
    if chart.appearance is not None and chart.appearance.series is not None:
        y_config = []
        for series_cfg in chart.appearance.series:
            # Only create YConfig if at least one property is set
            if any(
                v is not None
                for v in (
                    series_cfg.axis,
                    series_cfg.color,
                )
            ):
                y_config.append(
                    YConfig(
                        forAccessor=series_cfg.metric_id,
                        axisMode=series_cfg.axis,
                        color=series_cfg.color,
                    )
                )

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
        xAccessor=dimension_ids[0] if len(dimension_ids) > 0 else None,
        position='top',
        seriesType=series_type,
        showGridlines=False,
        layerType='data',
        colorMapping=kbn_color_mapping,
        splitAccessor=breakdown_id,
        yConfig=y_config if y_config is not None and len(y_config) > 0 else None,
        xScaleType=x_scale,
    )

    # Configure legend
    legend_visible = True
    legend_position = 'right'

    if chart.legend is not None:
        if chart.legend.visible is not None:
            legend_visible = chart.legend.visible
        if chart.legend.position is not None:
            legend_position = chart.legend.position

    return KbnXYVisualizationState(
        preferredSeriesType=series_type,
        layers=[kbn_layer_visualization],
        legend={'isVisible': legend_visible, 'position': legend_position},
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
    layer_id = lens_xy_chart.id or random_id_generator()

    metric_ids: list[str] = []
    kbn_metric_columns: dict[str, KbnLensMetricColumnTypes] = {}
    for metric in lens_xy_chart.metrics:
        metric_id, kbn_metric = compile_lens_metric(metric=metric)
        metric_ids.append(metric_id)
        kbn_metric_columns[metric_id] = kbn_metric

    kbn_dimension_columns = compile_lens_dimensions(
        dimensions=lens_xy_chart.dimensions,
        kbn_metric_column_by_id=kbn_metric_columns,
    )
    dimension_ids = list(kbn_dimension_columns.keys())

    breakdown_id = None
    if lens_xy_chart.breakdown is not None:
        kbn_breakdown_columns = compile_lens_dimensions(dimensions=[lens_xy_chart.breakdown], kbn_metric_column_by_id=kbn_metric_columns)
        breakdown_id = next(iter(kbn_breakdown_columns.keys()))

        dimension_ids.append(breakdown_id)

        kbn_dimension_columns[breakdown_id] = kbn_breakdown_columns[breakdown_id]

    kbn_columns = {**kbn_dimension_columns, **kbn_metric_columns}

    return (
        layer_id,
        kbn_columns,
        compile_xy_chart_visualization_state(
            layer_id=layer_id,
            chart=lens_xy_chart,
            dimension_ids=dimension_ids,
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
    layer_id = esql_xy_chart.id or random_id_generator()

    metrics = [compile_esql_metric(esql_xy_chart.metrics[0])]  # For now just handle first metric
    metric_ids = [metric.columnId for metric in metrics]

    dimensions = compile_esql_dimensions(dimensions=esql_xy_chart.dimensions)
    dimension_ids = [column.columnId for column in dimensions]

    breakdown_id = None
    if esql_xy_chart.breakdown is not None:
        breakdown = compile_esql_dimensions(dimensions=[esql_xy_chart.breakdown])
        breakdown_id = breakdown[0].columnId
        dimensions.extend(breakdown)

    kbn_columns = [*metrics, *dimensions]

    return (
        layer_id,
        kbn_columns,
        compile_xy_chart_visualization_state(
            layer_id=layer_id,
            chart=esql_xy_chart,
            dimension_ids=dimension_ids,
            metric_ids=metric_ids,
            breakdown_id=breakdown_id,
        ),
    )
