"""Configuration for Links Panel."""

from typing import Literal, Self

from pydantic import Field

from dashboard_compiler.panels.base import BasePanel
from dashboard_compiler.shared.config import BaseCfgModel


class BaseLink(BaseCfgModel):
    """Base class for defining link objects within a Links panel.

    Specific link types (e.g., DashboardLink, UrlLink) inherit from this base class.
    """

    id: str | None = Field(default=None)
    """An optional unique identifier for the link. Not normally required."""

    label: str | None = Field(default=None)
    """The text that will be displayed for the link. Kibana defaults to showing the URL if not set."""


type LinkTypes = DashboardLink | UrlLink


class DashboardLink(BaseLink):
    """Represents a link to another dashboard within a Links panel."""

    dashboard: str = Field(...)
    """The ID of the dashboard that the link points to."""

    new_tab: bool | None = Field(default=None)
    """If `true`, links will open in a new browser tab. Kibana defaults to `false` if not set."""

    with_time: bool | None = Field(default=None)
    """If `true`, the links will inherit the time range from the dashboard. Kibana defaults to `True` if not set."""

    with_filters: bool | None = Field(default=None)
    """If `true`, the links will inherit the filters from the dashboard. Kibana defaults to `True` if not set."""


class UrlLink(BaseLink):
    """Represents a link to an external URL within a Links panel."""

    url: str = Field(...)
    """The Web URL that the link points to."""

    encode: bool | None = Field(default=None)
    """If `true`, the URL will be URL-encoded. Kibana defaults to `True` if not set."""

    new_tab: bool | None = Field(default=None)
    """If `true`, the link will open in a new browser tab. Kibana defaults to `false` if not set."""


class LinksPanel(BasePanel):
    """Represents a Links panel configuration.

    Links panels are used to display a collection of links to other dashboards,
    saved objects, or external URLs.
    """

    type: Literal['links'] = 'links'

    layout: Literal['horizontal', 'vertical'] | None = Field(default=None)
    """The layout of the links in the panel, either 'horizontal' or 'vertical'. Kibana defaults to 'horizontal' if not set."""

    links: list[LinkTypes] = Field(default_factory=list)
    """A list of link objects to be displayed in the panel."""

    def add_link(self, link: LinkTypes) -> Self:
        """Add a link object to the Links panel's links list.

        Args:
            link (LinkTypes): The link object to add.

        Returns:
            Self: The current instance of the LinksPanel for method chaining.

        """
        self.links.append(link)
        return self
