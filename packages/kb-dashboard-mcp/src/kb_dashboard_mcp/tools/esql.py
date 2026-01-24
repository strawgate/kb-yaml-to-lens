"""ES|QL query execution tool."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

from fastmcp.tools import Tool

from kb_dashboard_mcp.models import EsqlQueryResult

if TYPE_CHECKING:
    from elasticsearch import AsyncElasticsearch
    from fastmcp import FastMCP


def register_esql_tools(mcp: FastMCP, es: AsyncElasticsearch) -> None:
    """Register ES|QL query tools with the MCP server."""

    async def execute_esql(
        query: Annotated[str, 'The ES|QL query to execute'],
        columnar: Annotated[bool, 'Return results in columnar format'] = False,
    ) -> EsqlQueryResult:
        """Execute an ES|QL query against the Elasticsearch cluster.

        Returns query results with column definitions and values.
        """
        if len(query.strip()) == 0:
            msg = 'Query cannot be empty'
            raise ValueError(msg)

        result = await es.esql.query(query=query, format='json', columnar=columnar)

        columns: list[dict[str, str]] = result.get('columns', [])
        values: list[list[Any]] = result.get('values', [])

        return EsqlQueryResult(
            columns=columns,
            values=values,
            is_columnar=columnar,
        )

    mcp.add_tool(Tool.from_function(execute_esql, tags={'esql', 'query'}))
