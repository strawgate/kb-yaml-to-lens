"""Compile dashboard queries into their Kibana view model representation."""

import re

from dashboard_compiler.queries.config import KqlQuery, LuceneQuery
from dashboard_compiler.queries.types import ESQLQueryTypes, LegacyQueryTypes
from dashboard_compiler.queries.view import KbnESQLQuery, KbnQuery


def extract_index_pattern_from_esql(query: ESQLQueryTypes) -> str | None:
    """Extract the index pattern from an ES|QL query.

    Args:
        query: The ES|QL query object

    Returns:
        The index pattern (e.g., "logs-*") or None if not found
    """
    # ES|QL queries start with FROM <index-pattern>
    # Extract the first index pattern after FROM
    match = re.search(r'FROM\s+([^\s|]+)', query.root, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


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
