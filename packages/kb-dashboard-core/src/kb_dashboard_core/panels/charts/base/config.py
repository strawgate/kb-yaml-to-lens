from enum import StrEnum
from typing import Literal

from pydantic import Field, model_validator

from kb_dashboard_core.shared.config import BaseCfgModel, BaseIdentifiableModel


class BaseChart(BaseIdentifiableModel):
    """Base configuration for all chart types."""

    # data_view: str = Field(default=...)


class LegendWidthEnum(StrEnum):
    """Represents the possible values for the width/size of the legend."""

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


class ColorValueAssignment(BaseCfgModel):
    """Manual color assignment to specific categorical values."""

    value: str | None = Field(default=None)
    """A single category value to assign a color to."""

    values: list[str] | None = Field(default=None)
    """Multiple category values to assign the same color to."""

    color: str = Field(...)
    """The hex color code to assign (e.g., '#FF0000')."""

    @model_validator(mode='after')
    def check_value_or_values(self) -> 'ColorValueAssignment':
        """Validate that at least one of value or values is provided."""
        if self.value is None and (self.values is None or len(self.values) == 0):
            msg = "At least one of 'value' or 'values' must be provided"
            raise ValueError(msg)
        return self


class ColorValueMapping(BaseCfgModel):
    """Categorical color mapping for charts keyed by exact values."""

    palette: str = Field(default='eui_amsterdam_color_blind')
    """The palette ID to use for unassigned colors.

    Available palettes:
    - 'default' - Standard EUI palette
    - 'eui_amsterdam_color_blind' - Color-blind safe palette (default)
    - 'kibana_palette' or 'legacy' - Legacy Kibana colors
    - 'elastic_brand' - Elastic brand colors
    - 'gray' - Grayscale palette
    """

    assignments: list[ColorValueAssignment] = Field(default_factory=list)
    """Manual color assignments to specific data values."""


class ColorRangeStop(BaseCfgModel):
    """Single stop in a range-based color map."""

    stop: float = Field(...)
    """The numeric stop value."""

    color: str = Field(...)
    """The color applied at this stop (hex color code)."""


class ColorRangeMapping(BaseCfgModel):
    """Range/threshold-based color mapping for numeric values."""

    range_type: Literal['number', 'percent'] = Field(default='number')
    """How stop values are interpreted by Kibana."""

    stops: list[ColorRangeStop] = Field(default_factory=list, min_length=1)
    """Ordered range stops used to build gauge-style color palettes."""
