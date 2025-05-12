"""Compile dashboard queries into their Kibana view model representation."""

from dashboard_compiler.queries.config import KqlQuery, LuceneQuery
from dashboard_compiler.queries.types import ESQLQueryTypes, LegacyQueryTypes
from dashboard_compiler.queries.view import KbnESQLQuery, KbnQuery
from dashboard_compiler.shared.errors import UnexpectedTypeError


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

    if isinstance(query, LuceneQuery):
        return KbnQuery(
            query=query.lucene,
            language='lucene',
        )

    raise UnexpectedTypeError(LegacyQueryTypes, type(query))
