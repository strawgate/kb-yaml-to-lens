"""Configuration for dashboard panels."""

from typing import Literal

from pydantic import AliasChoices, Field, field_validator, model_validator

from dashboard_compiler.shared.config import BaseCfgModel

# Standard Kibana dashboard grid width
KIBANA_GRID_WIDTH = 48

# Semantic width constants
GRID_WIDTH_WHOLE = 48
GRID_WIDTH_HALF = 24
GRID_WIDTH_THIRD = 16
GRID_WIDTH_QUARTER = 12
GRID_WIDTH_SIXTH = 8
GRID_WIDTH_EIGHTH = 6

# Semantic height constants
GRID_HEIGHT_WHOLE = 48
GRID_HEIGHT_HALF = 24
GRID_HEIGHT_THIRD = 16
GRID_HEIGHT_QUARTER = 12
GRID_HEIGHT_SIXTH = 8
GRID_HEIGHT_EIGHTH = 6

# Type aliases for semantic dimensions
SemanticWidth = Literal['whole', 'half', 'third', 'quarter', 'sixth', 'eighth']
SemanticHeight = Literal['whole', 'half', 'third', 'quarter', 'sixth', 'eighth']


def resolve_semantic_width(value: int | SemanticWidth) -> int:
    """Resolve semantic width to numeric value.

    Args:
        value: Either an integer width or a semantic width string.

    Returns:
        int: The numeric width value.

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
    return mapping[value]


def resolve_semantic_height(value: int | SemanticHeight) -> int:
    """Resolve semantic height to numeric value.

    Args:
        value: Either an integer height or a semantic height string.

    Returns:
        int: The numeric height value.

    """
    if isinstance(value, int):
        return value

    mapping = {
        'whole': GRID_HEIGHT_WHOLE,
        'half': GRID_HEIGHT_HALF,
        'third': GRID_HEIGHT_THIRD,
        'quarter': GRID_HEIGHT_QUARTER,
        'sixth': GRID_HEIGHT_SIXTH,
        'eighth': GRID_HEIGHT_EIGHTH,
    }
    return mapping[value]


class Size(BaseCfgModel):
    """Panel size configuration.

    Determines the width and height of a panel on the dashboard grid.
    """

    w: int | SemanticWidth = Field(default=GRID_WIDTH_HALF, validation_alias=AliasChoices('w', 'width'))
    """The width of the panel in grid units. Defaults to 24 (half width)."""

    h: int | SemanticHeight = Field(default=12, validation_alias=AliasChoices('h', 'height'))
    """The height of the panel in grid units. Defaults to 12."""

    @field_validator('w', mode='before')
    @classmethod
    def resolve_width(cls, v: int | SemanticWidth) -> int:
        """Resolve semantic width values to integers."""
        return resolve_semantic_width(v)

    @field_validator('h', mode='before')
    @classmethod
    def resolve_height(cls, v: int | SemanticHeight) -> int:
        """Resolve semantic height values to integers."""
        return resolve_semantic_height(v)

    @field_validator('w', 'h')
    @classmethod
    def validate_dimensions(cls, v: int) -> int:
        """Validate that width and height are positive."""
        if v <= 0:
            msg = 'Width and height (w, h) must be positive'
            raise ValueError(msg)
        return v

    @model_validator(mode='after')
    def validate_width_bounds(self) -> 'Size':
        """Validate that panel width does not exceed standard Kibana grid width.

        Raises:
            ValueError: If w exceeds KIBANA_GRID_WIDTH (48 units).

        Returns:
            Size: The validated Size instance.

        """
        if self.w > KIBANA_GRID_WIDTH:
            msg = f'Panel width exceeds standard Kibana grid width ({KIBANA_GRID_WIDTH} units): w={self.w}'
            raise ValueError(msg)
        return self


class Position(BaseCfgModel):
    """Panel position configuration.

    Determines the x/y coordinates of a panel on the dashboard grid.
    If not specified, the panel will be auto-positioned.
    """

    x: int | None = Field(default=None, validation_alias=AliasChoices('x', 'from_left'))
    """The horizontal starting position of the panel on the grid (0-based). If None, position will be auto-calculated."""

    y: int | None = Field(default=None, validation_alias=AliasChoices('y', 'from_top'))
    """The vertical starting position of the panel on the grid (0-based). If None, position will be auto-calculated."""

    @field_validator('x', 'y')
    @classmethod
    def validate_position(cls, v: int | None) -> int | None:
        """Validate that position coordinates are non-negative."""
        if v is not None and v < 0:
            msg = 'Position coordinates (x, y) must be non-negative'
            raise ValueError(msg)
        return v


class Grid(BaseCfgModel):
    """Represents the grid layout configuration for a panel.

    This determines the panel's position and size on the dashboard grid.
    """

    x: int = Field(..., validation_alias=AliasChoices('x', 'from_left'))
    """The horizontal starting position of the panel on the grid (0-based)."""

    y: int = Field(..., validation_alias=AliasChoices('y', 'from_top'))
    """The vertical starting position of the panel on the grid (0-based)."""

    w: int = Field(..., validation_alias=AliasChoices('w', 'width'))
    """The width of the panel in grid units."""

    h: int = Field(..., validation_alias=AliasChoices('h', 'height'))
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
