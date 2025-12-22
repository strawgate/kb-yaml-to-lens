"""Configuration for dashboard panels."""

from pydantic import Field, field_validator

from dashboard_compiler.shared.config import BaseCfgModel


class Grid(BaseCfgModel):
    """Represents the grid layout configuration for a panel.

    This determines the panel's position and size on the dashboard grid.
    """

    x: int = Field(...)
    """The horizontal starting position of the panel on the grid (0-based)."""

    y: int = Field(...)
    """The vertical starting position of the panel on the grid (0-based)."""

    w: int = Field(...)
    """The width of the panel in grid units."""

    h: int = Field(...)
    """The height of the panel in grid units."""

    @field_validator('x', 'y')
    @classmethod
    def validate_position(cls, v: int) -> int:
        """Validate that position coordinates are non-negative."""
        if v < 0:
            msg = 'Position coordinates (x, y) must be non-negative'
            raise ValueError(msg)
        return v

    @field_validator('w', 'h')
    @classmethod
    def validate_dimensions(cls, v: int) -> int:
        """Validate that width and height are positive."""
        if v <= 0:
            msg = 'Width and height (w, h) must be positive'
            raise ValueError(msg)
        return v
