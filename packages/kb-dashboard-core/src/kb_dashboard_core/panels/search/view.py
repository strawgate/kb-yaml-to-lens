"""View models for Search panels."""

from typing import Any, Literal

from pydantic import BaseModel, Field

from kb_dashboard_core.panels.view import KbnBasePanel

# Model Relationships:
# - KbnSearchPanel
#   - KbnSearchEmbeddableConfig


# Define nested models for Search panel embeddableConfig based on samples
class KbnSearchEmbeddableConfig(BaseModel):
    enhancements: dict[str, Any] = Field(default_factory=dict)
    savedSearchRefName: str


class KbnSearchPanel(KbnBasePanel):
    """Represents a Search panel in the Kibana JSON structure."""

    type: Literal['search'] = 'search'
    embeddableConfig: KbnSearchEmbeddableConfig
