import json
from typing import Any, Literal

from pydantic import BaseModel, Field, field_serializer


class KbnGridData(BaseModel):
    """Represents the 'gridData' object in the Kibana JSON structure."""

    x: int
    y: int
    w: int
    h: int
    i: str


class KbnFilter(BaseModel):
    """Represents a filter object within state.filters in the Kibana JSON structure."""

    state: dict[str, str] = Field(default_factory=lambda: {"store": "appState"}, alias="$state")
    meta: dict[str, Any]
    query: dict[str, Any] = Field(default_factory=dict)  # Can be empty


class KbnQuery(BaseModel):
    """Represents the query object within state.query in the Kibana JSON structure."""

    query: str = ""
    language: Literal["kuery", "lucene"] = Field(default="kuery")  # Default to 'kuery' if not specified


class KbnBasePanelEmbeddableConfig(BaseModel):
    enhancements: dict[str, Any] = Field(default_factory=lambda: {"dynamicActions": {"events": []}})


class KbnBasePanel(BaseModel):
    """Base model for panel objects in the Kibana JSON structure."""

    # type: Literal["visualization", "search", "map", "lens", "links"]
    panelIndex: str
    gridData: KbnGridData
    # embeddableConfig: KbnBasePanelEmbeddableConfig


class KbnSearchSourceJSON(BaseModel):
    filter: list[KbnFilter] = Field(default_factory=list)
    query: KbnQuery = Field(default_factory=KbnQuery)


class KbnSavedObjectMeta(BaseModel):
    searchSourceJSON: KbnSearchSourceJSON = Field(
        default_factory=lambda: KbnSearchSourceJSON(filter=[], query={"query": "", "language": "kuery"})
    )

    @field_serializer("searchSourceJSON", when_used="always")
    def search_source_json_stringified(self, searchSourceJSON: KbnSearchSourceJSON):
        """Kibana wants this field to be stringified JSON."""
        return json.dumps(searchSourceJSON.model_dump(serialize_as_any=True, exclude_none=True))


class KbnReference(BaseModel):
    """Represents a reference object in the Kibana JSON structure."""

    type: str
    id: str
    name: str
