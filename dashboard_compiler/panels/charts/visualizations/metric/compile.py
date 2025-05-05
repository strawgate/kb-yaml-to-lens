from dashboard_compiler.panels.lens.charts.metric.config import ESQLMetricsChart, LensMetricChart
from dashboard_compiler.panels.lens.charts.metric.view import (
    KbnMetricStateVisualizationLayer,
    KbnMetricVisualizationState,
)
from dashboard_compiler.panels.lens.view import KbnColumn
from dashboard_compiler.shared.config import stable_id_generator


def compile_lens_metrics_chart(
    chart: LensMetricChart,
    index_pattern: str,
    metrics_by_id: dict[str, KbnColumn],
    metrics_by_name: dict[str, str],
) -> tuple[KbnMetricVisualizationState, str]:
    """Compile a LensMetricsChart config object into a Kibana Lens Metric visualization state.

    Args:
        chart (LensMetricsChart): The LensMetricsChart config object.
        index_pattern (str): The index pattern associated with the panel.
        metrics_by_id (dict[str, KbnColumn]): Dictionary of compiled metrics by ID.
        metrics_by_name (dict[str, str]): Dictionary mapping metric labels to IDs.

    Returns:
        tuple[KbnLensMetricsVisualizationState, str]: The compiled visualization state and the layer ID.

    Raises:
        ValueError: If the primary metric cannot be found in the compiled metrics.

    """
    layer_id = chart.id or stable_id_generator(['metric', *metrics_by_id.keys()])

    # Assuming the first metric in the list is the primary one for the metric visualization
    primary_metric_label = chart.metrics[0].label
    primary_metric_id = metrics_by_name.get(primary_metric_label)

    if not primary_metric_id:
        # This should not happen if compile_metrics was successful and chart.metrics is not empty
        msg = f'Could not find compiled ID for primary metric: {primary_metric_label}'
        raise ValueError(msg)

    kbn_layer_visualization = KbnMetricStateVisualizationLayer(layerId=layer_id, metricAccessor=primary_metric_id)

    kbn_state_visualization = KbnMetricVisualizationState(layers=[kbn_layer_visualization])

    return kbn_state_visualization


def compile_esql_lens_metrics_chart(chart: ESQLMetricsChart, columns: list[KbnColumn]) -> KbnMetricVisualizationState:
    """Compile an ESQL-based Lens Metrics chart into its Kibana view model representation."""
    # Generate a stable layer ID
    layer_id = chart.id or stable_id_generator(['esql-metric'])  # No metrics in ESQL chart config

    # Use the explicitly defined primary metric column from the chart config
    primary_metric_accessor = chart.primary_metric_column

    kbn_layer_visualization = KbnMetricStateVisualizationLayer(layerId=layer_id, metricAccessor=primary_metric_accessor)

    kbn_state_visualization = KbnMetricVisualizationState(layers=[kbn_layer_visualization])

    return kbn_state_visualization
