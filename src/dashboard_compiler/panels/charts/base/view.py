"""Base classes for chart visualizations."""

from typing import Annotated, Any

from pydantic import Field

from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone


class KbnLayerColorMappingRule(BaseVwModel):
    """View model for color mapping rule configuration.

    Defines a rule for color assignment in visualization layers. Rules can be 'other'
    for default assignments or specific rule types for conditional color mapping.

    See Also:
        Related to color mapping types in Kibana Lens visualizations.
    """

    type: str = 'other'
    """Type of color mapping rule ('other' for default)."""


class KbnLayerColorMappingColor(BaseVwModel):
    """View model for color mapping color configuration.

    Defines the color assignment strategy for visualization layers. The 'loop' type
    means colors are assigned in a repeating pattern from the palette.

    See Also:
        Related to color mapping types in Kibana Lens visualizations.
    """

    type: str = 'loop'
    """Color assignment type ('loop' for repeating pattern)."""


class KbnLayerColorMappingSpecialAssignment(BaseVwModel):
    """View model for special color assignment configuration.

    Defines a special case color assignment rule for visualization layers, combining
    a color rule with a color assignment strategy and tracking whether it has been
    modified by the user.

    See Also:
        Related to color mapping types in Kibana Lens visualizations.
    """

    rule: KbnLayerColorMappingRule = Field(default_factory=KbnLayerColorMappingRule)
    """The color mapping rule to apply."""

    color: KbnLayerColorMappingColor = Field(default_factory=KbnLayerColorMappingColor)
    """The color assignment strategy."""

    touched: bool = False
    """Whether this assignment has been modified by the user."""


class KbnLayerColorMapping(BaseVwModel):
    """View model for color mapping configuration for visualization layers.

    Defines how colors are assigned to data series in a visualization layer. Includes
    the color palette to use, color assignment mode, and special assignment rules for
    specific conditions or categories.

    This model is used across different visualization types (XY, pie, etc.) to maintain
    consistent color mapping behavior.

    See Also:
        Related to color mapping types in Kibana Lens visualizations.
    """

    assignments: list[Any] = Field(default_factory=list)
    """List of color assignments for specific categories or series."""

    specialAssignments: list[KbnLayerColorMappingSpecialAssignment] = Field(
        default_factory=lambda: [KbnLayerColorMappingSpecialAssignment()],
    )
    """List of special color assignment rules for exceptional cases."""

    paletteId: str = 'eui_amsterdam_color_blind'
    """ID of the color palette to use (defaults to 'eui_amsterdam_color_blind')."""

    colorMode: dict[str, str] = Field(default_factory=lambda: {'type': 'categorical'})
    """Color assignment mode configuration (e.g., 'categorical' for category-based colors)."""


class KbnBaseStateVisualizationLayer(BaseVwModel):
    """Base view model for visualization layer configuration.

    Serves as the foundation for all visualization layer types across different chart types
    (XY, pie, metric, etc.). Defines common attributes that all layers share, including
    layer identification and color mapping configuration.

    Subclasses extend this model with visualization-specific attributes for their layer type.

    See Also:
        Related to layer types in Kibana Lens visualizations.
    """

    layerId: str
    """Unique identifier for this layer within the visualization."""

    layerType: str
    """Type of the layer (e.g., 'data', 'referenceLine', 'annotations')."""

    colorMapping: Annotated[KbnLayerColorMapping | None, OmitIfNone()] = None
    """Optional color mapping configuration for this layer."""


class KbnBaseStateVisualization(BaseVwModel):
    """Base view model for visualization state configuration.

    Serves as the foundation for all visualization state types after compilation to
    Kibana Lens format. Defines the common structure that all visualizations share,
    primarily the list of layers that comprise the visualization.

    Subclasses extend this model with visualization-specific configuration options
    for different chart types (XY, pie, metric, etc.).

    See Also:
        Related to visualization state types in Kibana Lens.
    """

    layers: list[KbnBaseStateVisualizationLayer] = Field(...)
    """List of layers that comprise this visualization."""
