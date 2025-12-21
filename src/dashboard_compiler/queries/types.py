from typing import Annotated

from pydantic import Discriminator, Tag

from dashboard_compiler.queries.config import ESQLQuery, KqlQuery, LuceneQuery


def get_query_type(v: dict | object) -> str:  # noqa: PLR0911
    """Extract query type for discriminated union validation.

    Args:
        v: Either a dict (during validation) or a query instance.

    Returns:
        str: The query type identifier ('kql', 'lucene', or 'esql').

    """
    if isinstance(v, dict):
        if 'kql' in v:
            return 'kql'
        if 'lucene' in v:
            return 'lucene'
        if 'root' in v:
            return 'esql'
        return 'unknown'
    if hasattr(v, 'kql'):
        return 'kql'
    if hasattr(v, 'lucene'):
        return 'lucene'
    if hasattr(v, 'root'):
        return 'esql'
    return 'unknown'


type LegacyQueryTypes = Annotated[
    Annotated[KqlQuery, Tag('kql')] | Annotated[LuceneQuery, Tag('lucene')],
    Discriminator(get_query_type),
]

type ESQLQueryTypes = ESQLQuery

type QueryTypes = Annotated[
    Annotated[KqlQuery, Tag('kql')] | Annotated[LuceneQuery, Tag('lucene')] | Annotated[ESQLQuery, Tag('esql')],
    Discriminator(get_query_type),
]
