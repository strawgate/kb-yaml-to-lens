from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional

from dashboard_compiler.models.views.panels.lens import KbnBaseStateVisualization, KbnBaseStateVisualizationLayer



# Define nested models for Pie Visualization Layer based on samples
class KbnPieLayerColorMappingRule(BaseModel):
    type: str = "other"


class KbnPieLayerColorMappingColor(BaseModel):
    type: str = "loop"


class KbnPieLayerColorMappingSpecialAssignment(BaseModel):
    rule: KbnPieLayerColorMappingRule = Field(default_factory=KbnPieLayerColorMappingRule)
    color: KbnPieLayerColorMappingColor = Field(default_factory=KbnPieLayerColorMappingColor)
    touched: bool = False


class KbnPieLayerColorMapping(BaseModel):
    assignments: List[Any] = Field(default_factory=list)
    specialAssignments: List[KbnPieLayerColorMappingSpecialAssignment] = Field(
        default_factory=lambda: [KbnPieLayerColorMappingSpecialAssignment()]
    )
    paletteId: str = "default"
    colorMode: Dict[str, str] = Field(default_factory=lambda: {"type": "categorical"})


class KbnPieStateVisualizationLayer(KbnBaseStateVisualizationLayer):
    layerId: str
    primaryGroups: List[str]  # List of column IDs for dimensions
    metrics: List[str]  # List of column IDs for metrics
    numberDisplay: str
    categoryDisplay: str
    legendDisplay: str
    nestedLegend: bool
    layerType: str
    colorMapping: KbnPieLayerColorMapping


# Subclass Kbnfor Pie visualizations state (JSON structure)
class KbnPieVisualizationState(KbnBaseStateVisualization):
    """Represents the 'visualization' object for a Pie chart in the Kibana JSON structure."""

    shape: Literal["pie"] = "pie"
    layers: List[KbnPieStateVisualizationLayer] = Field(default_factory=list)  # Use specific layer model
    palette: Dict[str, Any]