"""Base classes and data structures for panels in Kibana dashboards."""

import json
from typing import TYPE_CHECKING, Annotated, Any

from pydantic import Field, field_serializer

from dashboard_compiler.filters.view import KbnFilter
from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone

if TYPE_CHECKING:
    from dashboard_compiler.panels.charts.view import KbnLensPanel
    from dashboard_compiler.panels.links.view import KbnLinksPanel
    from dashboard_compiler.panels.markdown.view import KbnMarkdownPanel
    from dashboard_compiler.panels.search.view import KbnSearchPanel

__all__ = [
    'KbnBasePanel',
    'KbnBasePanelEmbeddableConfig',
    'KbnGridData',
    'KbnPanelTypes',
    'KbnSavedObjectMeta',
    'KbnSearchSourceJSON',
]

type KbnPanelTypes = 'KbnMarkdownPanel | KbnSearchPanel | KbnLinksPanel | KbnLensPanel'


class KbnGridData(BaseVwModel):
    """Represents the 'gridData' object in the Kibana JSON structure."""

    x: int
    y: int
    w: int
    h: int
    i: str


class KbnBasePanelEmbeddableConfig(BaseVwModel):
    """Base model for embeddable configuration in Kibana panels."""

    enhancements: dict[str, Any] = Field(default_factory=dict)
    description: Annotated[str | None, OmitIfNone()] = Field(default=None)
    hidePanelTitles: Annotated[bool | None, OmitIfNone()] = None


class KbnBasePanel(BaseVwModel):
    """Base model for panel objects in the Kibana JSON structure."""

    panelIndex: str
    gridData: KbnGridData


class KbnSearchSourceJSON(BaseVwModel):
    """Represents the 'searchSourceJSON' object in the Kibana JSON structure."""

    filter: list[KbnFilter] = Field(...)
    query: KbnQuery = Field(...)


class KbnSavedObjectMeta(BaseVwModel):
    """Represents the 'kibanaSavedObjectMeta' object in the Kibana JSON structure."""

    searchSourceJSON: KbnSearchSourceJSON = Field(...)

    @field_serializer('searchSourceJSON', when_used='always')
    def search_source_json_stringified(self, searchSourceJSON: KbnSearchSourceJSON) -> str:
        """Kibana wants this field to be stringified JSON.

        Returns:
            str: The JSON string representation of the search source.

        """
        return json.dumps(searchSourceJSON.model_dump(serialize_as_any=True, exclude_none=True))
