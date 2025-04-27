"""Types for Kibana Links panel in the dashboard compiler.

Reference: https://github.com/elastic/kibana/blob/main/src/platform/plugins/private/links/common/content_management/v1/types.ts
"""

from typing import Literal

from pydantic import BaseModel, Field

from dashboard_compiler.models.views.base import KbnBasePanel, KbnBasePanelEmbeddableConfig

# Model relationships:
# - KbnLinksPanel
#   - KbnLinksPanelEmbeddableConfig
#     - KbnLinksPanelAttributes
#       - KbnLink
#       - KbnLink
#       - KbnLink


# Define nested models for Links panel embeddableConfig based on samples
class KbnLink(BaseModel):
    type: Literal["dashboardLink", "urlLink"]
    id: str | None = None
    url: str | None = None
    label: str | None = None
    order: int
    destinationRefName: str | None = None


class KbnLinksPanelAttributes(BaseModel):
    layout: Literal["horizontal", "vertical"]
    links: list[KbnLink] = Field(default_factory=list)


class KbnLinksPanelEmbeddableConfig(KbnBasePanelEmbeddableConfig):
    attributes: KbnLinksPanelAttributes


class KbnLinksPanel(KbnBasePanel):
    """Represents a Links panel in the Kibana Kbn structure."""

    type: Literal["links"] = "links"
    embeddableConfig: KbnLinksPanelEmbeddableConfig
