from pydantic import BaseModel, Field
from typing import Dict, Any, Literal, List  # Import Optional
import uuid  # Import uuid

from dashboard_compiler.models.views.base import KbnBasePanel, KbnGridData  # Import base view models
from dashboard_compiler.models.config.panels.markdown import MarkdownPanel as ConfigMarkdownPanel  # Import config model


# Example Model relationships:
# - KbnLinksPanel
#   - KbnLinksPanelEmbeddableConfig
#     - KbnLinksPanelAttributes
#       - KbnLink
#       - KbnLink
#       - KbnLink

# KbnMarkdownPanel
# - KbnMarkdownEmbeddableConfig
#   - KbnMarkdownSavedVis
#     - KbnMarkdownSavedVisData
#       - KbnMarkdownSavedVisDataSearchSource


# My guess is this model is not specific to Markdown Panels
class KbnMarkdownSavedVisDataSearchSource(BaseModel):
    query: Dict[str, str] = Field(default_factory=lambda: {"query": "", "language": "kuery"})
    filter: List[Any] = Field(default_factory=list)


class KbnMarkdownSavedVisData(BaseModel):
    aggs: List[Any] = Field(default_factory=list)
    searchSource: KbnMarkdownSavedVisDataSearchSource = Field(default_factory=KbnMarkdownSavedVisDataSearchSource)


class KbnMarkdownSavedVisParams(BaseModel):
    fontSize: int
    openLinksInNewTab: bool
    markdown: str


class KbnMarkdownSavedVis(BaseModel):
    id: str = ""  # Appears blank in samples
    title: str
    description: str = ""
    type: Literal["markdown"] = "markdown"
    params: KbnMarkdownSavedVisParams
    uiState: Dict[str, Any] = Field(default_factory=dict)
    data: KbnMarkdownSavedVisData = Field(default_factory=KbnMarkdownSavedVisData)


class KbnMarkdownEmbeddableConfig(BaseModel):
    enhancements: Dict[str, Any] = Field(default_factory=lambda: {"dynamicActions": {"events": []}})
    savedVis: KbnMarkdownSavedVis


class KbnMarkdownPanel(KbnBasePanel):
    """Represents a Markdown panel in the Kibana Kbn structure."""

    type: Literal["visualization"] = "visualization"  # Markdown panels have type "visualization" in Kbn
    embeddableConfig: KbnMarkdownEmbeddableConfig

    # No to_Kbn or to_dict methods here - these models are for representing Kbn output

    @classmethod
    def render_from_config(cls, config_panel: ConfigMarkdownPanel) -> "KbnMarkdownPanel":
        """Renders a KbnMarkdownPanel view model from a ConfigMarkdownPanel config model."""
        # Call render_from_config on the base KbnBasePanel to handle common attributes and get panelIndex/gridData
        # Note: KbnBasePanel.render_from_config currently returns KbnBasePanel, not the specific subclass.
        # This will need to be addressed in the base KbnBasePanel render_from_config or by
        # instantiating KbnMarkdownPanel directly here and passing common attributes.
        # For now, let's instantiate KbnMarkdownPanel directly and handle common attributes manually.
        # This might require passing panelIndex and gridData from a higher level compiler function.
        # Let's assume for now that panelIndex and gridData are generated/handled at a higher level
        # and passed down, or we generate them here and pass them up/use them.
        # Given the plan, render_from_config is on the view model, so it should handle its own ID/gridData.

        # Generate unique panel ID and grid data
        panel_id = str(uuid.uuid4())  # Need to import uuid
        view_grid_data = KbnGridData(  # Need to import KbnGridData
            x=config_panel.grid.x, y=config_panel.grid.y, w=config_panel.grid.w, h=config_panel.grid.h, i=panel_id
        )

        # Build embeddableConfig
        view_saved_vis_params = KbnMarkdownSavedVisParams(
            fontSize=12,  # Default value based on samples
            openLinksInNewTab=False,  # Default value based on samples
            markdown=config_panel.content,
        )
        view_saved_vis_data_search_source = KbnMarkdownSavedVisDataSearchSource()
        view_saved_vis_data = KbnMarkdownSavedVisData(searchSource=view_saved_vis_data_search_source)
        view_saved_vis = KbnMarkdownSavedVis(
            id="",  # Blank in samples
            title=config_panel.title,
            description=config_panel.description,
            type="markdown",
            params=view_saved_vis_params,
            uiState={},  # Default based on samples
            data=view_saved_vis_data,
        )
        view_embeddable_config = KbnMarkdownEmbeddableConfig(
            enhancements={"dynamicActions": {"events": []}},  # Default based on samples
            savedVis=view_saved_vis,
        )

        return cls(
            type="visualization",  # Markdown panels have type "visualization" in Kbn
            panelIndex=panel_id,
            gridData=view_grid_data,
            embeddableConfig=view_embeddable_config,
        )
