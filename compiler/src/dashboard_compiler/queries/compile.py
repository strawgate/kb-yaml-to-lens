"""Compile dashboard queries into their Kibana view model representation."""

import json
import re

from dashboard_compiler.queries.config import KqlQuery, LuceneQuery
from dashboard_compiler.queries.types import ESQLQueryTypes, LegacyQueryTypes
from dashboard_compiler.queries.view import KbnESQLQuery, KbnQuery


def extract_index_pattern_from_esql(query: str) -> str:
    """Extract the index pattern from an ES|QL query.

    Args:
        query (str): The ES|QL query string.

    Returns:
        str: The index pattern extracted from the FROM clause.

    Raises:
        ValueError: If no index pattern can be extracted from the query.

    """
    match = re.search(r'FROM\s+([^\s|]+)', query, re.IGNORECASE)
    if match is None:
        msg = f'Could not extract index pattern from ES|QL query: {query}'
        raise ValueError(msg)
    return match.group(1)


def build_esql_index_reference(index_pattern: str, time_field: str) -> str:
    """Build the JSON-encoded index reference string for ES|QL text-based datasources.

    Args:
        index_pattern (str): The index pattern (e.g., 'logs-*').
        time_field (str): The time field name (e.g., '@timestamp').

    Returns:
        str: JSON-encoded string in the format '{"index":"logs-*","timeFieldName":"@timestamp"}'.

    """
    return json.dumps({'index': index_pattern, 'timeFieldName': time_field}, separators=(',', ':'))


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
