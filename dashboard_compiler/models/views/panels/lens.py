from typing import Any, Literal

from pydantic import BaseModel, Field, RootModel

from dashboard_compiler.models.views.base import KbnBasePanel, KbnBasePanelEmbeddableConfig, KbnFilter, KbnReference

# Model relationships:
# - KbnLensPanel
#   - KbnLensPanelEmbeddableConfig
#     - KbnLensPanelAttributes
#       - KbnLensPanelState
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
    params: dict[str, Any] = Field(default_factory=dict)
    # isMetric: Optional[bool] = None  # Only present for metrics


class KbnLayerDataSourceState(BaseModel):
    """Represents the datasource state for a single layer within a Lens panel in the Kibana JSON structure."""

    columns: dict[str, KbnColumn] = Field(default_factory=dict)
    columnOrder: list[str] = Field(default_factory=list)
    incompleteColumns: dict[str, Any] = Field(default_factory=dict)
    sampling: int


class KbnLayerDataSourceStateById(RootModel):
    """Represents a mapping of layer IDs to their corresponding KbnLayerDataSourceState objects."""

    root: dict[str, KbnLayerDataSourceState] = Field(default_factory=dict)


class KbnFormBasedDataSourceState(BaseModel):
    layers: KbnLayerDataSourceStateById = Field(default_factory=lambda: KbnLayerDataSourceStateById())


class KbnTextBasedDataSourceState(BaseModel):
    layers: KbnLayerDataSourceStateById = Field(default_factory=lambda: KbnLayerDataSourceStateById())


class KbnIndexPatternDataSourceState(BaseModel):
    layers: KbnLayerDataSourceStateById = Field(default_factory=lambda: KbnLayerDataSourceStateById())


class KbnDataSourceState(BaseModel):
    """Represents the overall datasource states for a Lens panel in the Kibana JSON structure."""

    formBased: KbnIndexPatternDataSourceState = Field(
        default_factory=KbnIndexPatternDataSourceState
    )  # Structure: formBased -> layers -> {layerId: KbnLayerDataSourceState}
    indexpattern: KbnIndexPatternDataSourceState = Field(
        default_factory=KbnIndexPatternDataSourceState
    )  # Structure: indexpattern -> layers -> {layerId: KbnLayerDataSourceState}
    textBased: KbnTextBasedDataSourceState = Field(
        default_factory=KbnTextBasedDataSourceState
    )  # Structure: textBased -> layers -> {layerId: KbnLayerDataSourceState}


class KbnLayerColorMappingRule(BaseModel):
    type: str = "other"


class KbnLayerColorMappingColor(BaseModel):
    type: str = "loop"


class KbnLayerColorMappingSpecialAssignment(BaseModel):
    rule: KbnLayerColorMappingRule = Field(default_factory=KbnLayerColorMappingRule)
    color: KbnLayerColorMappingColor = Field(default_factory=KbnLayerColorMappingColor)
    touched: bool = False


class KbnLayerColorMapping(BaseModel):
    assignments: list[Any] = Field(default_factory=list)
    specialAssignments: list[KbnLayerColorMappingSpecialAssignment] = Field(
        default_factory=lambda: [KbnLayerColorMappingSpecialAssignment()]
    )
    paletteId: str = "default"
    colorMode: dict[str, str] = Field(default_factory=lambda: {"type": "categorical"})


class KbnBaseStateVisualizationLayer(BaseModel):
    layerId: str
    # ... to be populated by subclasses
    layerType: str
    colorMapping: KbnLayerColorMapping = Field(default_factory=KbnLayerColorMapping)


class KbnBaseStateVisualization(BaseModel):
    shape: str
    layers: list[KbnBaseStateVisualizationLayer] = Field(default_factory=list)


class KbnLensPanelState(BaseModel):
    """Represents the 'state' object within a Lens panel in the Kibana JSON structure."""

    visualization: KbnBaseStateVisualization  # Holds the specific visualization state
    query: dict[str, str] = Field(default_factory=lambda: {"query": "", "language": "kuery"})
    filters: list[KbnFilter] = Field(default_factory=list)
    datasourceStates: KbnDataSourceState = Field(default_factory=KbnDataSourceState)
    internalReferences: list[Any] = Field(default_factory=list)
    adHocDataViews: dict[str, Any] = Field(default_factory=dict)


class KbnLensPanelAttributes(BaseModel):
    title: str = ""
    visualizationType: Literal["lnsXY", "lnsPie"]
    type: Literal["lens"] = "lens"
    references: list[KbnReference] = Field(default_factory=list)
    state: KbnLensPanelState


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
    query: dict[str, Any] = Field(
        default_factory=lambda: {"query": "", "language": "kuery"},
        description="(Optional) Query object for the Lens visualization. Defaults to empty query with 'kuery' language.",
    )


class KbnLensPanel(KbnBasePanel):
    """Represents a Lens panel in the Kibana Kbn structure."""

    type: Literal["lens"] = "lens"
    embeddableConfig: KbnLensPanelEmbeddableConfig
