"""Compiler logic for Search panels."""

from kb_dashboard_core.panels.search.config import SearchPanel
from kb_dashboard_core.panels.search.view import KbnSearchEmbeddableConfig
from kb_dashboard_core.shared.view import KbnReference


def compile_search_panel_config(panel: SearchPanel, panel_index: str) -> tuple[list[KbnReference], KbnSearchEmbeddableConfig, str]:
    """Compile a SearchPanel configuration into its Kibana view model representation.

    Args:
        panel (SearchPanel): The SearchPanel object to compile.
        panel_index (str): The compiled panel index/id.

    Returns:
        tuple[list[KbnReference], KbnSearchEmbeddableConfig, str]: A tuple containing
            the list of references, the compiled embeddable configuration, and the
            panel-level reference name.

    """
    panel_ref_name = f'panel_{panel_index}'
    references: list[KbnReference] = [
        KbnReference(
            name=panel_ref_name,
            type='search',
            id=panel.search.saved_search_id,
        )
    ]

    embeddable_config = KbnSearchEmbeddableConfig(savedObjectId=panel.search.saved_search_id)

    return references, embeddable_config, panel_ref_name
