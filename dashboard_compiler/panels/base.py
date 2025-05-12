from pydantic import Field

from dashboard_compiler.panels.config import Grid
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

    grid: Grid = Field(...)
    """Defines the panel's position and size on the dashboard grid."""
