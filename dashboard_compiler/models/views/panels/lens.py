from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional

from dashboard_compiler.models.views.base import KbnBasePanel, KbnBasePanelEmbeddableConfig



# Model relationships:
# - KbnLensPanel
#   - KbnLensPanelEmbeddableConfig
#     - KbnLensPanelAttributes
#       - KbnLensState
#         - KbnBaseStateVisualization <--- The subclassed visualizations replace this
#           - KbnBaseStateVisualizationLayer <--- The subclassed visualizations replace this
#         - KbnDataSourceState
#           - KbnLayerDataSourceState
#             - KbnColumn


# Inheriting modules must inherit from:
#  - KbnBaseStateVisualization for visualization state
#  - KbnBaseStateVisualizationLayer for layer state


class KbnColumn(BaseModel):
    """Represents a column definition within KbnDataSourceStates.formBased.layers.<layerId>.columns in the Kibana JSON structure."""

    label: str
    dataType: str
    operationType: str
    sourceField: str
    isBucketed: bool
    scale: str
    params: Dict[str, Any] = Field(default_factory=dict)
    isMetric: Optional[bool] = None  # Only present for metrics


class KbnLayerDataSourceState(BaseModel):
    """Represents the datasource state for a single layer within a Lens panel in the Kibana JSON structure."""

    columns: Dict[str, KbnColumn] = Field(default_factory=dict)
    columnOrder: List[str] = Field(default_factory=list)
    incompleteColumns: Dict[str, Any] = Field(default_factory=dict)
    sampling: int


class KbnDataSourceState(BaseModel):
    """Represents the overall datasource states for a Lens panel in the Kibana JSON structure."""

    formBased: Dict[str, Dict[str, KbnLayerDataSourceState]] = Field(
        default_factory=dict
    )  # Structure: formBased -> layers -> {layerId: KbnLayerDataSourceState}
    indexpattern: Dict[str, Any] = Field(default_factory=dict)  # Based on samples, seems to be empty
    textBased: Dict[str, Any] = Field(default_factory=dict)  # Based on samples, seems to be empty


class KbnFilter(BaseModel):
    """Represents a filter object within state.filters in the Kibana JSON structure."""

    state: Dict[str, str] = Field(default_factory=lambda: {"store": "appState"})
    meta: Dict[str, Any]
    query: Dict[str, str] = Field(default_factory=dict)  # Can be empty


class KbnReference(BaseModel):
    """Represents a reference object in the Kibana JSON structure."""

    type: str
    id: str
    name: str


class KbnLayerColorMappingRule(BaseModel):
    type: str = "other"


class KbnLayerColorMappingColor(BaseModel):
    type: str = "loop"


class KbnLayerColorMappingSpecialAssignment(BaseModel):
    rule: KbnLayerColorMappingRule = Field(default_factory=KbnLayerColorMappingRule)
    color: KbnLayerColorMappingColor = Field(default_factory=KbnLayerColorMappingColor)
    touched: bool = False


class KbnLayerColorMapping(BaseModel):
    assignments: List[Any] = Field(default_factory=list)
    specialAssignments: List[KbnLayerColorMappingSpecialAssignment] = Field(
        default_factory=lambda: [KbnLayerColorMappingSpecialAssignment()]
    )
    paletteId: str = "default"
    colorMode: Dict[str, str] = Field(default_factory=lambda: {"type": "categorical"})


class KbnBaseStateVisualizationLayer(BaseModel):
    layerId: str
    # ... to be populated by subclasses
    layerType: str
    colorMapping: KbnLayerColorMapping | None


class KbnBaseStateVisualization(BaseModel):
    shape: str
    layers: list[KbnBaseStateVisualizationLayer] = Field(default_factory=list)


class KbnLensState(BaseModel):
    """Represents the 'state' object within a Lens panel in the Kibana JSON structure."""

    visualization: KbnBaseStateVisualization  # Holds the specific visualization state
    query: Dict[str, str] = Field(default_factory=lambda: {"query": "", "language": "kuery"})
    filters: List[KbnFilter] = Field(default_factory=list)
    DataSourceStates: KbnDataSourceState = Field(default_factory=KbnDataSourceState)
    internalReferences: List[Any] = Field(default_factory=list)
    adHocDataViews: Dict[str, Any] = Field(default_factory=dict)


class KbnLensPanelAttributes(BaseModel):
    title: str = ""
    visualizationType: Literal["lnsXY", "lnsPie"]
    type: Literal["lens"]
    references: list = Field(default_factory=list)
    state: KbnLensState


class KbnLensPanelEmbeddableConfig(KbnBasePanelEmbeddableConfig):
    attributes: KbnLensPanelAttributes
    syncColors: bool = Field(
        default=False,
        description="(Optional) Whether to sync colors across visualizations. Defaults to False.",
    )
    syncCursor: bool = Field(
        default=True,
        description="(Optional) Whether to sync cursor across visualizations. Defaults to True.",
    )
    syncTooltips: bool = Field(
        default=False,
        description="(Optional) Whether to sync tooltips across visualizations. Defaults to False.",
    )
    filters: list = Field(
        default_factory=list,
        description="(Optional) List of filters applied to the Lens visualization. Defaults to empty list.",
    )
    query: Dict[str, Any] = Field(
        default_factory=lambda: {"query": "", "language": "kuery"},
        description="(Optional) Query object for the Lens visualization. Defaults to empty query with 'kuery' language.",
    )


class KbnLensPanel(KbnBasePanel):
    """Represents a Lens panel in the Kibana Kbn structure."""

    type: Literal["lens"] = "lens"
    embeddableConfig: KbnLensPanelEmbeddableConfig
