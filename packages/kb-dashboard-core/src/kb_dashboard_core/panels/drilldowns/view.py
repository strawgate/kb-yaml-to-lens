"""View models for Kibana drilldown JSON structures."""

from enum import StrEnum
from typing import Any

from pydantic import Field

from kb_dashboard_core.shared.view import BaseVwModel

# Factory ID constants
DASHBOARD_TO_DASHBOARD_DRILLDOWN = 'DASHBOARD_TO_DASHBOARD_DRILLDOWN'
URL_DRILLDOWN = 'URL_DRILLDOWN'


class KbnDrilldownTrigger(StrEnum):
    """Kibana drilldown trigger types."""

    VALUE_CLICK_TRIGGER = 'VALUE_CLICK_TRIGGER'
    FILTER_TRIGGER = 'FILTER_TRIGGER'
    SELECT_RANGE_TRIGGER = 'SELECT_RANGE_TRIGGER'


class KbnDashboardDrilldownConfig(BaseVwModel):
    """Configuration for dashboard-to-dashboard drilldown."""

    useCurrentFilters: bool
    useCurrentDateRange: bool


class KbnUrlDrilldownConfig(BaseVwModel):
    """Configuration for URL drilldown."""

    url: dict[str, str]
    openInNewTab: bool
    encodeUrl: bool = True


class KbnDrilldownAction(BaseVwModel):
    """Drilldown action configuration."""

    factoryId: str
    name: str
    config: dict[str, Any]


class KbnDrilldownEvent(BaseVwModel):
    """Drilldown event configuration."""

    eventId: str
    triggers: list[str]
    action: KbnDrilldownAction


class KbnDynamicActions(BaseVwModel):
    """Dynamic actions configuration for enhancements."""

    events: list[KbnDrilldownEvent] = Field(default_factory=list)


class KbnEnhancements(BaseVwModel):
    """Enhancements configuration for panel embeddable config."""

    dynamicActions: KbnDynamicActions = Field(default_factory=KbnDynamicActions)
