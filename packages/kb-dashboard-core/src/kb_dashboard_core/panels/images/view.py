"""Markdown panel view model."""

from typing import Literal

from pydantic import Field

from kb_dashboard_core.panels.view import KbnBasePanel, KbnBasePanelEmbeddableConfig
from kb_dashboard_core.shared.view import BaseVwModel

# The following is an example of the JSON structure that these models represent. Do not remove:
# {
#     "type": "image",
#     "embeddableConfig": {                      <---- KbnImageEmbeddableConfig
#         "enhancements": {
#             "dynamicActions": {
#                 "events": []
#             }
#         },
#         "imageConfig": {                       <---- KbnImageConfig
#             "src": {                           <---- KbnUrlImageInfoSrc
#                 "type": "url",
#                 "url": "https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg"
#             },
#             "altText": "",
#             "backgroundColor": "",
#             "sizing": {                        <---- KbnUrlImageSizing
#                 "objectFit": "contain"
#             }
#         }
#     },
#     "panelIndex": "780e08fc-1a39-401b-849f-703b951bc243",
#     "gridData": {
#         "x": 0,
#         "y": 0,
#         "w": 24,
#         "h": 15,
#         "i": "780e08fc-1a39-401b-849f-703b951bc243"
#     }
# }


class KbnUrlImageInfoSrc(BaseVwModel):
    type: Literal['url'] = 'url'
    url: str


class KbnUrlImageSizing(BaseVwModel):
    objectFit: Literal['contain', 'cover', 'fill', 'none']


class KbnImageConfig(BaseVwModel):
    src: KbnUrlImageInfoSrc = Field(...)
    altText: str = Field(...)
    backgroundColor: str = Field(...)
    sizing: KbnUrlImageSizing = Field(...)


class KbnImageEmbeddableConfig(KbnBasePanelEmbeddableConfig):
    imageConfig: KbnImageConfig = Field(...)


class KbnImagePanel(KbnBasePanel):
    """Represents an image panel in the Kibana Kbn structure."""

    type: Literal['image'] = 'image'
    embeddableConfig: KbnImageEmbeddableConfig
