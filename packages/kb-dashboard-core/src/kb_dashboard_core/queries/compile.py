"""Compile dashboard queries into their Kibana view model representation."""

from kb_dashboard_core.queries.config import KqlQuery, LuceneQuery
from kb_dashboard_core.queries.types import ESQLQueryTypes, LegacyQueryTypes
from kb_dashboard_core.queries.view import KbnESQLQuery, KbnQuery


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
