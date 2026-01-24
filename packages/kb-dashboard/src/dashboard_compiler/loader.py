"""Configuration loader for dashboard YAML files."""

from typing import ClassVar

from pydantic import ConfigDict, Field

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.shared.config import BaseCfgModel


class DashboardConfig(BaseCfgModel):
    """Root configuration model for loading dashboards from YAML.

    Note: extra='allow' is needed to support YAML anchors (e.g., .base_query: &anchor)
    which get parsed as root-level keys but are ignored after anchor resolution.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    dashboards: list[Dashboard] = Field(...)
    """List of dashboard configurations."""
