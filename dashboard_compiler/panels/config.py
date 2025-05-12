"""Configuration for dashboard panels."""

from pydantic import Field

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
