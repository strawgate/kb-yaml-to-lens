"""Base classes for chart visualizations."""

from typing import Annotated, Any

from pydantic import Field

from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone


class KbnLayerColorMappingRule(BaseVwModel):
    """Color mapping rule configuration."""

    type: str = 'other'


class KbnLayerColorMappingColor(BaseVwModel):
    """Color mapping color configuration."""

    type: str = 'loop'


class KbnLayerColorMappingSpecialAssignment(BaseVwModel):
    """Special assignment for color mapping."""

    rule: KbnLayerColorMappingRule = Field(default_factory=KbnLayerColorMappingRule)
    color: KbnLayerColorMappingColor = Field(default_factory=KbnLayerColorMappingColor)
    touched: bool = False


class KbnLayerColorMapping(BaseVwModel):
    """Represents color mapping configuration for a visualization layer."""

    assignments: list[Any] = Field(default_factory=list)
    specialAssignments: list[KbnLayerColorMappingSpecialAssignment] = Field(
        default_factory=lambda: [KbnLayerColorMappingSpecialAssignment()],
    )
    paletteId: str = 'eui_amsterdam_color_blind'
    colorMode: dict[str, str] = Field(default_factory=lambda: {'type': 'categorical'})


class KbnBaseStateVisualizationLayer(BaseVwModel):
    """Base class for visualization layers."""

    layerId: str
    layerType: str
    colorMapping: Annotated[KbnLayerColorMapping | None, OmitIfNone()] = None


class KbnBaseStateVisualization(BaseVwModel):
    """Base class for visualization state."""

    layers: list[KbnBaseStateVisualizationLayer] = Field(...)
