from typing import Any

from pydantic import Field, model_validator

from dashboard_compiler.panels.config import Position, Size
from dashboard_compiler.shared.config import BaseCfgModel


class BasePanel(BaseCfgModel):
    """Base model for all panel types defined.

    All specific panel types (e.g., Markdown, Search, Lens) inherit from this base class
    to include common configuration fields.
    """

    id: str | None = Field(
        default=None,
    )
    """A unique identifier for the panel. If not provided, one may be generated during compilation."""

    title: str = Field('')
    """The title displayed on the panel header. Can be an empty string."""

    hide_title: bool | None = Field(
        default=None,
    )
    """If `true`, the panel title will be hidden. Defaults to `false` (title is shown)."""

    description: str | None = Field(default=None)
    """A brief description of the panel's content or purpose. Defaults to an empty string."""

    size: Size = Field(default_factory=Size)
    """Defines the panel's size on the dashboard grid."""

    position: Position = Field(default_factory=Position)
    """Defines the panel's position on the dashboard grid. If not specified, position will be auto-calculated."""

    @model_validator(mode='before')
    @classmethod
    def resolve_grid_to_size_position(cls, data: dict[str, Any] | Any) -> dict[str, Any] | Any:
        """Convert legacy grid field to size and position fields.

        If grid is specified, it takes precedence and populates size/position.
        This maintains backward compatibility.
        """
        if not isinstance(data, dict):
            return data  # pyright: ignore[reportAny]

        # Type narrowed to dict[str, Any] after isinstance check
        grid: Any = data.get('grid')  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        if grid is None:
            return data  # pyright: ignore[reportUnknownVariableType]

        # Legacy grid field provided - convert to size and position
        if 'size' not in data:
            data['size'] = {}
        if 'position' not in data:
            data['position'] = {}

        # Extract values from grid dict
        if isinstance(grid, dict):
            if 'w' in grid:
                data['size']['w'] = grid['w']
            if 'h' in grid:
                data['size']['h'] = grid['h']
            if 'x' in grid:
                data['position']['x'] = grid['x']
            if 'y' in grid:
                data['position']['y'] = grid['y']

        # Remove grid field after conversion to prevent extra_forbid error
        data.pop('grid', None)  # pyright: ignore[reportUnknownMemberType]

        return data  # pyright: ignore[reportUnknownVariableType]
