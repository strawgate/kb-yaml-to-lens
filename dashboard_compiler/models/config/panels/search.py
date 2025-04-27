from typing import Literal

from pydantic import Field

from dashboard_compiler.models.config.panels.base import BasePanel


class SearchPanel(BasePanel):
    """Represents a Search panel in the YAML schema."""

    type: Literal["search"] = "search"
    saved_search_id: str = Field(..., description="(Required) The ID of the Kibana saved search object.")
