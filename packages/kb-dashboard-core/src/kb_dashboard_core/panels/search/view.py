"""View models for Search panels."""

from typing import Literal

from kb_dashboard_core.panels.view import KbnBasePanel, KbnBasePanelEmbeddableConfig

# Model Relationships:
# - KbnSearchPanel
#   - KbnSearchEmbeddableConfig


# Define nested models for Search panel embeddableConfig based on samples
class KbnSearchEmbeddableConfig(KbnBasePanelEmbeddableConfig):
    savedObjectId: str


class KbnSearchPanel(KbnBasePanel):
    """Represents a Search panel in the Kibana JSON structure."""

    type: Literal['search'] = 'search'
    panelRefName: str
    embeddableConfig: KbnSearchEmbeddableConfig
