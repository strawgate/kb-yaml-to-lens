"""Compile Vega panels into their Kibana representations."""

import json

from kb_dashboard_core.panels.vega.config import VegaPanel
from kb_dashboard_core.panels.vega.view import (
    KbnVegaEmbeddableConfig,
    KbnVegaSavedVis,
    KbnVegaSavedVisData,
    KbnVegaSavedVisDataSearchSource,
    KbnVegaSavedVisParams,
)
from kb_dashboard_core.queries.view import KbnQuery
from kb_dashboard_core.shared.view import KbnReference


def compile_vega_saved_vis_data() -> KbnVegaSavedVisData:
    """Compile the saved visualization data for a VegaPanel.

    Returns:
        KbnVegaSavedVisData: The compiled saved visualization data.

    """
    return KbnVegaSavedVisData(
        aggs=[],
        searchSource=KbnVegaSavedVisDataSearchSource(
            query=KbnQuery(query='', language='kuery'),
            filter=[],
        ),
    )


def compile_vega_saved_vis_params(vega_panel: VegaPanel) -> KbnVegaSavedVisParams:
    """Compile the saved visualization parameters for a VegaPanel.

    Args:
        vega_panel (VegaPanel): The Vega panel to compile.

    Returns:
        KbnVegaSavedVisParams: The compiled saved visualization parameters.

    """
    return KbnVegaSavedVisParams(
        spec=json.dumps(vega_panel.vega.spec),
    )


def compile_vega_saved_vis(vega_panel: VegaPanel) -> KbnVegaSavedVis:
    """Compile a VegaPanel into its Kibana saved visualization representation.

    Args:
        vega_panel (VegaPanel): The Vega panel to compile.

    Returns:
        KbnVegaSavedVis: The compiled Kibana Vega saved visualization.

    """
    return KbnVegaSavedVis(
        id='',
        title=vega_panel.title,
        description=vega_panel.description if vega_panel.description is not None else '',
        type='vega',
        params=compile_vega_saved_vis_params(vega_panel=vega_panel),
        uiState={},
        data=compile_vega_saved_vis_data(),
    )


def compile_vega_panel_config(vega_panel: VegaPanel) -> tuple[list[KbnReference], KbnVegaEmbeddableConfig]:
    """Compile a VegaPanel into its Kibana view model representation.

    Args:
        vega_panel (VegaPanel): The Vega panel to compile.

    Returns:
        tuple[list[KbnReference], KbnVegaEmbeddableConfig]: The compiled references and embeddable config.

    """
    return [], KbnVegaEmbeddableConfig(
        hidePanelTitles=vega_panel.hide_title,
        enhancements={'dynamicActions': {'events': []}},
        description=None,
        savedVis=compile_vega_saved_vis(vega_panel=vega_panel),
    )
