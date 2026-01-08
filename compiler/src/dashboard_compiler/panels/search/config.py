"""Configuration for a Search panel in a dashboard."""

from pydantic import Field

from dashboard_compiler.panels.base import BasePanel
from dashboard_compiler.shared.config import BaseCfgModel


class SearchPanelConfig(BaseCfgModel):
    """Configuration specific to Search panels."""

    saved_search_id: str = Field(...)
    """The ID of the saved Kibana search object to display in the panel."""


class SearchPanel(BasePanel):
    """Represents a Search panel configuration.

    Search panels are used to display the results of a saved Kibana search.

    Examples:
        Minimal search panel:
        ```yaml
        dashboards:
          - name: "Log Monitoring Dashboard"
            panels:
              - title: "All System Logs"
                grid: { x: 0, y: 0, w: 48, h: 10 }
                search:
                  saved_search_id: "a1b2c3d4-e5f6-7890-1234-567890abcdef"
        ```

        Search panel with hidden title:
        ```yaml
        dashboards:
          - name: "Security Incidents Overview"
            panels:
              - hide_title: true
                description: "Critical security alerts from the last 24 hours"
                grid: { x: 0, y: 0, w: 48, h: 8 }
                search:
                  saved_search_id: "critical-security-alerts-saved-search"
        ```
    """

    search: SearchPanelConfig = Field(...)
    """Search panel configuration."""
