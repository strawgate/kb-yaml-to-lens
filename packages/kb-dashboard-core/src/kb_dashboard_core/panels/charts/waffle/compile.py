"""Compile Lens waffle visualizations into their Kibana view models."""

from kb_dashboard_core.panels.charts.base.compile import build_collapse_fns, compile_color_value_mapping, map_legend_size
from kb_dashboard_core.panels.charts.esql.columns.compile import compile_esql_dimensions, compile_esql_metric
from kb_dashboard_core.panels.charts.esql.columns.view import KbnESQLColumnTypes
from kb_dashboard_core.panels.charts.lens.columns.view import (
    KbnLensColumnTypes,
    KbnLensMetricColumnTypes,
)
from kb_dashboard_core.panels.charts.lens.dimensions.compile import (
    compile_lens_dimensions,
)
from kb_dashboard_core.panels.charts.lens.metrics.compile import compile_lens_metric
from kb_dashboard_core.panels.charts.waffle.config import ESQLWaffleChart, LensWaffleChart
from kb_dashboard_core.panels.charts.waffle.view import (
    KbnWaffleStateVisualizationLayer,
    KbnWaffleVisualizationState,
)
from kb_dashboard_core.shared.defaults import default_false


def compile_waffle_chart_visualization_state(
    *,
    layer_id: str,
    chart: LensWaffleChart | ESQLWaffleChart,
    breakdown_id: str | None,
    metric_id: str,
    collapse_fns: dict[str, str] | None,
) -> KbnWaffleVisualizationState:
    """Compile a WaffleChart config object into a Kibana Waffle visualization state.

    Args:
        layer_id: The ID of the layer.
        chart: The WaffleChart config object.
        breakdown_id: The ID of the breakdown dimension, or None if not specified.
        metric_id: The ID of the metric.
        collapse_fns: Mapping of dimension ID to collapse function.

    Returns:
        The compiled visualization state for the waffle chart.

    """
    number_display = 'percent'
    if chart.appearance is not None and chart.appearance.values is not None and chart.appearance.values.format is not None:
        fmt = chart.appearance.values.format
        number_display = 'hidden' if fmt == 'hide' else fmt

    category_display = 'default'

    legend_display = 'default'
    legend_size = None
    truncate_legend = None
    legend_max_lines = None
    nested_legend = None
    show_single_series = None
    legend_position = 'right'

    if chart.legend is not None:
        if chart.legend.visible is not None:
            legend_display = 'default' if chart.legend.visible == 'auto' else chart.legend.visible
        if chart.legend.width is not None:
            legend_size = map_legend_size(chart.legend.width)
        if chart.legend.truncate_labels is not None:
            # Kibana mapping: 0 explicitly disables truncation (truncateLegend=False),
            # otherwise set legendMaxLines and let Kibana use its default truncation behavior
            if chart.legend.truncate_labels == 0:
                truncate_legend = False
            else:
                legend_max_lines = chart.legend.truncate_labels
        if chart.legend.nested is not None:
            nested_legend = chart.legend.nested
        if chart.legend.show_single_series is not None:
            show_single_series = chart.legend.show_single_series
        if chart.legend.position is not None:
            legend_position = chart.legend.position

    kbn_color_mapping = compile_color_value_mapping(chart.color)

    percent_decimals = None
    if chart.appearance is not None and chart.appearance.values is not None and chart.appearance.values.decimal_places is not None:
        percent_decimals = chart.appearance.values.decimal_places

    kbn_layer_visualization = KbnWaffleStateVisualizationLayer(
        layerId=layer_id,
        primaryGroups=[breakdown_id] if breakdown_id is not None else [],
        secondaryGroups=None,
        metrics=[metric_id],
        allowMultipleMetrics=False,
        collapseFns=collapse_fns if collapse_fns is not None and len(collapse_fns) > 0 else None,
        numberDisplay=number_display,
        categoryDisplay=category_display,
        legendDisplay=legend_display,
        legendPosition=legend_position,
        nestedLegend=default_false(nested_legend),
        layerType='data',
        colorMapping=kbn_color_mapping,
        legendSize=legend_size,
        truncateLegend=False if truncate_legend is False else None,
        legendMaxLines=legend_max_lines,
        showSingleSeries=show_single_series,
        percentDecimals=percent_decimals,
    )

    return KbnWaffleVisualizationState(shape='waffle', layers=[kbn_layer_visualization])


def compile_lens_waffle_chart(
    lens_waffle_chart: LensWaffleChart,
) -> tuple[str, dict[str, KbnLensColumnTypes], KbnWaffleVisualizationState]:
    """Compile a LensWaffleChart config object into a Kibana Waffle visualization state.

    Args:
        lens_waffle_chart: The LensWaffleChart config object.

    Returns:
        A tuple containing:
        - The layer ID
        - A dictionary of column IDs to column configurations
        - The compiled visualization state

    """
    layer_id = lens_waffle_chart.get_id()

    # Compile the single metric
    kbn_metric_column_by_id: dict[str, KbnLensMetricColumnTypes] = {}
    result = compile_lens_metric(metric=lens_waffle_chart.metric)
    metric_id = result.primary_id
    metric = result.primary_column
    kbn_metric_column_by_id[metric_id] = metric
    kbn_metric_column_by_id.update(result.helper_columns)

    # Compile the breakdown (if present)
    breakdown_id: str | None = None
    breakdown_columns: dict[str, KbnLensColumnTypes] = {}
    collapse_dimensions: list[tuple[str, str | None]] = []
    if lens_waffle_chart.breakdown is not None:
        compiled_breakdown = compile_lens_dimensions(
            dimensions=[lens_waffle_chart.breakdown], kbn_metric_column_by_id=kbn_metric_column_by_id
        )
        breakdown_id = next(iter(compiled_breakdown.keys()))
        breakdown_columns = dict(compiled_breakdown)
        collapse_dimensions.append((breakdown_id, lens_waffle_chart.breakdown.collapse))
    collapse_fns = build_collapse_fns(collapse_dimensions)

    kbn_columns: dict[str, KbnLensColumnTypes] = {**breakdown_columns, **kbn_metric_column_by_id}

    return (
        layer_id,
        kbn_columns,
        compile_waffle_chart_visualization_state(
            layer_id=layer_id,
            chart=lens_waffle_chart,
            breakdown_id=breakdown_id,
            metric_id=metric_id,
            collapse_fns=collapse_fns,
        ),
    )


def compile_esql_waffle_chart(
    esql_waffle_chart: ESQLWaffleChart,
) -> tuple[str, list[KbnESQLColumnTypes], KbnWaffleVisualizationState]:
    """Compile an ESQLWaffleChart config object into a Kibana Waffle visualization state.

    Args:
        esql_waffle_chart: The ESQLWaffleChart config object.

    Returns:
        A tuple containing:
        - The layer ID
        - A list of ESQL column configurations
        - The compiled visualization state

    """
    layer_id = esql_waffle_chart.get_id()

    # Compile the single metric
    metric = compile_esql_metric(esql_waffle_chart.metric)
    metric_id = metric.columnId

    # Compile the breakdown (if present)
    breakdown_id: str | None = None
    breakdown_columns: list[KbnESQLColumnTypes] = []
    collapse_dimensions: list[tuple[str, str | None]] = []
    if esql_waffle_chart.breakdown is not None:
        compiled_breakdown = compile_esql_dimensions(dimensions=[esql_waffle_chart.breakdown])
        breakdown_id = compiled_breakdown[0].columnId
        breakdown_columns = list(compiled_breakdown)
        collapse_dimensions.append((breakdown_id, esql_waffle_chart.breakdown.collapse))
    collapse_fns = build_collapse_fns(collapse_dimensions)

    kbn_columns: list[KbnESQLColumnTypes] = [metric, *breakdown_columns]

    return (
        layer_id,
        kbn_columns,
        compile_waffle_chart_visualization_state(
            layer_id=layer_id,
            chart=esql_waffle_chart,
            breakdown_id=breakdown_id,
            metric_id=metric_id,
            collapse_fns=collapse_fns,
        ),
    )
