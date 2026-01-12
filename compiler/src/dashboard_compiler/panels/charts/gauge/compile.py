"""Compilation logic for gauge chart visualizations."""

from typing import TYPE_CHECKING

from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_metric
from dashboard_compiler.panels.charts.esql.columns.config import ESQLStaticValue
from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
from dashboard_compiler.panels.charts.gauge.config import ESQLGaugeChart, LensGaugeChart
from dashboard_compiler.panels.charts.gauge.view import KbnGaugeVisualizationState
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.lens.metrics.config import LensStaticValue
from dashboard_compiler.shared.compile import normalize_static_metric

if TYPE_CHECKING:
    from dashboard_compiler.panels.charts.lens.columns.view import KbnLensColumnTypes


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
    # Extract appearance settings with defaults
    appearance = chart.appearance
    shape = appearance.shape if appearance is not None and appearance.shape is not None else 'arc'
    ticks_position = appearance.ticks_position if appearance is not None and appearance.ticks_position is not None else 'auto'
    label_major = appearance.label_major if appearance is not None else None
    label_minor = appearance.label_minor if appearance is not None else None
    color_mode = appearance.color_mode if appearance is not None else None

    label_major_mode = 'custom' if label_major is not None else 'auto'

    return KbnGaugeVisualizationState(
        layerId=layer_id,
        metricAccessor=metric_id,
        minAccessor=min_id,
        maxAccessor=max_id,
        goalAccessor=goal_id,
        shape=shape,
        ticksPosition=ticks_position,
        labelMajor=label_major,
        labelMinor=label_minor,
        labelMajorMode=label_major_mode,
        colorMode=color_mode,
    )


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

    kbn_columns_by_id: dict[str, KbnLensColumnTypes] = {}

    # Compile primary metric
    result = compile_lens_metric(lens_gauge_chart.metric)
    metric_id = result.primary_id
    metric_column = result.primary_column
    kbn_columns_by_id[metric_id] = metric_column
    kbn_columns_by_id.update(result.helper_columns)

    # Compile optional min/max/goal - handle both static values and metrics
    if lens_gauge_chart.minimum is not None:
        minimum_metric = normalize_static_metric(lens_gauge_chart.minimum, LensStaticValue)
        min_result = compile_lens_metric(minimum_metric)
        min_id = min_result.primary_id
        min_column = min_result.primary_column
        kbn_columns_by_id[min_id] = min_column
        kbn_columns_by_id.update(min_result.helper_columns)

    if lens_gauge_chart.maximum is not None:
        maximum_metric = normalize_static_metric(lens_gauge_chart.maximum, LensStaticValue)
        max_result = compile_lens_metric(maximum_metric)
        max_id = max_result.primary_id
        max_column = max_result.primary_column
        kbn_columns_by_id[max_id] = max_column
        kbn_columns_by_id.update(max_result.helper_columns)

    if lens_gauge_chart.goal is not None:
        goal_metric = normalize_static_metric(lens_gauge_chart.goal, LensStaticValue)
        goal_result = compile_lens_metric(goal_metric)
        goal_id = goal_result.primary_id
        goal_column = goal_result.primary_column
        kbn_columns_by_id[goal_id] = goal_column
        kbn_columns_by_id.update(goal_result.helper_columns)

    layer_id = lens_gauge_chart.get_id()

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
        tuple[str, list[KbnESQLColumnTypes], KbnGaugeVisualizationState]: A tuple containing:
            - layer_id (str): The ID of the layer.
            - kbn_columns (list[KbnESQLColumnTypes]): A list of columns for the layer.
            - kbn_state_visualization (KbnGaugeVisualizationState): The compiled visualization state.

    """
    kbn_columns: list[KbnESQLColumnTypes] = []

    # Compile primary metric
    metric_column = compile_esql_metric(esql_gauge_chart.metric)
    metric_id: str = metric_column.columnId
    kbn_columns.append(metric_column)

    layer_id = esql_gauge_chart.get_id()

    # Compile optional min/max/goal - handle both static values and metrics
    min_id: str | None = None
    if esql_gauge_chart.minimum is not None:
        minimum_metric = normalize_static_metric(esql_gauge_chart.minimum, ESQLStaticValue)
        min_column = compile_esql_metric(minimum_metric)
        min_id = min_column.columnId
        kbn_columns.append(min_column)

    max_id: str | None = None
    if esql_gauge_chart.maximum is not None:
        maximum_metric = normalize_static_metric(esql_gauge_chart.maximum, ESQLStaticValue)
        max_column = compile_esql_metric(maximum_metric)
        max_id = max_column.columnId
        kbn_columns.append(max_column)

    goal_id: str | None = None
    if esql_gauge_chart.goal is not None:
        goal_metric = normalize_static_metric(esql_gauge_chart.goal, ESQLStaticValue)
        goal_column = compile_esql_metric(goal_metric)
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
