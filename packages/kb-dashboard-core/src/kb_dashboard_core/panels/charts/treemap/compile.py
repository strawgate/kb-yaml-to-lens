"""Compile Lens treemap visualizations into their Kibana view models."""

from kb_dashboard_core.panels.charts.base.compile import (
    build_collapse_fns,
    compile_color_value_mapping,
    compile_partition_category_display,
    compile_partition_legend_options,
    compile_partition_number_display,
)
from kb_dashboard_core.panels.charts.esql.columns.compile import compile_esql_dimensions, compile_esql_metric
from kb_dashboard_core.panels.charts.esql.columns.view import KbnESQLColumnTypes
from kb_dashboard_core.panels.charts.lens.columns.view import (
    KbnLensColumnTypes,
    KbnLensMetricColumnTypes,
)
from kb_dashboard_core.panels.charts.lens.dimensions.compile import compile_lens_dimensions
from kb_dashboard_core.panels.charts.lens.metrics.compile import compile_lens_metric
from kb_dashboard_core.panels.charts.pie.view import (
    KbnPieStateVisualizationLayer,
    KbnPieVisualizationState,
)
from kb_dashboard_core.panels.charts.treemap.config import (
    ESQLTreemapChart,
    LensTreemapChart,
)
from kb_dashboard_core.shared.defaults import default_false


def compile_treemap_chart_visualization_state(
    *,
    layer_id: str,
    chart: LensTreemapChart | ESQLTreemapChart,
    slice_by_ids: list[str],
    metric_ids: list[str],
    collapse_fns: dict[str, str] | None,
) -> KbnPieVisualizationState:
    """Compile a TreemapChart config object into a Kibana treemap visualization state."""
    values = chart.appearance.values if chart.appearance is not None else None
    categories = chart.appearance.categories if chart.appearance is not None else None
    number_display = compile_partition_number_display(
        values.format if values is not None else None,
    )
    category_display = compile_partition_category_display(
        categories.position if categories is not None else None,
    )
    legend_options = compile_partition_legend_options(chart.legend)
    kbn_color_mapping = compile_color_value_mapping(chart.color)

    percent_decimals = None
    if values is not None and values.decimal_places is not None:
        percent_decimals = values.decimal_places

    kbn_layer_visualization = KbnPieStateVisualizationLayer(
        layerId=layer_id,
        primaryGroups=slice_by_ids,
        secondaryGroups=None,
        metrics=metric_ids,
        allowMultipleMetrics=None,
        collapseFns=collapse_fns or None,
        numberDisplay=number_display,
        categoryDisplay=category_display,
        legendDisplay=legend_options.legend_display,
        legendPosition=legend_options.legend_position or 'right',
        nestedLegend=default_false(legend_options.nested_legend),
        layerType='data',
        colorMapping=kbn_color_mapping,
        emptySizeRatio=None,
        legendSize=legend_options.legend_size,
        truncateLegend=False if legend_options.truncate_legend is False else None,
        legendMaxLines=legend_options.legend_max_lines,
        showSingleSeries=legend_options.show_single_series,
        percentDecimals=percent_decimals,
    )

    return KbnPieVisualizationState(shape='treemap', layers=[kbn_layer_visualization])


def compile_lens_treemap_chart(
    lens_treemap_chart: LensTreemapChart,
) -> tuple[str, dict[str, KbnLensColumnTypes], KbnPieVisualizationState]:
    """Compile a LensTreemapChart config object into a Kibana treemap visualization state."""
    layer_id = lens_treemap_chart.get_id()

    kbn_metric_column_by_id: dict[str, KbnLensMetricColumnTypes] = {}
    result = compile_lens_metric(metric=lens_treemap_chart.metric)
    metric_id = result.primary_id
    kbn_metric_column_by_id[metric_id] = result.primary_column
    kbn_metric_column_by_id.update(result.helper_columns)
    metric_ids = [metric_id]

    slices_by_ids = compile_lens_dimensions(dimensions=lens_treemap_chart.breakdowns, kbn_metric_column_by_id=kbn_metric_column_by_id)
    all_dimension_ids = list(slices_by_ids.keys())

    collapse_fns = build_collapse_fns(
        [
            (compiled_dim_id, dim_config.collapse)
            for dim_config, compiled_dim_id in zip(lens_treemap_chart.breakdowns, all_dimension_ids, strict=True)
        ]
    )

    kbn_columns: dict[str, KbnLensColumnTypes] = {**slices_by_ids, **kbn_metric_column_by_id}

    return (
        layer_id,
        kbn_columns,
        compile_treemap_chart_visualization_state(
            layer_id=layer_id,
            chart=lens_treemap_chart,
            slice_by_ids=all_dimension_ids,
            metric_ids=metric_ids,
            collapse_fns=collapse_fns,
        ),
    )


def compile_esql_treemap_chart(
    esql_treemap_chart: ESQLTreemapChart,
) -> tuple[str, list[KbnESQLColumnTypes], KbnPieVisualizationState]:
    """Compile an ESQLTreemapChart config object into a Kibana treemap visualization state."""
    layer_id = esql_treemap_chart.get_id()

    metric = compile_esql_metric(esql_treemap_chart.metric)
    metric_ids = [metric.columnId]

    dimensions = compile_esql_dimensions(dimensions=esql_treemap_chart.breakdowns)
    all_dimension_ids = [d.columnId for d in dimensions]

    # ES|QL treemap breakdowns do not support collapse
    collapse_fns = build_collapse_fns([])

    kbn_columns: list[KbnESQLColumnTypes] = [metric, *dimensions]

    return (
        layer_id,
        kbn_columns,
        compile_treemap_chart_visualization_state(
            layer_id=layer_id,
            chart=esql_treemap_chart,
            slice_by_ids=all_dimension_ids,
            metric_ids=metric_ids,
            collapse_fns=collapse_fns,
        ),
    )
