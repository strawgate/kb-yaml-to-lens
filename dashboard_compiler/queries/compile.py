"""Compile dashboard queries into their Kibana view model representation."""

from dashboard_compiler.queries.config import KqlQuery, LuceneQuery, QueryTypes
from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.shared.errors import UnexpectedTypeError


def compile_query(query: QueryTypes) -> KbnQuery:
    """Compile the query of a Dashboard object into its Kibana view model representation.

    Args:
        query (QueryTypes): The query object to compile.

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

    raise UnexpectedTypeError(QueryTypes, type(query))
