"""Tests for MCP tools."""

from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastmcp import FastMCP

from kb_dashboard_mcp.tools.data_streams import (
    list_data_streams,
    register_data_stream_tools,
    summarize_data_streams,
    summarize_single_data_stream,
)
from kb_dashboard_mcp.tools.esql import execute_esql, register_esql_tools
from kb_dashboard_mcp.tools.patterns import register_pattern_tools, run_dissect_pattern_test, run_grok_pattern_test


class TestDataStreamTools:
    """Tests for data stream tools."""

    @pytest.fixture
    def mcp_with_data_stream_tools(self, mock_kibana_client: AsyncMock) -> FastMCP:
        """Create MCP server with data stream tools registered."""
        mcp = FastMCP(name='test')
        register_data_stream_tools(mcp, mock_kibana_client)
        return mcp

    def test_tools_registered(self, mcp_with_data_stream_tools: FastMCP) -> None:
        """Test that data stream tools are registered."""
        tool_names = [t.name for t in mcp_with_data_stream_tools._tool_manager._tools.values()]
        assert 'summarize_data_streams' in tool_names
        assert 'list_data_streams' in tool_names


class TestEsqlTools:
    """Tests for ES|QL tools."""

    @pytest.fixture
    def mcp_with_esql_tools(self, mock_kibana_client: AsyncMock) -> FastMCP:
        """Create MCP server with ES|QL tools registered."""
        mcp = FastMCP(name='test')
        register_esql_tools(mcp, mock_kibana_client)
        return mcp

    def test_tool_registered(self, mcp_with_esql_tools: FastMCP) -> None:
        """Test that ES|QL tool is registered."""
        tool_names = [t.name for t in mcp_with_esql_tools._tool_manager._tools.values()]
        assert 'execute_esql' in tool_names


class TestPatternTools:
    """Tests for pattern testing tools."""

    @pytest.fixture
    def mcp_with_pattern_tools(self, mock_kibana_client: AsyncMock) -> FastMCP:
        """Create MCP server with pattern tools registered."""
        mcp = FastMCP(name='test')
        register_pattern_tools(mcp, mock_kibana_client)
        return mcp

    def test_tools_registered(self, mcp_with_pattern_tools: FastMCP) -> None:
        """Test that pattern tools are registered."""
        tool_names = [t.name for t in mcp_with_pattern_tools._tool_manager._tools.values()]
        assert 'test_grok_pattern' in tool_names
        assert 'test_dissect_pattern' in tool_names


class TestDataStreamSummarize:
    """Tests for data stream summarization."""

    async def test_summarize_with_data(
        self,
        mock_kibana_client: AsyncMock,
        sample_esql_response: dict[str, Any],
    ) -> None:
        """Test summarizing a data stream with data."""
        mock_kibana_client.esql_query_raw.return_value = sample_esql_response

        result = await summarize_single_data_stream(mock_kibana_client, 'logs-test')

        assert result.data_stream == 'logs-test'
        assert len(result.fields) == 3
        assert len(result.sample_rows) == 3
        mock_kibana_client.esql_query_raw.assert_called_once_with(query='FROM logs-test | LIMIT 200')

    async def test_summarize_empty_data_stream(self, mock_kibana_client: AsyncMock) -> None:
        """Test summarizing an empty data stream."""
        mock_kibana_client.esql_query_raw.return_value = {'columns': [], 'values': []}

        result = await summarize_single_data_stream(mock_kibana_client, 'empty-stream')

        assert result.data_stream == 'empty-stream'
        assert len(result.fields) == 0
        assert len(result.sample_rows) == 0

    async def test_summarize_invalid_data_stream_name(self, mock_kibana_client: AsyncMock) -> None:
        """Test that invalid data stream names raise ValueError."""
        with pytest.raises(ValueError, match='Invalid data stream name'):
            await summarize_single_data_stream(mock_kibana_client, 'invalid;name')

    async def test_summarize_multiple_data_streams(
        self,
        mock_kibana_client: AsyncMock,
        sample_esql_response: dict[str, Any],
    ) -> None:
        """Test summarizing multiple data streams."""
        mock_kibana_client.esql_query_raw.return_value = sample_esql_response

        result = await summarize_data_streams(mock_kibana_client, ['logs-test', 'metrics-test'])

        assert len(result) == 2
        assert result[0].data_stream == 'logs-test'
        assert result[1].data_stream == 'metrics-test'
        assert mock_kibana_client.esql_query_raw.call_count == 2


class TestListDataStreams:
    """Tests for listing data streams."""

    async def test_list_data_streams(
        self,
        mock_kibana_client: AsyncMock,
        sample_data_stream_response: dict[str, Any],
    ) -> None:
        """Test listing data streams."""
        mock_kibana_client.get_data_streams.return_value = sample_data_stream_response

        result = await list_data_streams(mock_kibana_client)

        assert len(result) == 2
        assert result[0].name == 'logs-nginx-default'
        assert result[0].timestamp_field == '@timestamp'
        assert len(result[0].backing_indices) == 1
        mock_kibana_client.get_data_streams.assert_called_once_with(name=None)

    async def test_list_data_streams_with_pattern(
        self,
        mock_kibana_client: AsyncMock,
        sample_data_stream_response: dict[str, Any],
    ) -> None:
        """Test listing data streams with a pattern filter."""
        mock_kibana_client.get_data_streams.return_value = sample_data_stream_response

        await list_data_streams(mock_kibana_client, pattern='logs-*')

        mock_kibana_client.get_data_streams.assert_called_once_with(name='logs-*')

    async def test_list_data_streams_empty(self, mock_kibana_client: AsyncMock) -> None:
        """Test listing when no data streams exist."""
        mock_kibana_client.get_data_streams.return_value = {'data_streams': []}

        result = await list_data_streams(mock_kibana_client)

        assert len(result) == 0


class TestExecuteEsql:
    """Tests for ES|QL query execution."""

    async def test_execute_esql(
        self,
        mock_kibana_client: AsyncMock,
        sample_esql_response: dict[str, Any],
    ) -> None:
        """Test executing an ES|QL query."""
        mock_kibana_client.esql_query_raw.return_value = sample_esql_response

        result = await execute_esql(mock_kibana_client, 'FROM logs-* | LIMIT 10')

        assert len(result.columns) == 3
        assert len(result.values) == 3
        assert result.is_columnar is False
        mock_kibana_client.esql_query_raw.assert_called_once_with(query='FROM logs-* | LIMIT 10', columnar=False)

    async def test_execute_esql_columnar(
        self,
        mock_kibana_client: AsyncMock,
        sample_esql_response: dict[str, Any],
    ) -> None:
        """Test executing an ES|QL query in columnar format."""
        mock_kibana_client.esql_query_raw.return_value = sample_esql_response

        result = await execute_esql(mock_kibana_client, 'FROM logs-* | LIMIT 10', columnar=True)

        assert result.is_columnar is True
        mock_kibana_client.esql_query_raw.assert_called_once_with(query='FROM logs-* | LIMIT 10', columnar=True)

    async def test_execute_esql_empty_query(self, mock_kibana_client: AsyncMock) -> None:
        """Test that empty queries raise ValueError."""
        with pytest.raises(ValueError, match='Query cannot be empty'):
            await execute_esql(mock_kibana_client, '   ')


class TestGrokPattern:
    """Tests for grok pattern testing."""

    async def test_grok_pattern_match(
        self,
        mock_kibana_client: AsyncMock,
        sample_grok_match_response: dict[str, Any],
    ) -> None:
        """Test grok pattern matching."""
        mock_kibana_client.test_grok_pattern.return_value = sample_grok_match_response

        result = await run_grok_pattern_test(
            mock_kibana_client,
            '%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}',
            '2024-01-01 00:00:00 INFO Test log message',
        )

        assert result.matched is True
        assert result.fields['level'] == 'INFO'
        assert result.fields['message'] == 'Test log message'

    async def test_grok_pattern_no_match(self, mock_kibana_client: AsyncMock) -> None:
        """Test grok pattern that doesn't match."""
        mock_kibana_client.test_grok_pattern.return_value = {'matches': []}

        result = await run_grok_pattern_test(
            mock_kibana_client,
            '%{IP:client}',
            'not an IP address',
        )

        assert result.matched is False
        assert result.fields == {}

    async def test_grok_pattern_empty_pattern(self, mock_kibana_client: AsyncMock) -> None:
        """Test that empty patterns raise ValueError."""
        with pytest.raises(ValueError, match='Pattern cannot be empty'):
            await run_grok_pattern_test(mock_kibana_client, '   ', 'test text')

    async def test_grok_pattern_with_custom_patterns(
        self,
        mock_kibana_client: AsyncMock,
        sample_grok_match_response: dict[str, Any],
    ) -> None:
        """Test grok pattern with custom pattern definitions."""
        mock_kibana_client.test_grok_pattern.return_value = sample_grok_match_response

        await run_grok_pattern_test(
            mock_kibana_client,
            '%{CUSTOM:value}',
            'custom_value',
            custom_patterns={'CUSTOM': '[a-z_]+'},
        )

        mock_kibana_client.test_grok_pattern.assert_called_once_with(
            grok_pattern='%{CUSTOM:value}',
            text=['custom_value'],
            pattern_definitions={'CUSTOM': '[a-z_]+'},
        )


class TestDissectPattern:
    """Tests for dissect pattern testing."""

    async def test_dissect_pattern_match(
        self,
        mock_kibana_client: AsyncMock,
        sample_dissect_response: dict[str, Any],
    ) -> None:
        """Test dissect pattern matching."""
        mock_kibana_client.simulate_ingest.return_value = sample_dissect_response

        result = await run_dissect_pattern_test(
            mock_kibana_client,
            'user=%{user} action=%{action}',
            ['user=john action=login', 'user=jane action=logout'],
        )

        assert len(result) == 2
        assert result[0].success is True
        assert result[0].fields['user'] == 'john'
        assert result[0].fields['action'] == 'login'
        assert result[1].success is True
        assert result[1].fields['user'] == 'jane'

    async def test_dissect_pattern_error(
        self,
        mock_kibana_client: AsyncMock,
        sample_dissect_error_response: dict[str, Any],
    ) -> None:
        """Test dissect pattern that fails to match."""
        mock_kibana_client.simulate_ingest.return_value = sample_dissect_error_response

        result = await run_dissect_pattern_test(
            mock_kibana_client,
            'user=%{user}',
            ['invalid format'],
        )

        assert len(result) == 1
        assert result[0].success is False
        assert result[0].error is not None
        assert 'Unable to find match' in result[0].error

    async def test_dissect_pattern_empty_pattern(self, mock_kibana_client: AsyncMock) -> None:
        """Test that empty patterns raise ValueError."""
        with pytest.raises(ValueError, match='Pattern cannot be empty'):
            await run_dissect_pattern_test(mock_kibana_client, '   ', ['test'])

    async def test_dissect_pattern_empty_documents(self, mock_kibana_client: AsyncMock) -> None:
        """Test dissect with empty documents list."""
        result = await run_dissect_pattern_test(mock_kibana_client, 'pattern', [])

        assert result == []
        mock_kibana_client.simulate_ingest.assert_not_called()

    async def test_dissect_pattern_custom_field(
        self,
        mock_kibana_client: AsyncMock,
        sample_dissect_response: dict[str, Any],
    ) -> None:
        """Test dissect pattern with custom field name."""
        mock_kibana_client.simulate_ingest.return_value = sample_dissect_response

        await run_dissect_pattern_test(
            mock_kibana_client,
            'user=%{user}',
            ['user=john'],
            field='log_message',
        )

        call_args = mock_kibana_client.simulate_ingest.call_args
        pipeline = call_args.kwargs['pipeline']
        assert pipeline['processors'][0]['dissect']['field'] == 'log_message'
