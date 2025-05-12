from enum import StrEnum

from pydantic import Field

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
