from typing import TYPE_CHECKING, Any, Literal

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
)
from kb_dashboard_core.panels.charts.lens.dimensions.compile import compile_lens_dimension
from kb_dashboard_core.panels.charts.lens.metrics.compile import compile_lens_metric
from kb_dashboard_core.panels.charts.metric.config import BaseMetricChart, ESQLMetricChart, LensMetricChart
from kb_dashboard_core.panels.charts.metric.view import (
    KbnESQLMetricVisualizationState,
    KbnMetricVisualizationState,
    KbnSecondaryTrendNone,
)


def _extract_metric_style_kwargs(chart: BaseMetricChart) -> dict[str, Any]:
    """Extract appearance and titles_and_text fields from a metric chart config.

    Returns a dict of keyword arguments suitable for passing to both
    ``KbnMetricVisualizationState`` and ``KbnESQLMetricVisualizationState``.

    Args:
        chart (BaseMetricChart): The source chart configuration containing optional style fields.

    Returns:
        dict[str, Any]: Keyword arguments for metric visualization state constructors.

    """
    appearance = chart.appearance
    titles_and_text = chart.titles_and_text

    return {
        'icon': appearance.icon if appearance is not None else None,
        'iconAlign': appearance.icon_align if appearance is not None else None,
        'showBar': appearance.show_bar if appearance is not None else None,
        'progressDirection': appearance.progress_direction if appearance is not None else None,
        'maxCols': appearance.max_cols if appearance is not None else None,
        'valueFontMode': appearance.value_font_mode if appearance is not None else None,
        'primaryPosition': appearance.primary_position if appearance is not None else None,
        'subtitle': titles_and_text.subtitle if titles_and_text is not None else None,
        'secondaryLabel': titles_and_text.secondary_label if titles_and_text is not None else None,
        'titlesTextAlign': titles_and_text.titles_text_align if titles_and_text is not None else None,
        'primaryAlign': titles_and_text.primary_align if titles_and_text is not None else None,
        'secondaryAlign': titles_and_text.secondary_align if titles_and_text is not None else None,
        'titleWeight': titles_and_text.title_weight if titles_and_text is not None else None,
    }


def compile_metric_chart_visualization_state(  # noqa: PLR0913
    *,
    layer_id: str,
    chart: BaseMetricChart,
    primary_metric_id: str,
    secondary_metric_id: str | None,
    max_metric_id: str | None,
    breakdown_dimension_id: str | None,
    apply_to: Literal['value', 'background'],
) -> KbnMetricVisualizationState:
    """Compile a metric chart config object into a Kibana Lens Metric visualization state.

    Args:
        layer_id (str): The ID of the layer.
        chart (BaseMetricChart): The source chart configuration containing optional style fields.
        primary_metric_id (str): The ID of the primary metric.
        secondary_metric_id (str | None): The ID of the secondary metric.
        max_metric_id (str | None): The ID of the maximum metric.
        breakdown_dimension_id (str | None): The ID of the breakdown dimension.
        apply_to (Literal['value', 'background']): Where Kibana applies metric color styling.

    Returns:
        KbnMetricVisualizationState: The compiled visualization state.

    """
    return KbnMetricVisualizationState(
        layerId=layer_id,
        metricAccessor=primary_metric_id,
        secondaryTrend=KbnSecondaryTrendNone(),
        secondaryLabelPosition='before',
        secondaryMetricAccessor=secondary_metric_id,
        maxAccessor=max_metric_id,
        breakdownByAccessor=breakdown_dimension_id,
        applyColorTo=apply_to,
        **_extract_metric_style_kwargs(chart),
    )


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
            primary_metric_id=primary_metric_id,
            secondary_metric_id=secondary_metric_id,
            max_metric_id=max_metric_id,
            breakdown_dimension_id=breakdown_dimension_id,
            apply_to=lens_metric_chart.apply_to,
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

    style_kwargs = _extract_metric_style_kwargs(esql_metric_chart)
    # ESQL metrics default showBar to False when not explicitly set
    if style_kwargs['showBar'] is None:
        style_kwargs['showBar'] = False

    return (
        layer_id,
        kbn_columns,
        KbnESQLMetricVisualizationState(
            layerId=layer_id,
            metricAccessor=primary_metric_id,
            secondaryMetricAccessor=secondary_metric_id,
            maxAccessor=max_metric_id,
            breakdownByAccessor=breakdown_dimension_id,
            applyColorTo=esql_metric_chart.apply_to,
            **style_kwargs,
        ),
    )
