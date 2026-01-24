"""Tests for MCP server setup."""

from __future__ import annotations

from typing import TYPE_CHECKING

from kb_dashboard_mcp.server import build_mcp_server

if TYPE_CHECKING:
    from unittest.mock import AsyncMock


class TestBuildMcpServer:
    """Tests for build_mcp_server function."""

    async def test_build_server(self, mock_es_client: AsyncMock) -> None:
        """Test building the MCP server."""
        mcp = await build_mcp_server(mock_es_client)

        assert mcp.name == 'kb-dashboard-mcp'

        tool_names = [t.name for t in mcp._tool_manager._tools.values()]
        assert 'summarize_data_streams' in tool_names
        assert 'list_data_streams' in tool_names
        assert 'execute_esql' in tool_names
        assert 'test_grok_pattern' in tool_names
        assert 'test_dissect_pattern' in tool_names

    async def test_all_tools_have_descriptions(self, mock_es_client: AsyncMock) -> None:
        """Test that all tools have descriptions."""
        mcp = await build_mcp_server(mock_es_client)

        for tool in mcp._tool_manager._tools.values():
            assert tool.description is not None
            assert len(tool.description) > 0
