from dashboard_compiler.compile.panels.base import compile_panel_shared
from dashboard_compiler.compile.panels.lens_charts.components import compile_dimensions, compile_metrics
from dashboard_compiler.compile.panels.lens_charts.metrics import compile_lens_metrics_chart
from dashboard_compiler.compile.panels.lens_charts.pie import compile_lens_pie_chart
from dashboard_compiler.compile.panels.lens_charts.xy import compile_lens_xy_chart
from dashboard_compiler.models.config.panels import LensPanel
from dashboard_compiler.models.config.panels.lens_charts.base import BaseLensChart
from dashboard_compiler.models.config.panels.lens_charts.metrics import LensMetricsChart
from dashboard_compiler.models.config.panels.lens_charts.pie import LensPieChart
from dashboard_compiler.models.config.panels.lens_charts.xy import LensXYChart
from dashboard_compiler.models.views.panels.lens import (
    KbnBaseStateVisualization,
    KbnDataSourceState,
    KbnLayerDataSourceState,
    KbnLensPanel,
    KbnLensPanelAttributes,
    KbnLensPanelEmbeddableConfig,
    KbnLensPanelState,
    KbnReference,
)


def chart_type_to_kbn_type(chart: BaseLensChart) -> str:
    """
    Convert a BaseLensChart type to its corresponding Kibana visualization type.

    Args:
        chart (BaseLensChart): The chart object to convert.

    Returns:
        str: The Kibana visualization type.
    """
    if isinstance(chart, LensPieChart):
        return "lnsPie"
    elif isinstance(chart, LensXYChart):
        return "lnsXY"
    elif isinstance(chart, LensMetricsChart):
        return "lnsMetric"
    else:
        raise ValueError(f"Unsupported chart type: {type(chart)}")


def compile_lens_panel(panel: LensPanel) -> tuple[list[KbnReference], KbnLensPanel]:
    panel_index, grid_data = compile_panel_shared(panel)

    metrics_by_id = {}
    metrics_by_name = {}
    dimensions_by_id = {}

    if hasattr(panel.chart, "metrics") and panel.chart.metrics:
        metrics_by_id, metrics_by_name = compile_metrics(panel.chart.metrics)

    if hasattr(panel.chart, "dimensions") and panel.chart.dimensions:
        dimensions_by_id = compile_dimensions(panel.chart.dimensions, metrics_by_name)

    state_visualization: KbnBaseStateVisualization

    if isinstance(panel.chart, LensPieChart):
        state_visualization = compile_lens_pie_chart(
            panel.chart, dimension_ids=list(dimensions_by_id.keys()), metric_ids=list(metrics_by_id.keys())
        )

    elif isinstance(panel.chart, LensXYChart):
        state_visualization = compile_lens_xy_chart(
            panel.chart,
            dimension_ids=list(dimensions_by_id.keys()),
            metric_ids=list(metrics_by_id.keys()),
            metrics_by_name=metrics_by_name,  # Pass metrics_by_name
        )

    elif isinstance(panel.chart, LensMetricsChart):
        state_visualization = compile_lens_metrics_chart(
            panel.chart,
            panel.index_pattern,
            metrics_by_id,
            metrics_by_name,
        )

    else:
        raise ValueError(f"Unsupported chart type: {type(panel.chart)}")

    layer_id = next(iter(state_visualization.layers)).layerId

    layer_data_source_state = KbnLayerDataSourceState(
        columns={**dimensions_by_id, **metrics_by_id},
        columnOrder=list(dimensions_by_id.keys()) + list(metrics_by_id.keys()),
        incompleteColumns={},
        sampling=1,  # Default based on sample
    )

    kbn_reference = KbnReference(type="index-pattern", id=panel.index_pattern, name=f"indexpattern-datasource-layer-{layer_id}")

    return [kbn_reference], KbnLensPanel(
        panelIndex=panel_index,
        gridData=grid_data,
        type="lens",
        embeddableConfig=KbnLensPanelEmbeddableConfig(
            hidePanelTitles=panel.hide_title,
            attributes=KbnLensPanelAttributes(
                title=panel.title,
                description=panel.description,
                visualizationType=chart_type_to_kbn_type(panel.chart),
                state=KbnLensPanelState(
                    visualization=state_visualization,
                    datasourceStates=KbnDataSourceState(
                        formBased={"layers": {layer_id: layer_data_source_state}},
                        indexpattern={},  # Add indexpattern datasource state if needed
                        textBased={},  # Add textBased datasource state if needed
                    ),
                    filters=[],  # Add panel filters compilation if needed
                    references=[],  # Add panel references compilation if needed
                    internalReferences=[],  # Add internal references compilation if needed
                    adHocDataViews={},  # Add adHocDataViews compilation if needed
                ),
                references=[kbn_reference],  # Panel references
            ),
        ),
    )
