"""Configuration for Links Panel."""

from typing import Annotated, Literal

from pydantic import Discriminator, Field, Tag

from kb_dashboard_core.panels.base import BasePanel
from kb_dashboard_core.shared.config import BaseCfgModel


class BaseLink(BaseCfgModel):
    """Base class for defining link objects within a Links panel.

    Specific link types (e.g., DashboardLink, UrlLink) inherit from this base class.
    """

    id: str | None = Field(default=None)
    """An optional unique identifier for the link. Not normally required."""

    label: str | None = Field(default=None)
    """The text that will be displayed for the link. Kibana defaults to showing the URL if not set."""


def get_link_type(v: dict[str, object] | object) -> str:
    """Extract link type for discriminated union validation.

    Args:
        v: Either a dict (during validation) or a link instance.

    Returns:
        str: The link type identifier ('dashboard' or 'url').

    """
    if isinstance(v, dict):
        if 'dashboard' in v:
            return 'dashboard'
        if 'url' in v:
            return 'url'
        msg = f'Cannot determine link type from dict with keys: {list(v)}'  # pyright: ignore[reportUnknownArgumentType]
        raise ValueError(msg)
    if hasattr(v, 'dashboard'):
        return 'dashboard'
    if hasattr(v, 'url'):
        return 'url'
    msg = f'Cannot determine link type from object: {type(v).__name__}'
    raise ValueError(msg)


type LinkTypes = Annotated[
    Annotated[DashboardLink, Tag('dashboard')] | Annotated[UrlLink, Tag('url')],
    Discriminator(get_link_type),
]


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


class LinksPanelConfig(BaseCfgModel):
    """Configuration specific to Links panels."""

    layout: Literal['horizontal', 'vertical'] | None = Field(default=None)
    """The layout of the links in the panel, either 'horizontal' or 'vertical'. Kibana defaults to 'horizontal' if not set."""

    items: list[LinkTypes] = Field(default_factory=list)
    """A list of link objects to be displayed in the panel."""


class LinksPanel(BasePanel):
    """Represents a Links panel configuration.

    Links panels are used to display a collection of links to other dashboards,
    saved objects, or external URLs.

    Examples:
        Linking to another Dashboard:
        ```yaml
        dashboards:
          - name: "Main Overview"
            panels:
              - title: "Navigate to User Details"
                size: { w: 24, h: 2 }
                links:
                  items:
                    - label: "View User Activity Dashboard"
                      dashboard: "user-activity-dashboard-id"
        ```

        Linking to an External URL:
        ```yaml
        dashboards:
          - name: "Main Overview"
            panels:
              - title: "External Resources"
                size: { w: 24, h: 2 }
                links:
                  items:
                    - label: "Project Documentation"
                      url: "https://docs.example.com/project-alpha"
                      new_tab: true
        ```

        Complex configuration with multiple link types:
        ```yaml
        dashboards:
          - name: "Operations Hub"
            panels:
              - title: "Quick Access"
                size: { w: 48, h: 3 }
                links:
                  layout: "vertical"
                  items:
                  - label: "Service Health Dashboard"
                    dashboard: "service-health-monitor-v2"
                  - label: "Runbook Wiki"
                    url: "https://internal.wiki/ops/runbooks"
                    new_tab: true
        ```
    """

    links_config: LinksPanelConfig = Field(..., alias='links')
    """Links panel configuration."""
