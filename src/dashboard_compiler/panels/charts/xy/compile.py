"""Compile Lens XY visualizations into their Kibana view models."""

from dashboard_compiler.panels.charts.base.compile import create_default_color_mapping
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
    KbnXYVisualizationState,
    XYDataLayerConfig,
    XYReferenceLineLayerConfig,
    YConfig,
)
from dashboard_compiler.shared.config import random_id_generator


def compile_lens_reference_line_layer(
    layer: 'LensReferenceLineLayer',
) -> tuple[str, dict[str, KbnLensStaticValueColumn], list[XYReferenceLineLayerConfig]]:
    """Compile a LensReferenceLineLayer into Kibana reference line layers and columns.

    Args:
        layer: The reference line layer configuration.

    Returns:
        tuple[str, dict[str, KbnLensStaticValueColumn], list[XYReferenceLineLayerConfig]]:
            - layer_id: The primary layer ID (used for data view reference)
            - columns: Dictionary of accessor ID -> static value column
            - ref_layers: List of reference line layer configs (one per reference line)
    """
    # Generate a primary layer ID for the data view reference
    primary_layer_id = random_id_generator()

    reference_line_layers: list[XYReferenceLineLayerConfig] = []
    reference_line_columns: dict[str, KbnLensStaticValueColumn] = {}

    for ref_line in layer.reference_lines:
        # All reference lines in this layer share the same datasource layer (primary_layer_id)
        ref_layer, ref_column = compile_reference_line_layer(ref_line, primary_layer_id)
        reference_line_layers.append(ref_layer)
        # Use the accessor ID from the layer to key the column
        accessor_id = ref_layer.accessors[0]
        reference_line_columns[accessor_id] = ref_column

    return primary_layer_id, reference_line_columns, reference_line_layers


def compile_reference_line_layer(ref_line: XYReferenceLine, layer_id: str) -> tuple[XYReferenceLineLayerConfig, KbnLensStaticValueColumn]:
    """Compile a reference line into a Kibana reference line layer and column.

    Args:
        ref_line: The reference line configuration.
        layer_id: The unique layer ID for this reference line layer.

    Returns:
        tuple[XYReferenceLineLayerConfig, KbnLensStaticValueColumn]: The compiled reference line layer and column.
    """
    # Generate accessor ID
    accessor_id = ref_line.id or random_id_generator()

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
        label=ref_line.label or f'Static value: {numeric_value}',
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

    return (
        XYReferenceLineLayerConfig(
            layerId=layer_id,
            accessors=[accessor_id],
            yConfig=[y_config],
            layerType='referenceLine',
        ),
        static_value_column,
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

    kbn_color_mapping = create_default_color_mapping()

    kbn_layer_visualization = XYDataLayerConfig(
        layerId=layer_id,
        accessors=metric_ids,
        xAccessor=dimension_ids[0] if dimension_ids else None,
        position='top',
        seriesType=series_type,
        showGridlines=False,
        layerType='data',
        colorMapping=kbn_color_mapping,
        splitAccessor=breakdown_id,
    )

    return KbnXYVisualizationState(
        preferredSeriesType=series_type,
        layers=[kbn_layer_visualization],
        legend={'isVisible': True, 'position': 'right'},
        valueLabels='hide',
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
    if lens_xy_chart.breakdown:
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
    if esql_xy_chart.breakdown:
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
