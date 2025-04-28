from typing import Literal

from pydantic import BaseModel, Field

from dashboard_compiler.models.config.panels.base import BasePanel


class BaseLink(BaseModel):
    """Represents a link object within a Links panel in the YAML schema."""

    label: str | None = Field(None, description="(Optional) Display text for the link.")


class DashboardLink(BaseLink):
    """Represents a link object within a Links panel in the YAML schema."""

    dashboard: str | None = Field(None, description="(Optional) ID of dashboard or other object for dashboardLink.")


class UrlLink(BaseLink):
    """Represents a link object within a Links panel in the YAML schema."""

    url: str | None = Field(None, description="(Optional) URL for urlLink.")


class LinksPanel(BasePanel):
    """Represents a Links panel in the YAML schema."""

    type: Literal["links"] = "links"
    layout: Literal["horizontal","vertical"] | None = Field("horizontal", description="(Optional) Layout of the links (e.g., horizontal, vertical).")
    links: list[DashboardLink | UrlLink] = Field(..., description="(Required) List of link objects.")

    def add_link(self, link: DashboardLink | UrlLink) -> None:
        """
        Add a link to the Links panel.

        Args:
            link (DashboardLink | UrlLink): The link to add.
        """
        self.links.append(link)