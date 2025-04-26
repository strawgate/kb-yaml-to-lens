from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional


# Base class for Lens visualization state
class KbnLensVisualizationState(BaseModel):
    """Base model for the 'visualization' object within a Lens panel state in the Kibana JSON structure."""

    layers: List[Dict[str, Any]] = Field(default_factory=list)  # Common field, specific layer models in subclasses


# Define nested models for XY Visualization Layer based on samples
class KbnXYVisualizationLayerColorMappingRule(BaseModel):
    type: str = "other"


class KbnXYVisualizationLayerColorMappingColor(BaseModel):
    type: str = "loop"


class KbnXYVisualizationLayerColorMappingSpecialAssignment(BaseModel):
    rule: KbnXYVisualizationLayerColorMappingRule = Field(default_factory=KbnXYVisualizationLayerColorMappingRule)
    color: KbnXYVisualizationLayerColorMappingColor = Field(default_factory=KbnXYVisualizationLayerColorMappingColor)
    touched: bool = False


class KbnXYVisualizationLayerColorMapping(BaseModel):
    assignments: List[Any] = Field(default_factory=list)
    specialAssignments: List[KbnXYVisualizationLayerColorMappingSpecialAssignment] = Field(
        default_factory=lambda: [KbnXYVisualizationLayerColorMappingSpecialAssignment()]
    )
    paletteId: str = "default"
    colorMode: Dict[str, str] = Field(default_factory=lambda: {"type": "categorical"})


class KbnXYVisualizationLayer(BaseModel):
    layerId: str
    accessors: List[str]  # List of column IDs for metrics (Y-axis)
    xAccessor: str  # Column ID for dimension (X-axis)
    position: str
    seriesType: str
    showGridlines: bool
    layerType: str
    colorMapping: KbnXYVisualizationLayerColorMapping
    splitAccessor: Optional[str] = None
    # Add yConfig if needed based on sample JSON


# Subclass Kbnfor XY visualizations state (JSON structure)
class KbnXYVisualizationState(KbnLensVisualizationState):
    """Represents the 'visualization' object for XY charts (bar, line, area) in the Kibana JSON structure."""

    legend: Dict[str, Any]
    valueLabels: str
    fittingFunction: str
    axisTitlesVisibilitySettings: Dict[str, bool]
    tickLabelsVisibilitySettings: Dict[str, bool]
    labelsOrientation: Dict[str, int]
    gridlinesVisibilitySettings: Dict[str, bool]
    preferredSeriesType: str
    layers: List[KbnXYVisualizationLayer] = Field(default_factory=list)  # Use specific layer model
    showCurrentTimeMarker: bool
    yLeftExtent: Dict[str, Any]
    yLeftScale: str
    yRightScale: str
    yTitle: str
    # Add other XY specific fields from sample JSON as needed
