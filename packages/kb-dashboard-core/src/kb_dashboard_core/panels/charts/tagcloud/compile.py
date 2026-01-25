"""Compile Lens tagcloud visualizations into their Kibana view models."""

from kb_dashboard_core.panels.charts.esql.columns.compile import compile_esql_dimensions, compile_esql_metric
from kb_dashboard_core.panels.charts.esql.columns.view import KbnESQLColumnTypes
from kb_dashboard_core.panels.charts.lens.columns.view import KbnLensColumnTypes
from kb_dashboard_core.panels.charts.lens.dimensions.compile import compile_lens_dimensions
from kb_dashboard_core.panels.charts.lens.metrics.compile import compile_lens_metric
from kb_dashboard_core.panels.charts.tagcloud.config import ESQLTagcloudChart, LensTagcloudChart
from kb_dashboard_core.panels.charts.tagcloud.view import KbnTagcloudVisualizationState


def compile_tagcloud_chart_visualization_state(
    layer_id: str,
    chart: LensTagcloudChart | ESQLTagcloudChart,
    tag_accessor_id: str,
    value_accessor_id: str,
) -> KbnTagcloudVisualizationState:
    """Compile tagcloud config into Kibana visualization state.

    Args:
        layer_id (str): The ID of the layer.
        chart (LensTagcloudChart | ESQLTagcloudChart): The tagcloud config object.
        tag_accessor_id (str): The ID of the tag dimension.
        value_accessor_id (str): The ID of the metric.

    Returns:
        KbnTagcloudVisualizationState: The compiled visualization state.

    """
    # Extract appearance settings with Kibana defaults
    min_font_size = 12
    max_font_size = 72
    orientation = 'single'
    show_label = True

    if chart.appearance is not None:
        if chart.appearance.min_font_size is not None:
            min_font_size = chart.appearance.min_font_size
        if chart.appearance.max_font_size is not None:
            max_font_size = chart.appearance.max_font_size
        if chart.appearance.orientation is not None:
            orientation = chart.appearance.orientation
        if chart.appearance.show_label is not None:
            show_label = chart.appearance.show_label

    return KbnTagcloudVisualizationState(
        layerId=layer_id,
        tagAccessor=tag_accessor_id,
        valueAccessor=value_accessor_id,
        maxFontSize=max_font_size,
        minFontSize=min_font_size,
        orientation=orientation,
        showLabel=show_label,
    )


def compile_lens_tagcloud_chart(
    chart: LensTagcloudChart,
) -> tuple[str, dict[str, KbnLensColumnTypes], KbnTagcloudVisualizationState]:
    """Compile Lens tagcloud chart.

    Args:
        chart (LensTagcloudChart): The LensTagcloudChart config object.

    Returns:
        tuple[str, dict[str, KbnLensColumnTypes], KbnTagcloudVisualizationState]: The layer ID, columns, and visualization state.

    """
    # Compile metric first
    result = compile_lens_metric(metric=chart.metric)
    metric_id = result.primary_id
    metric_column = result.primary_column
    kbn_metric_column_by_id = {metric_id: metric_column}
    kbn_metric_column_by_id.update(result.helper_columns)

    # Compile dimension (pass metrics for proper ordering)
    dimension_columns = compile_lens_dimensions(dimensions=[chart.dimension], kbn_metric_column_by_id=kbn_metric_column_by_id)
    tag_accessor_id = next(iter(dimension_columns.keys()))

    kbn_columns = {**dimension_columns, **kbn_metric_column_by_id}

    layer_id = chart.get_id()

    visualization_state = compile_tagcloud_chart_visualization_state(layer_id, chart, tag_accessor_id, metric_id)

    return (layer_id, kbn_columns, visualization_state)


def compile_esql_tagcloud_chart(
    chart: ESQLTagcloudChart,
) -> tuple[str, list[KbnESQLColumnTypes], KbnTagcloudVisualizationState]:
    """Compile ES|QL tagcloud chart.

    Args:
        chart (ESQLTagcloudChart): The ESQLTagcloudChart config object.

    Returns:
        tuple[str, list[KbnESQLColumnTypes], KbnTagcloudVisualizationState]: The layer ID, columns, and visualization state.

    """
    # Compile dimension to get tag_accessor_id for visualization state
    dimensions = compile_esql_dimensions(dimensions=[chart.dimension])
    tag_accessor_id = dimensions[0].columnId

    # Compile metric
    metric = compile_esql_metric(chart.metric)
    metric_id = metric.columnId

    kbn_columns: list[KbnESQLColumnTypes] = [*dimensions, metric]

    layer_id = chart.get_id()

    visualization_state = compile_tagcloud_chart_visualization_state(layer_id, chart, tag_accessor_id, metric_id)

    return (layer_id, kbn_columns, visualization_state)
