"""Base classes for chart visualizations."""

from typing import Annotated

from pydantic import Field

from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone

# Default values for color mapping - set during compilation
KBN_DEFAULT_COLOR_MAPPING_RULE_TYPE = 'other'
KBN_DEFAULT_COLOR_MAPPING_RULE_TYPE_MATCH_EXACTLY = 'matchExactly'
KBN_DEFAULT_COLOR_MAPPING_COLOR_TYPE = 'loop'
KBN_DEFAULT_COLOR_MAPPING_COLOR_TYPE_COLOR_CODE = 'colorCode'
KBN_DEFAULT_COLOR_MAPPING_TOUCHED = False
KBN_DEFAULT_COLOR_MAPPING_PALETTE_ID = 'eui_amsterdam_color_blind'
KBN_DEFAULT_COLOR_MAPPING_COLOR_MODE_TYPE = 'categorical'


class KbnLayerColorMappingRule(BaseVwModel):
    """View model for color mapping rule configuration.

    Defines a rule for color assignment in visualization layers. Rules can be 'other'
    for default assignments, 'matchExactly' for specific value matching, or other rule
    types for conditional color mapping. Values are set during compilation using the
    default constants defined above.

    See Also:
        Related to color mapping types in Kibana Lens visualizations.
    """

    type: str = Field(...)
    """Type of color mapping rule (set during compilation, typically 'other' for default or 'matchExactly' for categorical)."""

    values: Annotated[list[str] | None, OmitIfNone()] = None
    """Values to match for categorical assignments (used with 'matchExactly' type)."""


class KbnLayerColorMappingColor(BaseVwModel):
    """View model for color mapping color configuration.

    Defines the color assignment strategy for visualization layers. The 'loop' type
    means colors are assigned in a repeating pattern from the palette. The 'colorCode'
    type assigns a specific custom color. Values are set during compilation using the
    default constants defined above.

    See Also:
        Related to color mapping types in Kibana Lens visualizations.
    """

    type: str = Field(...)
    """Color assignment type (set during compilation, typically 'loop' for palette or 'colorCode' for custom)."""

    colorCode: Annotated[str | None, OmitIfNone()] = None
    """Hex color code (e.g., '#FF0000') for custom color assignments (used with 'colorCode' type)."""


class KbnLayerColorMappingAssignment(BaseVwModel):
    """View model for manual color assignment to specific values.

    Defines a manual color assignment for specific categorical values in the visualization.
    Combines a rule (what to match), a color (what color to use), and tracking whether
    the user has modified this assignment. Values are set during compilation.

    See Also:
        Related to color mapping types in Kibana Lens visualizations.
    """

    rule: KbnLayerColorMappingRule = Field(...)
    """The color mapping rule defining what values this assignment applies to."""

    color: KbnLayerColorMappingColor = Field(...)
    """The color assignment strategy for matched values."""

    touched: bool = Field(...)
    """Whether this assignment has been modified by the user."""


class KbnLayerColorMappingSpecialAssignment(BaseVwModel):
    """View model for special color assignment configuration.

    Defines a special case color assignment rule for visualization layers, combining
    a color rule with a color assignment strategy and tracking whether it has been
    modified by the user. Values are set during compilation using the default constants.

    See Also:
        Related to color mapping types in Kibana Lens visualizations.
    """

    rule: KbnLayerColorMappingRule = Field(...)
    """The color mapping rule to apply."""

    color: KbnLayerColorMappingColor = Field(...)
    """The color assignment strategy."""

    touched: bool = Field(...)
    """Whether this assignment has been modified by the user."""


class KbnLayerColorMapping(BaseVwModel):
    """View model for color mapping configuration for visualization layers.

    Defines how colors are assigned to data series in a visualization layer. Includes
    the color palette to use, color assignment mode, manual assignments for specific
    values, and special assignment rules for fallback colors. Values are set during
    compilation using the default constants defined above.

    This model is used across different visualization types (XY, pie, metric, etc.) to maintain
    consistent color mapping behavior.

    See Also:
        Related to color mapping types in Kibana Lens visualizations.
    """

    assignments: list[KbnLayerColorMappingAssignment] = Field(...)
    """List of manual color assignments for specific categories or series."""

    specialAssignments: list[KbnLayerColorMappingSpecialAssignment] = Field(...)
    """List of special color assignment rules for exceptional cases (fallback colors)."""

    paletteId: str = Field(...)
    """ID of the color palette to use (set during compilation)."""

    colorMode: dict[str, str] = Field(...)
    """Color assignment mode configuration (set during compilation)."""


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
