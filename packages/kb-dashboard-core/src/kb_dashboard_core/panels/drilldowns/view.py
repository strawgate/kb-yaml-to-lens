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

    useCurrentFilters: bool = Field()
    """Whether to inherit current filters."""

    useCurrentDateRange: bool = Field()
    """Whether to inherit current time range."""


class KbnUrlDrilldownConfig(BaseVwModel):
    """Configuration for URL drilldown."""

    url: dict[str, str] = Field()
    """URL template payload."""

    openInNewTab: bool = Field()
    """Whether to open in a new tab."""

    encodeUrl: bool = Field(default=True)
    """Whether to URL-encode template variables."""


class KbnDrilldownAction(BaseVwModel):
    """Drilldown action configuration."""

    factoryId: str = Field()
    """Factory identifier for the drilldown type."""

    name: str = Field()
    """Display name for the drilldown."""

    config: dict[str, Any] = Field()
    """Configuration payload for the drilldown action."""


class KbnDrilldownEvent(BaseVwModel):
    """Drilldown event configuration."""

    eventId: str = Field()
    """Unique identifier for the drilldown event."""

    triggers: list[str] = Field()
    """List of trigger types that activate this drilldown."""

    action: KbnDrilldownAction = Field()
    """Action to perform when triggered."""


class KbnDynamicActions(BaseVwModel):
    """Dynamic actions configuration for enhancements."""

    events: list[KbnDrilldownEvent] = Field(default_factory=list)
    """List of drilldown events."""


class KbnEnhancements(BaseVwModel):
    """Enhancements configuration for panel embeddable config."""

    dynamicActions: KbnDynamicActions = Field(default_factory=KbnDynamicActions)
    """Dynamic actions configuration containing drilldown events."""
