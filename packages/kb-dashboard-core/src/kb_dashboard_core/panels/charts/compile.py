from collections.abc import Sequence
from typing import TYPE_CHECKING

from kb_dashboard_core.filters.compile import compile_filters
from kb_dashboard_core.filters.config import FilterTypes
from kb_dashboard_core.panels.charts.config import (
    AllChartTypes,
    ESQLChartTypes,
    ESQLPanel,
    LensAreaPanelConfig,
    LensBarPanelConfig,
    LensChartTypes,
    LensLinePanelConfig,
    LensPanel,
)
from kb_dashboard_core.panels.charts.datatable.compile import compile_esql_datatable_chart, compile_lens_datatable_chart
from kb_dashboard_core.panels.charts.datatable.config import ESQLDatatableChart, LensDatatableChart
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLMetric, ESQLMetricTypes, ESQLStaticValue
from kb_dashboard_core.panels.charts.gauge.compile import (
    compile_esql_gauge_chart,
    compile_lens_gauge_chart,
    prepare_esql_gauge_chart,
)
from kb_dashboard_core.panels.charts.gauge.config import ESQLGaugeChart, LensGaugeChart
from kb_dashboard_core.panels.charts.heatmap.compile import compile_esql_heatmap_chart, compile_lens_heatmap_chart
from kb_dashboard_core.panels.charts.heatmap.config import ESQLHeatmapChart, LensHeatmapChart
from kb_dashboard_core.panels.charts.metric.compile import compile_esql_metric_chart, compile_lens_metric_chart
from kb_dashboard_core.panels.charts.metric.config import ESQLMetricChart, LensMetricChart
from kb_dashboard_core.panels.charts.mosaic.compile import compile_esql_mosaic_chart, compile_lens_mosaic_chart
from kb_dashboard_core.panels.charts.mosaic.config import ESQLMosaicChart, LensMosaicChart
from kb_dashboard_core.panels.charts.pie.compile import compile_esql_pie_chart, compile_lens_pie_chart
from kb_dashboard_core.panels.charts.pie.config import ESQLPieChart, LensPieChart
from kb_dashboard_core.panels.charts.tagcloud.compile import compile_esql_tagcloud_chart, compile_lens_tagcloud_chart
from kb_dashboard_core.panels.charts.tagcloud.config import ESQLTagcloudChart, LensTagcloudChart
from kb_dashboard_core.panels.charts.view import (
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
from kb_dashboard_core.panels.charts.xy.compile import compile_esql_xy_chart, compile_lens_reference_line_layer, compile_lens_xy_chart
from kb_dashboard_core.panels.charts.xy.config import (
    ESQLAreaChart,
    ESQLBarChart,
    ESQLLineChart,
    LensAreaChart,
    LensBarChart,
    LensLineChart,
    LensReferenceLineLayer,
)
from kb_dashboard_core.panels.charts.xy.metrics import ESQLXYMetricTypes, XYESQLMetric, XYESQLStaticValue
from kb_dashboard_core.panels.charts.xy.view import KbnXYVisualizationState
from kb_dashboard_core.panels.drilldowns import compile_drilldowns
from kb_dashboard_core.queries.compile import compile_esql_query, compile_nonesql_query
from kb_dashboard_core.queries.config import ESQLQuery
from kb_dashboard_core.queries.types import LegacyQueryTypes
from kb_dashboard_core.queries.view import KbnQuery
from kb_dashboard_core.shared.view import KbnReference

if TYPE_CHECKING:
    from kb_dashboard_core.panels.charts.esql.columns.view import KbnESQLColumnTypes
    from kb_dashboard_core.panels.charts.lens.columns.view import KbnLensColumnTypes
    from kb_dashboard_core.panels.charts.view import KbnVisualizationStateTypes
    from kb_dashboard_core.panels.charts.xy.view import XYReferenceLineLayerConfig


def chart_type_to_kbn_type_lens(chart: AllChartTypes) -> KbnVisualizationTypeEnum:  # noqa: PLR0911
    """Convert a LensChartTypes type to its corresponding Kibana visualization type."""
    match chart:
        case LensPieChart() | ESQLPieChart() | LensMosaicChart() | ESQLMosaicChart():
            return KbnVisualizationTypeEnum.PIE
        case (
            LensLineChart()
            | LensBarChart()
            | LensAreaChart()
            | LensReferenceLineLayer()
            | ESQLAreaChart()
            | ESQLBarChart()
            | ESQLLineChart()
        ):
            return KbnVisualizationTypeEnum.XY
        case LensMetricChart() | ESQLMetricChart():
            return KbnVisualizationTypeEnum.METRIC
        case LensDatatableChart() | ESQLDatatableChart():
            return KbnVisualizationTypeEnum.DATATABLE
        case LensGaugeChart() | ESQLGaugeChart():
            return KbnVisualizationTypeEnum.GAUGE
        case LensHeatmapChart() | ESQLHeatmapChart():
            return KbnVisualizationTypeEnum.HEATMAP
        case LensTagcloudChart() | ESQLTagcloudChart():
            return KbnVisualizationTypeEnum.TAGCLOUD
        case _:  # pyright: ignore[reportUnnecessaryComparison]
            msg = f'Unsupported Lens chart type: {type(chart)}'
            raise NotImplementedError(msg)  # pyright: ignore[reportUnreachable]


def _format_esql_numeric(value: int | float) -> str:
    """Format a numeric literal for ESQL ``EVAL`` expressions."""
    return str(value) if isinstance(value, int) else repr(value)


def _build_static_field_name(chart_type: str, role: str, column_id: str) -> str:
    """Generate a deterministic synthetic field name for static ES|QL values."""
    return f'__kb_{chart_type}_{role}_{column_id.replace("-", "_")}'


def _rewrite_esql_metric_static_value(
    metric: ESQLMetricTypes,
    *,
    chart_type: str,
    role: str,
    eval_assignments: list[str],
) -> ESQLMetric:
    """Rewrite ESQL static metric values to synthetic query-backed fields."""
    if isinstance(metric, ESQLStaticValue):
        field_name = _build_static_field_name(chart_type, role, metric.get_id())
        eval_assignments.append(f'{field_name} = {_format_esql_numeric(metric.value)}')
        return ESQLMetric(
            id=metric.get_id(),
            field=field_name,
            label=metric.label if metric.label is not None else str(metric.value),
        )
    return metric


def _rewrite_esql_xy_metric_static_value(
    metric: ESQLXYMetricTypes,
    *,
    chart_type: str,
    role: str,
    eval_assignments: list[str],
) -> ESQLXYMetricTypes:
    """Rewrite XY ESQL static metric values while preserving axis/color appearance."""
    if isinstance(metric, XYESQLStaticValue):
        field_name = _build_static_field_name(chart_type, role, metric.get_id())
        eval_assignments.append(f'{field_name} = {_format_esql_numeric(metric.value)}')
        return XYESQLMetric(
            id=metric.get_id(),
            field=field_name,
            label=metric.label if metric.label is not None else str(metric.value),
            axis=metric.axis,
            color=metric.color,
        )
    return metric


def _prepare_esql_chart_static_values(
    chart: ESQLChartTypes,
    query: ESQLQuery,
) -> tuple[ESQLChartTypes, ESQLQuery]:
    """Rewrite static values in ES|QL chart configs into synthetic ``EVAL`` fields."""
    if isinstance(chart, ESQLGaugeChart):
        prepared_chart, prepared_query = prepare_esql_gauge_chart(chart, query=query)
        return prepared_chart, prepared_query if prepared_query is not None else query

    eval_assignments: list[str] = []
    updates: dict[str, object] = {}

    match chart:
        case ESQLMetricChart():
            updates['primary'] = _rewrite_esql_metric_static_value(
                chart.primary,
                chart_type=chart.type,
                role='primary',
                eval_assignments=eval_assignments,
            )
            if chart.secondary is not None:
                updates['secondary'] = _rewrite_esql_metric_static_value(
                    chart.secondary,
                    chart_type=chart.type,
                    role='secondary',
                    eval_assignments=eval_assignments,
                )
            if chart.maximum is not None:
                updates['maximum'] = _rewrite_esql_metric_static_value(
                    chart.maximum,
                    chart_type=chart.type,
                    role='maximum',
                    eval_assignments=eval_assignments,
                )
        case ESQLHeatmapChart():
            updates['value'] = _rewrite_esql_metric_static_value(
                chart.value,
                chart_type=chart.type,
                role='value',
                eval_assignments=eval_assignments,
            )
        case ESQLPieChart():
            updates['metrics'] = [
                _rewrite_esql_metric_static_value(
                    metric,
                    chart_type=chart.type,
                    role=f'metric_{index}',
                    eval_assignments=eval_assignments,
                )
                for index, metric in enumerate(chart.metrics)
            ]
        case ESQLDatatableChart():
            updates['metrics'] = [
                _rewrite_esql_metric_static_value(
                    metric,
                    chart_type=chart.type,
                    role=f'metric_{index}',
                    eval_assignments=eval_assignments,
                )
                for index, metric in enumerate(chart.metrics)
            ]
        case ESQLTagcloudChart():
            updates['metric'] = _rewrite_esql_metric_static_value(
                chart.metric,
                chart_type=chart.type,
                role='metric',
                eval_assignments=eval_assignments,
            )
        case ESQLMosaicChart():
            updates['metric'] = _rewrite_esql_metric_static_value(
                chart.metric,
                chart_type=chart.type,
                role='metric',
                eval_assignments=eval_assignments,
            )
        case ESQLBarChart() | ESQLLineChart() | ESQLAreaChart():
            updates['metrics'] = [
                _rewrite_esql_xy_metric_static_value(
                    metric,
                    chart_type=chart.type,
                    role=f'metric_{index}',
                    eval_assignments=eval_assignments,
                )
                for index, metric in enumerate(chart.metrics)
            ]

    prepared_chart = chart.model_copy(update=updates) if len(updates) > 0 else chart
    prepared_query = ESQLQuery(root=f'{query.root}\n| EVAL {", ".join(eval_assignments)}') if len(eval_assignments) > 0 else query

    return prepared_chart, prepared_query


def compile_lens_chart_state(  # noqa: PLR0912
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
        match chart:
            case LensLineChart() | LensBarChart() | LensAreaChart():
                layer_id, lens_columns_by_id, visualization_state = compile_lens_xy_chart(chart)
            case LensPieChart():
                layer_id, lens_columns_by_id, visualization_state = compile_lens_pie_chart(chart)
            case LensMetricChart():
                layer_id, lens_columns_by_id, visualization_state = compile_lens_metric_chart(chart)
            case LensDatatableChart():
                layer_id, lens_columns_by_id, visualization_state = compile_lens_datatable_chart(chart)
            case LensGaugeChart():
                layer_id, lens_columns_by_id, visualization_state = compile_lens_gauge_chart(chart)
            case LensHeatmapChart():
                layer_id, lens_columns_by_id, visualization_state = compile_lens_heatmap_chart(chart)
            case LensTagcloudChart():
                layer_id, lens_columns_by_id, visualization_state = compile_lens_tagcloud_chart(chart)
            case LensMosaicChart():
                layer_id, lens_columns_by_id, visualization_state = compile_lens_mosaic_chart(chart)
            case LensReferenceLineLayer():
                # Reference line layers contribute layers and columns but no visualization state
                layer_id, lens_columns_static, ref_line_layers = compile_lens_reference_line_layer(chart)
                # Cast to the general type since KbnLensStaticValueColumn is a subtype of KbnLensColumnTypes
                lens_columns_by_id: dict[str, KbnLensColumnTypes] = dict(lens_columns_static)
                # Store reference line layers to be added to XY visualization state
                all_reference_line_layers.extend(ref_line_layers)
                # Don't update visualization_state for reference line layers
                # They will be merged into the XY visualization state after the loop
            case _:  # pyright: ignore[reportUnnecessaryComparison]
                msg = f'Unsupported chart type: {type(chart)}'
                raise NotImplementedError(msg)  # pyright: ignore[reportUnreachable]

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
    prepared_chart, prepared_query = _prepare_esql_chart_static_values(chart, query=chart.query)
    compiled_query = compile_esql_query(prepared_query)

    match prepared_chart:
        case ESQLMetricChart():
            layer_id, esql_columns, visualization_state = compile_esql_metric_chart(prepared_chart)
        case ESQLGaugeChart():
            layer_id, esql_columns, visualization_state = compile_esql_gauge_chart(prepared_chart)
        case ESQLHeatmapChart():
            layer_id, esql_columns, visualization_state = compile_esql_heatmap_chart(prepared_chart)
        case ESQLPieChart():
            layer_id, esql_columns, visualization_state = compile_esql_pie_chart(prepared_chart)
        case ESQLDatatableChart():
            layer_id, esql_columns, visualization_state = compile_esql_datatable_chart(prepared_chart)
        case ESQLTagcloudChart():
            layer_id, esql_columns, visualization_state = compile_esql_tagcloud_chart(prepared_chart)
        case ESQLMosaicChart():
            layer_id, esql_columns, visualization_state = compile_esql_mosaic_chart(prepared_chart)
        case ESQLBarChart() | ESQLLineChart() | ESQLAreaChart():
            layer_id, esql_columns, visualization_state = compile_esql_xy_chart(prepared_chart)
        case _:  # pyright: ignore[reportUnnecessaryComparison]
            msg = f'Unsupported ESQL chart type: {type(chart)}'
            raise NotImplementedError(msg)  # pyright: ignore[reportUnreachable]

    text_based_datasource_state_layer_by_id[layer_id] = KbnTextBasedDataSourceStateLayer(
        query=compiled_query,
        columns=esql_columns,
        allColumns=esql_columns,
        timeField=panel.esql.time_field,
    )

    datasource_states = KbnDataSourceState(
        textBased=KbnTextBasedDataSourceState(layers=KbnTextBasedDataSourceStateLayerById(text_based_datasource_state_layer_by_id))
    )

    panel_state = KbnLensPanelState(
        visualization=visualization_state,
        query=compiled_query,
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

    match panel:
        case LensPanel():
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
        case ESQLPanel():
            chart_state, _ = compile_esql_chart_state(panel)
            visualization_type = chart_type_to_kbn_type_lens(panel.esql)
            references = []
        case _:  # pyright: ignore[reportUnnecessaryComparison]
            msg = f'Unsupported panel type: {type(panel)}'
            raise NotImplementedError(msg)  # pyright: ignore[reportUnreachable]

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

    # Compile drilldowns if present
    enhancements: dict[str, object]
    if panel.drilldowns is not None and len(panel.drilldowns) > 0:
        drilldown_refs, enhancements_model = compile_drilldowns(panel.drilldowns)
        references.extend(drilldown_refs)
        enhancements = enhancements_model.model_dump(by_alias=True)
    else:
        enhancements = {'dynamicActions': {'events': []}}

    return references, KbnLensPanelEmbeddableConfig(
        hidePanelTitles=panel.hide_title,
        enhancements=enhancements,
        attributes=attributes,
        syncTooltips=False,
        syncColors=False,
        syncCursor=True,
        filters=[],
        query=KbnQuery(query='', language='kuery'),
    )
