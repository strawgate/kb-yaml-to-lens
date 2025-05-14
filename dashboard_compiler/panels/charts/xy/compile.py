"""Compile Lens XY visualizations into their Kibana view models."""

from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_dimensions, compile_esql_metric
from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
from dashboard_compiler.panels.charts.lens.columns.view import KbnLensColumnTypes
from dashboard_compiler.panels.charts.lens.dimensions.compile import compile_lens_dimensions
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.view import KbnLayerColorMapping
from dashboard_compiler.panels.charts.xy.config import (
    ESQLAreaChart,
    ESQLBarChart,
    ESQLLineChart,
    ESQLXYChartTypes,
    LensAreaChart,
    LensBarChart,
    LensLineChart,
    LensXYChartTypes,
)
from dashboard_compiler.panels.charts.xy.view import (
    KbnXYVisualizationState,
    XYDataLayerConfig,
)
from dashboard_compiler.shared.config import random_id_generator


def compile_series_type(chart: LensXYChartTypes | ESQLXYChartTypes) -> str:
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
    elif isinstance(chart, LensAreaChart | ESQLAreaChart):
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

    return KbnXYVisualizationState(preferredSeriesType=series_type, layers=[kbn_layer_visualization], legend={
        'isVisible': True,
        'position': 'right'
    }, valueLabels="hide")


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
