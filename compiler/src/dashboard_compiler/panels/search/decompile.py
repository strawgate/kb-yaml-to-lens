"""Decompile Kibana search panels back to config models."""

from typing import Any

from dashboard_compiler.panels.config import Position, Size
from dashboard_compiler.panels.search.config import SearchPanel, SearchPanelConfig
from dashboard_compiler.shared.decompile import ReferenceResolver
from dashboard_compiler.shared.decompile_context import DecompileContext


def decompile_search_panel(
    kbn_panel: dict[str, Any],
    *,
    context: DecompileContext,  # noqa: ARG001
    reference_resolver: ReferenceResolver,
) -> SearchPanel:
    """Decompile a Kibana search panel to config model.

    Args:
        kbn_panel: The Kibana panel dict.
        context: Decompilation context for warnings.
        reference_resolver: Resolver for panel references.

    Returns:
        The decompiled SearchPanel config.

    """
    grid_data = kbn_panel.get('gridData', {})
    embeddable_config = kbn_panel.get('embeddableConfig', {})

    # Extract grid info
    size = Size(
        w=grid_data.get('w', 12),
        h=grid_data.get('h', 8),
    )
    position = Position(
        x=grid_data.get('x'),
        y=grid_data.get('y'),
    )

    # Resolve saved search ID from reference
    ref_name = embeddable_config.get('savedSearchRefName', '')
    ref = reference_resolver.resolve_by_name(ref_name)
    saved_search_id = ref.id if ref is not None else ''

    # If no reference found, try extracting from savedSearchId field
    if len(saved_search_id) == 0:
        saved_search_id = embeddable_config.get('savedSearchId', '')

    search_config = SearchPanelConfig(saved_search_id=saved_search_id)

    # Extract panel metadata
    panel_id = kbn_panel.get('panelIndex', '')
    hide_title = embeddable_config.get('hidePanelTitles')
    title = embeddable_config.get('title', '')
    description = embeddable_config.get('description', '')

    return SearchPanel(
        id=panel_id,
        title=title,
        description=description if len(description) > 0 else None,
        hide_title=hide_title if hide_title else None,
        size=size,
        position=position,
        search=search_config,
    )
