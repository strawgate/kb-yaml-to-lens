"""MCP server setup and tool registration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastmcp import FastMCP

from kb_dashboard_mcp.tools import register_data_stream_tools, register_esql_tools, register_pattern_tools

if TYPE_CHECKING:
    from kb_dashboard_tools.kibana_client import KibanaClient


async def build_mcp_server(client: KibanaClient) -> FastMCP:
    """Build and configure the MCP server with all tools.

    Args:
        client: KibanaClient for cluster operations.

    Returns:
        Configured FastMCP server ready to run.
    """
    mcp = FastMCP(name='kb-dashboard-mcp')

    register_data_stream_tools(mcp, client)
    register_esql_tools(mcp, client)
    register_pattern_tools(mcp, client)

    return mcp
