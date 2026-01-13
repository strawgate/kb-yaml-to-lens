"""Compile Lens tagcloud visualizations into their Kibana view models."""

from typing import TypeVar

from dashboard_compiler.panels.charts.base.protocol import ColumnCompiler
from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
from dashboard_compiler.panels.charts.esql.compiler import ESQLColumnCompiler
from dashboard_compiler.panels.charts.lens.columns.view import KbnLensColumnTypes
from dashboard_compiler.panels.charts.lens.compiler import LensColumnCompiler
from dashboard_compiler.panels.charts.tagcloud.config import ESQLTagcloudChart, LensTagcloudChart
from dashboard_compiler.panels.charts.tagcloud.view import KbnTagcloudVisualizationState

# Type variables for generic tagcloud chart compilation
ColumnT = TypeVar('ColumnT')
MetricColumnT = TypeVar('MetricColumnT')
DimensionColumnT = TypeVar('DimensionColumnT')
MetricConfigT = TypeVar('MetricConfigT')
DimensionConfigT = TypeVar('DimensionConfigT')


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


def _compile_tagcloud_chart(
    chart: LensTagcloudChart | ESQLTagcloudChart,
    compiler: ColumnCompiler[ColumnT, MetricColumnT, DimensionColumnT, MetricConfigT, DimensionConfigT],
    metric: MetricConfigT,
    dimension: DimensionConfigT,
) -> tuple[str, ColumnT, KbnTagcloudVisualizationState]:
    """Compile a tagcloud chart using the provided column compiler.

    Args:
        chart: The tagcloud chart configuration (Lens or ESQL).
        compiler: The column compiler to use for metrics and dimensions.
        metric: The metric configuration to compile.
        dimension: The dimension configuration to compile.

    Returns:
        tuple: (layer_id, columns, visualization_state)
    """
    layer_id = chart.get_id()

    # Compile using the compiler
    result = compiler.compile_all(metrics=[metric], dimensions=[dimension])

    # Get accessor IDs for visualization state
    tag_accessor_id = result.dimension_ids[0]
    value_accessor_id = result.metric_ids[0]

    visualization_state = compile_tagcloud_chart_visualization_state(layer_id, chart, tag_accessor_id, value_accessor_id)

    return layer_id, result.columns, visualization_state


def compile_lens_tagcloud_chart(
    chart: LensTagcloudChart,
) -> tuple[str, dict[str, KbnLensColumnTypes], KbnTagcloudVisualizationState]:
    """Compile Lens tagcloud chart.

    Args:
        chart (LensTagcloudChart): The LensTagcloudChart config object.

    Returns:
        tuple[str, dict[str, KbnLensColumnTypes], KbnTagcloudVisualizationState]: The layer ID, columns, and visualization state.
    """
    compiler = LensColumnCompiler()
    return _compile_tagcloud_chart(
        chart=chart,
        compiler=compiler,
        metric=chart.metric,
        dimension=chart.dimension,
    )


def compile_esql_tagcloud_chart(
    chart: ESQLTagcloudChart,
) -> tuple[str, list[KbnESQLColumnTypes], KbnTagcloudVisualizationState]:
    """Compile ES|QL tagcloud chart.

    Args:
        chart (ESQLTagcloudChart): The ESQLTagcloudChart config object.

    Returns:
        tuple[str, list[KbnESQLColumnTypes], KbnTagcloudVisualizationState]: The layer ID, columns, and visualization state.
    """
    compiler = ESQLColumnCompiler()
    return _compile_tagcloud_chart(
        chart=chart,
        compiler=compiler,
        metric=chart.metric,
        dimension=chart.dimension,
    )
