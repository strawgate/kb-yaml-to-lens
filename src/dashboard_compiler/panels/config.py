"""Configuration for dashboard panels."""

from pydantic import Field, field_validator, model_validator

from dashboard_compiler.shared.config import BaseCfgModel

# Standard Kibana dashboard grid width
KIBANA_GRID_WIDTH = 48


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

    @model_validator(mode='after')
    def validate_width_bounds(self) -> 'Grid':
        """Validate that panel does not extend beyond standard Kibana grid width.

        Raises:
            ValueError: If x + w exceeds KIBANA_GRID_WIDTH (48 units).

        Returns:
            Grid: The validated Grid instance.

        """
        if self.x + self.w > KIBANA_GRID_WIDTH:
            msg = (
                f'Panel extends beyond standard Kibana grid width ({KIBANA_GRID_WIDTH} units): x={self.x} + w={self.w} = {self.x + self.w}'
            )
            raise ValueError(msg)
        return self

    def overlaps_with(self, other: 'Grid') -> bool:
        """Check if this grid overlaps with another grid.

        Args:
            other: The other grid to check for overlap.

        Returns:
            bool: True if the grids overlap, False otherwise.

        """
        return not (
            self.x + self.w <= other.x  # self is left of other
            or other.x + other.w <= self.x  # other is left of self
            or self.y + self.h <= other.y  # self is above other
            or other.y + other.h <= self.y  # other is above self
        )
