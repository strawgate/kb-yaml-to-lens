from __future__ import annotations

from typing import TYPE_CHECKING

from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_dimension, compile_esql_metric

if TYPE_CHECKING:
    from dashboard_compiler.panels.charts.esql.columns.view import (
        KbnESQLColumnTypes,
        KbnESQLFieldDimensionColumn,
        KbnESQLMetricColumnTypes,
    )
    from dashboard_compiler.panels.charts.lens.columns.view import (
        KbnLensColumnTypes,
        KbnLensMetricColumnTypes,
    )
    from dashboard_compiler.panels.charts.metric.config import ESQLMetricChart, LensMetricChart
from dashboard_compiler.panels.charts.lens.dimensions.compile import compile_lens_dimension
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.metric.view import (
    KbnESQLMetricVisualizationState,
    KbnMetricVisualizationState,
    KbnSecondaryTrendNone,
)
from dashboard_compiler.shared.config import get_layer_id


def compile_metric_chart_visualization_state(
    *,
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
    return KbnMetricVisualizationState(
        layerId=layer_id,
        metricAccessor=primary_metric_id,
        secondaryTrend=KbnSecondaryTrendNone(),
        secondaryLabelPosition='before',
        secondaryMetricAccessor=secondary_metric_id,
        breakdownByAccessor=breakdown_dimension_id,
    )


def compile_lens_metric_chart(
    lens_metric_chart: LensMetricChart,
) -> tuple[str, dict[str, KbnLensColumnTypes], KbnMetricVisualizationState]:
    """Compile a LensMetricChart config object into a Kibana Lens Metric visualization state.

    Args:
        lens_metric_chart (LensMetricChart): The LensMetricChart object to compile.

    Returns:
        tuple[str, dict[str, KbnLensMetricColumnTypes], KbnMetricVisualizationState]: A tuple containing:
            - layer_id (str): The ID of the layer.
            - kbn_columns (dict[str, KbnLensColumnTypes]): A dictionary of columns for the layer.
            - kbn_state_visualization (KbnMetricVisualizationState): The compiled visualization state.

    """
    primary_metric_id: str
    secondary_metric_id: str | None = None
    breakdown_dimension_id: str | None = None

    kbn_metric_columns_by_id: dict[str, KbnLensMetricColumnTypes] = {}

    primary_metric_id, primary_metric = compile_lens_metric(lens_metric_chart.primary)
    kbn_metric_columns_by_id[primary_metric_id] = primary_metric

    if lens_metric_chart.secondary:
        secondary_metric_id, secondary_metric = compile_lens_metric(lens_metric_chart.secondary)
        kbn_metric_columns_by_id[secondary_metric_id] = secondary_metric

    kbn_columns_by_id: dict[str, KbnLensColumnTypes] = {**kbn_metric_columns_by_id}

    if lens_metric_chart.breakdown:
        breakdown_dimension_id, breakdown_dimension = compile_lens_dimension(
            dimension=lens_metric_chart.breakdown, kbn_metric_column_by_id=kbn_metric_columns_by_id
        )
        kbn_columns_by_id[breakdown_dimension_id] = breakdown_dimension

    layer_id = get_layer_id(lens_metric_chart)

    return (
        layer_id,
        kbn_columns_by_id,
        compile_metric_chart_visualization_state(
            layer_id=layer_id,
            primary_metric_id=primary_metric_id,
            secondary_metric_id=secondary_metric_id,
            breakdown_dimension_id=breakdown_dimension_id,
        ),
    )


def compile_esql_metric_chart(
    esql_metric_chart: ESQLMetricChart,
) -> tuple[str, list[KbnESQLColumnTypes], KbnESQLMetricVisualizationState]:
    """Compile an ESQLMetricChart config object into a Kibana ES|QL Metric visualization state.

    Args:
        esql_metric_chart (ESQLMetricChart): The ESQLMetricChart object to compile.

    Returns:
        tuple[str, list[KbnESQLColumnTypes], KbnESQLMetricVisualizationState]: A tuple containing:
            - layer_id (str): The ID of the layer.
            - kbn_columns (list[KbnESQLColumnTypes]): A list of columns for the layer.
            - kbn_state_visualization (KbnESQLMetricVisualizationState): The compiled visualization state.

    """
    layer_id = get_layer_id(esql_metric_chart)

    kbn_columns: list[KbnESQLColumnTypes]

    primary_metric: KbnESQLMetricColumnTypes = compile_esql_metric(esql_metric_chart.primary)
    primary_metric_id: str = primary_metric.columnId
    kbn_columns = [primary_metric]

    secondary_metric: KbnESQLMetricColumnTypes | None = None
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
        KbnESQLMetricVisualizationState(
            layerId=layer_id,
            metricAccessor=primary_metric_id,
            showBar=False,
            secondaryMetricAccessor=secondary_metric_id,
            breakdownByAccessor=breakdown_dimension_id,
        ),
    )
