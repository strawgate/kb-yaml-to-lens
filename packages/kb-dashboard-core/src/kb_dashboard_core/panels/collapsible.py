"""Configuration for collapsible section panels."""

from pydantic import Field, model_validator

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

    @model_validator(mode='after')
    def validate_unsupported_base_fields(self) -> 'CollapsiblePanel':
        """Reject base panel fields that Kibana section headers do not support."""
        if self.hide_title is not None:
            msg = "CollapsiblePanel does not support 'hide_title'; Kibana always renders section headers."
            raise ValueError(msg)
        if self.description is not None:
            msg = "CollapsiblePanel does not support 'description'."
            raise ValueError(msg)
        if self.drilldowns is not None:
            msg = "CollapsiblePanel does not support 'drilldowns'."
            raise ValueError(msg)
        if self.size.width != GRID_WIDTH_WHOLE or self.size.h != 1:
            msg = 'CollapsiblePanel size is fixed to full width and 1 row (size: {w: whole, h: 1}).'
            raise ValueError(msg)
        if self.position.x not in (None, 0):
            msg = 'CollapsiblePanel position.x must be 0 because section headers are full-width.'
            raise ValueError(msg)
        return self
