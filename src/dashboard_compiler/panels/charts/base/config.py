from enum import StrEnum
from typing import ClassVar, Literal

from pydantic import Field, model_validator

from dashboard_compiler.shared.config import BaseCfgModel


class BaseChart(BaseCfgModel):
    """Represents a base chart configuration."""

    id: str | None = Field(default=None)

    # data_view: str = Field(default=...)


class LegendWidthEnum(StrEnum):
    """Represents the possible values for the width of the legend in a pie chart."""

    SMALL = 'small'
    """Small legend."""

    MEDIUM = 'medium'
    """Medium legend."""

    LARGE = 'large'
    """Large legend."""

    EXTRA_LARGE = 'extra_large'
    """Extra large legend."""


class LegendVisibleEnum(StrEnum):
    """Represents the possible values for the visibility of the legend in a pie chart."""

    SHOW = 'show'
    """Show the legend."""

    HIDE = 'hide'
    """Hide the legend."""

    AUTO = 'auto'
    """Automatically determine the visibility of the legend based on the data."""


class ColorAssignment(BaseCfgModel):
    """Manual color assignment to specific data values."""

    value: str | None = Field(default=None)
    """A single category value to assign a color to."""

    values: list[str] | None = Field(default=None)
    """Multiple category values to assign the same color to."""

    color: str = Field(...)
    """The hex color code to assign (e.g., '#FF0000')."""

    @model_validator(mode='after')
    def check_value_or_values(self) -> 'ColorAssignment':
        """Validate that at least one of value or values is provided."""
        if self.value is None and not self.values:
            msg = "At least one of 'value' or 'values' must be provided"
            raise ValueError(msg)
        return self


class RangeColorAssignment(BaseCfgModel):
    """Range-based color assignment for gradient visualizations."""

    min: float = Field(...)
    """Minimum value of the range."""

    max: float = Field(...)
    """Maximum value of the range."""

    color: str = Field(...)
    """The hex color code to assign to this range (e.g., '#FF0000')."""

    @model_validator(mode='after')
    def check_min_less_than_max(self) -> 'RangeColorAssignment':
        """Validate that min is less than max."""
        if self.min >= self.max:
            msg = "'min' must be less than 'max'"
            raise ValueError(msg)
        return self


class GradientConfig(BaseCfgModel):
    """Gradient color palette configuration."""

    SEQUENTIAL_COLOR_COUNT: ClassVar[int] = 2
    DIVERGENT_COLOR_COUNT: ClassVar[int] = 3

    type: Literal['sequential', 'divergent'] = Field(default='sequential')
    """Type of gradient: sequential (2 colors) or divergent (3 colors)."""

    colors: list[str] = Field(...)
    """List of hex color codes for the gradient. Use 2 colors for sequential, 3 for divergent."""

    @model_validator(mode='after')
    def check_color_count(self) -> 'GradientConfig':
        """Validate that color count matches gradient type."""
        if self.type == 'sequential' and len(self.colors) != self.SEQUENTIAL_COLOR_COUNT:
            msg = f'Sequential gradients require exactly {self.SEQUENTIAL_COLOR_COUNT} colors'
            raise ValueError(msg)
        if self.type == 'divergent' and len(self.colors) != self.DIVERGENT_COLOR_COUNT:
            msg = f'Divergent gradients require exactly {self.DIVERGENT_COLOR_COUNT} colors'
            raise ValueError(msg)
        return self


class ColorMapping(BaseCfgModel):
    """Color configuration for chart visualizations."""

    palette: str = Field(default='eui_amsterdam_color_blind')
    """The palette ID to use for unassigned colors.

    Available palettes:
    - 'default' - Standard EUI palette
    - 'eui_amsterdam_color_blind' - Color-blind safe palette (default)
    - 'kibana_palette' or 'legacy' - Legacy Kibana colors
    - 'elastic_brand' - Elastic brand colors
    - 'gray' - Grayscale palette
    """

    mode: Literal['categorical', 'gradient'] = Field(default='categorical')
    """Color mode: 'categorical' for discrete categories, 'gradient' for continuous data."""

    assignments: list[ColorAssignment] = Field(default_factory=list)
    """Manual color assignments to specific data values (categorical mode)."""

    range_assignments: list[RangeColorAssignment] = Field(default_factory=list)
    """Range-based color assignments for gradient mode."""

    gradient: GradientConfig | None = Field(default=None)
    """Gradient configuration for gradient mode."""
