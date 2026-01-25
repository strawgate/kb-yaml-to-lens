"""MCP server for Kibana dashboard building with Elasticsearch data exploration."""

from __future__ import annotations

from kb_dashboard_mcp.client import KibanaClient, KibanaClientConfig

__version__ = '0.1.0'

__all__ = ['KibanaClient', 'KibanaClientConfig', '__version__']
