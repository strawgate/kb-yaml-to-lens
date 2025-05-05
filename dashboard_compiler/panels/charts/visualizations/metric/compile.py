from dashboard_compiler.panels.charts.columns.view import (
    KbnESQLColumnTypes,
    KbnESQLFieldDimensionColumn,
    KbnESQLFieldMetricColumn,
    KbnLensColumnTypes,
    KbnLensMetricColumnTypes,
)
from dashboard_compiler.panels.charts.dimensions.compile import compile_esql_dimension, compile_lens_dimension
from dashboard_compiler.panels.charts.metrics.compile import compile_esql_metric, compile_lens_metric
from dashboard_compiler.panels.charts.visualizations.metric.config import ESQLMetricChart, LensMetricChart
from dashboard_compiler.panels.charts.visualizations.metric.view import (
    KbnMetricStateVisualizationLayer,
    KbnMetricVisualizationState,
)
from dashboard_compiler.shared.config import random_id_generator


def compile_metric_chart_visualization_state(
    layer_id: str,
    primary_metric_id: str,
    secondary_metric_id: str | None,
    breakdown_dimension_id: str | None,
) -> KbnMetricVisualizationState:
    """Compile a LensMetricChart config object into a Kibana Lens Metric visualization state.

    Args:
        layer_id (str): The ID of the layer.
        primary_metric_id (str): The ID of the primary metric.
        secondary_metric_id (str | None): The ID of the secondary metric.
        breakdown_dimension_id (str | None): The ID of the breakdown dimension.

    Returns:
        KbnMetricVisualizationState: The compiled visualization state.
    """
    kbn_layer_visualization = KbnMetricStateVisualizationLayer(
        layerId=layer_id,
        metricAccessor=primary_metric_id,
        secondaryMetricAccessor=secondary_metric_id,
        breakdownByAccessor=breakdown_dimension_id,
    )

    return KbnMetricVisualizationState(layers=[kbn_layer_visualization])


def compile_lens_metric_visualization(
    lens_metric_chart: LensMetricChart,
) -> tuple[str, dict[str, KbnLensColumnTypes], KbnMetricVisualizationState]:
    """Compile a LensMetricChart config object into a Kibana Lens Metric visualization state.

    Args:
        lens_metric_chart (LensMetricChart): The LensMetricChart object to compile.

    Returns:
        tuple[str, dict[str, KbnLensMetricColumnTypes], KbnStateVisualizationType]: A tuple containing:
            - layer_id (str): The ID of the layer.
            - kbn_columns (dict[str, KbnLensColumnTypes]): A dictionary of columns for the layer.
            - kbn_state_visualization (KbnStateVisualizationType): The compiled visualization state.
    """
    primary_metric_id: str
    secondary_metric_id: str | None = None
    breakdown_dimension_id: str | None = None

    kbn_metric_columns_by_id: dict[str, KbnLensMetricColumnTypes] = {}

    primary_metric_id, primary_metric = compile_lens_metric(lens_metric_chart.primary)
    kbn_metric_columns_by_id[primary_metric_id] = primary_metric

    # If a secondary metric is provided, compile it
    if lens_metric_chart.secondary:
        secondary_metric_id, secondary_metric = compile_lens_metric(lens_metric_chart.secondary)
        kbn_metric_columns_by_id[secondary_metric_id] = secondary_metric

    kbn_columns_by_id: dict[str, KbnLensColumnTypes] = {**kbn_metric_columns_by_id}

    # If a breakdown dimension is provided, compile it
    if lens_metric_chart.breakdown:
        breakdown_dimension_id, breakdown_dimension = compile_lens_dimension(
            dimension=lens_metric_chart.breakdown, kbn_metric_column_by_id=kbn_metric_columns_by_id
        )
        kbn_columns_by_id[breakdown_dimension_id] = breakdown_dimension

    layer_id = lens_metric_chart.id or random_id_generator()

    return (
        layer_id,
        kbn_columns_by_id,
        compile_metric_chart_visualization_state(layer_id, primary_metric_id, secondary_metric_id, breakdown_dimension_id),
    )


def compile_esql_metric_visualization(
    esql_metric_chart: ESQLMetricChart,
) -> tuple[str, list[KbnESQLColumnTypes], KbnMetricVisualizationState]:
    """Compile an ESQL LensMetricChart config object into a Kibana Lens Metric visualization state.

    Args:
        esql_metric_chart (ESQLMetricChart): The ESQLMetricChart object to compile.

    Returns:
        tuple[str, list[KbnESQLColumnTypes], KbnMetricVisualizationState]: A tuple containing:
            - layer_id (str): The ID of the layer.
            - kbn_columns (list[KbnESQLColumnTypes]): A list of columns for the layer.
            - kbn_state_visualization (KbnMetricVisualizationState): The compiled visualization state.
    """
    layer_id = esql_metric_chart.id or random_id_generator()

    kbn_columns: list[KbnESQLColumnTypes]

    primary_metric: KbnESQLFieldMetricColumn = compile_esql_metric(esql_metric_chart.primary)
    primary_metric_id: str = primary_metric.columnId
    kbn_columns = [primary_metric]

    secondary_metric: KbnESQLFieldMetricColumn | None = None
    secondary_metric_id: str | None = None

    if esql_metric_chart.secondary:
        secondary_metric = compile_esql_metric(esql_metric_chart.secondary)
        secondary_metric_id = secondary_metric.columnId
        kbn_columns.append(secondary_metric)

    breakdown_dimension: KbnESQLFieldDimensionColumn | None = None
    breakdown_dimension_id: str | None = None

    if esql_metric_chart.breakdown:
        breakdown_dimension = compile_esql_dimension(esql_metric_chart.breakdown)
        breakdown_dimension_id = breakdown_dimension.columnId
        kbn_columns.append(breakdown_dimension)

    return (
        layer_id,
        kbn_columns,
        compile_metric_chart_visualization_state(
            layer_id=layer_id,
            primary_metric_id=primary_metric_id,
            secondary_metric_id=secondary_metric_id,
            breakdown_dimension_id=breakdown_dimension_id,
        ),
    )
