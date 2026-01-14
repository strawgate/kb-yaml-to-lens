"""Alerts table panel view model."""

from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.view import KbnBasePanel, KbnBasePanelEmbeddableConfig
from dashboard_compiler.shared.view import BaseVwModel

# The following is an example of the JSON structure that these models represent. Do not remove:
# {                                                 <-- KbnAlertsPanel
#     "type": "alerts_table",
#     "embeddableConfig": {                         <-- KbnAlertsEmbeddableConfig
#         "enhancements": {},
#         "tableConfig": {                          <-- KbnAlertsTableConfig
#             "solution": "observability",
#             "query": {                            <-- KbnAlertsQuery
#                 "type": "alertsFilters",
#                 "filters": []
#             }
#         }
#     },
#     "panelIndex": "780e08fc-1a39-401b-849f-703b951bc243",
#     "gridData": {                                 <-- KbnGridData
#         "x": 0,
#         "y": 0,
#         "w": 24,
#         "h": 15,
#         "i": "780e08fc-1a39-401b-849f-703b951bc243"
#     }
# }


class KbnAlertsFilterExpression(BaseVwModel):
    """A single filter expression for alerts."""

    field: str = Field(...)
    """The field to filter on."""

    values: list[str] = Field(...)
    """The values to match."""


class KbnAlertsQuery(BaseVwModel):
    """Query configuration for the alerts table."""

    type: Literal['alertsFilters'] = 'alertsFilters'
    """The query type - always 'alertsFilters' for alert embeddables."""

    filters: list[KbnAlertsFilterExpression] = Field(default_factory=list)
    """The filter expressions to apply."""


class KbnAlertsTableConfig(BaseVwModel):
    """Configuration for the alerts table embeddable."""

    solution: str = Field(...)
    """The solution context (observability, security, or stack)."""

    query: KbnAlertsQuery = Field(...)
    """The query/filter configuration."""


class KbnAlertsEmbeddableConfig(KbnBasePanelEmbeddableConfig):
    """Embeddable configuration for alerts table panels."""

    tableConfig: KbnAlertsTableConfig = Field(...)
    """The table-specific configuration."""


class KbnAlertsPanel(KbnBasePanel):
    """Represents an Alerts Table panel in the Kibana JSON structure."""

    type: Literal['alerts_table'] = 'alerts_table'
    """The panel type identifier for alerts table panels."""

    embeddableConfig: KbnAlertsEmbeddableConfig
    """The embeddable configuration for the alerts table."""
