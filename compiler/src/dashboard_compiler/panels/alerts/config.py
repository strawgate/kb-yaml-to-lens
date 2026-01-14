"""Configuration for an Alerts Table Panel in a dashboard."""

from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.base import BasePanel
from dashboard_compiler.shared.config import BaseCfgModel

AlertSolution = Literal['observability', 'security', 'stack']
"""The solution context for the alerts table (observability, security, or stack)."""


class AlertsFilter(BaseCfgModel):
    """A filter condition for the alerts table."""

    field: str = Field(...)
    """The field to filter on (e.g., 'kibana.alert.status', 'kibana.alert.rule.name')."""

    values: list[str] = Field(...)
    """The values to match for this filter."""


class AlertsPanelConfig(BaseCfgModel):
    """Configuration specific to Alerts Table panels."""

    solution: AlertSolution = Field(...)
    """The solution context for alerts (observability, security, or stack)."""

    filters: list[AlertsFilter] = Field(default_factory=list)
    """Optional filters to apply to the alerts displayed in the table."""


class AlertsPanel(BasePanel):
    """Represents an Alerts Table panel configuration.

    Alerts Table panels display alerts from Kibana Observability, Security, or Stack applications.
    They provide a way to monitor and view alerts directly on dashboards.

    Examples:
        Basic Alerts panel for Observability:
        ```yaml
        dashboards:
          - name: "Monitoring Dashboard"
            panels:
              - title: "Active Alerts"
                size: { w: 48, h: 15 }
                alerts:
                  solution: observability
        ```

        Alerts panel with filters:
        ```yaml
        dashboards:
          - name: "Security Dashboard"
            panels:
              - title: "Critical Security Alerts"
                size: { w: 48, h: 20 }
                alerts:
                  solution: security
                  filters:
                    - field: kibana.alert.severity
                      values: ["critical", "high"]
                    - field: kibana.alert.status
                      values: ["active"]
        ```
    """

    alerts: AlertsPanelConfig = Field(...)
    """Alerts table panel configuration."""
