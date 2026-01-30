"""Config models for user-facing YAML drilldown configuration."""

from enum import StrEnum
from typing import Annotated

from pydantic import BeforeValidator, Discriminator, Field, Tag

from kb_dashboard_core.shared.config import BaseCfgModel


class DrilldownTrigger(StrEnum):
    """User-facing drilldown trigger types."""

    click = 'click'
    filter = 'filter'
    range = 'range'


def _coerce_trigger(v: object) -> DrilldownTrigger:
    """Coerce string values to DrilldownTrigger enum.

    Required because BaseCfgModel uses strict=True which prevents automatic coercion.

    Args:
        v: A value to coerce to DrilldownTrigger.

    Returns:
        DrilldownTrigger: The coerced enum value.

    Raises:
        TypeError: If the value is not a string or DrilldownTrigger.
    """
    if isinstance(v, DrilldownTrigger):
        return v
    if isinstance(v, str):
        return DrilldownTrigger(v)
    msg = f'Expected str or DrilldownTrigger, got {type(v).__name__}'
    raise TypeError(msg)


def _coerce_triggers(v: object) -> list[DrilldownTrigger]:
    """Coerce a list of string values to DrilldownTrigger enums.

    Args:
        v: A value to coerce to a list of DrilldownTriggers.

    Returns:
        list[DrilldownTrigger]: The coerced list of enum values.

    Raises:
        TypeError: If the value is not a list.
    """
    if isinstance(v, list):
        return [_coerce_trigger(item) for item in v]  # pyright: ignore[reportUnknownArgumentType,reportUnknownVariableType]
    msg = f'Expected list, got {type(v).__name__}'
    raise TypeError(msg)


class BaseDrilldown(BaseCfgModel):
    """Base configuration for all drilldown types."""

    id: str | None = Field(default=None)
    """Optional unique identifier for the drilldown. If not provided, one will be generated."""

    name: str = Field(...)
    """Display name for the drilldown."""

    triggers: Annotated[list[DrilldownTrigger], BeforeValidator(_coerce_triggers)] = Field(default_factory=lambda: [DrilldownTrigger.click])
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


def get_drilldown_type(v: dict[str, object] | object) -> str:
    """Discriminator function to determine drilldown type.

    Args:
        v: Dictionary or object to check.

    Returns:
        str: Either 'dashboard' or 'url'.

    Raises:
        ValueError: If the drilldown type cannot be determined.
    """
    if isinstance(v, dict):
        if 'dashboard' in v:
            return 'dashboard'
        if 'url' in v:
            return 'url'
        msg = f'Cannot determine drilldown type from: {list(v.keys())}'  # pyright: ignore[reportUnknownArgumentType]
        raise ValueError(msg)
    if isinstance(v, DashboardDrilldown):
        return 'dashboard'
    if isinstance(v, UrlDrilldown):
        return 'url'
    msg = f'Cannot determine drilldown type: {type(v).__name__}'
    raise ValueError(msg)


type DrilldownTypes = Annotated[
    Annotated[DashboardDrilldown, Tag('dashboard')] | Annotated[UrlDrilldown, Tag('url')],
    Discriminator(get_drilldown_type),
]
