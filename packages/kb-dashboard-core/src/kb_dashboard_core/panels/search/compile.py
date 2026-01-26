"""Compiler logic for Search panels."""

from kb_dashboard_core.panels.search.config import SearchPanel
from kb_dashboard_core.panels.search.view import KbnSearchEmbeddableConfig
from kb_dashboard_core.shared.view import KbnReference


def compile_search_panel_config(panel: SearchPanel) -> tuple[list[KbnReference], KbnSearchEmbeddableConfig]:
    """Compile a SearchPanel configuration into its Kibana view model representation.

    Args:
        panel (SearchPanel): The SearchPanel object to compile.

    Returns:
        tuple[list[KbnReference], KbnSearchEmbeddableConfig]: A tuple containing the
            list of references and the compiled embeddable configuration.

    """
    ref_name = f'search:{panel.search.saved_search_id}'
    references: list[KbnReference] = [
        KbnReference(
            name=ref_name,
            type='search',
            id=panel.search.saved_search_id,
        )
    ]

    # In Saved Object exports, search panels use savedSearchId in embeddableConfig
    # which is actually a reference key.
    embeddable_config = KbnSearchEmbeddableConfig(savedSearchRefName=ref_name)

    return references, embeddable_config
