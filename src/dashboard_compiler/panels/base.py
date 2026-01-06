from typing import Any

from pydantic import Field, model_validator

from dashboard_compiler.panels.config import Grid, Position, Size
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

    grid: Grid | None = Field(default=None)
    """Defines the panel's position and size on the dashboard grid. Deprecated in favor of size and position."""

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

        if 'size' not in data:
            data['size'] = {}
        if 'position' not in data:
            data['position'] = {}

        if isinstance(grid, dict):
            data['size']['w'] = grid.get('w')  # pyright: ignore[reportUnknownMemberType]
            data['size']['h'] = grid.get('h')  # pyright: ignore[reportUnknownMemberType]
            data['position']['x'] = grid.get('x')  # pyright: ignore[reportUnknownMemberType]
            data['position']['y'] = grid.get('y')  # pyright: ignore[reportUnknownMemberType]
        elif isinstance(grid, Grid):
            data['size']['w'] = grid.w
            data['size']['h'] = grid.h
            data['position']['x'] = grid.x
            data['position']['y'] = grid.y

        return data  # pyright: ignore[reportUnknownVariableType]

    @model_validator(mode='after')
    def compute_grid_from_size_position(self) -> 'BasePanel':
        """Compute grid from size and position after all validators run.

        This ensures grid is always available for backward compatibility.
        """
        if self.grid is None and self.position.x is not None and self.position.y is not None:
            object.__setattr__(
                self,
                'grid',
                Grid(x=self.position.x, y=self.position.y, w=self.size.w, h=self.size.h),
            )
        return self
