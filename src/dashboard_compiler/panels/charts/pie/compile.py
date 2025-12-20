"""Compile Lens pie visualizations into their Kibana view models."""

from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_dimensions, compile_esql_metric
from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnESQLColumnTypes,
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
from dashboard_compiler.panels.charts.view import (
    KbnLayerColorMapping,
)
from dashboard_compiler.shared.config import random_id_generator


def compile_pie_chart_visualization_state(
    layer_id: str,
    chart: LensPieChart | ESQLPieChart,
    slice_by_ids: list[str],
    secondary_slice_by_ids: list[str] | None,
    metric_ids: list[str],
) -> KbnPieVisualizationState:
    """Compile a PieChart config object into a Kibana Pie visualization state.

    Args:
        layer_id (str): The ID of the layer.
        chart (LensPieChart | ESQLPieChart): The PieChart config object.
        slice_by_ids (list[str]): The IDs of the slice by dimensions.
        secondary_slice_by_ids (list[str] | None): The IDs of the secondary slice by dimensions.
        metric_ids (list[str]): The IDs of the metric.

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

    kbn_color_mapping = KbnLayerColorMapping(paletteId='default')
    if chart.color and chart.color.palette:
        kbn_color_mapping = KbnLayerColorMapping(paletteId=chart.color.palette)

    # Determine if multiple metrics are allowed
    allow_multiple_metrics = True if len(metric_ids) > 1 else None
    empty_size_ratio = 0.0 if len(metric_ids) > 1 else None

    kbn_layer_visualization = KbnPieStateVisualizationLayer(
        layerId=layer_id,
        primaryGroups=slice_by_ids,
        secondaryGroups=secondary_slice_by_ids if secondary_slice_by_ids else None,
        metrics=metric_ids,
        allowMultipleMetrics=allow_multiple_metrics,
        collapseFns=chart.collapse_fns if chart.collapse_fns else None,
        numberDisplay=number_display,
        categoryDisplay=category_display,
        legendDisplay=legend_display,
        nestedLegend=False,
        layerType='data',
        colorMapping=kbn_color_mapping,
        emptySizeRatio=empty_size_ratio,
        legendSize=legend_size,
        truncateLegend=False if truncate_legend == 0 else None,
        legendMaxLines=legend_max_lines,
    )

    return KbnPieVisualizationState(shape=shape, layers=[kbn_layer_visualization])


def compile_lens_pie_chart(lens_pie_chart: LensPieChart) -> tuple[str, dict[str, KbnLensColumnTypes], KbnPieVisualizationState]:
    """Compile a LensPieChart config object into a Kibana Pie visualization state.

    Args:
        lens_pie_chart (LensPieChart): The LensPieChart config object.

    Returns:
        tuple[str, dict[str, KbnLensColumnTypes], KbnPieVisualizationState]: The layer ID and the compiled visualization state.

    """
    layer_id = lens_pie_chart.id or random_id_generator()

    # Handle both single metric and multiple metrics
    kbn_metric_column_by_id: dict[str, KbnLensMetricColumnTypes] = {}
    metric_ids: list[str] = []

    if lens_pie_chart.metrics:
        # Multiple metrics mode
        for metric_cfg in lens_pie_chart.metrics:
            metric_id, metric = compile_lens_metric(metric=metric_cfg)
            kbn_metric_column_by_id[metric_id] = metric
            metric_ids.append(metric_id)
    elif lens_pie_chart.metric:
        # Single metric mode (backward compatibility)
        metric_id, metric = compile_lens_metric(metric=lens_pie_chart.metric)
        kbn_metric_column_by_id[metric_id] = metric
        metric_ids.append(metric_id)
    else:
        raise ValueError('Either metric or metrics must be provided for LensPieChart')

    # Compile primary dimensions
    slices_by_ids = compile_lens_dimensions(dimensions=lens_pie_chart.slice_by, kbn_metric_column_by_id=kbn_metric_column_by_id)
    slice_by_ids = list(slices_by_ids.keys())

    # Compile secondary dimensions if provided
    secondary_slice_by_ids = None
    secondary_slices_by_ids = {}
    if lens_pie_chart.secondary_slice_by:
        secondary_slices_by_ids = compile_lens_dimensions(
            dimensions=lens_pie_chart.secondary_slice_by, kbn_metric_column_by_id=kbn_metric_column_by_id
        )
        secondary_slice_by_ids = list(secondary_slices_by_ids.keys())

    kbn_columns: dict[str, KbnLensColumnTypes] = {**slices_by_ids, **secondary_slices_by_ids, **kbn_metric_column_by_id}

    return (
        layer_id,
        kbn_columns,
        compile_pie_chart_visualization_state(layer_id, lens_pie_chart, slice_by_ids, secondary_slice_by_ids, metric_ids),
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
    layer_id = esql_pie_chart.id or random_id_generator()

    # Handle both single metric and multiple metrics
    metrics: list[KbnESQLColumnTypes] = []
    metric_ids: list[str] = []

    if esql_pie_chart.metrics:
        # Multiple metrics mode
        for metric_cfg in esql_pie_chart.metrics:
            metric = compile_esql_metric(metric_cfg)
            metrics.append(metric)
            metric_ids.append(metric.columnId)
    elif esql_pie_chart.metric:
        # Single metric mode (backward compatibility)
        metric = compile_esql_metric(esql_pie_chart.metric)
        metrics.append(metric)
        metric_ids.append(metric.columnId)
    else:
        raise ValueError('Either metric or metrics must be provided for ESQLPieChart')

    # Compile primary dimensions
    dimensions = compile_esql_dimensions(dimensions=esql_pie_chart.slice_by)

    # Compile secondary dimensions if provided
    secondary_dimensions = []
    secondary_slice_by_ids = None
    if esql_pie_chart.secondary_slice_by:
        secondary_dimensions = compile_esql_dimensions(dimensions=esql_pie_chart.secondary_slice_by)
        secondary_slice_by_ids = [column.columnId for column in secondary_dimensions]

    kbn_columns: list[KbnESQLColumnTypes] = [*metrics, *dimensions, *secondary_dimensions]

    return (
        layer_id,
        kbn_columns,
        compile_pie_chart_visualization_state(
            layer_id=layer_id,
            chart=esql_pie_chart,
            slice_by_ids=[column.columnId for column in dimensions],
            secondary_slice_by_ids=secondary_slice_by_ids,
            metric_ids=metric_ids,
        ),
    )
