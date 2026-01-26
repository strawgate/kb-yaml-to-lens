"""Compile Lens mosaic visualizations into their Kibana view models."""

from kb_dashboard_core.panels.charts.base.compile import compile_color_mapping
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
from kb_dashboard_core.panels.charts.mosaic.config import ESQLMosaicChart, LensMosaicChart
from kb_dashboard_core.panels.charts.mosaic.view import (
    KbnMosaicStateVisualizationLayer,
    KbnMosaicVisualizationState,
)
from kb_dashboard_core.shared.defaults import default_false


def compile_mosaic_chart_visualization_state(  # noqa: PLR0913
    *,
    layer_id: str,
    chart: LensMosaicChart | ESQLMosaicChart,
    dimension_id: str,
    breakdown_id: str | None,
    metric_id: str,
    collapse_fns: dict[str, str] | None,
) -> KbnMosaicVisualizationState:
    """Compile a MosaicChart config object into a Kibana Mosaic visualization state.

    Args:
        layer_id: The ID of the layer.
        chart: The MosaicChart config object.
        dimension_id: The ID of the primary dimension.
        breakdown_id: The ID of the breakdown dimension, or None if not specified.
        metric_id: The ID of the metric.
        collapse_fns: Mapping of dimension ID to collapse function.

    Returns:
        The compiled visualization state for the mosaic chart.

    """
    number_display = 'percent'
    if chart.titles_and_text is not None and chart.titles_and_text.value_format is not None:
        number_display = chart.titles_and_text.value_format

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
            legend_display = chart.legend.visible
        if chart.legend.width is not None:
            legend_size = chart.legend.width
        if chart.legend.truncate_labels is not None:
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

    kbn_color_mapping = compile_color_mapping(chart.color)

    percent_decimals = None
    if chart.titles_and_text is not None and chart.titles_and_text.value_decimal_places is not None:
        percent_decimals = chart.titles_and_text.value_decimal_places

    kbn_layer_visualization = KbnMosaicStateVisualizationLayer(
        layerId=layer_id,
        primaryGroups=[dimension_id],
        secondaryGroups=[breakdown_id] if breakdown_id is not None else None,
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

    return KbnMosaicVisualizationState(shape='mosaic', layers=[kbn_layer_visualization])


def compile_lens_mosaic_chart(
    lens_mosaic_chart: LensMosaicChart,
) -> tuple[str, dict[str, KbnLensColumnTypes], KbnMosaicVisualizationState]:
    """Compile a LensMosaicChart config object into a Kibana Mosaic visualization state.

    Args:
        lens_mosaic_chart: The LensMosaicChart config object.

    Returns:
        A tuple containing:
        - The layer ID
        - A dictionary of column IDs to column configurations
        - The compiled visualization state

    """
    layer_id = lens_mosaic_chart.get_id()

    # Compile the single metric
    kbn_metric_column_by_id: dict[str, KbnLensMetricColumnTypes] = {}
    result = compile_lens_metric(metric=lens_mosaic_chart.metric)
    metric_id = result.primary_id
    metric = result.primary_column
    kbn_metric_column_by_id[metric_id] = metric
    kbn_metric_column_by_id.update(result.helper_columns)

    # Compile the dimension
    dimension_columns = compile_lens_dimensions(dimensions=[lens_mosaic_chart.dimension], kbn_metric_column_by_id=kbn_metric_column_by_id)
    dimension_id = next(iter(dimension_columns.keys()))

    # Compile the breakdown (if present)
    breakdown_id: str | None = None
    breakdown_columns: dict[str, KbnLensColumnTypes] = {}
    if lens_mosaic_chart.breakdown is not None:
        compiled_breakdown = compile_lens_dimensions(
            dimensions=[lens_mosaic_chart.breakdown], kbn_metric_column_by_id=kbn_metric_column_by_id
        )
        breakdown_id = next(iter(compiled_breakdown.keys()))
        breakdown_columns = dict(compiled_breakdown)

    # Build collapse functions
    collapse_fns: dict[str, str] | None = None
    if lens_mosaic_chart.dimension.collapse is not None:
        collapse_fns = {dimension_id: str(lens_mosaic_chart.dimension.collapse)}
    if lens_mosaic_chart.breakdown is not None and lens_mosaic_chart.breakdown.collapse is not None and breakdown_id is not None:
        if collapse_fns is None:
            collapse_fns = {}
        collapse_fns[breakdown_id] = str(lens_mosaic_chart.breakdown.collapse)

    kbn_columns: dict[str, KbnLensColumnTypes] = {**dict(dimension_columns), **breakdown_columns, **kbn_metric_column_by_id}

    return (
        layer_id,
        kbn_columns,
        compile_mosaic_chart_visualization_state(
            layer_id=layer_id,
            chart=lens_mosaic_chart,
            dimension_id=dimension_id,
            breakdown_id=breakdown_id,
            metric_id=metric_id,
            collapse_fns=collapse_fns,
        ),
    )


def compile_esql_mosaic_chart(
    esql_mosaic_chart: ESQLMosaicChart,
) -> tuple[str, list[KbnESQLColumnTypes], KbnMosaicVisualizationState]:
    """Compile an ESQLMosaicChart config object into a Kibana Mosaic visualization state.

    Args:
        esql_mosaic_chart: The ESQLMosaicChart config object.

    Returns:
        A tuple containing:
        - The layer ID
        - A list of ESQL column configurations
        - The compiled visualization state

    """
    layer_id = esql_mosaic_chart.get_id()

    # Compile the single metric
    metric = compile_esql_metric(esql_mosaic_chart.metric)
    metric_id = metric.columnId

    # Compile the dimension
    dimensions = compile_esql_dimensions(dimensions=[esql_mosaic_chart.dimension])
    dimension_id = dimensions[0].columnId

    # Compile the breakdown (if present)
    breakdown_id: str | None = None
    breakdown_columns: list[KbnESQLColumnTypes] = []
    if esql_mosaic_chart.breakdown is not None:
        compiled_breakdown = compile_esql_dimensions(dimensions=[esql_mosaic_chart.breakdown])
        breakdown_id = compiled_breakdown[0].columnId
        breakdown_columns = list(compiled_breakdown)

    # Build collapse functions
    collapse_fns: dict[str, str] | None = None
    if esql_mosaic_chart.dimension.collapse is not None:
        collapse_fns = {dimension_id: str(esql_mosaic_chart.dimension.collapse)}
    if esql_mosaic_chart.breakdown is not None and esql_mosaic_chart.breakdown.collapse is not None and breakdown_id is not None:
        if collapse_fns is None:
            collapse_fns = {}
        collapse_fns[breakdown_id] = str(esql_mosaic_chart.breakdown.collapse)

    kbn_columns: list[KbnESQLColumnTypes] = [metric, *list(dimensions), *breakdown_columns]

    return (
        layer_id,
        kbn_columns,
        compile_mosaic_chart_visualization_state(
            layer_id=layer_id,
            chart=esql_mosaic_chart,
            dimension_id=dimension_id,
            breakdown_id=breakdown_id,
            metric_id=metric_id,
            collapse_fns=collapse_fns,
        ),
    )
