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
    """

    search: SearchPanelConfig = Field(...)
    """Search panel configuration."""
