"""Compile Lens treemap visualizations into their Kibana view models."""

from dataclasses import dataclass

from kb_dashboard_core.panels.charts.base.compile import build_collapse_fns, compile_color_value_mapping
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
from kb_dashboard_core.panels.charts.pie.view import (
    KbnPieStateVisualizationLayer,
    KbnPieVisualizationState,
)
from kb_dashboard_core.panels.charts.treemap.config import ESQLTreemapChart, LensTreemapChart, TreeMapLegend, TreemapTitlesAndText
from kb_dashboard_core.shared.defaults import default_false


@dataclass
class LegendOptions:
    """Compiled legend options for treemap visualization."""

    display: str
    position: str | None
    size: str | None
    truncate: bool | None
    max_lines: int | None
    nested: bool | None
    show_single_series: bool | None


def _compile_number_display(titles_and_text: TreemapTitlesAndText | None) -> str:
    """Compile number display setting from YAML config to Kibana format."""
    if titles_and_text is None or titles_and_text.slice_values is None:
        return 'percent'
    slice_values = titles_and_text.slice_values
    if slice_values == 'integer':
        return 'value'
    if slice_values == 'hide':
        return 'hidden'
    return slice_values


def _compile_category_display(titles_and_text: TreemapTitlesAndText | None) -> str:
    """Compile category display setting from YAML config to Kibana format."""
    if titles_and_text is None or titles_and_text.slice_labels is None:
        return 'default'
    return 'default' if titles_and_text.slice_labels == 'show' else 'hide'


def _compile_legend_options(legend: TreeMapLegend | None) -> LegendOptions:
    """Compile legend options from YAML config to Kibana format."""
    if legend is None:
        return LegendOptions(
            display='default',
            position=None,
            size=None,
            truncate=None,
            max_lines=None,
            nested=None,
            show_single_series=None,
        )

    legend_display = 'default'
    if legend.visible is not None:
        legend_display = 'default' if legend.visible == 'auto' else legend.visible

    truncate_legend = None
    legend_max_lines = None
    if isinstance(legend.truncate_labels, int):
        if legend.truncate_labels == 0:
            truncate_legend = False
        else:
            legend_max_lines = legend.truncate_labels

    return LegendOptions(
        display=legend_display,
        position=legend.position,
        size=legend.width,
        truncate=truncate_legend,
        max_lines=legend_max_lines,
        nested=legend.nested,
        show_single_series=legend.show_single_series,
    )


def compile_treemap_chart_visualization_state(
    *,
    layer_id: str,
    chart: LensTreemapChart | ESQLTreemapChart,
    slice_by_ids: list[str],
    metric_ids: list[str],
    collapse_fns: dict[str, str] | None,
) -> KbnPieVisualizationState:
    """Compile a TreemapChart config object into a Kibana treemap visualization state."""
    number_display = _compile_number_display(chart.titles_and_text)
    category_display = _compile_category_display(chart.titles_and_text)
    legend_options = _compile_legend_options(chart.legend)
    kbn_color_mapping = compile_color_value_mapping(chart.color)

    allow_multiple_metrics = True if len(metric_ids) > 1 else None
    percent_decimals = None
    if chart.titles_and_text is not None and chart.titles_and_text.value_decimal_places is not None:
        percent_decimals = chart.titles_and_text.value_decimal_places

    kbn_layer_visualization = KbnPieStateVisualizationLayer(
        layerId=layer_id,
        primaryGroups=slice_by_ids,
        secondaryGroups=None,
        metrics=metric_ids,
        allowMultipleMetrics=allow_multiple_metrics,
        collapseFns=collapse_fns if collapse_fns else None,
        numberDisplay=number_display,
        categoryDisplay=category_display,
        legendDisplay=legend_options.display,
        legendPosition=legend_options.position,
        nestedLegend=default_false(legend_options.nested),
        layerType='data',
        colorMapping=kbn_color_mapping,
        emptySizeRatio=None,
        legendSize=legend_options.size,
        truncateLegend=False if legend_options.truncate is False else None,
        legendMaxLines=legend_options.max_lines,
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
    metric_ids: list[str] = []
    for metric_config in lens_treemap_chart.metrics:
        result = compile_lens_metric(metric=metric_config)
        metric_id = result.primary_id
        metric = result.primary_column
        kbn_metric_column_by_id[metric_id] = metric
        kbn_metric_column_by_id.update(result.helper_columns)
        metric_ids.append(metric_id)

    slices_by_ids = compile_lens_dimensions(dimensions=lens_treemap_chart.dimensions, kbn_metric_column_by_id=kbn_metric_column_by_id)
    all_dimension_ids = list(slices_by_ids.keys())

    collapse_fns = build_collapse_fns(
        [
            (compiled_dim_id, dim_config.collapse)
            for dim_config, compiled_dim_id in zip(lens_treemap_chart.dimensions, all_dimension_ids, strict=True)
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

    metrics = [compile_esql_metric(m) for m in esql_treemap_chart.metrics]
    metric_ids = [m.columnId for m in metrics]

    dimensions = compile_esql_dimensions(dimensions=esql_treemap_chart.dimensions)
    all_dimension_ids = [d.columnId for d in dimensions]

    collapse_fns = build_collapse_fns(
        [
            (compiled_dim.columnId, dim_config.collapse)
            for dim_config, compiled_dim in zip(esql_treemap_chart.dimensions, dimensions, strict=True)
        ]
    )

    kbn_columns: list[KbnESQLColumnTypes] = [*metrics, *dimensions]

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
