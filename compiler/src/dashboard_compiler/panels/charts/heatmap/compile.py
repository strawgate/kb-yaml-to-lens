"""Compilation logic for heatmap chart visualizations."""

from typing import TYPE_CHECKING, TypeVar

from dashboard_compiler.panels.charts.base.config import LegendVisibleEnum
from dashboard_compiler.panels.charts.base.protocol import ColumnCompiler
from dashboard_compiler.panels.charts.esql.compiler import ESQLColumnCompiler
from dashboard_compiler.panels.charts.heatmap.view import (
    KbnHeatmapGridConfig,
    KbnHeatmapLegendConfig,
    KbnHeatmapVisualizationState,
)
from dashboard_compiler.panels.charts.lens.compiler import LensColumnCompiler
from dashboard_compiler.shared.defaults import default_false

if TYPE_CHECKING:
    from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
    from dashboard_compiler.panels.charts.heatmap.config import ESQLHeatmapChart, LensHeatmapChart
    from dashboard_compiler.panels.charts.lens.columns.view import KbnLensColumnTypes

# Type variables for generic heatmap chart compilation
ColumnT = TypeVar('ColumnT')
MetricColumnT = TypeVar('MetricColumnT')
DimensionColumnT = TypeVar('DimensionColumnT')
MetricConfigT = TypeVar('MetricConfigT')
DimensionConfigT = TypeVar('DimensionConfigT')


def compile_heatmap_chart_visualization_state(
    layer_id: str,
    x_accessor_id: str,
    value_accessor_id: str,
    chart: 'LensHeatmapChart | ESQLHeatmapChart',
    y_accessor_id: str | None = None,
) -> KbnHeatmapVisualizationState:
    """Compile a heatmap chart config object into a Kibana Lens Heatmap visualization state.

    Args:
        layer_id (str): The ID of the layer.
        x_accessor_id (str): The ID of the X-axis dimension.
        value_accessor_id (str): The ID of the value metric.
        chart (LensHeatmapChart | ESQLHeatmapChart): The heatmap chart config object.
        y_accessor_id (str | None): The ID of the Y-axis dimension.

    Returns:
        KbnHeatmapVisualizationState: The compiled visualization state.

    """
    # Compile grid configuration (always present, use defaults if not provided)
    if chart.grid_config is not None:
        gc = chart.grid_config
        # Handle nested cell configuration
        cell_labels = default_false(gc.cells.show_labels) if gc.cells is not None else False
        # Handle nested axis configuration
        x_axis_labels = default_false(gc.x_axis.show_labels) if gc.x_axis is not None else False
        x_axis_title = default_false(gc.x_axis.show_title) if gc.x_axis is not None else False
        y_axis_labels = default_false(gc.y_axis.show_labels) if gc.y_axis is not None else False
        y_axis_title = default_false(gc.y_axis.show_title) if gc.y_axis is not None else False

        grid_config = KbnHeatmapGridConfig(
            isCellLabelVisible=cell_labels,
            isXAxisLabelVisible=x_axis_labels,
            isXAxisTitleVisible=x_axis_title,
            isYAxisLabelVisible=y_axis_labels,
            isYAxisTitleVisible=y_axis_title,
        )
    else:
        grid_config = KbnHeatmapGridConfig()

    # Compile legend configuration (always present, use defaults if not provided)
    if chart.legend is not None:
        # Map enum values: 'show' -> True, 'hide' -> False, None -> True (Kibana default)
        legend_visible = chart.legend.visible != LegendVisibleEnum.HIDE if chart.legend.visible is not None else True

        legend = KbnHeatmapLegendConfig(
            isVisible=legend_visible,
            position=chart.legend.position if chart.legend.position is not None else 'right',
        )
    else:
        legend = KbnHeatmapLegendConfig()

    return KbnHeatmapVisualizationState(
        layerId=layer_id,
        xAccessor=x_accessor_id,
        yAccessor=y_accessor_id,
        valueAccessor=value_accessor_id,
        gridConfig=grid_config,
        legend=legend,
    )


def _compile_heatmap_chart(
    chart: 'LensHeatmapChart | ESQLHeatmapChart',
    compiler: ColumnCompiler[ColumnT, MetricColumnT, DimensionColumnT, MetricConfigT, DimensionConfigT],
    x_axis: DimensionConfigT,
    y_axis: DimensionConfigT | None,
    value: MetricConfigT,
) -> tuple[str, ColumnT, KbnHeatmapVisualizationState]:
    """Compile a heatmap chart using the provided column compiler.

    Args:
        chart: The heatmap chart configuration (Lens or ESQL).
        compiler: The column compiler to use for metrics and dimensions.
        x_axis: The X-axis dimension configuration.
        y_axis: The optional Y-axis dimension configuration.
        value: The value metric configuration.

    Returns:
        tuple: (layer_id, columns, visualization_state)
    """
    layer_id = chart.get_id()

    # Build list of dimensions (x_axis is required, y_axis is optional)
    dimensions: list[DimensionConfigT] = [x_axis]
    if y_axis is not None:
        dimensions.append(y_axis)

    # Compile using the compiler
    result = compiler.compile_all(metrics=[value], dimensions=dimensions)

    # Get accessor IDs for visualization state
    x_accessor_id = result.dimension_ids[0]
    y_accessor_id = result.dimension_ids[1] if len(result.dimension_ids) > 1 else None
    value_accessor_id = result.metric_ids[0]

    visualization_state = compile_heatmap_chart_visualization_state(
        layer_id=layer_id,
        x_accessor_id=x_accessor_id,
        value_accessor_id=value_accessor_id,
        chart=chart,
        y_accessor_id=y_accessor_id,
    )

    return layer_id, result.columns, visualization_state


def compile_lens_heatmap_chart(
    lens_heatmap_chart: 'LensHeatmapChart',
) -> 'tuple[str, dict[str, KbnLensColumnTypes], KbnHeatmapVisualizationState]':
    """Compile a LensHeatmapChart config object into a Kibana Lens Heatmap visualization state.

    Args:
        lens_heatmap_chart (LensHeatmapChart): The LensHeatmapChart object to compile.

    Returns:
        tuple[str, dict[str, KbnLensColumnTypes], KbnHeatmapVisualizationState]: A tuple containing:
            - layer_id (str): The ID of the layer.
            - kbn_columns (dict[str, KbnLensColumnTypes]): A dictionary of columns for the layer.
            - kbn_state_visualization (KbnHeatmapVisualizationState): The compiled visualization state.
    """
    compiler = LensColumnCompiler()
    return _compile_heatmap_chart(
        chart=lens_heatmap_chart,
        compiler=compiler,
        x_axis=lens_heatmap_chart.x_axis,
        y_axis=lens_heatmap_chart.y_axis,
        value=lens_heatmap_chart.value,
    )


def compile_esql_heatmap_chart(
    esql_heatmap_chart: 'ESQLHeatmapChart',
) -> 'tuple[str, list[KbnESQLColumnTypes], KbnHeatmapVisualizationState]':
    """Compile an ESQL HeatmapChart config object into a Kibana Lens Heatmap visualization state.

    Args:
        esql_heatmap_chart (ESQLHeatmapChart): The ESQLHeatmapChart object to compile.

    Returns:
        tuple[str, list[KbnESQLColumnTypes], KbnHeatmapVisualizationState]: A tuple containing:
            - layer_id (str): The ID of the layer.
            - kbn_columns (list[KbnESQLColumnTypes]): A list of columns for the layer.
            - kbn_state_visualization (KbnHeatmapVisualizationState): The compiled visualization state.
    """
    compiler = ESQLColumnCompiler()
    return _compile_heatmap_chart(
        chart=esql_heatmap_chart,
        compiler=compiler,
        x_axis=esql_heatmap_chart.x_axis,
        y_axis=esql_heatmap_chart.y_axis,
        value=esql_heatmap_chart.value,
    )
