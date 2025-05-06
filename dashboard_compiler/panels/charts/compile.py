from typing import TYPE_CHECKING

from dashboard_compiler.filters.compile import compile_filters
from dashboard_compiler.filters.config import AllFilterTypes
from dashboard_compiler.panels.charts.config import (
    AllChartTypes,
    ESQLPanel,
    LensPanel,
)
from dashboard_compiler.panels.charts.metric.compile import compile_esql_metric_chart, compile_lens_metric_chart
from dashboard_compiler.panels.charts.metric.config import ESQLMetricChart, LensMetricChart
from dashboard_compiler.panels.charts.pie.compile import compile_esql_pie_chart, compile_lens_pie_chart
from dashboard_compiler.panels.charts.pie.config import ESQLPieChart, LensPieChart
from dashboard_compiler.panels.charts.view import (
    KbnDataSourceState,
    KbnFormBasedDataSourceState,
    KbnFormBasedDataSourceStateLayer,
    KbnFormBasedDataSourceStateLayerById,
    KbnLensPanelAttributes,
    KbnLensPanelEmbeddableConfig,
    KbnLensPanelState,
    KbnTextBasedDataSourceState,
    KbnTextBasedDataSourceStateLayer,
    KbnTextBasedDataSourceStateLayerById,
    KbnVisualizationStateTypes,
    KbnVisualizationTypeEnum,
)
from dashboard_compiler.queries.compile import compile_esql_query, compile_nonesql_query
from dashboard_compiler.queries.config import QueryTypes
from dashboard_compiler.queries.view import KbnQuery

if TYPE_CHECKING:
    from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
    from dashboard_compiler.panels.charts.lens.columns.view import KbnLensColumnTypes

CHART_TYPE_TO_KBN_TYPE_MAP = {
    'metric': KbnVisualizationTypeEnum.METRIC,
    'pie': KbnVisualizationTypeEnum.PIE,
}


def chart_type_to_kbn_type_lens(chart: AllChartTypes) -> KbnVisualizationTypeEnum:
    """Convert a LensChartTypes type to its corresponding Kibana visualization type."""
    if isinstance(chart, LensPieChart):
        return KbnVisualizationTypeEnum.PIE
    # if isinstance(chart, LensXYChart):
    #     return KbnVisualizationTypeEnum.XY
    if isinstance(chart, LensMetricChart):
        return KbnVisualizationTypeEnum.METRIC
    # if isinstance(chart, LensDatatableChart):
    #     return KbnVisualizationTypeEnum.DATATABLE

    msg = f'Unsupported Lens chart type: {type(chart)}'
    raise NotImplementedError(msg)


def compile_lens_chart_state(
    query: QueryTypes | None,
    filters: list[AllFilterTypes] | None,
    charts: list[AllChartTypes],
) -> KbnLensPanelState:
    """Compile a multi-layer chart into its Kibana view model representation."""
    layer_id: str
    lens_columns_by_id: dict[str, KbnLensColumnTypes]
    visualization_state: KbnVisualizationStateTypes

    form_based_datasource_state_layer_by_id: dict[str, KbnFormBasedDataSourceStateLayer] = {}

    for chart in charts:
        if isinstance(chart, LensMetricChart):
            layer_id, lens_columns_by_id, visualization_state = compile_lens_metric_chart(chart)
        elif isinstance(chart, LensPieChart):
            layer_id, lens_columns_by_id, visualization_state = compile_lens_pie_chart(chart)

        form_based_datasource_state_layer_by_id[layer_id] = KbnFormBasedDataSourceStateLayer(columns=lens_columns_by_id, sampling=100)

    datasource_states = KbnDataSourceState(
        formBased=KbnFormBasedDataSourceState(layers=KbnFormBasedDataSourceStateLayerById(form_based_datasource_state_layer_by_id))
    )

    kbn_query = compile_nonesql_query(query=query) if query else KbnQuery(query='', language='kuery')
    kbn_filters = compile_filters(filters=filters) if filters else []

    return KbnLensPanelState(
        visualization=visualization_state,
        query=kbn_query,
        filters=kbn_filters,
        datasourceStates=datasource_states,
        internalReferences=[],
        adHocDataViews={},
    )


def compile_esql_chart_state(panel: ESQLPanel) -> KbnLensPanelState:
    """Compile an ESQLPanel into its Kibana view model representation."""
    layer_id: str
    esql_columns: list[KbnESQLColumnTypes]

    visualization_state: KbnVisualizationStateTypes

    text_based_datasource_state_layer_by_id: dict[str, KbnTextBasedDataSourceStateLayer] = {}

    if isinstance(panel.chart, ESQLMetricChart):
        layer_id, esql_columns, visualization_state = compile_esql_metric_chart(panel.chart)
    elif isinstance(panel.chart, ESQLPieChart):
        layer_id, esql_columns, visualization_state = compile_esql_pie_chart(panel.chart)

    text_based_datasource_state_layer_by_id[layer_id] = KbnTextBasedDataSourceStateLayer(
        query=compile_esql_query(panel.query),
        columns=esql_columns,
    )

    datasource_states = KbnDataSourceState(
        textBased=KbnTextBasedDataSourceState(
            layers=KbnTextBasedDataSourceStateLayerById(text_based_datasource_state_layer_by_id),
        )
    )

    return KbnLensPanelState(
        visualization=visualization_state,
        query=compile_esql_query(panel.query),
        filters=[],
        datasourceStates=datasource_states,
        internalReferences=[],
        adHocDataViews={},
    )


def compile_charts_attributes(panel: LensPanel | ESQLPanel) -> KbnLensPanelAttributes:
    """Compile a LensPanel into its Kibana view model representation.

    Args:
        panel (LensPanel | ESQLPanel): The panel to compile.

    Returns:
        KbnLensPanelAttributes: The compiled Kibana Lens panel view model.

    """
    chart_state = (
        compile_lens_chart_state(
            query=panel.query,
            filters=panel.filters,
            charts=[panel.chart],
        )
        if isinstance(panel, LensPanel)
        else compile_esql_chart_state(panel)
    )

    return KbnLensPanelAttributes(
        title=panel.title,
        visualizationType=chart_type_to_kbn_type_lens(panel.chart),
        references=[],
        state=chart_state,
    )


def compile_charts_embeddable_config(panel: LensPanel | ESQLPanel) -> KbnLensPanelEmbeddableConfig:
    """Compile a LensPanel into an embeddable config.

    Args:
        panel (LensPanel | ESQLPanel): The panel to compile.

    Returns:
        KbnLensPanelEmbeddableConfig: The compiled Kibana Lens panel embeddable config.

    """
    return KbnLensPanelEmbeddableConfig(attributes=compile_charts_attributes(panel))
