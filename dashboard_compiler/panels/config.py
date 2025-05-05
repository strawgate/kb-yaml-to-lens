"""Configuration for dashboard panels."""

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from dashboard_compiler.panels.images import ImagePanel
    from dashboard_compiler.panels.links import LinksPanel
    from dashboard_compiler.panels.markdown import MarkdownPanel
    from dashboard_compiler.panels.search import SearchPanel

type PanelTypes = 'MarkdownPanel | SearchPanel | LinksPanel | ImagePanel'  # | LensPanel


class Grid(BaseModel):
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


class BasePanel(BaseModel):
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

    grid: Grid = Field(...)
    """Defines the panel's position and size on the dashboard grid."""
