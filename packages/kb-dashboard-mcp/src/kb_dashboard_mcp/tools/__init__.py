"""MCP tool implementations."""

from __future__ import annotations

from kb_dashboard_mcp.tools.data_streams import register_data_stream_tools
from kb_dashboard_mcp.tools.esql import register_esql_tools
from kb_dashboard_mcp.tools.patterns import register_pattern_tools

__all__ = ['register_data_stream_tools', 'register_esql_tools', 'register_pattern_tools']
