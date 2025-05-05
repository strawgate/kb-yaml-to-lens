"""Markdown panel view model."""

from typing import Any, Literal

from pydantic import Field

from dashboard_compiler.panels.view import KbnBasePanel, KbnBasePanelEmbeddableConfig
from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.shared.view import BaseVwModel

# The following is an example of the JSON structure that these models represent. Do not remove:
# {                                                 <-- KbnMarkdownPanel
#     "type": "visualization",
#     "embeddableConfig": {                         <-- KbnMarkdownEmbeddableConfig
#         "enhancements": {
#             "dynamicActions": {
#                 "events": []
#             }
#         },
#         "savedVis": {                             <-- KbnMarkdownSavedVis
#             "id": "",
#             "title": "Markdown Panel",
#             "description": "Cool description",
#             "type": "markdown",
#             "params": {                           <-- KbnMarkdownSavedVisParams
#                 "fontSize": 12,
#                 "openLinksInNewTab": false,
#                 "markdown": "# This is markdown"
#             },
#             "uiState": {},
#             "data": {                             <-- KbnMarkdownSavedVisData
#                 "aggs": [],
#                 "searchSource": {                 <-- KbnMarkdownSavedVisDataSearchSource
#                     "query": {                    <-- KbnQuery
#                         "query": "",
#                         "language": "kuery"
#                     },
#                     "filter": []                  <-- list[KbnFilter], empty in this case
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

KBN_MARKDOWN_DEFAULT_FONT_SIZE = 12
KBN_MARKDOWN_DEFAULT_OPEN_LINKS_IN_NEW_TAB = False


class KbnMarkdownSavedVisDataSearchSource(BaseVwModel):
    query: KbnQuery
    filter: list[Any]


class KbnMarkdownSavedVisData(BaseVwModel):
    aggs: list[Any] = Field(default_factory=list)
    searchSource: KbnMarkdownSavedVisDataSearchSource


class KbnMarkdownSavedVisParams(BaseVwModel):
    fontSize: int
    openLinksInNewTab: bool
    markdown: str


class KbnMarkdownSavedVis(BaseVwModel):
    type: Literal['markdown'] = 'markdown'
    id: str = ''
    title: str
    description: str = ''
    params: KbnMarkdownSavedVisParams
    uiState: dict[str, Any] = Field(default_factory=dict)
    data: KbnMarkdownSavedVisData


class KbnMarkdownEmbeddableConfig(KbnBasePanelEmbeddableConfig):
    savedVis: KbnMarkdownSavedVis


class KbnMarkdownPanel(KbnBasePanel):
    """Represents a Markdown panel in the Kibana Kbn structure."""

    type: Literal['visualization'] = 'visualization'
    embeddableConfig: KbnMarkdownEmbeddableConfig
