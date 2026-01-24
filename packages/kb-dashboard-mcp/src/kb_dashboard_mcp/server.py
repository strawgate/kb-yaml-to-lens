"""MCP server setup and tool registration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastmcp import FastMCP

from kb_dashboard_mcp.tools import register_data_stream_tools, register_esql_tools, register_pattern_tools

if TYPE_CHECKING:
    from elasticsearch import AsyncElasticsearch


async def build_mcp_server(es: AsyncElasticsearch) -> FastMCP:
    """Build and configure the MCP server with all tools.

    Args:
        es: AsyncElasticsearch client for cluster operations.

    Returns:
        Configured FastMCP server ready to run.
    """
    mcp = FastMCP(name='kb-dashboard-mcp')

    register_data_stream_tools(mcp, es)
    register_esql_tools(mcp, es)
    register_pattern_tools(mcp, es)

    return mcp
