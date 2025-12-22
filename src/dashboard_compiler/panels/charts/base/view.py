"""Base classes for chart visualizations."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone


class KbnLayerColorMappingRule(BaseVwModel):
    """Color mapping rule configuration."""

    type: str = 'matchExactly'
    """Type of rule: 'matchExactly' for categorical values, 'other' for fallback."""

    values: Annotated[list[str] | None, OmitIfNone()] = None
    """Values to match for categorical assignments."""


class KbnLayerColorMappingColor(BaseVwModel):
    """Color mapping color configuration."""

    type: str = 'loop'
    """Type of color: 'loop' for palette cycling, 'colorCode' for custom hex colors."""

    colorCode: Annotated[str | None, OmitIfNone()] = None
    """Hex color code (e.g., '#FF0000') for custom color assignments."""


class KbnLayerColorMappingAssignment(BaseVwModel):
    """Manual color assignment for specific values."""

    rule: KbnLayerColorMappingRule
    color: KbnLayerColorMappingColor
    touched: bool = False


class KbnLayerColorMappingSpecialAssignment(BaseVwModel):
    """Special assignment for color mapping (fallback/default colors)."""

    rule: KbnLayerColorMappingRule = Field(default_factory=lambda: KbnLayerColorMappingRule(type='other'))
    color: KbnLayerColorMappingColor = Field(default_factory=KbnLayerColorMappingColor)
    touched: bool = False


class KbnLayerColorMapping(BaseVwModel):
    """Represents color mapping configuration for a visualization layer."""

    assignments: list[KbnLayerColorMappingAssignment] = Field(default_factory=list)
    """Manual color assignments to specific data values."""

    specialAssignments: list[KbnLayerColorMappingSpecialAssignment] = Field(
        default_factory=lambda: [KbnLayerColorMappingSpecialAssignment()],
    )
    """Special assignments for fallback colors."""

    paletteId: str = 'eui_amsterdam_color_blind'
    """Palette ID to use for unassigned colors."""

    colorMode: dict[str, str] = Field(default_factory=lambda: {'type': 'categorical'})
    """Color mode configuration."""


class KbnBaseStateVisualizationLayer(BaseVwModel):
    """Base class for visualization layers."""

    layerId: str
    layerType: str
    colorMapping: Annotated[KbnLayerColorMapping | None, OmitIfNone()] = None


class KbnBaseStateVisualization(BaseVwModel):
    """Base class for visualization state."""

    layers: list[KbnBaseStateVisualizationLayer] = Field(...)
