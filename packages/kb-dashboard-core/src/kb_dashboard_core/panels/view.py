"""Base classes and data structures for panels in Kibana dashboards."""

from typing import Annotated, Any

from pydantic import Field, field_serializer

from kb_dashboard_core.filters.view import KbnFilter
from kb_dashboard_core.queries.view import KbnQuery
from kb_dashboard_core.shared.model import BaseModel
from kb_dashboard_core.shared.view import BaseVwModel, OmitIfNone

__all__ = [
    'KbnBasePanel',
    'KbnBasePanelEmbeddableConfig',
    'KbnGridData',
    'KbnSavedObjectMeta',
    'KbnSearchSourceJSON',
]


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


class KbnSavedObjectMeta(BaseModel):
    """Represents the 'kibanaSavedObjectMeta' object in the Kibana JSON structure."""

    searchSourceJSON: KbnSearchSourceJSON = Field(...)

    @field_serializer('searchSourceJSON', when_used='always')
    def search_source_json_stringified(self, searchSourceJSON: KbnSearchSourceJSON) -> str:
        """Kibana wants this field to be stringified JSON.

        Returns:
            str: The JSON string representation of the search source.

        """
        return searchSourceJSON.model_dump_json(by_alias=True)
