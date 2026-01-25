from enum import StrEnum

from pydantic import Field, model_validator

from dashboard_compiler.shared.config import BaseCfgModel, BaseIdentifiableModel


class BaseChart(BaseIdentifiableModel):
    """Base configuration for all chart types."""

    # data_view: str = Field(default=...)


class LegendWidthEnum(StrEnum):
    """Legend width/size options."""

    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    EXTRA_LARGE = 'extra_large'


class LegendVisibleEnum(StrEnum):
    """Legend visibility options."""

    SHOW = 'show'
    HIDE = 'hide'
    AUTO = 'auto'


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
        if self.value is None and (self.values is None or len(self.values) == 0):
            msg = "At least one of 'value' or 'values' must be provided"
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

    assignments: list[ColorAssignment] = Field(default_factory=list)
    """Manual color assignments to specific data values."""
