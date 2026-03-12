"""Configuration for collapsible section panels."""

from pydantic import Field

from kb_dashboard_core.panels.base import BasePanel
from kb_dashboard_core.panels.config import GRID_WIDTH_WHOLE, Size
from kb_dashboard_core.panels.types import PanelTypes
from kb_dashboard_core.shared.config import BaseCfgModel


class SectionConfig(BaseCfgModel):
    """Configuration for a collapsible section's content and behavior."""

    collapsed: bool | None = Field(default=None)
    """Whether the section is collapsed by default in Kibana."""

    panels: list[PanelTypes] = Field(default_factory=list)
    """Panels contained within this collapsible section.

    Inner panels use a **relative** coordinate space — their (x, y) positions
    start at (0, 0) within the section body, independent of the section's
    absolute position in the outer dashboard grid.

    Nested CollapsiblePanels are not supported and will be rejected by the
    Dashboard-level discriminator.
    """


class CollapsiblePanel(BasePanel):
    """A collapsible section that groups panels under a named, expandable header.

    In the outer dashboard grid, a collapsible panel occupies a single full-width row
    (the section header). Its inner panels are laid out in a separate coordinate space
    relative to the section.

    Examples:
        ```yaml
        dashboards:
          - name: "Dashboard with Sections"
            panels:
              - title: "Overview"
                size: { w: 48, h: 6 }
                markdown:
                  content: "# Overview"
              - title: "Details"
                section:
                  collapsed: true
                  panels:
                    - title: "CPU Usage"
                      size: { w: 48, h: 12 }
                      markdown:
                        content: "# CPU"
        ```
    """

    size: Size = Field(default_factory=lambda: Size(w=GRID_WIDTH_WHOLE, h=1))
    """Section header size. Defaults to full width (48) and 1 row tall."""

    section: SectionConfig = Field(...)
    """Section configuration including collapsed state and inner panels."""
