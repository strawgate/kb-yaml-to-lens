"""Pydantic models for MCP tool requests and responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, RootModel


class DataStreamFieldSummary(BaseModel):
    """Summary of a single field in a data stream."""

    field: str = Field(description='The name of the field')
    type: str = Field(description='The Elasticsearch type of the field')
    sample_values: list[str | bool | int | float | None] | None = Field(
        default=None,
        description='A sample of unique values from the field (up to 10)',
    )


class DataStreamRowExample(RootModel[dict[str, Any]]):
    """A single row example from a data stream."""


class DataStreamSummary(BaseModel):
    """Summary of a data stream including fields and sample rows."""

    data_stream: str = Field(description='The name of the data stream')
    fields: list[DataStreamFieldSummary] = Field(
        default_factory=list,
        description='Summary of fields in the data stream',
    )
    sample_rows: list[DataStreamRowExample] = Field(
        default_factory=list,
        description='Sample rows from the data stream (up to 5)',
    )


class DataStreamInfo(BaseModel):
    """Information about a data stream."""

    name: str = Field(description='The name of the data stream')
    timestamp_field: str = Field(description='The timestamp field for the data stream')
    backing_indices: list[str] = Field(
        default_factory=list,
        description='List of backing indices',
    )


class EsqlQueryResult(BaseModel):
    """Result of an ES|QL query execution."""

    columns: list[dict[str, str]] = Field(
        default_factory=list,
        description='Column definitions with name and type',
    )
    values: list[list[Any]] = Field(
        default_factory=list,
        description='Query result values',
    )
    is_columnar: bool = Field(
        default=False,
        description='Whether the result is in columnar format',
    )


class GrokMatchResult(BaseModel):
    """Result of a grok pattern match."""

    matched: bool = Field(description='Whether the pattern matched')
    fields: dict[str, Any] = Field(
        default_factory=dict,
        description='Extracted fields and values',
    )


class DissectMatchResult(BaseModel):
    """Result of a dissect pattern match for a single document."""

    document_index: int = Field(description='Index of the document in the input list')
    success: bool = Field(description='Whether the pattern matched successfully')
    fields: dict[str, Any] = Field(
        default_factory=dict,
        description='Extracted fields and values',
    )
    error: str | None = Field(
        default=None,
        description='Error message if the pattern failed',
    )
