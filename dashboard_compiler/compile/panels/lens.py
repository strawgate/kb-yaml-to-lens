from dashboard_compiler.compile.panels.base import compile_panel_shared
from dashboard_compiler.compile.utils import stable_id_generator
from dashboard_compiler.models.config.panels import LensPanel
from dashboard_compiler.models.config.panels.lens_charts.base import BaseLensChart
from dashboard_compiler.models.config.panels.lens_charts.components.dimension import Dimension
from dashboard_compiler.models.config.panels.lens_charts.components.metric import Metric
from dashboard_compiler.models.config.panels.lens_charts.pie import LensPieChart
from dashboard_compiler.models.config.panels.lens_charts.xy import LensXYChart
from dashboard_compiler.models.views.panels.lens import (
    KbnBaseStateVisualization,
    KbnColumn,
    KbnDataSourceState,
    KbnLayerDataSourceState,
    KbnLensPanel,
    KbnLensPanelAttributes,
    KbnLensPanelEmbeddableConfig,
    KbnLensPanelState,
    KbnReference,
)
from dashboard_compiler.models.views.panels.lens_chart.pie import KbnPieStateVisualizationLayer, KbnPieVisualizationState


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
    else:
        raise ValueError(f"Unsupported chart type: {type(chart)}")


def compile_metrics(metrics: list[Metric]) -> tuple[dict[str, KbnColumn], dict[str, KbnColumn]]:
    metrics_by_id = {}
    metrics_by_name = {}

    for metric in metrics:
        id = metric.id or stable_id_generator([metric.type, metric.label, metric.field])

        metrics_by_id[id] = KbnColumn(
            label=metric.label,
            dataType="number",
            operationType=metric.type,
            scale="ratio",
            sourceField=metric.field,
            isBucketed=False,
            params={
                "emptyAsNull": True,
            },
        )

        metrics_by_name[metric.label] = id

    return metrics_by_id, metrics_by_name


def compile_dimensions(dimensions: list[Dimension], metrics_by_name: dict[str, str]) -> dict[str, KbnColumn]:
    dimensions_by_id = {}

    for dimension in dimensions:
        id = dimension.id or stable_id_generator([dimension.type, dimension.label, dimension.field])

        dimensions_by_id[id] = KbnColumn(
            label=dimension.label,
            dataType="string",
            operationType=dimension.type,
            scale="ordinal",
            sourceField=dimension.field,
            isBucketed=True,
            params={
                "size": dimension.size,
                "orderBy": {"type": "column", "columnId": metrics_by_name[dimension.sort.by]},
                "orderDirection": dimension.sort.direction if dimension.sort else "asc",
                "otherBucket": True,
                "missingBucket": False,
                "parentFormat": {
                    "id": dimension.type,
                },
                "include": [],
                "exclude": [],
                "includeIsRegex": False,
                "excludeIsRegex": False,
            },
        )

    return dimensions_by_id


def compile_lens_pie_chart(chart: LensPieChart, dimension_ids: list[str], metric_ids: list[str]) -> KbnBaseStateVisualization:
    layer_id = chart.id or stable_id_generator(["pie", *dimension_ids, *metric_ids])

    kbn_state_visualization_layer = KbnPieStateVisualizationLayer(
        layerId=layer_id,
        primaryGroups=dimension_ids,
        metrics=metric_ids,
        numberDisplay="percent",
        categoryDisplay="default",
        legendDisplay="default",
        nestedLegend=False,
    )

    kbn_state_visualization = KbnPieVisualizationState(
        shape="pie",
        layers=[kbn_state_visualization_layer],
        # palette={}
    )

    # Placeholder for actual pie chart compilation logic
    return kbn_state_visualization


def compile_lens_xy_chart() -> LensXYChart:
    # Placeholder for actual XY chart compilation logic
    return LensXYChart()


def compile_lens_panel(panel: LensPanel) -> tuple[list[KbnReference], KbnLensPanel]:
    panel_index, grid_data = compile_panel_shared(panel)

    metrics_by_id, metrics_by_name = compile_metrics(panel.chart.metrics)
    dimensions_by_id = compile_dimensions(panel.chart.dimensions, metrics_by_name)

    state_visualization: KbnBaseStateVisualization = None

    if isinstance(panel.chart, LensPieChart):
        state_visualization = compile_lens_pie_chart(
            panel.chart, dimension_ids=list(dimensions_by_id.keys()), metric_ids=list(metrics_by_id.keys())
        )

    if isinstance(panel.chart, LensXYChart):
        state_visualization = compile_lens_xy_chart(
            panel.chart, dimension_ids=list(dimensions_by_id.keys()), metric_ids=list(metrics_by_id.keys())
        )

    layer_id = next(state_visualization_layer.layerId for state_visualization_layer in state_visualization.layers)

    layer_data_source_state = KbnLayerDataSourceState(
        columns={**dimensions_by_id, **metrics_by_id},
        columnOrder=list(dimensions_by_id.keys()) + list(metrics_by_id.keys()),
        incompleteColumns={},
        sampling=1,
    )

    kbn_reference = KbnReference(type="index-pattern", id=panel.index_pattern, name=f"indexpattern-datasource-layer-{layer_id}")

    return [kbn_reference], KbnLensPanel(
        panelIndex=panel_index,
        gridData=grid_data,
        type="lens",
        embeddableConfig=KbnLensPanelEmbeddableConfig(
            attributes=KbnLensPanelAttributes(
                title=panel.title,
                description=panel.description,
                visualizationType=chart_type_to_kbn_type(panel.chart),
                state=KbnLensPanelState(
                    visualization=state_visualization,
                    datasourceStates=KbnDataSourceState(
                        formBased={"layers": {layer_id: layer_data_source_state}},
                        indexpattern={},
                        textBased={},
                    ),
                    filters=[],
                    references=[],
                ),
                references=[kbn_reference],
            )
        ),
    )
