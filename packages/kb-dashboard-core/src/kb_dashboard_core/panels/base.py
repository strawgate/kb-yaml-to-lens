from pydantic import Field

from kb_dashboard_core.panels.config import Position, Size
from kb_dashboard_core.panels.drilldowns.config import DrilldownTypes
from kb_dashboard_core.shared.config import BaseCfgModel


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

    drilldowns: list[DrilldownTypes] | None = Field(default=None)
    """Optional list of drilldowns to attach to this panel."""
