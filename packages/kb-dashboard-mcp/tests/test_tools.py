"""Tests for MCP tools."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from fastmcp import FastMCP

from kb_dashboard_mcp.tools.data_streams import _summarize_single_data_stream, register_data_stream_tools
from kb_dashboard_mcp.tools.esql import register_esql_tools
from kb_dashboard_mcp.tools.patterns import register_pattern_tools

if TYPE_CHECKING:
    from unittest.mock import AsyncMock


class TestDataStreamTools:
    """Tests for data stream tools."""

    @pytest.fixture
    def mcp_with_data_stream_tools(self, mock_es_client: AsyncMock) -> FastMCP:
        """Create MCP server with data stream tools registered."""
        mcp = FastMCP(name='test')
        register_data_stream_tools(mcp, mock_es_client)
        return mcp

    def test_tools_registered(self, mcp_with_data_stream_tools: FastMCP) -> None:
        """Test that data stream tools are registered."""
        tool_names = [t.name for t in mcp_with_data_stream_tools._tool_manager._tools.values()]
        assert 'summarize_data_streams' in tool_names
        assert 'list_data_streams' in tool_names


class TestEsqlTools:
    """Tests for ES|QL tools."""

    @pytest.fixture
    def mcp_with_esql_tools(self, mock_es_client: AsyncMock) -> FastMCP:
        """Create MCP server with ES|QL tools registered."""
        mcp = FastMCP(name='test')
        register_esql_tools(mcp, mock_es_client)
        return mcp

    def test_tool_registered(self, mcp_with_esql_tools: FastMCP) -> None:
        """Test that ES|QL tool is registered."""
        tool_names = [t.name for t in mcp_with_esql_tools._tool_manager._tools.values()]
        assert 'execute_esql' in tool_names


class TestPatternTools:
    """Tests for pattern testing tools."""

    @pytest.fixture
    def mcp_with_pattern_tools(self, mock_es_client: AsyncMock) -> FastMCP:
        """Create MCP server with pattern tools registered."""
        mcp = FastMCP(name='test')
        register_pattern_tools(mcp, mock_es_client)
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
        mock_es_client: AsyncMock,
        sample_esql_response: dict[str, Any],
    ) -> None:
        """Test summarizing a data stream with data."""
        mock_es_client.esql.query.return_value = sample_esql_response

        result = await _summarize_single_data_stream(mock_es_client, 'logs-test')

        assert result.data_stream == 'logs-test'
        assert len(result.fields) == 3
        assert len(result.sample_rows) == 3

    async def test_summarize_empty_data_stream(self, mock_es_client: AsyncMock) -> None:
        """Test summarizing an empty data stream."""
        mock_es_client.esql.query.return_value = {'columns': [], 'values': []}

        result = await _summarize_single_data_stream(mock_es_client, 'empty-stream')

        assert result.data_stream == 'empty-stream'
        assert len(result.fields) == 0
        assert len(result.sample_rows) == 0

    async def test_summarize_invalid_data_stream_name(self, mock_es_client: AsyncMock) -> None:
        """Test that invalid data stream names raise ValueError."""
        with pytest.raises(ValueError, match='Invalid data stream name'):
            await _summarize_single_data_stream(mock_es_client, 'invalid;name')
