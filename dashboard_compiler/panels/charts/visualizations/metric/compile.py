from dashboard_compiler.panels.charts.columns.view import KbnESQLDimensionColumnTypes, KbnESQLMetricColumnTypes, KbnLensMetricColumnTypes
from dashboard_compiler.panels.charts.dimensions.compile import compile_esql_dimension
from dashboard_compiler.panels.charts.metrics.compile import compile_esql_metric, compile_lens_metric
from dashboard_compiler.panels.charts.visualizations.metric.config import ESQLMetricChart, LensMetricChart
from dashboard_compiler.panels.charts.visualizations.metric.view import (
    KbnMetricStateVisualizationLayer,
    KbnMetricVisualizationState,
)
from dashboard_compiler.panels.charts.visualizations.view import KbnStateVisualizationType
from dashboard_compiler.shared.config import stable_id_generator


def compile_metric_chart_visualization_state(
    layer_id: str,
    primary_metric_id: str,
    secondary_metric_id: str | None,
    breakdown_dimension_id: str | None,
) -> KbnMetricVisualizationState:
    """Compile a LensMetricChart config object into a Kibana Lens Metric visualization state."""
    kbn_layer_visualization = KbnMetricStateVisualizationLayer(
        layerId=layer_id,
        metricAccessor=primary_metric_id,
        secondaryMetricAccessor=secondary_metric_id,
        breakdownByAccessor=breakdown_dimension_id,
    )

    return KbnMetricVisualizationState(layers=[kbn_layer_visualization])


def compile_lens_metric_visualization(
    lens_metric_chart: LensMetricChart,
) -> tuple[str, dict[str, KbnLensMetricColumnTypes], KbnStateVisualizationType]:
    """Compile a LensMetricChart config object into a Kibana Lens Metric visualization state."""
    primary_metric_id, primary_metric = compile_lens_metric(lens_metric_chart.primary)
    secondary_metric_id, secondary_metric = compile_lens_metric(lens_metric_chart.secondary) if lens_metric_chart.secondary else None, None
    breakdown_dimension_id, breakdown_dimension = (
        compile_lens_metric(lens_metric_chart.breakdown) if lens_metric_chart.breakdown else None,
        None,
    )

    kbn_columns_by_id = {
        primary_metric_id: primary_metric,
        secondary_metric_id: secondary_metric,
        breakdown_dimension_id: breakdown_dimension,
    }

    layer_id = lens_metric_chart.id or stable_id_generator(
        ['metric', lens_metric_chart.primary.field, lens_metric_chart.secondary.field, lens_metric_chart.breakdown.field]
    )

    return layer_id, kbn_columns_by_id, compile_metric_chart_visualization_state(
        layer_id, primary_metric_id, secondary_metric_id, breakdown_dimension_id
    )


def compile_esql_metric_visualization(
    esql_metric_chart: ESQLMetricChart,
) -> tuple[str, list[KbnESQLMetricColumnTypes], KbnStateVisualizationType]:
    """Compile an ESQL LensMetricChart config object into a Kibana Lens Metric visualization state."""
    layer_id = esql_metric_chart.id or stable_id_generator(
        ['metric', esql_metric_chart.primary.field, esql_metric_chart.secondary.field, esql_metric_chart.breakdown.field]
    )

    primary_metric_id, primary_metric = compile_esql_metric(esql_metric_chart.primary)
    secondary_metric_id, secondary_metric = compile_esql_metric(esql_metric_chart.secondary) if esql_metric_chart.secondary else None, None
    breakdown_dimension_id, breakdown_dimension = (
        compile_esql_dimension(esql_metric_chart.breakdown) if esql_metric_chart.breakdown else None,
    )

    kbn_columns = [primary_metric, secondary_metric, breakdown_dimension]

    return layer_id, kbn_columns, compile_metric_chart_visualization_state(layer_id, primary_metric_id, secondary_metric_id, breakdown_dimension_id)
