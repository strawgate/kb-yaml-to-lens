"""Compile Map panels into their Kibana representations."""

from dashboard_compiler.panels.maps.config import MapPanel
from dashboard_compiler.panels.maps.view import KbnMapCenter, KbnMapEmbeddableConfig
from dashboard_compiler.shared.view import KbnReference


def compile_map_panel_config(map_panel: MapPanel) -> tuple[list[KbnReference], KbnMapEmbeddableConfig]:
    """Compile a MapPanel into its Kibana view model representation.

    Args:
        map_panel (MapPanel): The Map panel to compile.

    Returns:
        tuple: A tuple containing:
            - list[KbnReference]: References to the saved map object
            - KbnMapEmbeddableConfig: The compiled embeddable configuration

    """
    # Create reference to the saved map object
    references = [
        KbnReference(
            type='map',
            id=map_panel.saved_map_id,
            name=f'panel_{map_panel.id or "map"}',
        )
    ]

    # Compile map center if provided
    map_center = None
    if map_panel.map_center is not None:
        map_center = KbnMapCenter(
            lat=map_panel.map_center.lat,
            lon=map_panel.map_center.lon,
            zoom=map_panel.map_center.zoom,
        )

    embeddable_config = KbnMapEmbeddableConfig(
        hidePanelTitles=map_panel.hide_title,
        isLayerTOCOpen=map_panel.is_layer_toc_open,
        hiddenLayers=map_panel.hidden_layers,
        mapCenter=map_center,
        openTOCDetails=map_panel.open_toc_details,
        enhancements={'dynamicActions': {'events': []}},
    )

    return references, embeddable_config
