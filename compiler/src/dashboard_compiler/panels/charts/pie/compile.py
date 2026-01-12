"""Compile Lens pie visualizations into their Kibana view models."""

from dashboard_compiler.panels.charts.base.compile import compile_color_mapping
from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_dimensions, compile_esql_metric
from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnLensColumnTypes,
    KbnLensMetricColumnTypes,
)
from dashboard_compiler.panels.charts.lens.dimensions.compile import (
    compile_lens_dimensions,
)
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.pie.config import ESQLPieChart, LensPieChart
from dashboard_compiler.panels.charts.pie.view import (
    KbnPieStateVisualizationLayer,
    KbnPieVisualizationState,
)
from dashboard_compiler.shared.compile import split_dimensions
from dashboard_compiler.shared.defaults import default_false


def compile_pie_chart_visualization_state(  # noqa: PLR0913
    *,
    layer_id: str,
    chart: LensPieChart | ESQLPieChart,
    slice_by_ids: list[str],
    secondary_slice_by_ids: list[str] | None,
    metric_ids: list[str],
    collapse_fns: dict[str, str] | None,
) -> KbnPieVisualizationState:
    """Compile a PieChart config object into a Kibana Pie visualization state.

    Args:
        layer_id (str): The ID of the layer.
        chart (LensPieChart | ESQLPieChart): The PieChart config object.
        slice_by_ids (list[str]): The IDs of the slice by dimensions.
        secondary_slice_by_ids (list[str] | None): The IDs of the secondary slice by dimensions.
        metric_ids (list[str]): The IDs of the metrics.
        collapse_fns (dict[str, str] | None): Mapping of dimension ID to collapse function.

    Returns:
        tuple[str, KbnPieVisualizationState]: The layer ID and the compiled visualization state.

    """
    shape = 'pie'
    if chart.appearance and chart.appearance.donut:
        shape = 'donut'

    number_display = 'percent'
    if chart.titles_and_text and chart.titles_and_text.slice_values:
        number_display = chart.titles_and_text.slice_values

        if chart.titles_and_text.slice_values == 'integer':
            number_display = 'value'

    category_display = 'default'
    if chart.titles_and_text and chart.titles_and_text.slice_labels:
        category_display = chart.titles_and_text.slice_labels

    legend_display = 'default'
    if chart.legend and chart.legend.visible:
        legend_display = chart.legend.visible

    legend_size = None
    if chart.legend and chart.legend.width:
        legend_size = chart.legend.width

    truncate_legend = None
    legend_max_lines = None
    if chart.legend and isinstance(chart.legend.truncate_labels, int):
        if chart.legend.truncate_labels == 0:
            truncate_legend = False
        else:
            legend_max_lines = chart.legend.truncate_labels

    nested_legend = None
    if chart.legend and chart.legend.nested is not None:
        nested_legend = chart.legend.nested

    show_single_series = None
    if chart.legend and chart.legend.show_single_series is not None:
        show_single_series = chart.legend.show_single_series

    kbn_color_mapping = compile_color_mapping(chart.color)

    allow_multiple_metrics = True if len(metric_ids) > 1 else None
    empty_size_ratio = 0.0 if len(metric_ids) > 1 else None

    kbn_layer_visualization = KbnPieStateVisualizationLayer(
        layerId=layer_id,
        primaryGroups=slice_by_ids,
        secondaryGroups=secondary_slice_by_ids if secondary_slice_by_ids else None,
        metrics=metric_ids,
        allowMultipleMetrics=allow_multiple_metrics,
        collapseFns=collapse_fns if collapse_fns else None,
        numberDisplay=number_display,
        categoryDisplay=category_display,
        legendDisplay=legend_display,
        nestedLegend=default_false(nested_legend),
        layerType='data',
        colorMapping=kbn_color_mapping,
        emptySizeRatio=empty_size_ratio,
        legendSize=legend_size,
        truncateLegend=False if truncate_legend == 0 else None,
        legendMaxLines=legend_max_lines,
        showSingleSeries=show_single_series,
    )

    return KbnPieVisualizationState(shape=shape, layers=[kbn_layer_visualization])


def compile_lens_pie_chart(lens_pie_chart: LensPieChart) -> tuple[str, dict[str, KbnLensColumnTypes], KbnPieVisualizationState]:
    """Compile a LensPieChart config object into a Kibana Pie visualization state.

    Args:
        lens_pie_chart (LensPieChart): The LensPieChart config object.

    Returns:
        tuple[str, dict[str, KbnLensColumnTypes], KbnPieVisualizationState]: The layer ID and the compiled visualization state.

    """
    layer_id = lens_pie_chart.get_id()

    kbn_metric_column_by_id: dict[str, KbnLensMetricColumnTypes] = {}
    metric_ids: list[str] = []
    for metric_config in lens_pie_chart.metrics:
        metric_id, metric = compile_lens_metric(metric=metric_config)
        kbn_metric_column_by_id[metric_id] = metric
        metric_ids.append(metric_id)

    slices_by_ids = compile_lens_dimensions(dimensions=lens_pie_chart.dimensions, kbn_metric_column_by_id=kbn_metric_column_by_id)
    all_dimension_ids = list(slices_by_ids.keys())

    primary_dimension_ids, secondary_dimension_ids = split_dimensions(all_dimension_ids)

    collapse_fns: dict[str, str] | None = None
    for dim_config, compiled_dim_id in zip(lens_pie_chart.dimensions, all_dimension_ids, strict=True):
        if dim_config.collapse:
            if collapse_fns is None:
                collapse_fns = {}
            collapse_fns[compiled_dim_id] = str(dim_config.collapse)

    kbn_columns: dict[str, KbnLensColumnTypes] = {**slices_by_ids, **kbn_metric_column_by_id}

    return (
        layer_id,
        kbn_columns,
        compile_pie_chart_visualization_state(
            layer_id=layer_id,
            chart=lens_pie_chart,
            slice_by_ids=primary_dimension_ids,
            secondary_slice_by_ids=secondary_dimension_ids,
            metric_ids=metric_ids,
            collapse_fns=collapse_fns,
        ),
    )


def compile_esql_pie_chart(
    esql_pie_chart: ESQLPieChart,
) -> tuple[str, list[KbnESQLColumnTypes], KbnPieVisualizationState]:
    """Compile an ESQLPieChart config object into a Kibana Pie visualization state.

    Args:
        esql_pie_chart (ESQLPieChart): The ESQLPieChart config object.

    Returns:
        tuple[str, list[KbnESQLMetricColumnTypes], KbnESQLDimensionColumnTypes]: The layer ID and the compiled visualization state.

    """
    layer_id = esql_pie_chart.get_id()

    metrics = [compile_esql_metric(m) for m in esql_pie_chart.metrics]
    metric_ids = [m.columnId for m in metrics]

    dimensions = compile_esql_dimensions(dimensions=esql_pie_chart.dimensions)
    all_dimension_ids = [d.columnId for d in dimensions]

    primary_dimension_ids, secondary_dimension_ids = split_dimensions(all_dimension_ids)

    collapse_fns: dict[str, str] | None = None
    for dim_config, compiled_dim in zip(esql_pie_chart.dimensions, dimensions, strict=True):
        if dim_config.collapse:
            if collapse_fns is None:
                collapse_fns = {}
            collapse_fns[compiled_dim.columnId] = str(dim_config.collapse)

    kbn_columns: list[KbnESQLColumnTypes] = [*metrics, *dimensions]

    return (
        layer_id,
        kbn_columns,
        compile_pie_chart_visualization_state(
            layer_id=layer_id,
            chart=esql_pie_chart,
            slice_by_ids=primary_dimension_ids,
            secondary_slice_by_ids=secondary_dimension_ids,
            metric_ids=metric_ids,
            collapse_fns=collapse_fns,
        ),
    )
