"""Configuration for a Search panel in a dashboard."""

from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.base import BasePanel


class SearchPanel(BasePanel):
    """Represents a Search panel configuration.

    Search panels are used to display the results of a saved Kibana search.
    """

    type: Literal['search'] = 'search'
    saved_search_id: str = Field(..., description='The ID of the saved Kibana search object to display in the panel.')
