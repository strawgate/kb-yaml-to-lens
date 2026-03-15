"""Compile Lens pie visualizations into their Kibana view models."""

from dataclasses import dataclass
from typing import Literal

from kb_dashboard_core.panels.charts.base.compile import build_collapse_fns, compile_color_value_mapping, map_legend_size
from kb_dashboard_core.panels.charts.base.view import KbnLegendSize
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
from kb_dashboard_core.panels.charts.pie.config import ESQLPieChart, LensPieChart, PieLegend, PieTitlesAndText
from kb_dashboard_core.panels.charts.pie.view import (
    KbnPieStateVisualizationLayer,
    KbnPieVisualizationState,
)
from kb_dashboard_core.shared.compile import split_dimensions
from kb_dashboard_core.shared.defaults import default_false

DONUT_SIZE_RATIOS: dict[str, float] = {'small': 0.3, 'medium': 0.5, 'large': 0.7}


@dataclass
class LegendOptions:
    """Compiled legend options for pie chart visualization."""

    display: str
    """Legend display mode ('default', 'show', 'hide')."""

    position: str | None
    """Legend position ('top', 'right', 'bottom', 'left')."""

    size: KbnLegendSize | None
    """Legend size/width."""

    truncate: bool | None
    """Whether to truncate legend labels."""

    max_lines: int | None
    """Maximum number of lines for legend labels."""

    nested: bool | None
    """Whether to nest legend entries."""

    show_single_series: bool | None
    """Whether to show legend for single series."""


def _compile_number_display(titles_and_text: PieTitlesAndText | None) -> str:
    """Compile number display setting from YAML config to Kibana format."""
    if titles_and_text is None or titles_and_text.slice_values is None:
        return 'percent'
    slice_values = titles_and_text.slice_values
    if slice_values == 'integer':
        return 'value'
    if slice_values == 'hide':
        return 'hidden'
    return slice_values


def _compile_category_display(titles_and_text: PieTitlesAndText | None) -> str:
    """Compile category display setting from YAML config to Kibana format."""
    if titles_and_text is None or titles_and_text.slice_labels is None:
        return 'default'
    return 'default' if titles_and_text.slice_labels == 'auto' else titles_and_text.slice_labels


def _compile_legend_options(legend: PieLegend | None) -> LegendOptions:
    """Compile legend options from YAML config to Kibana format.

    Args:
        legend: The legend configuration from YAML.

    Returns:
        LegendOptions with compiled legend settings.

    """
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
        size=map_legend_size(legend.width),
        truncate=truncate_legend,
        max_lines=legend_max_lines,
        nested=legend.nested,
        show_single_series=legend.show_single_series,
    )


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
    shape: Literal['pie', 'donut'] = 'pie'
    empty_size_ratio: float | None = None

    if chart.appearance is not None and chart.appearance.donut is not None:
        shape = 'donut'
        donut_size = chart.appearance.donut
        ratio = DONUT_SIZE_RATIOS.get(donut_size)
        if ratio is None:
            msg = f"Unsupported donut size: '{donut_size}'. Supported values: {list(DONUT_SIZE_RATIOS.keys())}"
            raise ValueError(msg)
        empty_size_ratio = ratio

    number_display = _compile_number_display(chart.titles_and_text)
    category_display = _compile_category_display(chart.titles_and_text)

    legend_options = _compile_legend_options(chart.legend)

    kbn_color_mapping = compile_color_value_mapping(chart.color)

    allow_multiple_metrics = True if len(metric_ids) > 1 else None
    if len(metric_ids) > 1 and empty_size_ratio is None:
        empty_size_ratio = 0.0

    percent_decimals = None
    if chart.titles_and_text is not None and chart.titles_and_text.value_decimal_places is not None:
        percent_decimals = chart.titles_and_text.value_decimal_places

    kbn_layer_visualization = KbnPieStateVisualizationLayer(
        layerId=layer_id,
        primaryGroups=slice_by_ids,
        secondaryGroups=secondary_slice_by_ids if secondary_slice_by_ids else None,
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
        emptySizeRatio=empty_size_ratio,
        legendSize=legend_options.size,
        truncateLegend=False if legend_options.truncate is False else None,
        legendMaxLines=legend_options.max_lines,
        showSingleSeries=legend_options.show_single_series,
        percentDecimals=percent_decimals,
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
        result = compile_lens_metric(metric=metric_config)
        metric_id = result.primary_id
        metric = result.primary_column
        kbn_metric_column_by_id[metric_id] = metric
        kbn_metric_column_by_id.update(result.helper_columns)
        metric_ids.append(metric_id)

    slices_by_ids = compile_lens_dimensions(dimensions=lens_pie_chart.breakdowns, kbn_metric_column_by_id=kbn_metric_column_by_id)
    all_dimension_ids = list(slices_by_ids.keys())

    primary_dimension_ids, secondary_dimension_ids = split_dimensions(all_dimension_ids)

    collapse_fns = build_collapse_fns(
        [
            (compiled_dim_id, dim_config.collapse)
            for dim_config, compiled_dim_id in zip(lens_pie_chart.breakdowns, all_dimension_ids, strict=True)
        ]
    )

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

    dimensions = compile_esql_dimensions(dimensions=esql_pie_chart.breakdowns)
    all_dimension_ids = [d.columnId for d in dimensions]

    primary_dimension_ids, secondary_dimension_ids = split_dimensions(all_dimension_ids)

    collapse_fns = build_collapse_fns(
        [
            (compiled_dim.columnId, dim_config.collapse)
            for dim_config, compiled_dim in zip(esql_pie_chart.breakdowns, dimensions, strict=True)
        ]
    )

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
