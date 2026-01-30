"""ES|QL query execution tool."""

from typing import Annotated, Any, cast

from fastmcp import FastMCP
from fastmcp.tools import Tool

from kb_dashboard_mcp.models import EsqlQueryResult
from kb_dashboard_tools.kibana_client import KibanaClient


async def execute_esql(
    client: KibanaClient,
    query: str,
    columnar: bool = False,
) -> EsqlQueryResult:
    """Execute an ES|QL query against the Elasticsearch cluster.

    Args:
        client: KibanaClient instance.
        query: The ES|QL query to execute.
        columnar: Return results in columnar format.

    Returns:
        Query results with column definitions and values.

    Raises:
        ValueError: If the query is empty.
    """
    if len(query.strip()) == 0:
        msg = 'Query cannot be empty'
        raise ValueError(msg)

    result = await client.esql_query_raw(query=query, columnar=columnar)

    # ES|QL API returns dynamic JSON - cast to expected structure
    columns = cast('list[dict[str, str]]', result.get('columns', []))
    values = cast('list[list[Any]]', result.get('values', []))

    return EsqlQueryResult(
        columns=columns,
        values=values,
        is_columnar=columnar,
    )


def register_esql_tools(mcp: FastMCP, client: KibanaClient) -> None:
    """Register ES|QL query tools with the MCP server.

    Args:
        mcp: FastMCP server instance.
        client: KibanaClient instance.
    """

    async def _execute_esql(
        query: Annotated[str, 'The ES|QL query to execute'],
        columnar: Annotated[bool, 'Return results in columnar format'] = False,
    ) -> EsqlQueryResult:
        """Execute an ES|QL query against the Elasticsearch cluster.

        Returns query results with column definitions and values.
        """
        return await execute_esql(client, query, columnar)

    _ = mcp.add_tool(Tool.from_function(_execute_esql, name='execute_esql', tags={'esql', 'query'}))
