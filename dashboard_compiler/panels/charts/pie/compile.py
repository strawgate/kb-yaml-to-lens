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
    metric_ids: list[str],
) -> KbnPieVisualizationState:
    """Compile a PieChart config object into a Kibana Pie visualization state.

    Args:
        layer_id (str): The ID of the layer.
        chart (LensPieChart | ESQLPieChart): The PieChart config object.
        slice_by_ids (list[str]): The IDs of the slice by dimensions.
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

    kbn_layer_visualization = KbnPieStateVisualizationLayer(
        layerId=layer_id,
        primaryGroups=slice_by_ids,
        metrics=metric_ids,
        numberDisplay=number_display,
        categoryDisplay=category_display,
        legendDisplay=legend_display,
        nestedLegend=False,
        layerType='data',
        colorMapping=kbn_color_mapping,
        emptySizeRatio=0 if len(metric_ids) > 1 else None,
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
    metric_id: str
    metric: KbnLensMetricColumnTypes
    metric_id, metric = compile_lens_metric(metric=lens_pie_chart.metric)

    kbn_metric_column_by_id: dict[str, KbnLensMetricColumnTypes] = {metric_id: metric}

    slices_by_ids = compile_lens_dimensions(dimensions=lens_pie_chart.slice_by, kbn_metric_column_by_id=kbn_metric_column_by_id)
    slice_by_ids = list(slices_by_ids.keys())

    kbn_columns: dict[str, KbnLensColumnTypes] = {**slices_by_ids, metric_id: metric}

    return layer_id, kbn_columns, compile_pie_chart_visualization_state(layer_id, lens_pie_chart, slice_by_ids, [metric_id])


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

    metric = compile_esql_metric(esql_pie_chart.metric)

    dimensions = compile_esql_dimensions(dimensions=esql_pie_chart.slice_by)

    kbn_columns: list[KbnESQLColumnTypes] = [metric, *dimensions]

    return (
        layer_id,
        kbn_columns,
        compile_pie_chart_visualization_state(
            layer_id=layer_id,
            chart=esql_pie_chart,
            slice_by_ids=[column.columnId for column in dimensions],
            metric_ids=[metric.columnId],
        ),
    )
