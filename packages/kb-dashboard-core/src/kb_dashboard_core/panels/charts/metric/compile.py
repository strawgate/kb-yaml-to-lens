from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from kb_dashboard_core.panels.charts.base.compile import compile_color_range_mapping
from kb_dashboard_core.panels.charts.base.view import KbnRangePalette
from kb_dashboard_core.panels.charts.esql.columns.compile import compile_esql_dimension, compile_esql_metric

if TYPE_CHECKING:
    from kb_dashboard_core.panels.charts.esql.columns.view import (
        KbnESQLFieldDimensionColumn,
        KbnESQLMetricColumnTypes,
    )
    from kb_dashboard_core.panels.charts.lens.columns.view import (
        KbnLensMetricColumnTypes,
    )
from kb_dashboard_core.panels.charts.esql.columns.view import (
    KbnESQLColumnTypes,
)
from kb_dashboard_core.panels.charts.lens.columns.view import (
    KbnLensColumnTypes,
    KbnLensDateHistogramDimensionColumn,
    KbnLensDateHistogramDimensionColumnParams,
)
from kb_dashboard_core.panels.charts.lens.dimensions.compile import compile_lens_dimension
from kb_dashboard_core.panels.charts.lens.metrics.compile import compile_lens_metric
from kb_dashboard_core.panels.charts.metric.config import BaseMetricChart, ESQLMetricChart, LensMetricChart
from kb_dashboard_core.panels.charts.metric.metrics import MetricChartColorMixin
from kb_dashboard_core.panels.charts.metric.view import (
    KbnESQLMetricVisualizationState,
    KbnMetricVisualizationState,
    KbnSecondaryTrendNone,
)
from kb_dashboard_core.shared.config import stable_id_generator

DEFAULT_APPLY_TO: Literal['background'] = 'background'


@dataclass
class MetricVisualStyle:
    """Compiled visual style fields shared by Lens and ES|QL metric visualizations."""

    show_bar: bool | None
    progress_direction: Literal['horizontal', 'vertical'] | None
    secondary_label_position: Literal['before', 'after'] | None
    palette: KbnRangePalette | None
    apply_to: Literal['value', 'background']


def _compile_metric_visual_style(
    chart: BaseMetricChart,
    primary_metric: MetricChartColorMixin,
    *,
    default_show_bar: bool | None,
    default_secondary_label_position: Literal['before', 'after'] | None,
) -> MetricVisualStyle:
    """Compile common metric visual-style fields with caller-provided backend defaults."""
    appearance = chart.appearance
    primary = appearance.primary if appearance is not None else None
    secondary = appearance.secondary if appearance is not None else None

    show_bar: bool | None = default_show_bar
    progress_direction: Literal['horizontal', 'vertical'] | None = None

    background_chart = primary.background_chart if primary is not None else None
    if background_chart is not None:
        if background_chart.type == 'bar':
            show_bar = True
            progress_direction = background_chart.direction
        elif background_chart.type == 'line':
            show_bar = False
        elif background_chart.type == 'none':
            show_bar = None

    secondary_label_position = (
        secondary.label.position if secondary is not None and secondary.label is not None and secondary.label.position is not None else None
    )
    if secondary_label_position is None:
        secondary_label_position = default_secondary_label_position

    metric_color = primary_metric.color
    range_mapping = metric_color.to_range_mapping() if metric_color is not None else None
    palette = compile_color_range_mapping(range_mapping) if range_mapping is not None else None
    apply_to: Literal['value', 'background'] = (
        metric_color.apply_to if metric_color is not None and metric_color.apply_to is not None else DEFAULT_APPLY_TO
    )

    return MetricVisualStyle(
        show_bar=show_bar,
        progress_direction=progress_direction,
        secondary_label_position=secondary_label_position,
        palette=palette,
        apply_to=apply_to,
    )


def compile_metric_chart_visualization_state(  # noqa: PLR0913
    *,
    layer_id: str,
    chart: BaseMetricChart,
    primary_metric: MetricChartColorMixin,
    primary_metric_id: str,
    secondary_metric_id: str | None,
    max_metric_id: str | None,
    breakdown_dimension_id: str | None,
) -> KbnMetricVisualizationState:
    """Compile a metric chart config object into a Kibana Lens Metric visualization state.

    Args:
        layer_id (str): The ID of the layer.
        chart (BaseMetricChart): The source chart configuration containing optional style fields.
        primary_metric (MetricChartColorMixin): The primary metric with color settings.
        primary_metric_id (str): The ID of the primary metric.
        secondary_metric_id (str | None): The ID of the secondary metric.
        max_metric_id (str | None): The ID of the maximum metric.
        breakdown_dimension_id (str | None): The ID of the breakdown dimension.

    Returns:
        KbnMetricVisualizationState: The compiled visualization state.

    """
    appearance = chart.appearance
    titles_and_text = chart.titles_and_text

    primary = appearance.primary if appearance is not None else None
    secondary = appearance.secondary if appearance is not None else None
    breakdown = appearance.breakdown if appearance is not None else None

    style = _compile_metric_visual_style(
        chart,
        primary_metric,
        default_show_bar=None,
        default_secondary_label_position='before',
    )

    trendline_layer_id: str | None = None
    trendline_time_accessor: str | None = None
    trendline_metric_accessor: str | None = None
    trendline_secondary_metric_accessor: str | None = None
    trendline_layer_type: Literal['metricTrendline'] | None = None
    if primary is not None and primary.background_chart is not None and primary.background_chart.type == 'line':
        trendline_layer_id = stable_id_generator([layer_id, 'metric', 'trendline', 'layer'])
        trendline_time_accessor = stable_id_generator([layer_id, 'metric', 'trendline', 'time'])
        trendline_metric_accessor = primary_metric_id
        trendline_secondary_metric_accessor = secondary_metric_id
        trendline_layer_type = 'metricTrendline'

    return KbnMetricVisualizationState(
        layerId=layer_id,
        metricAccessor=primary_metric_id,
        secondaryTrend=KbnSecondaryTrendNone(),
        secondaryLabelPosition=style.secondary_label_position,
        secondaryMetricAccessor=secondary_metric_id,
        maxAccessor=max_metric_id,
        breakdownByAccessor=breakdown_dimension_id,
        applyColorTo=style.apply_to,
        icon=primary.icon if primary is not None else None,
        iconAlign=primary.icon_position if primary is not None else None,
        showBar=style.show_bar,
        progressDirection=style.progress_direction,
        maxCols=breakdown.column_count if breakdown is not None else None,
        valueFontMode=primary.font_size if primary is not None else None,
        primaryPosition=primary.position if primary is not None else None,
        subtitle=titles_and_text.subtitle if titles_and_text is not None else None,
        secondaryLabel=secondary.label.text if secondary is not None and secondary.label is not None else None,
        titlesTextAlign=titles_and_text.alignment if titles_and_text is not None else None,
        primaryAlign=primary.alignment if primary is not None else None,
        secondaryAlign=secondary.alignment if secondary is not None else None,
        titleWeight=titles_and_text.weight if titles_and_text is not None else None,
        palette=style.palette,
        trendlineLayerId=trendline_layer_id,
        trendlineLayerType=trendline_layer_type,
        trendlineTimeAccessor=trendline_time_accessor,
        trendlineMetricAccessor=trendline_metric_accessor,
        trendlineSecondaryMetricAccessor=trendline_secondary_metric_accessor,
    )


def compile_lens_metric_trendline_layer_columns(
    lens_metric_chart: LensMetricChart,
) -> tuple[dict[str, KbnLensColumnTypes], str]:
    """Compile columns for the metric trendline datasource layer."""
    layer_id = lens_metric_chart.get_id()
    trendline_time_accessor = stable_id_generator([layer_id, 'metric', 'trendline', 'time'])

    trendline_columns: dict[str, KbnLensColumnTypes] = {
        trendline_time_accessor: KbnLensDateHistogramDimensionColumn(
            label='@timestamp',
            dataType='date',
            customLabel=False,
            operationType='date_histogram',
            sourceField='@timestamp',
            isBucketed=True,
            scale='interval',
            params=KbnLensDateHistogramDimensionColumnParams(
                interval='auto',
                includeEmptyRows=True,
                dropPartials=False,
            ),
        )
    }

    if lens_metric_chart.secondary is not None:
        secondary_result = compile_lens_metric(lens_metric_chart.secondary)
        trendline_columns[secondary_result.primary_id] = secondary_result.primary_column
        trendline_columns.update(secondary_result.helper_columns)

    primary_result = compile_lens_metric(lens_metric_chart.primary)
    trendline_columns[primary_result.primary_id] = primary_result.primary_column
    trendline_columns.update(primary_result.helper_columns)

    return trendline_columns, trendline_time_accessor


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
    max_metric_id: str | None = None
    breakdown_dimension_id: str | None = None

    kbn_metric_columns_by_id: dict[str, KbnLensMetricColumnTypes] = {}

    primary_result = compile_lens_metric(lens_metric_chart.primary)
    primary_metric_id = primary_result.primary_id
    primary_metric = primary_result.primary_column
    kbn_metric_columns_by_id[primary_metric_id] = primary_metric
    kbn_metric_columns_by_id.update(primary_result.helper_columns)

    if lens_metric_chart.secondary is not None:
        secondary_result = compile_lens_metric(lens_metric_chart.secondary)
        secondary_metric_id = secondary_result.primary_id
        secondary_metric = secondary_result.primary_column
        kbn_metric_columns_by_id[secondary_metric_id] = secondary_metric
        kbn_metric_columns_by_id.update(secondary_result.helper_columns)

    if lens_metric_chart.maximum is not None:
        max_result = compile_lens_metric(lens_metric_chart.maximum)
        max_metric_id = max_result.primary_id
        max_metric = max_result.primary_column
        kbn_metric_columns_by_id[max_metric_id] = max_metric
        kbn_metric_columns_by_id.update(max_result.helper_columns)

    # Initialize kbn_columns_by_id as empty dict
    kbn_columns_by_id: dict[str, KbnLensColumnTypes] = {}

    # Add breakdown dimension FIRST (if present) - Kibana requires dimensions before metrics in columnOrder
    if lens_metric_chart.breakdown is not None:
        breakdown_dimension_id, breakdown_dimension = compile_lens_dimension(
            dimension=lens_metric_chart.breakdown, kbn_metric_column_by_id=kbn_metric_columns_by_id
        )
        kbn_columns_by_id[breakdown_dimension_id] = breakdown_dimension

    # Add metrics AFTER breakdown dimension
    kbn_columns_by_id.update(kbn_metric_columns_by_id)

    layer_id = lens_metric_chart.get_id()

    return (
        layer_id,
        kbn_columns_by_id,
        compile_metric_chart_visualization_state(
            layer_id=layer_id,
            chart=lens_metric_chart,
            primary_metric=lens_metric_chart.primary,
            primary_metric_id=primary_metric_id,
            secondary_metric_id=secondary_metric_id,
            max_metric_id=max_metric_id,
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
    primary_metric: KbnESQLMetricColumnTypes = compile_esql_metric(esql_metric_chart.primary)
    primary_metric_id: str = primary_metric.columnId
    kbn_metric_columns: list[KbnESQLColumnTypes] = [primary_metric]

    secondary_metric: KbnESQLMetricColumnTypes | None = None
    secondary_metric_id: str | None = None

    if esql_metric_chart.secondary is not None:
        secondary_metric = compile_esql_metric(esql_metric_chart.secondary)
        secondary_metric_id = secondary_metric.columnId
        kbn_metric_columns.append(secondary_metric)

    max_metric: KbnESQLMetricColumnTypes | None = None
    max_metric_id: str | None = None

    if esql_metric_chart.maximum is not None:
        max_metric = compile_esql_metric(esql_metric_chart.maximum)
        max_metric_id = max_metric.columnId
        kbn_metric_columns.append(max_metric)

    breakdown_dimension: KbnESQLFieldDimensionColumn | None = None
    breakdown_dimension_id: str | None = None

    kbn_columns: list[KbnESQLColumnTypes] = []

    # Keep breakdown dimensions ahead of metrics in column order.
    if esql_metric_chart.breakdown is not None:
        breakdown_dimension = compile_esql_dimension(esql_metric_chart.breakdown)
        breakdown_dimension_id = breakdown_dimension.columnId
        kbn_columns.append(breakdown_dimension)

    kbn_columns.extend(kbn_metric_columns)

    layer_id = esql_metric_chart.get_id()

    appearance = esql_metric_chart.appearance
    titles_and_text = esql_metric_chart.titles_and_text
    primary = appearance.primary if appearance is not None else None
    secondary = appearance.secondary if appearance is not None else None
    breakdown = appearance.breakdown if appearance is not None else None

    style = _compile_metric_visual_style(
        esql_metric_chart,
        esql_metric_chart.primary,
        default_show_bar=False,
        default_secondary_label_position=None,
    )

    return (
        layer_id,
        kbn_columns,
        KbnESQLMetricVisualizationState(
            layerId=layer_id,
            metricAccessor=primary_metric_id,
            secondaryLabelPosition=style.secondary_label_position,
            secondaryMetricAccessor=secondary_metric_id,
            maxAccessor=max_metric_id,
            breakdownByAccessor=breakdown_dimension_id,
            applyColorTo=style.apply_to,
            icon=primary.icon if primary is not None else None,
            iconAlign=primary.icon_position if primary is not None else None,
            showBar=style.show_bar,
            progressDirection=style.progress_direction,
            maxCols=breakdown.column_count if breakdown is not None else None,
            valueFontMode=primary.font_size if primary is not None else None,
            primaryPosition=primary.position if primary is not None else None,
            subtitle=titles_and_text.subtitle if titles_and_text is not None else None,
            secondaryLabel=secondary.label.text if secondary is not None and secondary.label is not None else None,
            titlesTextAlign=titles_and_text.alignment if titles_and_text is not None else None,
            primaryAlign=primary.alignment if primary is not None else None,
            secondaryAlign=secondary.alignment if secondary is not None else None,
            titleWeight=titles_and_text.weight if titles_and_text is not None else None,
            palette=style.palette,
        ),
    )
