from pydantic import BaseModel, Field
from typing import List, Optional, Literal

from dashboard_compiler.models.config.panels.base import BasePanel


class Link(BaseModel):
    """Represents a link object within a Links panel in the YAML schema."""

    type: Literal["dashboardLink", "urlLink"] = Field(..., description="(Required) Type of the link (e.g., dashboardLink, urlLink).")
    id: Optional[str] = Field(None, description="(Optional) ID of dashboard or other object for dashboardLink.")
    url: Optional[str] = Field(None, description="(Optional) URL for urlLink.")
    label: Optional[str] = Field(None, description="(Optional) Display text for the link.")


class LinksPanel(BasePanel):
    """Represents a Links panel in the YAML schema."""

    type: Literal["links"] = "links"
    layout: Optional[str] = Field(None, description="(Optional) Layout of the links (e.g., horizontal, vertical).")  # Inferred from JSON
    links: List[Link] = Field(..., description="(Required) List of link objects.")
