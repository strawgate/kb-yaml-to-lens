"""Compile dashboard queries into their Kibana view model representation."""

import json
import re

from dashboard_compiler.queries.config import KqlQuery, LuceneQuery
from dashboard_compiler.queries.types import ESQLQueryTypes, LegacyQueryTypes
from dashboard_compiler.queries.view import KbnESQLQuery, KbnQuery


def extract_index_from_esql(query_str: str) -> str:
    """Extract index pattern from ESQL query and format as JSON string.

    Args:
        query_str: The ESQL query string

    Returns:
        JSON string containing index and timeFieldName

    Example:
        >>> extract_index_from_esql("FROM logs-* | STATS count = COUNT()")
        '{"index":"logs-*","timeFieldName":"@timestamp"}'

    """
    match = re.search(r'FROM\s+([^\s|]+)', query_str, re.IGNORECASE)
    index_pattern = '*' if match is None else match.group(1).strip()

    index_obj = {'index': index_pattern, 'timeFieldName': '@timestamp'}

    return json.dumps(index_obj, separators=(',', ':'))


def compile_esql_query(query: ESQLQueryTypes) -> KbnESQLQuery:
    """Compile an ESQL query into its Kibana view model representation."""
    return KbnESQLQuery(
        esql=query.root,
    )


def compile_nonesql_query(query: LegacyQueryTypes) -> KbnQuery:
    """Compile the query of a Dashboard object into its Kibana view model representation.

    Args:
        query (LegacyQueryTypes): The query object to compile.

    Returns:
        KbnQuery: The compiled Kibana query view model.

    Raises:
        UnexpectedTypeError: If the query type is not recognized.

    """
    if isinstance(query, KqlQuery):
        return KbnQuery(
            query=query.kql,
            language='kuery',
        )

    if isinstance(query, LuceneQuery):  # pyright: ignore[reportUnnecessaryIsInstance]
        return KbnQuery(
            query=query.lucene,
            language='lucene',
        )

    # Explicit check to satisfy exhaustive checking pattern
    msg = f'Unknown query type: {type(query).__name__}'
    raise TypeError(msg)  # pyright: ignore[reportUnreachable]
