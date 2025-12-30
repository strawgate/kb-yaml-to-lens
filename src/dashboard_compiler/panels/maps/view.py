"""Map panel view model."""

from typing import Annotated, Literal

from pydantic import Field

from dashboard_compiler.panels.view import KbnBasePanel, KbnBasePanelEmbeddableConfig
from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone

# The following is an example of the JSON structure that these models represent. Do not remove:
# {
#     "version": "8.11.0",
#     "type": "map",
#     "gridData": {
#         "x": 0,
#         "y": 31,
#         "w": 24,
#         "h": 14,
#         "i": "11"
#     },
#     "panelIndex": "11",
#     "embeddableConfig": {                          <---- KbnMapEmbeddableConfig
#         "isLayerTOCOpen": false,
#         "hiddenLayers": [],
#         "mapCenter": {                             <---- KbnMapCenter
#             "lat": 45.88578,
#             "lon": -15.07605,
#             "zoom": 2.11
#         },
#         "openTOCDetails": [],
#         "enhancements": {
#             "dynamicActions": {
#                 "events": []
#             }
#         }
#     },
#     "panelRefName": "panel_11"
# }


class KbnMapCenter(BaseVwModel):
    """Map center configuration for Kibana."""

    lat: float
    lon: float
    zoom: float


class KbnMapEmbeddableConfig(KbnBasePanelEmbeddableConfig):
    """Embeddable configuration for a Kibana map panel."""

    isLayerTOCOpen: Annotated[bool | None, OmitIfNone] = Field(
        default=None,
        serialization_alias='isLayerTOCOpen',
    )
    hiddenLayers: Annotated[list[str] | None, OmitIfNone] = Field(
        default=None,
    )
    mapCenter: Annotated[KbnMapCenter | None, OmitIfNone] = Field(
        default=None,
    )
    openTOCDetails: Annotated[list[str] | None, OmitIfNone] = Field(
        default=None,
    )


class KbnMapPanel(KbnBasePanel):
    """Represents a Kibana map panel."""

    version: str = Field(default='8.11.0')
    type: Literal['map'] = 'map'
    embeddableConfig: KbnMapEmbeddableConfig
    panelRefName: str
