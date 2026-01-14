"""Collapsible section view model."""

from typing import Annotated

from pydantic import Field

from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone

# The following is an example of the JSON structure that these models represent. Do not remove:
# Sections are stored in the dashboard attributes as a separate 'sections' array:
# {
#     "attributes": {
#         "title": "My Dashboard",
#         "sections": [                             <-- List of KbnSection
#             {
#                 "uid": "section-uuid-1",
#                 "title": "System Metrics",
#                 "collapsed": false,
#                 "gridData": { "y": 0 }
#             },
#             {
#                 "uid": "section-uuid-2",
#                 "title": "Network Metrics",
#                 "collapsed": true,
#                 "gridData": { "y": 15 }
#             }
#         ],
#         "panelsJSON": [
#             {
#                 "gridData": {
#                     "x": 0,
#                     "y": 0,
#                     "w": 24,
#                     "h": 10,
#                     "i": "panel-1",
#                     "sectionId": "section-uuid-1"  <-- Links panel to section
#                 },
#                 ...
#             }
#         ],
#         ...
#     }
# }


class KbnSectionGridData(BaseVwModel):
    """Grid data for a section (only contains y position)."""

    y: int = Field(...)
    """The vertical position of the section on the dashboard grid."""


class KbnSection(BaseVwModel):
    """Represents a collapsible section in the Kibana dashboard structure."""

    uid: str = Field(...)
    """The unique identifier for the section."""

    title: str = Field(...)
    """The title displayed on the section header."""

    collapsed: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    """Whether the section is initially collapsed."""

    gridData: KbnSectionGridData = Field(...)
    """The grid positioning data for the section."""
