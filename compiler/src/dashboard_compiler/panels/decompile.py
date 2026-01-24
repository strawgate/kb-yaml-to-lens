"""Decompile Kibana panels back to config models."""

from collections.abc import Sequence
from typing import Any

from dashboard_compiler.panels.config import Position, Size
from dashboard_compiler.panels.types import PanelTypes
from dashboard_compiler.panels.view import KbnGridData
from dashboard_compiler.shared.decompile import ReferenceResolver
from dashboard_compiler.shared.decompile_context import DecompileContext


def decompile_grid_data(grid_data: KbnGridData) -> tuple[Size, Position]:
    """Decompile grid data to size and position.

    Args:
        grid_data: The Kibana grid data.

    Returns:
        Tuple of (size, position).

    """
    size = Size(w=grid_data.w, h=grid_data.h)
    position = Position(x=grid_data.x, y=grid_data.y)
    return size, position


def decompile_panel(
    kbn_panel: dict[str, Any],
    *,
    context: DecompileContext,
    reference_resolver: ReferenceResolver,
) -> PanelTypes | None:
    """Decompile a single panel.

    Args:
        kbn_panel: The Kibana panel dict (from panelsJSON).
        context: Decompilation context for warnings.
        reference_resolver: Resolver for panel references.

    Returns:
        The decompiled panel config, or None if unsupported.

    """
    panel_type = kbn_panel.get('type', 'unknown')

    # Get panel title for better warning messages
    embeddable_config = kbn_panel.get('embeddableConfig', {})
    saved_vis = embeddable_config.get('savedVis', {})
    panel_title = saved_vis.get('title', '') or embeddable_config.get('attributes', {}).get('title', '')

    # Import decompilers here to avoid circular imports
    # Handle visualization types (markdown)
    if panel_type == 'visualization' and saved_vis.get('type') == 'markdown':
        from dashboard_compiler.panels.markdown.decompile import decompile_markdown_panel

        return decompile_markdown_panel(kbn_panel, context=context)

    # Handle simple panel types
    if panel_type == 'links':
        from dashboard_compiler.panels.links.decompile import decompile_links_panel

        return decompile_links_panel(kbn_panel, context=context, reference_resolver=reference_resolver)

    if panel_type == 'image':
        from dashboard_compiler.panels.images.decompile import decompile_image_panel

        return decompile_image_panel(kbn_panel, context=context)

    if panel_type == 'search':
        from dashboard_compiler.panels.search.decompile import decompile_search_panel

        return decompile_search_panel(kbn_panel, context=context, reference_resolver=reference_resolver)

    if panel_type == 'lens':
        from dashboard_compiler.panels.charts.decompile import decompile_lens_panel

        return decompile_lens_panel(kbn_panel, context=context, reference_resolver=reference_resolver)

    # Unsupported panel type
    if panel_type == 'visualization':
        context.warn(
            f'Unsupported visualization type: {saved_vis.get("type", "unknown")}',
            panel_title=panel_title,
        )
    else:
        context.warn(
            f'Unsupported panel type: {panel_type}',
            panel_title=panel_title,
        )
    return None


def decompile_panels(
    kbn_panels: Sequence[dict[str, Any]],
    *,
    context: DecompileContext,
    reference_resolver: ReferenceResolver,
) -> list[PanelTypes]:
    """Decompile a list of Kibana panels.

    Args:
        kbn_panels: The Kibana panel dicts (from panelsJSON).
        context: Decompilation context for warnings.
        reference_resolver: Resolver for panel references.

    Returns:
        List of decompiled panel configs (unsupported panels are skipped).

    """
    panels: list[PanelTypes] = []

    for kbn_panel in kbn_panels:
        panel = decompile_panel(kbn_panel, context=context, reference_resolver=reference_resolver)
        if panel is not None:
            panels.append(panel)

    return panels
