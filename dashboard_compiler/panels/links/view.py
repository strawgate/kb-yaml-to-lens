"""Types for Kibana Links panel in the dashboard compiler.

Reference: https://github.com/elastic/kibana/blob/main/src/platform/plugins/private/links/common/content_management/v1/types.ts
"""

from typing import Annotated, Literal

from pydantic import Field

from dashboard_compiler.panels.view import KbnBasePanel, KbnBasePanelEmbeddableConfig
from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone

# The following is an example of the JSON structure that these models represent. Do not remove:
# {                                                 <-- KbnLinksPanel
#     "type": "links",
#     "embeddableConfig": {                         <-- KbnLinksPanelEmbeddableConfig
#         "attributes": {                           <-- KbnLinksPanelAttributes
#             "layout": "horizontal",
#             "links": [                            <-- list[KbnLinkTypes]
#                 {
#                     "type": "dashboardLink",
#                     "id": "9f2896f6-9ca0-4f63-9960-631d5af3840c",
#                     "order": 0,
#                     "destinationRefName": "link_9f2896f6-9ca0-4f63-9960-631d5af3840c_dashboard"
#                 }
#             ]
#         },
#         "enhancements": {}
#     },
#     "panelIndex": "e19a731d-0163-490a-a691-0bd1b1264d0b",
#     "gridData": {
#         "i": "e19a731d-0163-490a-a691-0bd1b1264d0b",
#         "y": 0,
#         "x": 0,
#         "w": 48,
#         "h": 2
#     }
# }


class KbnBaseLink(BaseVwModel):
    id: str = Field(...)
    """The unique identifier for the link."""

    order: int = Field(...)
    """Order of the link in the list."""

    label: str | None = Field(default=None)
    """Friendly label for the link. Optional, can be used for display purposes."""


type KbnLinkTypes = KbnDashboardLink | KbnWebLink


class KbnDashboardLinkOptions(BaseVwModel):
    """Options for a dashboard link in the Kibana Links panel."""

    openInNewTab: bool = Field(...)
    """If `true`, the link will open in a new browser tab."""

    useCurrentDateRange: bool = Field(...)
    """If `true`, the link will use the current date range when navigating to the dashboard."""

    useCurrentFilters: bool = Field(...)
    """If `true`, the link will use the current filters when navigating to the dashboard."""


class KbnDashboardLink(KbnBaseLink):
    """Represents a link to a dashboard."""

    type: Literal['dashboardLink'] = 'dashboardLink'
    """Type of the link, specifically for dashboard links."""

    options: Annotated[KbnDashboardLinkOptions | None, OmitIfNone()] = Field(default=None)
    """Options for the dashboard link, such as whether to open in a new tab or use current filters."""

    destinationRefName: str = Field(...)
    """Reference name for the destination dashboard."""


class KbnWebLinkOptions(BaseVwModel):
    """Options for a web link in the Kibana Links panel."""

    openInNewTab: bool = Field(...)
    """If `true`, the link will open in a new browser tab."""

    encodeUrl: bool = Field(...)
    """If `true`, the URL will be URL-encoded when navigating to the external resource."""


class KbnWebLink(KbnBaseLink):
    """Represents a link to an external web resource."""

    type: Literal['externalLink'] = 'externalLink'
    """Type of the link, specifically for web links."""

    options: Annotated[KbnWebLinkOptions | None, OmitIfNone()] = Field(default=None)

    destination: str = Field(...)
    """The URL to which the link points."""


class KbnLinksPanelAttributes(BaseVwModel):
    layout: Literal['horizontal', 'vertical']
    links: list[KbnLinkTypes] = Field(default_factory=list)


class KbnLinksPanelEmbeddableConfig(KbnBasePanelEmbeddableConfig):
    attributes: KbnLinksPanelAttributes


class KbnLinksPanel(KbnBasePanel):
    """Represents a Links panel in the Kibana Kbn structure."""

    type: Literal['links'] = 'links'
    embeddableConfig: KbnLinksPanelEmbeddableConfig
