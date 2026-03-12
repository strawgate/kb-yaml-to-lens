"""Tests for MCP server setup."""

from unittest.mock import AsyncMock

from kb_dashboard_mcp.server import build_mcp_server


class TestBuildMcpServer:
    """Tests for build_mcp_server function."""

    async def test_build_server(self, mock_kibana_client: AsyncMock) -> None:
        """Test building the MCP server."""
        mcp = await build_mcp_server(mock_kibana_client)

        assert mcp.name == 'kb-dashboard-mcp'

        tools = await mcp.get_tools()
        tool_names = list(tools.keys())
        assert 'summarize_data_streams' in tool_names
        assert 'list_data_streams' in tool_names
        assert 'execute_esql' in tool_names
        assert 'test_grok_pattern' in tool_names
        assert 'test_dissect_pattern' in tool_names

    async def test_all_tools_have_descriptions(self, mock_kibana_client: AsyncMock) -> None:
        """Test that all tools have descriptions."""
        mcp = await build_mcp_server(mock_kibana_client)

        tools = await mcp.get_tools()
        for tool in tools.values():
            assert tool.description is not None
            assert len(tool.description) > 0
