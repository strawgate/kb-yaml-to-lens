"""Compile Markdown panels into their Kibana representations."""

from dashboard_compiler.panels.markdown.config import MarkdownPanel
from dashboard_compiler.panels.markdown.view import (
    KBN_MARKDOWN_DEFAULT_FONT_SIZE,
    KBN_MARKDOWN_DEFAULT_OPEN_LINKS_IN_NEW_TAB,
    KbnMarkdownEmbeddableConfig,
    KbnMarkdownSavedVis,
    KbnMarkdownSavedVisData,
    KbnMarkdownSavedVisDataSearchSource,
    KbnMarkdownSavedVisParams,
)
from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.shared.view import KbnReference


def compile_markdown_saved_vis_data() -> KbnMarkdownSavedVisData:
    """Compile the saved visualization data for a MarkdownPanel.

    Args:
        panel (MarkdownPanel): The Markdown panel to compile.

    Returns:
        KbnMarkdownSavedVisData: The compiled saved visualization data.

    """
    return KbnMarkdownSavedVisData(
        aggs=[],
        searchSource=KbnMarkdownSavedVisDataSearchSource(
            query=KbnQuery(query='', language='kuery'),
            filter=[],
        ),
    )


def compile_markdown_saved_vis_params(markdown_panel: MarkdownPanel) -> KbnMarkdownSavedVisParams:
    """Compile the saved visualization parameters for a MarkdownPanel.

    Args:
        markdown_panel (MarkdownPanel): The Markdown panel to compile.

    Returns:
        KbnMarkdownSavedVisParams: The compiled saved visualization parameters.

    """
    return KbnMarkdownSavedVisParams(
        fontSize=markdown_panel.font_size or KBN_MARKDOWN_DEFAULT_FONT_SIZE,
        openLinksInNewTab=markdown_panel.links_in_new_tab or KBN_MARKDOWN_DEFAULT_OPEN_LINKS_IN_NEW_TAB,
        markdown=markdown_panel.content,
    )


def compile_markdown_saved_vis(markdown_panel: MarkdownPanel) -> KbnMarkdownSavedVis:
    """Compile a MarkdownPanel into its Kibana saved visualization representation.

    Args:
        markdown_panel (MarkdownPanel): The Markdown panel to compile.

    Returns:
        KbnMarkdownSavedVis: The compiled Kibana Markdown saved visualization.

    """
    return KbnMarkdownSavedVis(
        id='',
        title=markdown_panel.title,
        description=markdown_panel.description or '',
        type='markdown',
        params=compile_markdown_saved_vis_params(markdown_panel=markdown_panel),
        uiState={},
        data=compile_markdown_saved_vis_data(),
    )


def compile_markdown_panel_config(markdown_panel: MarkdownPanel) -> tuple[list[KbnReference], KbnMarkdownEmbeddableConfig]:
    """Compile a MarkdownPanel into its Kibana view model representation.

    Args:
        markdown_panel (MarkdownPanel): The Markdown panel to compile.

    Returns:
        KbnMarkdownPanel: The compiled Kibana Markdown panel view model.

    """
    return [], KbnMarkdownEmbeddableConfig(
        hidePanelTitles=markdown_panel.hide_title,
        enhancements={'dynamicActions': {'events': []}},
        description=None,
        savedVis=compile_markdown_saved_vis(markdown_panel=markdown_panel),
    )
