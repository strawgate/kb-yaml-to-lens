from collections.abc import Sequence
from typing import TYPE_CHECKING

from dashboard_compiler.filters.compile import compile_filters
from dashboard_compiler.filters.config import FilterTypes
from dashboard_compiler.panels.charts.config import (
    AllChartTypes,
    ESQLPanel,
    LensAreaPanelConfig,
    LensBarPanelConfig,
    LensChartTypes,
    LensLinePanelConfig,
    LensPanel,
)
from dashboard_compiler.panels.charts.datatable.compile import compile_esql_datatable_chart, compile_lens_datatable_chart
from dashboard_compiler.panels.charts.datatable.config import ESQLDatatableChart, LensDatatableChart
from dashboard_compiler.panels.charts.gauge.compile import compile_esql_gauge_chart, compile_lens_gauge_chart
from dashboard_compiler.panels.charts.gauge.config import ESQLGaugeChart, LensGaugeChart
from dashboard_compiler.panels.charts.metric.compile import compile_esql_metric_chart, compile_lens_metric_chart
from dashboard_compiler.panels.charts.metric.config import ESQLMetricChart, LensMetricChart
from dashboard_compiler.panels.charts.pie.compile import compile_esql_pie_chart, compile_lens_pie_chart
from dashboard_compiler.panels.charts.pie.config import ESQLPieChart, LensPieChart
from dashboard_compiler.panels.charts.tagcloud.compile import compile_esql_tagcloud_chart, compile_lens_tagcloud_chart
from dashboard_compiler.panels.charts.tagcloud.config import ESQLTagcloudChart, LensTagcloudChart
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
    KbnVisualizationTypeEnum,
)
from dashboard_compiler.panels.charts.xy.compile import compile_lens_reference_line_layer, compile_lens_xy_chart
from dashboard_compiler.panels.charts.xy.config import (
    ESQLAreaChart,
    ESQLBarChart,
    ESQLLineChart,
    LensAreaChart,
    LensBarChart,
    LensLineChart,
    LensReferenceLineLayer,
)
from dashboard_compiler.panels.charts.xy.view import KbnXYVisualizationState
from dashboard_compiler.queries.compile import compile_esql_query, compile_nonesql_query
from dashboard_compiler.queries.types import LegacyQueryTypes
from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.shared.view import KbnReference

if TYPE_CHECKING:
    from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
    from dashboard_compiler.panels.charts.lens.columns.view import KbnLensColumnTypes
    from dashboard_compiler.panels.charts.view import KbnVisualizationStateTypes
    from dashboard_compiler.panels.charts.xy.view import XYReferenceLineLayerConfig

CHART_TYPE_TO_KBN_TYPE_MAP = {
    'metric': KbnVisualizationTypeEnum.METRIC,
    'gauge': KbnVisualizationTypeEnum.GAUGE,
    'pie': KbnVisualizationTypeEnum.PIE,
}


def chart_type_to_kbn_type_lens(chart: AllChartTypes) -> KbnVisualizationTypeEnum:
    """Convert a LensChartTypes type to its corresponding Kibana visualization type."""
    if isinstance(chart, (LensPieChart, ESQLPieChart)):
        return KbnVisualizationTypeEnum.PIE
    if isinstance(chart, (LensLineChart, LensBarChart, LensAreaChart, LensReferenceLineLayer, ESQLAreaChart, ESQLBarChart, ESQLLineChart)):
        return KbnVisualizationTypeEnum.XY
    if isinstance(chart, (LensMetricChart, ESQLMetricChart)):
        return KbnVisualizationTypeEnum.METRIC
    if isinstance(chart, (LensDatatableChart, ESQLDatatableChart)):
        return KbnVisualizationTypeEnum.DATATABLE
    if isinstance(chart, (LensGaugeChart, ESQLGaugeChart)):
        return KbnVisualizationTypeEnum.GAUGE
    if isinstance(chart, (LensTagcloudChart, ESQLTagcloudChart)):  # pyright: ignore[reportUnnecessaryIsInstance]
        return KbnVisualizationTypeEnum.TAGCLOUD

    msg = f'Unsupported Lens chart type: {type(chart)}'  # pyright: ignore[reportUnreachable]
    raise NotImplementedError(msg)


def compile_lens_chart_state(
    query: LegacyQueryTypes | None,
    filters: list[FilterTypes] | None,
    charts: Sequence[LensChartTypes],
) -> tuple[KbnLensPanelState, list[KbnReference]]:
    """Compile a multi-layer chart into its Kibana view model representation."""
    if len(charts) == 0:
        msg = 'At least one chart must be provided'
        raise ValueError(msg)

    form_based_datasource_state_layer_by_id: dict[str, KbnFormBasedDataSourceStateLayer] = {}
    kbn_references: list[KbnReference] = []
    visualization_state: KbnVisualizationStateTypes | None = None

    # Collect reference line layers to be merged into XY visualization state
    all_reference_line_layers: list[XYReferenceLineLayerConfig] = []

    # IMPORTANT: When multiple charts are provided in a single panel, only the LAST chart's
    # visualization state is used. Earlier charts contribute their datasource layers, but
    # their visualization config (legend, colors, axis settings) is discarded.
    # This is a current limitation - multi-layer support is partial.
    for chart in charts:
        if isinstance(chart, (LensLineChart, LensBarChart, LensAreaChart)):
            layer_id, lens_columns_by_id, visualization_state = compile_lens_xy_chart(chart)
        elif isinstance(chart, LensPieChart):
            layer_id, lens_columns_by_id, visualization_state = compile_lens_pie_chart(chart)
        elif isinstance(chart, LensMetricChart):
            layer_id, lens_columns_by_id, visualization_state = compile_lens_metric_chart(chart)
        elif isinstance(chart, LensDatatableChart):
            layer_id, lens_columns_by_id, visualization_state = compile_lens_datatable_chart(chart)
        elif isinstance(chart, LensGaugeChart):
            layer_id, lens_columns_by_id, visualization_state = compile_lens_gauge_chart(chart)
        elif isinstance(chart, LensTagcloudChart):
            layer_id, lens_columns_by_id, visualization_state = compile_lens_tagcloud_chart(chart)
        elif isinstance(chart, LensReferenceLineLayer):  # pyright: ignore[reportUnnecessaryIsInstance]
            # Reference line layers contribute layers and columns but no visualization state
            layer_id, lens_columns_static, ref_line_layers = compile_lens_reference_line_layer(chart)
            # Cast to the general type since KbnLensStaticValueColumn is a subtype of KbnLensColumnTypes
            lens_columns_by_id: dict[str, KbnLensColumnTypes] = dict(lens_columns_static)
            # Store reference line layers to be added to XY visualization state
            all_reference_line_layers.extend(ref_line_layers)
            # Don't update visualization_state for reference line layers
            # They will be merged into the XY visualization state after the loop
        else:
            msg = f'Unsupported chart type: {type(chart)}'
            raise NotImplementedError(msg)

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

    if visualization_state is None:
        msg = 'No charts were successfully processed'
        raise ValueError(msg)

    # Merge reference line layers into XY visualization state
    # Reference line compatibility is validated in the config model
    if len(all_reference_line_layers) > 0 and isinstance(visualization_state, KbnXYVisualizationState):
        visualization_state.layers.extend(all_reference_line_layers)

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


def compile_esql_chart_state(panel: ESQLPanel) -> tuple[KbnLensPanelState, str]:
    """Compile an ESQLPanel into its Kibana view model representation.

    Returns:
        tuple[KbnLensPanelState, str]: A tuple containing the panel state and layer ID.

    """
    layer_id: str
    esql_columns: list[KbnESQLColumnTypes]

    visualization_state: KbnVisualizationStateTypes

    text_based_datasource_state_layer_by_id: dict[str, KbnTextBasedDataSourceStateLayer] = {}

    chart = panel.esql

    if isinstance(chart, ESQLMetricChart):
        layer_id, esql_columns, visualization_state = compile_esql_metric_chart(chart)
    elif isinstance(chart, ESQLGaugeChart):
        layer_id, esql_columns, visualization_state = compile_esql_gauge_chart(chart)
    elif isinstance(chart, ESQLPieChart):
        layer_id, esql_columns, visualization_state = compile_esql_pie_chart(chart)
    elif isinstance(chart, ESQLDatatableChart):
        layer_id, esql_columns, visualization_state = compile_esql_datatable_chart(chart)
    elif isinstance(chart, ESQLTagcloudChart):
        layer_id, esql_columns, visualization_state = compile_esql_tagcloud_chart(chart)
    else:
        msg = f'Unsupported ESQL chart type: {type(chart)}'
        raise NotImplementedError(msg)

    text_based_datasource_state_layer_by_id[layer_id] = KbnTextBasedDataSourceStateLayer(
        query=compile_esql_query(chart.query),
        columns=esql_columns,
        allColumns=esql_columns,
    )

    datasource_states = KbnDataSourceState(
        textBased=KbnTextBasedDataSourceState(
            layers=KbnTextBasedDataSourceStateLayerById(text_based_datasource_state_layer_by_id),
        )
    )

    panel_state = KbnLensPanelState(
        visualization=visualization_state,
        query=compile_esql_query(chart.query),
        filters=[],
        datasourceStates=datasource_states,
        internalReferences=[],
        adHocDataViews={},
    )

    return panel_state, layer_id


def compile_charts_attributes(panel: LensPanel | ESQLPanel) -> tuple[KbnLensPanelAttributes, list[KbnReference]]:
    """Compile a LensPanel or ESQLPanel into its Kibana view model representation.

    Args:
        panel (LensPanel | ESQLPanel): The panel to compile.

    Returns:
        KbnLensPanelAttributes: The compiled Kibana Lens panel view model.

    """
    chart_state: KbnLensPanelState
    visualization_type: KbnVisualizationTypeEnum
    references: list[KbnReference] = []

    if isinstance(panel, LensPanel):
        base_chart = panel.lens

        all_charts: list[LensChartTypes] = [base_chart]
        # Only XY charts (line, bar, area) support additional layers
        if isinstance(base_chart, (LensLinePanelConfig, LensBarPanelConfig, LensAreaPanelConfig)) and base_chart.layers is not None:
            all_charts.extend(base_chart.layers)

        chart_state, references = compile_lens_chart_state(
            query=base_chart.query,
            filters=base_chart.filters,
            charts=all_charts,
        )
        visualization_type = chart_type_to_kbn_type_lens(base_chart)
    elif isinstance(panel, ESQLPanel):  # pyright: ignore[reportUnnecessaryIsInstance]
        chart_state, _ = compile_esql_chart_state(panel)
        visualization_type = chart_type_to_kbn_type_lens(panel.esql)
        references = []
    else:
        msg = f'Unsupported panel type: {type(panel)}'  # pyright: ignore[reportUnreachable]
        raise NotImplementedError(msg)

    return (
        KbnLensPanelAttributes(
            title=panel.title,
            visualizationType=visualization_type,
            references=references,
            state=chart_state,
        ),
        references,
    )


def compile_charts_panel_config(
    panel: LensPanel | ESQLPanel,
) -> tuple[list[KbnReference], KbnLensPanelEmbeddableConfig]:
    """Compile a LensPanel or ESQLPanel into an embeddable config.

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
