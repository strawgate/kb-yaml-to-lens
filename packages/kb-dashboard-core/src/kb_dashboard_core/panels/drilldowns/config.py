"""Config models for user-facing YAML drilldown configuration."""

from enum import StrEnum
from typing import Annotated

from pydantic import Field

from kb_dashboard_core.shared.config import BaseCfgModel


class DrilldownTrigger(StrEnum):
    """User-facing drilldown trigger types."""

    click = 'click'
    filter = 'filter'
    range = 'range'


# Annotated type to allow string coercion for DrilldownTrigger in lists
_Trigger = Annotated[DrilldownTrigger, Field(strict=False)]


class BaseDrilldown(BaseCfgModel):
    """Base configuration for all drilldown types."""

    id: str | None = Field(default=None)
    """Optional unique identifier for the drilldown. If not provided, one will be generated."""

    name: str = Field(...)
    """Display name for the drilldown."""

    triggers: list[_Trigger] = Field(default_factory=lambda: [DrilldownTrigger.click])
    """List of triggers that activate this drilldown. Defaults to ['click']."""


class DashboardDrilldown(BaseDrilldown):
    """Dashboard-to-dashboard drilldown configuration."""

    dashboard: str = Field(...)
    """Target dashboard ID or friendly identifier."""

    with_filters: bool = Field(default=True)
    """Whether to carry over current filters to the target dashboard. Defaults to True."""

    with_time: bool = Field(default=True)
    """Whether to carry over current time range to the target dashboard. Defaults to True."""


class UrlDrilldown(BaseDrilldown):
    """URL drilldown configuration."""

    url: str = Field(...)
    """Target URL template. Can include Kibana template variables."""

    new_tab: bool = Field(default=False)
    """Whether to open the URL in a new tab. Defaults to False."""

    encode_url: bool = Field(default=True)
    """Whether to URL-encode the template variables. Defaults to True."""


type DrilldownTypes = DashboardDrilldown | UrlDrilldown
