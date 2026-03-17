"""Configuration for dashboard panels."""

from typing import Literal

from pydantic import AliasChoices, Field, model_validator

from kb_dashboard_core.shared.config import BaseCfgModel

# Standard Kibana dashboard grid width
KIBANA_GRID_WIDTH = 48

# Semantic width constants
GRID_WIDTH_WHOLE = 48
GRID_WIDTH_HALF = 24
GRID_WIDTH_THIRD = 16
GRID_WIDTH_QUARTER = 12
GRID_WIDTH_SIXTH = 8
GRID_WIDTH_EIGHTH = 6

# Type alias for semantic width
SemanticWidth = Literal['whole', 'half', 'third', 'quarter', 'sixth', 'eighth']


def resolve_semantic_width(value: int | SemanticWidth) -> int:
    """Resolve semantic width to numeric value.

    Args:
        value: Either an integer width or a semantic width string.

    Returns:
        int: The numeric width value.

    Raises:
        ValueError: If an unknown semantic width value is provided.

    """
    if isinstance(value, int):
        return value

    mapping = {
        'whole': GRID_WIDTH_WHOLE,
        'half': GRID_WIDTH_HALF,
        'third': GRID_WIDTH_THIRD,
        'quarter': GRID_WIDTH_QUARTER,
        'sixth': GRID_WIDTH_SIXTH,
        'eighth': GRID_WIDTH_EIGHTH,
    }

    if value not in mapping:
        msg = f"Unknown semantic width: '{value}'"
        raise ValueError(msg)

    return mapping[value]


class Size(BaseCfgModel):
    """Panel size configuration.

    Determines the width and height of a panel on the dashboard grid.
    Width accepts semantic values ('whole', 'half', etc.) or integers.
    """

    w: int | SemanticWidth = Field(
        default=GRID_WIDTH_QUARTER,
        validation_alias=AliasChoices('w', 'width'),
    )
    """The width of the panel in grid units.

    Defaults to 12 (quarter width). Accepts semantic values ('whole', 'half', 'third', 'quarter', 'sixth', 'eighth') or integers (1-48).
    """

    h: int = Field(default=8, gt=0, validation_alias=AliasChoices('h', 'height'))
    """The height of the panel in grid units. Defaults to 8."""

    @property
    def width(self) -> int:
        """Get the resolved width as an integer.

        Returns:
            int: The width in grid units (1-48).

        """
        resolved = resolve_semantic_width(self.w)
        if resolved <= 0 or resolved > KIBANA_GRID_WIDTH:
            msg = f'Width must be between 1 and {KIBANA_GRID_WIDTH}, got {resolved}'
            raise ValueError(msg)
        return resolved


class Position(BaseCfgModel):
    """Panel position configuration.

    Determines the x/y coordinates of a panel on the dashboard grid.
    If not specified, the panel will be auto-positioned.
    """

    x: int | None = Field(default=None, ge=0, le=KIBANA_GRID_WIDTH, validation_alias=AliasChoices('x', 'from_left'))
    """The horizontal starting position of the panel on the grid (0-based). If None, position will be auto-calculated."""

    y: int | None = Field(default=None, ge=0, validation_alias=AliasChoices('y', 'from_top'))
    """The vertical starting position of the panel on the grid (0-based). If None, position will be auto-calculated."""


class Grid(BaseCfgModel):
    """Represents the grid layout configuration for a panel.

    This determines the panel's position and size on the dashboard grid.
    """

    x: int = Field(..., ge=0, le=KIBANA_GRID_WIDTH, validation_alias=AliasChoices('x', 'from_left'))
    """The horizontal starting position of the panel on the grid (0-based)."""

    y: int = Field(..., ge=0, validation_alias=AliasChoices('y', 'from_top'))
    """The vertical starting position of the panel on the grid (0-based)."""

    w: int = Field(..., gt=0, le=KIBANA_GRID_WIDTH, validation_alias=AliasChoices('w', 'width'))
    """The width of the panel in grid units."""

    h: int = Field(..., gt=0, validation_alias=AliasChoices('h', 'height'))
    """The height of the panel in grid units."""

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
