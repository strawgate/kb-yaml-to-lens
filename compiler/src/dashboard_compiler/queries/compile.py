"""Compile dashboard queries into their Kibana view model representation."""

import re

from dashboard_compiler.queries.config import KqlQuery, LuceneQuery
from dashboard_compiler.queries.types import ESQLQueryTypes, LegacyQueryTypes
from dashboard_compiler.queries.view import KbnESQLQuery, KbnQuery


def extract_index_pattern_from_esql(query: str) -> str:
    """Extract the index pattern from an ES|QL query.

    Parses the FROM clause to extract the index pattern.
    ES|QL queries start with: FROM <index-pattern> | ...

    Args:
        query: The ES|QL query string

    Returns:
        The extracted index pattern (e.g., "logs-*", "metrics-*")

    Raises:
        ValueError: If no valid FROM clause is found

    """
    # Remove comments and normalize whitespace
    # ES|QL comments are // or /* */
    query_cleaned = re.sub(r'//.*?$', '', query, flags=re.MULTILINE)
    query_cleaned = re.sub(r'/\*.*?\*/', '', query_cleaned, flags=re.DOTALL)

    # Match FROM clause - case insensitive, handles whitespace and multiline
    # Pattern stops at: pipe (|), METADATA keyword, or end of string
    # Captures the index pattern between FROM and the terminator
    pattern = r'\bFROM\s+([^\s|]+(?:\s*,\s*[^\s|]+)*)'
    match = re.search(pattern, query_cleaned, re.IGNORECASE | re.MULTILINE)

    if match is None:
        msg = f'No valid FROM clause found in ES|QL query: {query[:100]}...'
        raise ValueError(msg)

    # Extract and clean the index pattern
    index_pattern = match.group(1).strip()

    # Handle multiple indices separated by commas (remove extra whitespace)
    return re.sub(r'\s*,\s*', ',', index_pattern)


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
