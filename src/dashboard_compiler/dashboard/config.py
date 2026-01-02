from typing import Self

from pydantic import Field, model_validator

from dashboard_compiler.controls import ControlTypes
from dashboard_compiler.controls.config import ControlSettings
from dashboard_compiler.filters.config import FilterTypes
from dashboard_compiler.panels.types import PanelTypes
from dashboard_compiler.queries.types import LegacyQueryTypes
from dashboard_compiler.sample_data.config import SampleData
from dashboard_compiler.shared.config import BaseCfgModel


class DashboardSyncSettings(BaseCfgModel):
    """Configure whether cursor, tooltips, and colors should sync across panels."""

    cursor: bool | None = Field(default=None)
    """Whether to synchronize the cursor across related panels. Defaults to true if not set."""
    tooltips: bool | None = Field(default=None)
    """Whether to synchronize tooltips across related panels. Defaults to true if not set."""
    colors: bool | None = Field(default=None)
    """Whether to apply the same color palette to all panels on the dashboard. Defaults to true if not set."""


class DashboardSettings(BaseCfgModel):
    """Global settings for a dashboard with options for margins, synchronization of colors."""

    margins: bool | None = Field(default=None)
    """Whether to put space between panels in the dashboard. Defaults to true if not set."""

    sync: DashboardSyncSettings = Field(default_factory=DashboardSyncSettings)

    controls: ControlSettings = Field(default_factory=ControlSettings)

    titles: bool | None = Field(default=None)
    """Whether to display the titles in the panel headers. Defaults to true if not set."""


class Dashboard(BaseCfgModel):
    """A dashboard with filters, controls, panels and more."""

    name: str = Field(...)
    """The name of the dashboard."""

    id: str | None = Field(default=None)
    """An optional unique identifier for the dashboard, useful for giving the generated dashboard a specific ID."""

    description: str | None = Field(default=None)
    """A brief description of the dashboard's purpose or content."""

    settings: DashboardSettings = Field(default_factory=DashboardSettings)

    query: LegacyQueryTypes | None = Field(default=None)
    """A query (KQL or Lucene) applied to the dashboard."""

    filters: list[FilterTypes] = Field(default_factory=list)
    """A list of filters applied to the dashboard."""

    controls: list[ControlTypes] = Field(default_factory=list)
    """A list of Controls for the dashboard."""

    panels: list[PanelTypes] = Field(default_factory=list)
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

    def add_panel(self, panel: PanelTypes) -> Self:
        """Add a panel object to the dashboard's panels list.

        Args:
            panel: The panel object to add.

        Returns:
            Self: The current instance of the Dashboard for method chaining.

        """
        self.panels.append(panel)

        return self

    @model_validator(mode='after')
    def validate_no_overlapping_panels(self) -> Self:
        """Validate that no panels overlap on the grid.

        Returns:
            Self: The current instance of the Dashboard.

        Raises:
            ValueError: If any panels overlap.

        """
        for i, panel1 in enumerate(self.panels):
            for panel2 in self.panels[i + 1 :]:
                if panel1.grid.overlaps_with(panel2.grid):
                    panel1_title = getattr(panel1, 'title', 'Untitled')
                    panel2_title = getattr(panel2, 'title', 'Untitled')
                    msg = (
                        f'Panel "{panel1_title}" at (x={panel1.grid.x}, y={panel1.grid.y}, '
                        f'w={panel1.grid.w}, h={panel1.grid.h}) overlaps with '
                        f'panel "{panel2_title}" at (x={panel2.grid.x}, y={panel2.grid.y}, '
                        f'w={panel2.grid.w}, h={panel2.grid.h})'
                    )
                    raise ValueError(msg)
        return self
