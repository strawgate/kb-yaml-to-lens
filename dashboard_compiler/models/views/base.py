from pydantic import BaseModel

from pydantic import Field
from typing import Dict, Any



class KbnGridData(BaseModel):
    """Represents the 'gridData' object in the Kibana JSON structure."""

    x: int
    y: int
    w: int
    h: int
    i: str

class KbnBasePanelEmbeddableConfig(BaseModel):
    enhancements: Dict[str, Any] = Field(default_factory=dict)


class KbnBasePanel(BaseModel):
    """Base model for panel objects in the Kibana JSON structure."""

    # type: Literal["visualization", "search", "map", "lens", "links"]
    panelIndex: str
    gridData: KbnGridData
    # embeddableConfig: KbnBasePanelEmbeddableConfig
