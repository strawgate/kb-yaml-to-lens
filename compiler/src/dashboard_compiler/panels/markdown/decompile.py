"""Decompile Kibana markdown panels back to config models."""

from typing import Any

from dashboard_compiler.panels.config import Position, Size
from dashboard_compiler.panels.markdown.config import MarkdownPanel, MarkdownPanelConfig
from dashboard_compiler.panels.markdown.view import KBN_MARKDOWN_DEFAULT_FONT_SIZE, KBN_MARKDOWN_DEFAULT_OPEN_LINKS_IN_NEW_TAB
from dashboard_compiler.shared.decompile_context import DecompileContext


def decompile_markdown_panel(
    kbn_panel: dict[str, Any],
    *,
    context: DecompileContext,  # noqa: ARG001
) -> MarkdownPanel:
    """Decompile a Kibana markdown panel to config model.

    Args:
        kbn_panel: The Kibana panel dict.
        context: Decompilation context for warnings.

    Returns:
        The decompiled MarkdownPanel config.

    """
    grid_data = kbn_panel.get('gridData', {})
    embeddable_config = kbn_panel.get('embeddableConfig', {})
    saved_vis = embeddable_config.get('savedVis', {})
    params = saved_vis.get('params', {})

    # Extract grid info
    size = Size(
        w=grid_data.get('w', 12),
        h=grid_data.get('h', 8),
    )
    position = Position(
        x=grid_data.get('x'),
        y=grid_data.get('y'),
    )

    # Extract markdown content
    content = params.get('markdown', '')
    font_size = params.get('fontSize', KBN_MARKDOWN_DEFAULT_FONT_SIZE)
    links_in_new_tab = params.get('openLinksInNewTab', KBN_MARKDOWN_DEFAULT_OPEN_LINKS_IN_NEW_TAB)

    # Only include non-default values
    markdown_config = MarkdownPanelConfig(
        content=content,
        font_size=font_size if font_size != KBN_MARKDOWN_DEFAULT_FONT_SIZE else None,
        links_in_new_tab=links_in_new_tab if links_in_new_tab != KBN_MARKDOWN_DEFAULT_OPEN_LINKS_IN_NEW_TAB else None,
    )

    # Extract panel metadata
    panel_id = kbn_panel.get('panelIndex')
    title = saved_vis.get('title', '')
    description = saved_vis.get('description', '') or None
    hide_title = embeddable_config.get('hidePanelTitles')

    return MarkdownPanel(
        id=panel_id,
        title=title,
        description=description if description else None,
        hide_title=hide_title if hide_title else None,
        size=size,
        position=position,
        markdown=markdown_config,
    )
