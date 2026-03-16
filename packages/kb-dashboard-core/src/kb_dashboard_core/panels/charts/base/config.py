import warnings
from enum import StrEnum
from typing import Any, Literal, cast

from pydantic import Field, model_validator

from kb_dashboard_core.shared.config import BaseCfgModel, BaseIdentifiableModel

PERCENT_MAX = 100
"""Maximum value for percent-based range stops."""


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


class BaseLegend(BaseCfgModel):
    """Shared legend fields common to all chart types."""

    visible: LegendVisibleEnum | None = Field(default=None, strict=False)
    """Visibility of the legend. Kibana defaults vary by chart type."""

    position: Literal['top', 'right', 'bottom', 'left'] | None = Field(default=None)
    """Position of the legend."""

    width: LegendWidthEnum | None = Field(default=None, strict=False)
    """Width of the legend."""


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


class ColorThreshold(BaseCfgModel):
    """Single threshold band in a range-based color map."""

    up_to: float = Field(...)
    """Upper bound for this threshold band."""

    color: str = Field(...)
    """The color applied within this threshold band (hex color code)."""


class ColorRangeMapping(BaseCfgModel):
    """Range/threshold-based color mapping for numeric values."""

    range_type: Literal['number', 'percent'] = Field(default='number')
    """How threshold values are interpreted by Kibana."""

    range_min: float | None = Field(default=0)
    """Optional lower bound for the palette domain. Use null for auto/open lower bound."""

    range_max: float | None = Field(default=None)
    """Optional upper bound for the palette domain. Use null for auto/open upper bound."""

    thresholds: list[ColorThreshold] = Field(min_length=1)
    """Ordered threshold bands used to build gauge-style color palettes."""

    @model_validator(mode='before')
    @classmethod
    def _translate_legacy_continuity(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data

        normalized_data: dict[str, Any] = dict(cast('dict[str, Any]', data))
        legacy_continuity = cast('object', normalized_data.pop('continuity', None))
        legacy_extend = cast('object', normalized_data.pop('extend_beyond_range', None))
        if legacy_continuity is not None:
            warnings.warn(
                "Color mapping field 'continuity' is deprecated and ignored.",
                DeprecationWarning,
                stacklevel=2,
            )
        if legacy_extend is not None:
            warnings.warn(
                "Color mapping field 'extend_beyond_range' is deprecated and ignored.",
                DeprecationWarning,
                stacklevel=2,
            )
        return normalized_data

    @model_validator(mode='after')
    def validate_thresholds(self) -> 'ColorRangeMapping':
        """Validate threshold ordering and percent bounds."""
        threshold_values = [threshold.up_to for threshold in self.thresholds]
        if threshold_values != sorted(threshold_values):
            msg = "'thresholds' must be sorted in ascending order"
            raise ValueError(msg)
        if self.range_type == 'percent':
            for threshold_value in threshold_values:
                if threshold_value < 0 or threshold_value > PERCENT_MAX:
                    msg = f'Percent-based thresholds must be between 0 and {PERCENT_MAX}'
                    raise ValueError(msg)
            if self.range_min is not None and (self.range_min < 0 or self.range_min > PERCENT_MAX):
                msg = f'Percent-based range_min must be between 0 and {PERCENT_MAX}'
                raise ValueError(msg)
            if self.range_max is not None and (self.range_max < 0 or self.range_max > PERCENT_MAX):
                msg = f'Percent-based range_max must be between 0 and {PERCENT_MAX}'
                raise ValueError(msg)
        if self.range_min is not None and self.range_max is not None and self.range_min >= self.range_max:
            msg = "'range_min' must be less than 'range_max'"
            raise ValueError(msg)
        return self
