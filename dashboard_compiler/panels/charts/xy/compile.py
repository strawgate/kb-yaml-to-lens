"""Compile Lens XY visualizations into their Kibana view models."""

from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_dimensions, compile_esql_metric
from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
from dashboard_compiler.panels.charts.lens.columns.view import KbnLensColumnTypes
from dashboard_compiler.panels.charts.lens.dimensions.compile import compile_lens_dimensions
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.view import KbnLayerColorMapping
from dashboard_compiler.panels.charts.xy.config import ESQLXYChartTypes, LensXYChartTypes
from dashboard_compiler.panels.charts.xy.view import (
    KbnXYVisualizationState,
    SeriesTypeEnum,
    XYDataLayerConfig,
)
from dashboard_compiler.shared.config import random_id_generator


def chart_to_series_type(chart_type: str, mode: str | None = None) -> SeriesTypeEnum:
    """Convert chart type and mode to Kibana SeriesType.

    Args:
        chart_type (str): The type of the chart (e.g., 'line', 'bar', 'area').
        mode (str | None): The mode of the chart (e.g., 'unstacked', 'percentage', 'stacked').

    Returns:
        SeriesTypeEnum: The corresponding Kibana SeriesType.
    """
    if chart_type == 'line':
        return SeriesTypeEnum.line

    if chart_type == 'bar':
        if mode == 'unstacked':
            return SeriesTypeEnum.bar
        if mode == 'percentage':
            return SeriesTypeEnum.bar_percentage_stacked
        return SeriesTypeEnum.bar_stacked

    if chart_type == 'area':
        if mode == 'unstacked':
            return SeriesTypeEnum.area
        if mode == 'percentage':
            return SeriesTypeEnum.area_percentage_stacked
        return SeriesTypeEnum.area_stacked

    msg = f'Unsupported chart type: {chart_type} with mode: {mode}'
    raise NotImplementedError(msg)


def compile_xy_chart_visualization_state(
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
    series_type = chart_to_series_type(chart.type, getattr(chart, 'mode', None))

    kbn_color_mapping = KbnLayerColorMapping()

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
        legend={}
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

    # Compile metrics
    metric_ids: list[str] = []
    kbn_metric_columns: dict[str, KbnLensColumnTypes] = {}
    for metric in lens_xy_chart.metrics:
        metric_id, kbn_metric = compile_lens_metric(metric=metric)
        metric_ids.append(metric_id)
        kbn_metric_columns[metric_id] = kbn_metric

    # Compile dimensions
    kbn_dimension_columns = compile_lens_dimensions(
        dimensions=lens_xy_chart.dimensions,
        kbn_metric_column_by_id=kbn_metric_columns,
    )
    dimension_ids = list(kbn_dimension_columns.keys())

    # Compile breakdown if present
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

    # Compile metrics
    metrics = [compile_esql_metric(esql_xy_chart.metrics[0])]  # For now just handle first metric
    metric_ids = [metric.columnId for metric in metrics]

    # Compile dimensions
    dimensions = compile_esql_dimensions(dimensions=esql_xy_chart.dimensions)
    dimension_ids = [column.columnId for column in dimensions]

    # Compile breakdown if present
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
