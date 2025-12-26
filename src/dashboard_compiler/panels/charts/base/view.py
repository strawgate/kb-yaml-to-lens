"""Base classes for chart visualizations."""

from typing import Annotated, Any

from pydantic import Field

from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone

# Default values for color mapping - set during compilation
KBN_DEFAULT_COLOR_MAPPING_RULE_TYPE = 'other'
KBN_DEFAULT_COLOR_MAPPING_COLOR_TYPE = 'loop'
KBN_DEFAULT_COLOR_MAPPING_TOUCHED = False
KBN_DEFAULT_COLOR_MAPPING_PALETTE_ID = 'eui_amsterdam_color_blind'
KBN_DEFAULT_COLOR_MAPPING_COLOR_MODE_TYPE = 'categorical'


class KbnLayerColorMappingRule(BaseVwModel):
    """Color mapping rule configuration."""

    type: str = Field(...)


class KbnLayerColorMappingColor(BaseVwModel):
    """Color mapping color configuration."""

    type: str = Field(...)


class KbnLayerColorMappingSpecialAssignment(BaseVwModel):
    """Special assignment for color mapping."""

    rule: KbnLayerColorMappingRule = Field(...)
    color: KbnLayerColorMappingColor = Field(...)
    touched: bool = Field(...)


class KbnLayerColorMapping(BaseVwModel):
    """Represents color mapping configuration for a visualization layer."""

    assignments: list[Any] = Field(...)
    specialAssignments: list[KbnLayerColorMappingSpecialAssignment] = Field(...)
    paletteId: str = Field(...)
    colorMode: dict[str, str] = Field(...)


class KbnBaseStateVisualizationLayer(BaseVwModel):
    """Base class for visualization layers."""

    layerId: str
    layerType: str
    colorMapping: Annotated[KbnLayerColorMapping | None, OmitIfNone()] = None


class KbnBaseStateVisualization(BaseVwModel):
    """Base class for visualization state."""

    layers: list[KbnBaseStateVisualizationLayer] = Field(...)
