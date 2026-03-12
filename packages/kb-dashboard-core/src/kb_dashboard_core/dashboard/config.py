from typing import Annotated, Self

from pydantic import Discriminator, Field, Tag

from kb_dashboard_core.controls import ControlTypes
from kb_dashboard_core.controls.config import ControlSettings
from kb_dashboard_core.filters.config import FilterTypes
from kb_dashboard_core.panels.auto_layout import LayoutAlgorithm
from kb_dashboard_core.panels.charts.config import ESQLPanel, LensPanel
from kb_dashboard_core.panels.collapsible import CollapsiblePanel
from kb_dashboard_core.panels.images import ImagePanel
from kb_dashboard_core.panels.links import LinksPanel
from kb_dashboard_core.panels.markdown import MarkdownPanel
from kb_dashboard_core.panels.search import SearchPanel
from kb_dashboard_core.panels.types import get_panel_type
from kb_dashboard_core.panels.vega import VegaPanel
from kb_dashboard_core.queries.types import LegacyQueryTypes
from kb_dashboard_core.sample_data.config import SampleData
from kb_dashboard_core.shared.config import BaseCfgModel


def get_dashboard_panel_type(v: dict[str, object] | object) -> str:
    """Extract panel type for discriminated union validation, including collapsible sections.

    Args:
        v: Either a dict (during validation) or a panel instance.

    Returns:
        str: The panel type identifier.

    """
    if isinstance(v, dict):
        if 'section' in v:
            return 'section'
        # Delegate to get_panel_type for non-section dicts, but update error message
        try:
            return get_panel_type(v)  # pyright: ignore[reportUnknownArgumentType]
        except ValueError:
            keys = list(v)  # pyright: ignore[reportUnknownArgumentType]
            msg = (
                f'Cannot determine dashboard panel type from dict with keys: {keys}. '
                'Each panel must have exactly one type discriminator key: '
                "'markdown', 'search', 'links', 'image', 'lens', 'esql', 'vega', or 'section'."
            )
            raise ValueError(msg) from None
    if isinstance(v, CollapsiblePanel):
        return 'section'
    return get_panel_type(v)


type DashboardPanelTypes = Annotated[
    Annotated[MarkdownPanel, Tag('markdown')]
    | Annotated[SearchPanel, Tag('search')]
    | Annotated[LinksPanel, Tag('links')]
    | Annotated[ImagePanel, Tag('image')]
    | Annotated[LensPanel, Tag('lens')]
    | Annotated[ESQLPanel, Tag('esql')]
    | Annotated[VegaPanel, Tag('vega')]
    | Annotated[CollapsiblePanel, Tag('section')],
    Discriminator(get_dashboard_panel_type),
]


class TimeRange(BaseCfgModel):
    """Configure a default time range for the dashboard."""

    from_time: str = Field(..., alias='from')
    """The start of the time range (e.g., 'now-30d/d', 'now-1h')."""

    to_time: str | None = Field(default=None, alias='to')
    """The end of the time range."""


class DashboardSyncSettings(BaseCfgModel):
    """Configure whether cursor, tooltips, and colors should sync across panels."""

    cursor: bool | None = Field(default=None)
    """Whether to synchronize the cursor across related panels. Defaults to true if not set."""
    tooltips: bool | None = Field(default=None)
    """Whether to synchronize tooltips across related panels. Defaults to false if not set."""
    colors: bool | None = Field(default=None)
    """Whether to apply the same color palette to all panels on the dashboard. Defaults to false if not set."""


class DashboardSettings(BaseCfgModel):
    """Global settings for a dashboard with options for margins, synchronization of colors."""

    margins: bool | None = Field(default=None)
    """Whether to put space between panels in the dashboard. Defaults to true if not set."""

    sync: DashboardSyncSettings = Field(default_factory=DashboardSyncSettings)

    controls: ControlSettings = Field(default_factory=ControlSettings)

    titles: bool | None = Field(default=None)
    """Whether to display the titles in the panel headers. Defaults to true if not set."""

    layout_algorithm: LayoutAlgorithm = Field(default='up-left')
    """The auto-layout algorithm to use for positioning panels without explicit coordinates. Defaults to 'up-left'."""


class Dashboard(BaseCfgModel):
    """A dashboard with filters, controls, panels and more."""

    name: str = Field(...)
    """The name of the dashboard."""

    id: str | None = Field(default=None)
    """An optional unique identifier for the dashboard, useful for giving the generated dashboard a specific ID."""

    description: str | None = Field(default=None)
    """A brief description of the dashboard's purpose or content."""

    time_range: TimeRange | None = Field(default=None)
    """A default time range to apply when opening the dashboard."""

    settings: DashboardSettings = Field(default_factory=DashboardSettings)

    query: LegacyQueryTypes | None = Field(default=None)
    """A query (KQL or Lucene) applied to the dashboard."""

    filters: list[FilterTypes] = Field(default_factory=list)
    """A list of filters applied to the dashboard."""

    controls: list[ControlTypes] = Field(default_factory=list)
    """A list of Controls for the dashboard."""

    panels: list[DashboardPanelTypes] = Field(default_factory=list)
    """A list of Panels defining the content and layout of the dashboard."""

    sample_data: SampleData | None = Field(default=None)
    """Optional sample data to bundle with the dashboard for testing and demonstration."""

    def add_filter(self, filter: FilterTypes) -> Self:
        """Add a filter to the dashboard's global filters list.

        Args:
            filter: The filter object to add.

        Returns:
            Self: The current instance of the Dashboard for method chaining.

        """
        self.filters.append(filter)

        return self

    def add_control(self, control: ControlTypes) -> Self:
        """Add a control panel configuration to the dashboard's controls list.

        Args:
            control: The control object to add.

        Returns:
            Self: The current instance of the Dashboard for method chaining.

        """
        self.controls.append(control)

        return self

    def add_panel(self, panel: DashboardPanelTypes) -> Self:
        """Add a panel object to the dashboard's panels list.

        Args:
            panel: The panel object to add.

        Returns:
            Self: The current instance of the Dashboard for method chaining.

        """
        self.panels.append(panel)

        return self
