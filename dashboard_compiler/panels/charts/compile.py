
from dashboard_compiler.filters.compile import compile_filters
from dashboard_compiler.panels.charts.view import KbnLensPanelAttributes, KbnLensPanelEmbeddableConfig, KbnLensPanelState
from dashboard_compiler.panels.charts.config import ESQLPanel, LensPanel
from dashboard_compiler.panels.charts.visualizations.metric.compile import compile_lens_metric_visualization
from dashboard_compiler.panels.charts.visualizations.metric.config import LensMetricChart
from dashboard_compiler.panels.charts.visualizations.pie.config import LensPieChart
from dashboard_compiler.panels.charts.visualizations.view import KbnDataSourceState, KbnFormBasedDataSourceState, KbnLayerDataSourceState, KbnLayerDataSourceStateById
from dashboard_compiler.queries.compile import compile_query
from dashboard_compiler.shared.config import stable_id_generator
from dashboard_compiler.shared.view import KbnReference


def compile_lens_panel_config(lens_panel: LensPanel) -> tuple[list[KbnReference], KbnLensPanelEmbeddableConfig]:
    """Compile a LensPanel into its Kibana view model representation.

    Args:
        lens_panel (LensPanel): The Lens panel to compile.

    Returns:
        tuple[list[KbnReference], KbnLensPanelEmbeddableConfig]: The compiled Kibana Lens panel view model.

    """
    layer_id = lens_panel.id or stable_id_generator(['panel', lens_panel.title])

    if isinstance(lens_panel.chart, LensMetricChart):
        columns_by_id, visualization_state = compile_lens_metric_visualization(lens_panel.chart)
    elif isinstance(lens_panel.chart, LensPieChart):
        columns_by_id, visualization_state = compile_lens_pie_visualization(lens_panel.chart)

    data_source_state = KbnDataSourceState(
        formBased=KbnFormBasedDataSourceState(
            layers=KbnLayerDataSourceStateById(
                {layer_id: KbnLayerDataSourceState(columns=columns_by_id)}
            )
        )
    )

    lens_panel_state = KbnLensPanelState(
        datasourceStates=data_source_state,
        filters=compile_filters(lens_panel.filters),
        query=compile_query(lens_panel.query),
        visualization=visualization_state,
    )

    lens_panel_attributes = KbnLensPanelAttributes(
        title=lens_panel.title,
        visualizationType=lens_panel.chart.type,
        references=[],
        state=lens_panel_state,
    )

    lens_panel_embeddable_config = KbnLensPanelEmbeddableConfig(
        attributes=lens_panel_attributes
    )

    return [], lens_panel_embeddable_config

def compile_esql_panel_config(esql_panel: ESQLPanel) -> tuple[list[KbnReference], KbnLensPanelEmbeddableConfig]:
    """Compile an ESQLPanel into its Kibana view model representation.

    Args:
        esql_panel (ESQLPanel): The ESQL panel to compile.

    Returns:
        tuple[list[KbnReference], KbnLensPanelEmbeddableConfig]: The compiled Kibana view model representation of the ESQL panel.

    """
    return [], KbnLensPanelEmbeddableConfig(
        attributes=KbnLensPanelAttributes(
            title=esql_panel.title,
            visualizationType=KbnVisualizationTypeEnum.ESQL,
            type=KbnPanelTypeEnum.ESQL,
            references=[]
        )
    )
