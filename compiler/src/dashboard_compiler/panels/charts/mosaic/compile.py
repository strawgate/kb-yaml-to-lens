"""Compile Lens mosaic visualizations into their Kibana view models."""

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
from dashboard_compiler.panels.charts.mosaic.config import ESQLMosaicChart, LensMosaicChart
from dashboard_compiler.panels.charts.mosaic.view import (
    KbnMosaicStateVisualizationLayer,
    KbnMosaicVisualizationState,
)
from dashboard_compiler.shared.compile import split_dimensions
from dashboard_compiler.shared.defaults import default_false


def compile_mosaic_chart_visualization_state(  # noqa: PLR0913
    *,
    layer_id: str,
    chart: LensMosaicChart | ESQLMosaicChart,
    group_by_ids: list[str],
    secondary_group_by_ids: list[str] | None,
    metric_ids: list[str],
    collapse_fns: dict[str, str] | None,
) -> KbnMosaicVisualizationState:
    """Compile a MosaicChart config object into a Kibana Mosaic visualization state.

    Args:
        layer_id: The ID of the layer.
        chart: The MosaicChart config object.
        group_by_ids: The IDs of the primary group by dimensions.
        secondary_group_by_ids: The IDs of the secondary group by dimensions.
        metric_ids: The IDs of the metrics.
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

    kbn_layer_visualization = KbnMosaicStateVisualizationLayer(
        layerId=layer_id,
        primaryGroups=group_by_ids,
        secondaryGroups=secondary_group_by_ids if secondary_group_by_ids else None,
        metrics=metric_ids,
        allowMultipleMetrics=False,
        collapseFns=collapse_fns if collapse_fns else None,
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

    kbn_metric_column_by_id: dict[str, KbnLensMetricColumnTypes] = {}
    metric_ids: list[str] = []
    for metric_config in lens_mosaic_chart.metrics:
        metric_id, metric = compile_lens_metric(metric=metric_config)
        kbn_metric_column_by_id[metric_id] = metric
        metric_ids.append(metric_id)

    groups_by_ids = compile_lens_dimensions(dimensions=lens_mosaic_chart.dimensions, kbn_metric_column_by_id=kbn_metric_column_by_id)
    all_dimension_ids = list(groups_by_ids.keys())

    primary_dimension_ids, secondary_dimension_ids = split_dimensions(all_dimension_ids)

    collapse_fns: dict[str, str] | None = None
    for dim_config, compiled_dim_id in zip(lens_mosaic_chart.dimensions, all_dimension_ids, strict=True):
        if dim_config.collapse is not None:
            if collapse_fns is None:
                collapse_fns = {}
            collapse_fns[compiled_dim_id] = str(dim_config.collapse)

    kbn_columns: dict[str, KbnLensColumnTypes] = {**groups_by_ids, **kbn_metric_column_by_id}

    return (
        layer_id,
        kbn_columns,
        compile_mosaic_chart_visualization_state(
            layer_id=layer_id,
            chart=lens_mosaic_chart,
            group_by_ids=primary_dimension_ids,
            secondary_group_by_ids=secondary_dimension_ids,
            metric_ids=metric_ids,
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

    metrics = [compile_esql_metric(m) for m in esql_mosaic_chart.metrics]
    metric_ids = [m.columnId for m in metrics]

    dimensions = compile_esql_dimensions(dimensions=esql_mosaic_chart.dimensions)
    all_dimension_ids = [d.columnId for d in dimensions]

    primary_dimension_ids, secondary_dimension_ids = split_dimensions(all_dimension_ids)

    collapse_fns: dict[str, str] | None = None
    for dim_config, compiled_dim in zip(esql_mosaic_chart.dimensions, dimensions, strict=True):
        if dim_config.collapse is not None:
            if collapse_fns is None:
                collapse_fns = {}
            collapse_fns[compiled_dim.columnId] = str(dim_config.collapse)

    kbn_columns: list[KbnESQLColumnTypes] = [*metrics, *dimensions]

    return (
        layer_id,
        kbn_columns,
        compile_mosaic_chart_visualization_state(
            layer_id=layer_id,
            chart=esql_mosaic_chart,
            group_by_ids=primary_dimension_ids,
            secondary_group_by_ids=secondary_dimension_ids,
            metric_ids=metric_ids,
            collapse_fns=collapse_fns,
        ),
    )
