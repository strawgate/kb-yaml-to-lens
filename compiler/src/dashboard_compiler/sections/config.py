"""Configuration for collapsible sections in dashboards."""

from __future__ import annotations

from pydantic import Field

from dashboard_compiler.panels.types import PanelTypes
from dashboard_compiler.shared.config import BaseCfgModel


class Section(BaseCfgModel):
    """A collapsible section that groups panels together in a dashboard.

    Sections provide a way to organize related panels into collapsible groups,
    improving dashboard navigation and readability. Panels within collapsed sections
    are not rendered until the section is expanded, improving performance.

    Examples:
        Basic section with panels:
        ```yaml
        dashboards:
          - name: "Dashboard with Sections"
            sections:
              - title: "System Metrics"
                collapsed: false
                panels:
                  - title: "CPU Usage"
                    size: { w: 24, h: 10 }
                    position: { x: 0, y: 0 }
                    markdown:
                      content: "CPU metrics displayed here"
              - title: "Network Metrics"
                collapsed: true
                panels:
                  - title: "Network Traffic"
                    size: { w: 24, h: 10 }
                    position: { x: 0, y: 0 }
                    markdown:
                      content: "Network metrics displayed here"
        ```

        Section at specific vertical position:
        ```yaml
        dashboards:
          - name: "Positioned Sections"
            sections:
              - title: "Top Section"
                y: 0
                panels:
                  - title: "Panel A"
                    size: { w: 48, h: 10 }
                    position: { x: 0, y: 0 }
                    markdown:
                      content: "Content A"
              - title: "Bottom Section"
                y: 15
                collapsed: true
                panels:
                  - title: "Panel B"
                    size: { w: 48, h: 10 }
                    position: { x: 0, y: 0 }
                    markdown:
                      content: "Content B"
        ```
    """

    id: str | None = Field(default=None)
    """A unique identifier for the section. If not provided, one will be generated."""

    title: str = Field(...)
    """The title displayed on the section header."""

    collapsed: bool = Field(default=False)
    """Whether the section is initially collapsed. Defaults to false (expanded)."""

    y: int | None = Field(default=None)
    """The vertical position of the section on the dashboard grid. Auto-calculated if not specified."""

    panels: list[PanelTypes] = Field(default_factory=list)
    """The panels contained within this section."""
