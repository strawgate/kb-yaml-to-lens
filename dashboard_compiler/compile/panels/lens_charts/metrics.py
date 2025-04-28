
from dashboard_compiler.compile.utils import stable_id_generator
from dashboard_compiler.models.config.panels.lens_charts.metrics import LensMetricsChart
from dashboard_compiler.models.views.panels.lens import KbnColumn
from dashboard_compiler.models.views.panels.lens_chart.metrics import (
    KbnLensMetricsVisualizationState,
    KbnMetricsStateVisualizationLayer,
)


def compile_lens_metrics_chart(
    chart: LensMetricsChart,
    index_pattern: str,
    metrics_by_id: dict[str, KbnColumn],
    metrics_by_name: dict[str, str],
) -> tuple[KbnLensMetricsVisualizationState, str]:
    """
    Compile a LensMetricsChart config object into a Kibana Lens Metric visualization state.

    Args:
        chart (LensMetricsChart): The LensMetricsChart config object.
        index_pattern (str): The index pattern associated with the panel.
        metrics_by_id (dict[str, KbnColumn]): Dictionary of compiled metrics by ID.
        metrics_by_name (dict[str, str]): Dictionary mapping metric labels to IDs.

    Returns:
        tuple[KbnLensMetricsVisualizationState, str]: The compiled visualization state and the layer ID.
    """
    layer_id = chart.id or stable_id_generator(["metric", *metrics_by_id.keys()])

    # Assuming the first metric in the list is the primary one for the metric visualization
    primary_metric_label = chart.metrics[0].label
    primary_metric_id = metrics_by_name.get(primary_metric_label)

    if not primary_metric_id:
        # This should not happen if compile_metrics was successful and chart.metrics is not empty
        raise ValueError(f"Could not find compiled ID for primary metric: {primary_metric_label}")

    kbn_layer_visualization = KbnMetricsStateVisualizationLayer(layerId=layer_id, metricAccessor=primary_metric_id)

    kbn_state_visualization = KbnLensMetricsVisualizationState(layers=[kbn_layer_visualization])

    return kbn_state_visualization
