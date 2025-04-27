from dashboard_compiler.compile.panels.base import compile_panel_shared
from dashboard_compiler.models.config.panels.markdown import MarkdownPanel
from dashboard_compiler.models.views.panels.markdown import (
    KbnMarkdownEmbeddableConfig,
    KbnMarkdownPanel,
    KbnMarkdownSavedVis,
    KbnMarkdownSavedVisParams,
)


def compile_markdown_panel(panel: MarkdownPanel) -> KbnMarkdownPanel:
    """
    Compile a MarkdownPanel into its Kibana view model representation.

    Args:
        panel (MarkdownPanel): The Markdown panel to compile.

    Returns:
        KbnMarkdownPanel: The compiled Kibana Markdown panel view model.
    """
    panel_index, grid_data = compile_panel_shared(panel)

    return KbnMarkdownPanel(
        type="visualization",
        panelIndex=panel_index,
        gridData=grid_data,
        embeddableConfig=KbnMarkdownEmbeddableConfig(
            savedVis=KbnMarkdownSavedVis(
                # id=panel_index, #appears blank in samples
                title=panel.title,
                description=panel.description,
                type="markdown",
                params=KbnMarkdownSavedVisParams(fontSize=12, openLinksInNewTab=False, markdown=panel.content),
            )
        ),
    )
