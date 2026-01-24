"""Decompile Kibana queries back to config models."""

from dashboard_compiler.queries.config import KqlQuery, LuceneQuery
from dashboard_compiler.queries.types import LegacyQueryTypes
from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.shared.decompile_context import DecompileContext


def decompile_query(
    kbn_query: KbnQuery,
    *,
    context: DecompileContext,
) -> LegacyQueryTypes | None:
    """Decompile a Kibana query to config model.

    Args:
        kbn_query: The Kibana query view model.
        context: Decompilation context for warnings.

    Returns:
        The decompiled query config model, or None if empty.

    """
    # Empty query returns None
    if not kbn_query.query or len(str(kbn_query.query).strip()) == 0:
        return None

    if kbn_query.language == 'kuery':
        return KqlQuery(kql=str(kbn_query.query))
    if kbn_query.language == 'lucene':
        return LuceneQuery(lucene=str(kbn_query.query))
    context.warn(f'Unknown query language: {kbn_query.language}')
    # Default to KQL
    return KqlQuery(kql=str(kbn_query.query))
