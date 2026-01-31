"""Pydantic models for Kibana API responses."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    'DataStreamIndex',
    'DataStreamInfo',
    'DataStreamTimestampField',
    'DataStreamsResponse',
    'EsqlColumn',
    'EsqlResponse',
    'GrokMatch',
    'GrokPatternResponse',
    'IngestSimulateDoc',
    'IngestSimulateDocResult',
    'IngestSimulateError',
    'IngestSimulateResponse',
]


class EsqlColumn(BaseModel):
    """Column definition in ES|QL query results."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    name: str
    """Column name."""
    type: str
    """Column data type (e.g., keyword, long, date)."""


class EsqlResponse(BaseModel):
    """Response from ES|QL query execution via Kibana.

    This model represents the structured result of an ES|QL query,
    containing column definitions and row values.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    columns: list[EsqlColumn]
    """Column definitions with name and type."""
    values: list[list[Any]]
    """Row values as nested arrays."""
    took: int | None = None
    """Query execution time in milliseconds."""
    is_partial: bool | None = None
    """Whether results are partial."""

    @property
    def row_count(self) -> int:
        """Return the number of rows in the result."""
        return len(self.values)

    @property
    def column_count(self) -> int:
        """Return the number of columns in the result."""
        return len(self.columns)

    def to_dicts(self) -> list[dict[str, Any]]:
        """Convert results to a list of dictionaries with column names as keys.

        Returns:
            List of dictionaries, each representing a row with column names as keys.
        """
        # Values are dynamic JSON types from Elasticsearch
        return [{col.name: val for col, val in zip(self.columns, row, strict=False)} for row in self.values]  # pyright: ignore[reportAny]


# ============================================================================
# Data Streams Response Models
# ============================================================================


class DataStreamTimestampField(BaseModel):
    """Timestamp field configuration for a data stream."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    name: str
    """Name of the timestamp field."""


class DataStreamIndex(BaseModel):
    """Backing index information for a data stream."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    index_name: str
    """Name of the backing index."""
    index_uuid: str | None = None
    """UUID of the backing index."""
    managed_by: str | None = None
    """Component managing this index."""


class DataStreamInfo(BaseModel):
    """Information about a single data stream."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    name: str
    """Name of the data stream."""
    timestamp_field: DataStreamTimestampField
    """Timestamp field configuration."""
    indices: list[DataStreamIndex] = Field(default_factory=list)
    """Backing indices for this data stream."""
    generation: int | None = None
    """Generation number of the data stream."""
    status: str | None = None
    """Health status of the data stream."""
    template: str | None = None
    """Index template this data stream uses."""


class DataStreamsResponse(BaseModel):
    """Response from Elasticsearch data streams API."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    data_streams: list[DataStreamInfo] = Field(default_factory=list)
    """List of data streams."""


# ============================================================================
# Grok Pattern Response Models
# ============================================================================


class GrokMatch(BaseModel):
    """A single grok pattern match result."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    matched: bool
    """Whether the pattern matched."""
    match: dict[str, Any] | None = None
    """Extracted fields from the match, if successful."""


class GrokPatternResponse(BaseModel):
    """Response from Elasticsearch text_structure grok pattern test API."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    matches: list[GrokMatch] = Field(default_factory=list)
    """List of match results for each input text line."""


# ============================================================================
# Ingest Simulate Response Models
# ============================================================================


class IngestSimulateError(BaseModel):
    """Error information from ingest simulation."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    type: str | None = None
    """Error type."""
    reason: str | None = None
    """Error reason."""


class IngestSimulateDoc(BaseModel):
    """Simulated document result."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow', populate_by_name=True)

    id: str | None = Field(default=None, alias='_id')
    """Document ID."""
    index: str | None = Field(default=None, alias='_index')
    """Target index."""
    source: dict[str, Any] = Field(default_factory=dict, alias='_source')
    """Document source after processing."""


class IngestSimulateDocResult(BaseModel):
    """Result for a single document in ingest simulation."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    doc: IngestSimulateDoc | None = None
    """Processed document, if successful."""
    error: IngestSimulateError | None = None
    """Error information, if processing failed."""

    @property
    def success(self) -> bool:
        """Whether this document was processed successfully."""
        return self.error is None and self.doc is not None


class IngestSimulateResponse(BaseModel):
    """Response from Elasticsearch ingest pipeline simulate API."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    docs: list[IngestSimulateDocResult] = Field(default_factory=list)
    """List of document processing results."""
