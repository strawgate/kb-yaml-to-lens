from typing import TYPE_CHECKING

from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_metric

if TYPE_CHECKING:
    from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLFieldMetricColumn

from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
from dashboard_compiler.panels.charts.gauge.config import ESQLGaugeChart, LensGaugeChart
from dashboard_compiler.panels.charts.gauge.view import (
    KbnGaugeStateVisualizationLayer,
    KbnGaugeVisualizationState,
)
from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnLensColumnTypes,
    KbnLensMetricColumnTypes,
)
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.shared.config import random_id_generator


def compile_gauge_chart_visualization_state(  # noqa: PLR0913
    layer_id: str,
    metric_id: str,
    min_id: str | None,
    max_id: str | None,
    goal_id: str | None,
    shape: str | None,
    ticks_position: str | None,
    label_major: str | None,
    label_minor: str | None,
    color_mode: str | None,
    respect_ranges: bool | None,
) -> KbnGaugeVisualizationState:
    """Compile a gauge config into a Kibana Lens Gauge visualization state.

    Args:
        layer_id (str): The ID of the layer.
        metric_id (str): The ID of the primary metric.
        min_id (str | None): The ID of the minimum value metric.
        max_id (str | None): The ID of the maximum value metric.
        goal_id (str | None): The ID of the goal metric.
        shape (str | None): The visual shape of the gauge.
        ticks_position (str | None): Position of ticks on the gauge.
        label_major (str | None): The major label text.
        label_minor (str | None): The minor label text.
        color_mode (str | None): Color mode for the gauge.
        respect_ranges (bool | None): Whether to respect the defined min/max ranges.

    Returns:
        KbnGaugeVisualizationState: The compiled visualization state.

    """
    kbn_layer_visualization = KbnGaugeStateVisualizationLayer(
        layerId=layer_id,
        metricAccessor=metric_id,
        minAccessor=min_id,
        maxAccessor=max_id,
        goalAccessor=goal_id,
        shape=shape,
        ticksPosition=ticks_position,
        labelMajor=label_major,
        labelMinor=label_minor,
        colorMode=color_mode,
        respectRanges=respect_ranges,
    )

    return KbnGaugeVisualizationState(layers=[kbn_layer_visualization])


def compile_lens_gauge_chart(
    lens_gauge_chart: LensGaugeChart,
) -> tuple[str, dict[str, KbnLensColumnTypes], KbnGaugeVisualizationState]:
    """Compile a LensGaugeChart config object into a Kibana Lens Gauge visualization state.

    Args:
        lens_gauge_chart (LensGaugeChart): The LensGaugeChart object to compile.

    Returns:
        tuple[str, dict[str, KbnLensColumnTypes], KbnGaugeVisualizationState]: A tuple containing:
            - layer_id (str): The ID of the layer.
            - kbn_columns (dict[str, KbnLensColumnTypes]): A dictionary of columns for the layer.
            - kbn_state_visualization (KbnGaugeVisualizationState): The compiled visualization state.

    """
    metric_id: str
    min_id: str | None = None
    max_id: str | None = None
    goal_id: str | None = None

    kbn_metric_columns_by_id: dict[str, KbnLensMetricColumnTypes] = {}

    metric_id, metric = compile_lens_metric(lens_gauge_chart.metric)
    kbn_metric_columns_by_id[metric_id] = metric

    if lens_gauge_chart.minimum:
        min_id, minimum_metric = compile_lens_metric(lens_gauge_chart.minimum)
        kbn_metric_columns_by_id[min_id] = minimum_metric

    if lens_gauge_chart.maximum:
        max_id, maximum_metric = compile_lens_metric(lens_gauge_chart.maximum)
        kbn_metric_columns_by_id[max_id] = maximum_metric

    if lens_gauge_chart.goal:
        goal_id, goal_metric = compile_lens_metric(lens_gauge_chart.goal)
        kbn_metric_columns_by_id[goal_id] = goal_metric

    kbn_columns_by_id: dict[str, KbnLensColumnTypes] = {**kbn_metric_columns_by_id}

    layer_id = lens_gauge_chart.id or random_id_generator()

    return (
        layer_id,
        kbn_columns_by_id,
        compile_gauge_chart_visualization_state(
            layer_id=layer_id,
            metric_id=metric_id,
            min_id=min_id,
            max_id=max_id,
            goal_id=goal_id,
            shape=lens_gauge_chart.shape,
            ticks_position=lens_gauge_chart.ticks_position,
            label_major=lens_gauge_chart.label_major,
            label_minor=lens_gauge_chart.label_minor,
            color_mode=lens_gauge_chart.color_mode,
            respect_ranges=lens_gauge_chart.respect_ranges,
        ),
    )


def compile_esql_gauge_chart(
    esql_gauge_chart: ESQLGaugeChart,
) -> tuple[str, list[KbnESQLColumnTypes], KbnGaugeVisualizationState]:
    """Compile an ESQL LensGaugeChart config object into a Kibana Lens Gauge visualization state.

    Args:
        esql_gauge_chart (ESQLGaugeChart): The ESQLGaugeChart object to compile.

    Returns:
        tuple[str, list[KbnESQLColumnTypes], KbnGaugeVisualizationState]: A tuple containing:
            - layer_id (str): The ID of the layer.
            - kbn_columns (list[KbnESQLColumnTypes]): A list of columns for the layer.
            - kbn_state_visualization (KbnGaugeVisualizationState): The compiled visualization state.

    """
    layer_id = esql_gauge_chart.id or random_id_generator()

    kbn_columns: list[KbnESQLColumnTypes]

    metric: KbnESQLFieldMetricColumn = compile_esql_metric(esql_gauge_chart.metric)
    metric_id: str = metric.columnId
    kbn_columns = [metric]

    minimum_metric: KbnESQLFieldMetricColumn | None = None
    min_id: str | None = None

    if esql_gauge_chart.minimum:
        minimum_metric = compile_esql_metric(esql_gauge_chart.minimum)
        min_id = minimum_metric.columnId
        kbn_columns.append(minimum_metric)

    maximum_metric: KbnESQLFieldMetricColumn | None = None
    max_id: str | None = None

    if esql_gauge_chart.maximum:
        maximum_metric = compile_esql_metric(esql_gauge_chart.maximum)
        max_id = maximum_metric.columnId
        kbn_columns.append(maximum_metric)

    goal_metric: KbnESQLFieldMetricColumn | None = None
    goal_id: str | None = None

    if esql_gauge_chart.goal:
        goal_metric = compile_esql_metric(esql_gauge_chart.goal)
        goal_id = goal_metric.columnId
        kbn_columns.append(goal_metric)

    return (
        layer_id,
        kbn_columns,
        compile_gauge_chart_visualization_state(
            layer_id=layer_id,
            metric_id=metric_id,
            min_id=min_id,
            max_id=max_id,
            goal_id=goal_id,
            shape=esql_gauge_chart.shape,
            ticks_position=esql_gauge_chart.ticks_position,
            label_major=esql_gauge_chart.label_major,
            label_minor=esql_gauge_chart.label_minor,
            color_mode=esql_gauge_chart.color_mode,
            respect_ranges=esql_gauge_chart.respect_ranges,
        ),
    )
