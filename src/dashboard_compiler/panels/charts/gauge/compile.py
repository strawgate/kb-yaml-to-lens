"""Compilation logic for gauge chart visualizations."""

from typing import TYPE_CHECKING

from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_metric
from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
from dashboard_compiler.panels.charts.gauge.config import ESQLGaugeChart, LensGaugeChart
from dashboard_compiler.panels.charts.gauge.view import (
    KbnGaugeStateVisualizationLayer,
    KbnGaugeVisualizationState,
)
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.shared.config import random_id_generator

if TYPE_CHECKING:
    from dashboard_compiler.panels.charts.lens.columns.view import KbnLensColumnTypes, KbnLensMetricColumnTypes


def compile_gauge_chart_visualization_state(  # noqa: PLR0913
    layer_id: str,
    metric_id: str,
    chart: LensGaugeChart | ESQLGaugeChart,
    min_id: str | None = None,
    max_id: str | None = None,
    goal_id: str | None = None,
) -> KbnGaugeVisualizationState:
    """Compile a gauge chart config object into a Kibana Lens Gauge visualization state.

    Args:
        layer_id (str): The ID of the layer.
        metric_id (str): The ID of the primary metric.
        chart (LensGaugeChart | ESQLGaugeChart): The gauge chart config object.
        min_id (str | None): The ID of the minimum value metric.
        max_id (str | None): The ID of the maximum value metric.
        goal_id (str | None): The ID of the goal metric.

    Returns:
        KbnGaugeVisualizationState: The compiled visualization state.

    """
    # Determine labelMajorMode based on whether label_major is provided
    label_major_mode = 'custom' if chart.label_major is not None else 'auto'

    kbn_layer_visualization = KbnGaugeStateVisualizationLayer(
        layerId=layer_id,
        metricAccessor=metric_id,
        minAccessor=min_id,
        maxAccessor=max_id,
        goalAccessor=goal_id,
        shape=chart.shape,
        ticksPosition=chart.ticks_position,
        labelMajor=chart.label_major,
        labelMinor=chart.label_minor,
        labelMajorMode=label_major_mode,
        colorMode=chart.color_mode,
    )

    return KbnGaugeVisualizationState(layers=[kbn_layer_visualization])


def compile_lens_gauge_chart(
    lens_gauge_chart: LensGaugeChart,
) -> tuple[str, dict[str, 'KbnLensColumnTypes'], KbnGaugeVisualizationState]:
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

    # Compile primary metric
    metric_id, metric_column = compile_lens_metric(lens_gauge_chart.metric)
    kbn_metric_columns_by_id[metric_id] = metric_column

    # Compile optional min/max/goal metrics
    if lens_gauge_chart.minimum is not None:
        min_id, min_column = compile_lens_metric(lens_gauge_chart.minimum)
        kbn_metric_columns_by_id[min_id] = min_column

    if lens_gauge_chart.maximum is not None:
        max_id, max_column = compile_lens_metric(lens_gauge_chart.maximum)
        kbn_metric_columns_by_id[max_id] = max_column

    if lens_gauge_chart.goal is not None:
        goal_id, goal_column = compile_lens_metric(lens_gauge_chart.goal)
        kbn_metric_columns_by_id[goal_id] = goal_column

    kbn_columns_by_id: dict[str, KbnLensColumnTypes] = {**kbn_metric_columns_by_id}

    layer_id = lens_gauge_chart.id or random_id_generator()

    return (
        layer_id,
        kbn_columns_by_id,
        compile_gauge_chart_visualization_state(
            layer_id=layer_id,
            metric_id=metric_id,
            chart=lens_gauge_chart,
            min_id=min_id,
            max_id=max_id,
            goal_id=goal_id,
        ),
    )


def compile_esql_gauge_chart(
    esql_gauge_chart: ESQLGaugeChart,
) -> tuple[str, list[KbnESQLColumnTypes], KbnGaugeVisualizationState]:
    """Compile an ESQL GaugeChart config object into a Kibana Lens Gauge visualization state.

    Args:
        esql_gauge_chart (ESQLGaugeChart): The ESQLGaugeChart object to compile.

    Returns:
        tuple[str, list[KbnESQLFieldMetricColumn], KbnGaugeVisualizationState]: A tuple containing:
            - layer_id (str): The ID of the layer.
            - kbn_columns (list[KbnESQLFieldMetricColumn]): A list of columns for the layer.
            - kbn_state_visualization (KbnGaugeVisualizationState): The compiled visualization state.

    """
    layer_id = esql_gauge_chart.id or random_id_generator()

    kbn_columns: list[KbnESQLColumnTypes] = []

    # Compile primary metric
    metric_column = compile_esql_metric(esql_gauge_chart.metric)
    metric_id: str = metric_column.columnId
    kbn_columns.append(metric_column)

    # Compile optional min/max/goal metrics
    min_id: str | None = None
    if esql_gauge_chart.minimum is not None:
        min_column = compile_esql_metric(esql_gauge_chart.minimum)
        min_id = min_column.columnId
        kbn_columns.append(min_column)

    max_id: str | None = None
    if esql_gauge_chart.maximum is not None:
        max_column = compile_esql_metric(esql_gauge_chart.maximum)
        max_id = max_column.columnId
        kbn_columns.append(max_column)

    goal_id: str | None = None
    if esql_gauge_chart.goal is not None:
        goal_column = compile_esql_metric(esql_gauge_chart.goal)
        goal_id = goal_column.columnId
        kbn_columns.append(goal_column)

    return (
        layer_id,
        kbn_columns,
        compile_gauge_chart_visualization_state(
            layer_id=layer_id,
            metric_id=metric_id,
            chart=esql_gauge_chart,
            min_id=min_id,
            max_id=max_id,
            goal_id=goal_id,
        ),
    )
