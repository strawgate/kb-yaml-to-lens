"""Vega panel view model."""

from typing import Any, Literal

from pydantic import Field

from kb_dashboard_core.panels.view import KbnBasePanel, KbnBasePanelEmbeddableConfig
from kb_dashboard_core.queries.view import KbnQuery
from kb_dashboard_core.shared.view import BaseVwModel

# The following is an example of the JSON structure that these models represent. Do not remove:
# {                                                 <-- KbnVegaPanel
#     "type": "visualization",
#     "embeddableConfig": {                         <-- KbnVegaEmbeddableConfig
#         "enhancements": {
#             "dynamicActions": {
#                 "events": []
#             }
#         },
#         "savedVis": {                             <-- KbnVegaSavedVis
#             "id": "",
#             "title": "Vega Panel",
#             "description": "A Vega visualization",
#             "type": "vega",
#             "params": {                           <-- KbnVegaSavedVisParams
#                 "spec": "{\"$schema\": \"https://vega.github.io/schema/vega/v3.json\", ...}"
#             },
#             "uiState": {},
#             "data": {                             <-- KbnVegaSavedVisData
#                 "aggs": [],
#                 "searchSource": {                 <-- KbnVegaSavedVisDataSearchSource
#                     "query": {                    <-- KbnQuery
#                         "query": "",
#                         "language": "kuery"
#                     },
#                     "filter": []
#                 }
#             }
#         }
#     },
#     "panelIndex": "780e08fc-1a39-401b-849f-703b951bc243",
#     "gridData": {                                 <-- KbnGridData
#         "x": 0,
#         "y": 0,
#         "w": 24,
#         "h": 15,
#         "i": "780e08fc-1a39-401b-849f-703b951bc243"
#     }
# }


class KbnVegaSavedVisDataSearchSource(BaseVwModel):
    query: KbnQuery
    filter: list[Any]


class KbnVegaSavedVisData(BaseVwModel):
    aggs: list[Any] = Field(...)
    searchSource: KbnVegaSavedVisDataSearchSource


class KbnVegaSavedVisParams(BaseVwModel):
    spec: str


class KbnVegaSavedVis(BaseVwModel):
    type: Literal['vega'] = 'vega'
    id: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    params: KbnVegaSavedVisParams = Field(...)
    uiState: dict[str, Any] = Field(...)
    data: KbnVegaSavedVisData = Field(...)


class KbnVegaEmbeddableConfig(KbnBasePanelEmbeddableConfig):
    savedVis: KbnVegaSavedVis


class KbnVegaPanel(KbnBasePanel):
    """Represents a Vega panel in the Kibana Kbn structure."""

    type: Literal['visualization'] = 'visualization'
    embeddableConfig: KbnVegaEmbeddableConfig
