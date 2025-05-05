
from dashboard_compiler.filters.compile import compile_filters
from dashboard_compiler.panels.charts.view import KbnLensPanelAttributes, KbnLensPanelEmbeddableConfig, KbnLensPanelState
from dashboard_compiler.panels.charts.config import ESQLPanel, LensPanel
from dashboard_compiler.panels.charts.visualizations.config import LensChartTypes
from dashboard_compiler.panels.charts.visualizations.metric.compile import compile_lens_metric_visualization
from dashboard_compiler.panels.charts.visualizations.metric.config import LensMetricChart
from dashboard_compiler.panels.charts.visualizations.pie.config import LensPieChart
from dashboard_compiler.panels.charts.visualizations.view import KbnDataSourceState, KbnFormBasedDataSourceState, KbnLayerDataSourceState, KbnLayerDataSourceStateById, KbnStateVisualizationType
from dashboard_compiler.queries.compile import compile_query
from dashboard_compiler.shared.config import stable_id_generator
from dashboard_compiler.shared.view import KbnReference


def compile_lens_panel_chart(lens_chart: LensChartTypes) -> tuple[list[KbnReference], KbnStateVisualizationType]:
    """Compile a LensPanel into its Kibana view model representation.

    Args:
        lens_panel (LensPanel): The Lens panel to compile.

    Returns:
        tuple[list[KbnReference], KbnLensPanelEmbeddableConfig]: The compiled Kibana Lens panel view model.

    """
    layer_id = lens_chart.id or stable_id_generator(['panel', lens_chart.title])

    if isinstance(lens_chart, LensMetricChart):
        columns_by_id, visualization_state = compile_lens_metric_visualization(lens_chart)
    elif isinstance(lens_chart, LensPieChart):
        columns_by_id, visualization_state = compile_lens_pie_visualization(lens_chart)

# from dashboard_compiler.panels.charts.visualizations.config import ChartTypes, LensChartTypes
# from dashboard_compiler.panels.charts.visualizations.metric.compile import (
#     compile_esql_lens_metrics_chart,
#     compile_lens_metric_visualization,
#     compile_lens_metrics_chart,
# )
# from dashboard_compiler.panels.charts.visualizations.metric.config import LensMetricChart
# from dashboard_compiler.panels.charts.visualizations.pie.compile import compile_esql_pie_chart, compile_lens_pie_chart
# from dashboard_compiler.panels.charts.visualizations.pie.config import LensPieChart
# from dashboard_compiler.panels.charts.visualizations.view import (
#     KbnDataSourceState,
#     KbnFormBasedDataSourceState,
#     KbnLayerDataSourceState,
#     KbnLayerDataSourceStateById,
# )
# from dashboard_compiler.shared.config import stable_id_generator


# def compile_charts_panel_config(
#     chart: ChartTypes
# ) -> KbnLensEmbeddableConfig | KbnESQLPanel:
#     """Compile a general visualization config object into its Kibana view model representation."""

#     if isinstance(chart, LensChartTypes):
#         if isinstance(chart, LensMetricChart):
#             columns_by_id, visualization_state = compile_lens_metric_visualization(chart)
#         elif isinstance(chart, LensPieChart):
#             columns_by_id, visualization_state = compile_lens_pie_visualization(chart)



#         data_source_state = KbnDataSourceState(
#             formBased=KbnFormBasedDataSourceState(
#                 layers=KbnLayerDataSourceStateById(
#                     {layer_id: KbnLayerDataSourceState(columns=columns_by_id)}
#                 )
#             )
#         )
#     else:
#         raise ValueError(f'Unknown chart type: {type(chart)}')



#     vis_type = visualization_config.get('type')

#     if vis_type == 'metric':
#         # Check if it's an ESQL metric config
#         if 'query' in visualization_config or 'primary_metric_column' in visualization_config:
#             return compile_esql_lens_metrics_chart(visualization_config, kbn_columns_by_id)
#         return compile_lens_metrics_chart(visualization_config, kbn_columns_by_id)
#     if vis_type == 'pie':
#         # Check if it's an ESQL pie config
#         if 'query' in visualization_config or 'metric_column' in visualization_config:
#             return compile_esql_pie_chart(visualization_config, kbn_columns_by_id)
#         return compile_lens_pie_chart(visualization_config, kbn_columns_by_id)
#     msg = f'Unknown visualization type: {vis_type}'
#     raise ValueError(msg)
