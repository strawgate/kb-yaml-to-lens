from typing import TYPE_CHECKING

from dashboard_compiler.filters.compile import compile_filters
from dashboard_compiler.filters.config import FilterTypes
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
    KbnIndexPatternBasedDataSourceState,
    KbnIndexPatternBasedDataSourceStateById,
    KbnLensPanelAttributes,
    KbnLensPanelEmbeddableConfig,
    KbnLensPanelState,
    KbnTextBasedDataSourceState,
    KbnTextBasedDataSourceStateLayer,
    KbnTextBasedDataSourceStateLayerById,
    KbnVisualizationStateTypes,
    KbnVisualizationTypeEnum,
)
from dashboard_compiler.panels.charts.xy.compile import compile_lens_xy_chart
from dashboard_compiler.panels.charts.xy.config import LensAreaChart, LensBarChart, LensLineChart
from dashboard_compiler.queries.compile import compile_esql_query, compile_nonesql_query
from dashboard_compiler.queries.types import LegacyQueryTypes
from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.shared.view import KbnReference

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
    if isinstance(chart, LensLineChart | LensBarChart | LensAreaChart):
        return KbnVisualizationTypeEnum.XY
    if isinstance(chart, LensMetricChart):
        return KbnVisualizationTypeEnum.METRIC
    # if isinstance(chart, LensDatatableChart):
    #     return KbnVisualizationTypeEnum.DATATABLE

    msg = f'Unsupported Lens chart type: {type(chart)}'
    raise NotImplementedError(msg)


def compile_lens_chart_state(
    query: LegacyQueryTypes | None,
    filters: list[FilterTypes] | None,
    charts: list[AllChartTypes],
) -> tuple[KbnLensPanelState, list[KbnReference]]:
    """Compile a multi-layer chart into its Kibana view model representation."""
    layer_id: str
    lens_columns_by_id: dict[str, KbnLensColumnTypes]
    visualization_state: KbnVisualizationStateTypes

    form_based_datasource_state_layer_by_id: dict[str, KbnFormBasedDataSourceStateLayer] = {}

    kbn_references: list[KbnReference] = []

    for chart in charts:
        if isinstance(chart, LensMetricChart):
            layer_id, lens_columns_by_id, visualization_state = compile_lens_metric_chart(chart)
        elif isinstance(chart, LensPieChart):
            layer_id, lens_columns_by_id, visualization_state = compile_lens_pie_chart(chart)
        elif isinstance(chart, LensLineChart | LensBarChart | LensAreaChart):
            layer_id, lens_columns_by_id, visualization_state = compile_lens_xy_chart(chart)

        kbn_references.append(
            KbnReference(
                type='index-pattern',
                id=chart.data_view,
                name=f'indexpattern-datasource-layer-{layer_id}',
            )
        )

        form_based_datasource_state_layer_by_id[layer_id] = KbnFormBasedDataSourceStateLayer(
            columns=lens_columns_by_id,
            columnOrder=list(lens_columns_by_id.keys()),
            sampling=1,
        )

    datasource_states = KbnDataSourceState(
        formBased=KbnFormBasedDataSourceState(layers=KbnFormBasedDataSourceStateLayerById(form_based_datasource_state_layer_by_id)),
        textBased=KbnTextBasedDataSourceState(layers=KbnTextBasedDataSourceStateLayerById()),
        indexpattern=KbnIndexPatternBasedDataSourceState(layers=KbnIndexPatternBasedDataSourceStateById()),
    )

    kbn_query = compile_nonesql_query(query=query) if query else KbnQuery(query='', language='kuery')
    kbn_filters = compile_filters(filters=filters) if filters else []

    return (
        KbnLensPanelState(
            visualization=visualization_state,
            query=kbn_query,
            filters=kbn_filters,
            datasourceStates=datasource_states,
            internalReferences=[],
            adHocDataViews={},
        ),
        kbn_references,
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
        query=compile_esql_query(panel.esql),
        columns=esql_columns,
    )

    datasource_states = KbnDataSourceState(
        textBased=KbnTextBasedDataSourceState(
            layers=KbnTextBasedDataSourceStateLayerById(text_based_datasource_state_layer_by_id),
        )
    )

    return KbnLensPanelState(
        visualization=visualization_state,
        query=compile_esql_query(panel.esql),
        filters=[],
        datasourceStates=datasource_states,
        internalReferences=[],
        adHocDataViews={},
    )


def compile_charts_attributes(panel: LensPanel | ESQLPanel) -> tuple[KbnLensPanelAttributes, list[KbnReference]]:
    """Compile a LensPanel into its Kibana view model representation.

    Args:
        panel (LensPanel | ESQLPanel): The panel to compile.

    Returns:
        KbnLensPanelAttributes: The compiled Kibana Lens panel view model.

    """
    chart_state: KbnLensPanelState
    references: list[KbnReference] = []

    if isinstance(panel, LensPanel):
        chart_state, references = compile_lens_chart_state(
            query=panel.query,
            filters=panel.filters,
            charts=[panel.chart],
        )
    elif isinstance(panel, ESQLPanel):
        chart_state = compile_esql_chart_state(panel)

    return (
        KbnLensPanelAttributes(
            title=panel.title,
            visualizationType=chart_type_to_kbn_type_lens(panel.chart),
            references=references,
            state=chart_state,
        ),
        references,
    )


def compile_charts_panel_config(panel: LensPanel | ESQLPanel) -> tuple[list[KbnReference], KbnLensPanelEmbeddableConfig]:
    """Compile a LensPanel into an embeddable config.

    Args:
        panel (LensPanel | ESQLPanel): The panel to compile.

    Returns:
        KbnLensPanelEmbeddableConfig: The compiled Kibana Lens panel embeddable config.

    """
    attributes, references = compile_charts_attributes(panel)
    return references, KbnLensPanelEmbeddableConfig(
        enhancements={'dynamicActions': {'events': []}},
        attributes=attributes,
        syncTooltips=False,
        syncColors=False,
        syncCursor=True,
        filters=[],
        query=KbnQuery(query='', language='kuery'),
    )
