"""Data stream exploration tools."""

from __future__ import annotations

import contextlib
import re
from typing import TYPE_CHECKING, Annotated, Any

from fastmcp.tools import Tool

from kb_dashboard_mcp.models import DataStreamFieldSummary, DataStreamInfo, DataStreamRowExample, DataStreamSummary

if TYPE_CHECKING:
    from elasticsearch import AsyncElasticsearch
    from fastmcp import FastMCP


# Pattern to validate data stream names (alphanumeric, -, _, ., and *)
DATA_STREAM_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\-_\.\*]+$')


def _extract_unique_values(values: list[list[Any]], col_index: int) -> set[Any]:
    """Extract unique non-null values from a column."""
    unique_values: set[Any] = set()
    for row in values:
        if col_index < len(row):
            value = row[col_index]
            if value is not None:
                with contextlib.suppress(TypeError):
                    unique_values.add(value)
    return unique_values


def _build_field_summaries(columns: list[dict[str, Any]], values: list[list[Any]]) -> list[DataStreamFieldSummary]:
    """Build field summaries from columns and values."""
    field_summaries: list[DataStreamFieldSummary] = []

    for col_index, column in enumerate(columns):
        field_name: str | None = column.get('name')
        field_type: str | None = column.get('type')

        if field_name is None or field_type is None:
            continue

        unique_values = _extract_unique_values(values, col_index)
        sample_values = list(unique_values)[:10] if len(unique_values) > 0 else None

        field_summaries.append(
            DataStreamFieldSummary(
                field=field_name,
                type=field_type,
                sample_values=sample_values,
            )
        )

    return field_summaries


def _build_row_examples(columns: list[dict[str, Any]], values: list[list[Any]]) -> list[DataStreamRowExample]:
    """Build row examples from columns and values."""
    row_examples: list[DataStreamRowExample] = []

    for row_index in range(min(5, len(values))):
        row = values[row_index]
        row_dict: dict[str, Any] = {}

        for col_index, column in enumerate(columns):
            if col_index < len(row):
                value = row[col_index]
                if value is not None:
                    col_name = column.get('name')
                    if col_name is not None:
                        row_dict[col_name] = value

        row_examples.append(DataStreamRowExample(root=row_dict))

    return row_examples


async def _summarize_single_data_stream(es: AsyncElasticsearch, data_stream: str) -> DataStreamSummary:
    """Summarize a single data stream with field information and sample rows."""
    if not DATA_STREAM_NAME_PATTERN.match(data_stream):
        msg = f'Invalid data stream name: {data_stream}'
        raise ValueError(msg)

    esql_query = f'FROM {data_stream} | LIMIT 200'
    result = await es.esql.query(query=esql_query, format='json')

    columns: list[dict[str, Any]] | None = result.get('columns')

    if columns is None or len(columns) == 0:
        return DataStreamSummary(data_stream=data_stream, fields=[], sample_rows=[])

    values: list[list[Any]] | None = result.get('values')

    if values is None or len(values) == 0:
        return DataStreamSummary(data_stream=data_stream, fields=[], sample_rows=[])

    field_summaries = _build_field_summaries(columns, values)
    row_examples = _build_row_examples(columns, values)

    return DataStreamSummary(
        data_stream=data_stream,
        fields=field_summaries,
        sample_rows=row_examples,
    )


def register_data_stream_tools(mcp: FastMCP, es: AsyncElasticsearch) -> None:
    """Register data stream exploration tools with the MCP server."""

    async def summarize_data_streams(
        data_streams: Annotated[list[str], 'The data streams to summarize'],
    ) -> list[DataStreamSummary]:
        """Summarize data streams with field information and sample rows.

        Returns field types, sample values (up to 10 per field), and 5 sample rows
        for each requested data stream.
        """
        summaries: list[DataStreamSummary] = []
        for data_stream in data_streams:
            summary = await _summarize_single_data_stream(es, data_stream)
            summaries.append(summary)
        return summaries

    async def list_data_streams(
        pattern: Annotated[str | None, 'Optional name pattern to filter data streams (supports wildcards)'] = None,
    ) -> list[DataStreamInfo]:
        """List available data streams in the cluster.

        Returns data stream names with backing indices and timestamp field.
        """
        kwargs: dict[str, Any] = {}
        if pattern is not None:
            kwargs['name'] = pattern

        response = await es.indices.get_data_stream(**kwargs)
        data_streams_list: list[dict[str, Any]] = response.get('data_streams', [])

        result: list[DataStreamInfo] = []
        for ds in data_streams_list:
            name = ds.get('name', '')
            timestamp_field = ds.get('timestamp_field', {}).get('name', '@timestamp')
            indices = ds.get('indices', [])
            backing_indices = [idx.get('index_name', '') for idx in indices]

            result.append(
                DataStreamInfo(
                    name=name,
                    timestamp_field=timestamp_field,
                    backing_indices=backing_indices,
                )
            )

        return result

    mcp.add_tool(Tool.from_function(summarize_data_streams, tags={'data_streams', 'summarize'}))
    mcp.add_tool(Tool.from_function(list_data_streams, tags={'data_streams', 'list'}))
