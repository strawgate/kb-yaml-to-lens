"""Data stream exploration tools."""

import contextlib
import re
from typing import Annotated, Any, cast

from fastmcp import FastMCP
from fastmcp.tools import Tool

from kb_dashboard_mcp.models import DataStreamFieldSummary, DataStreamInfo, DataStreamRowExample, DataStreamSummary
from kb_dashboard_tools.kibana_client import KibanaClient
from kb_dashboard_tools.models import EsqlColumn

# Pattern to validate data stream names (alphanumeric, -, _, ., and *)
DATA_STREAM_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\-_\.\*]+$')


def _extract_unique_values(values: list[list[Any]], col_index: int) -> list[str | bool | int | float]:
    """Extract unique non-null values from a column (up to 10)."""
    unique_values: set[str | bool | int | float] = set()
    for row in values:
        if col_index < len(row):
            raw_value: Any = row[col_index]  # pyright: ignore[reportAny]
            if raw_value is not None and isinstance(raw_value, (str, bool, int, float)):
                with contextlib.suppress(TypeError):
                    unique_values.add(raw_value)
                    if len(unique_values) >= 10:  # noqa: PLR2004
                        break
    return list(unique_values)


def _build_field_summaries(columns: list[EsqlColumn], values: list[list[Any]]) -> list[DataStreamFieldSummary]:
    """Build field summaries from columns and values."""
    field_summaries: list[DataStreamFieldSummary] = []

    for col_index, column in enumerate(columns):
        unique_values = _extract_unique_values(values, col_index)
        # Cast needed: list[T] is not assignable to list[T | None] due to invariance
        sample_values = cast('list[str | bool | int | float | None]', unique_values) if len(unique_values) > 0 else None

        field_summaries.append(
            DataStreamFieldSummary(
                field=column.name,
                type=column.type,
                sample_values=sample_values,
            )
        )

    return field_summaries


def _build_row_examples(columns: list[EsqlColumn], values: list[list[Any]]) -> list[DataStreamRowExample]:
    """Build row examples from columns and values."""
    row_examples: list[DataStreamRowExample] = []

    for row_index in range(min(5, len(values))):
        row = values[row_index]
        row_dict: dict[str, Any] = {}

        for col_index, column in enumerate(columns):
            if col_index < len(row):
                value: Any = row[col_index]  # pyright: ignore[reportAny]
                if value is not None:
                    row_dict[column.name] = value

        row_examples.append(DataStreamRowExample(root=row_dict))

    return row_examples


async def summarize_single_data_stream(client: KibanaClient, data_stream: str) -> DataStreamSummary:
    """Summarize a single data stream with field information and sample rows.

    Args:
        client: KibanaClient instance.
        data_stream: Name of the data stream to summarize.

    Returns:
        Summary including field types, sample values, and sample rows.

    Raises:
        ValueError: If the data stream name is invalid.
    """
    if not DATA_STREAM_NAME_PATTERN.match(data_stream):
        msg = f'Invalid data stream name: {data_stream}'
        raise ValueError(msg)

    esql_query = f'FROM {data_stream} | LIMIT 200'
    result = await client.execute_esql(query=esql_query)

    if len(result.columns) == 0 or len(result.values) == 0:
        return DataStreamSummary(data_stream=data_stream, fields=[], sample_rows=[])

    field_summaries = _build_field_summaries(result.columns, result.values)
    row_examples = _build_row_examples(result.columns, result.values)

    return DataStreamSummary(
        data_stream=data_stream,
        fields=field_summaries,
        sample_rows=row_examples,
    )


async def summarize_data_streams(client: KibanaClient, data_streams: list[str]) -> list[DataStreamSummary]:
    """Summarize data streams with field information and sample rows.

    Args:
        client: KibanaClient instance.
        data_streams: List of data stream names to summarize.

    Returns:
        List of summaries with field types, sample values (up to 10 per field),
        and 5 sample rows for each requested data stream.
    """
    summaries: list[DataStreamSummary] = []
    for data_stream in data_streams:
        summary = await summarize_single_data_stream(client, data_stream)
        summaries.append(summary)
    return summaries


async def list_data_streams(client: KibanaClient, pattern: str | None = None) -> list[DataStreamInfo]:
    """List available data streams in the cluster.

    Args:
        client: KibanaClient instance.
        pattern: Optional name pattern to filter data streams (supports wildcards).

    Returns:
        Data stream names with backing indices and timestamp field.

    Raises:
        ValueError: If the pattern contains invalid characters.
    """
    if pattern is not None and not DATA_STREAM_NAME_PATTERN.match(pattern):
        msg = f'Invalid data stream pattern: {pattern}'
        raise ValueError(msg)

    response = await client.get_data_streams(name=pattern)

    return [
        DataStreamInfo(
            name=ds.name,
            timestamp_field=ds.timestamp_field.name,
            backing_indices=[idx.index_name for idx in ds.indices],
        )
        for ds in response.data_streams
    ]


def register_data_stream_tools(mcp: FastMCP, client: KibanaClient) -> None:
    """Register data stream exploration tools with the MCP server.

    Args:
        mcp: FastMCP server instance.
        client: KibanaClient instance.
    """

    async def _summarize_data_streams(
        data_streams: Annotated[list[str], 'The data streams to summarize'],
    ) -> list[DataStreamSummary]:
        """Summarize data streams with field information and sample rows.

        Returns field types, sample values (up to 10 per field), and 5 sample rows
        for each requested data stream.
        """
        return await summarize_data_streams(client, data_streams)

    async def _list_data_streams(
        pattern: Annotated[str | None, 'Optional name pattern to filter data streams (supports wildcards)'] = None,
    ) -> list[DataStreamInfo]:
        """List available data streams in the cluster.

        Returns data stream names with backing indices and timestamp field.
        """
        return await list_data_streams(client, pattern)

    _ = mcp.add_tool(Tool.from_function(_summarize_data_streams, name='summarize_data_streams', tags={'data_streams', 'summarize'}))
    _ = mcp.add_tool(Tool.from_function(_list_data_streams, name='list_data_streams', tags={'data_streams', 'list'}))
