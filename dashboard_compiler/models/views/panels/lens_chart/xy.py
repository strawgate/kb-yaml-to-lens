# ignore: N815
from typing import Any

from pydantic import BaseModel, Field


# Base class for Lens visualization state
class KbnLensVisualizationState(BaseModel):
    """Base model for the 'visualization' object within a Lens panel state in the Kibana JSON structure."""

    layers: list[dict[str, Any]] = Field(default_factory=list)  # Common field, specific layer models in subclasses


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
    assignments: list[Any] = Field(default_factory=list)
    specialAssignments: list[KbnXYVisualizationLayerColorMappingSpecialAssignment] = Field(
        default_factory=lambda: [KbnXYVisualizationLayerColorMappingSpecialAssignment()]
    )
    paletteId: str = "default"
    colorMode: dict[str, str] = Field(default_factory=lambda: {"type": "categorical"})


class KbnXYVisualizationLayer(BaseModel):
    layerId: str
    accessors: list[str]  # List of column IDs for metrics (Y-axis)
    xAccessor: str  # Column ID for dimension (X-axis)
    position: str
    seriesType: str
    showGridlines: bool
    layerType: str
    colorMapping: KbnXYVisualizationLayerColorMapping
    splitAccessor: str | None = None
    # Add yConfig if needed based on sample JSON


# Subclass Kbnfor XY visualizations state (JSON structure)
class KbnXYVisualizationState(KbnLensVisualizationState):
    """Represents the 'visualization' object for XY charts (bar, line, area) in the Kibana JSON structure."""

    legend: dict[str, Any]
    valueLabels: str
    fittingFunction: str
    axisTitlesVisibilitySettings: dict[str, bool]
    tickLabelsVisibilitySettings: dict[str, bool]
    labelsOrientation: dict[str, int]
    gridlinesVisibilitySettings: dict[str, bool]
    preferredSeriesType: str
    layers: list[KbnXYVisualizationLayer] = Field(default_factory=list)  # Use specific layer model
    showCurrentTimeMarker: bool
    yLeftExtent: dict[str, Any]
    yLeftScale: str
    yRightScale: str
    yTitle: str
    # Add other XY specific fields from sample JSON as needed
