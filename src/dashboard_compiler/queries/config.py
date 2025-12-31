"""Configuration models for different types of queries used in Kibana dashboards."""

from pydantic import Field, field_validator

from dashboard_compiler.shared.config import BaseCfgModel
from dashboard_compiler.shared.model import BaseRootCfgModel

# Recursive type for nested query parts from YAML anchor expansion
type QueryPart = str | list['QueryPart']


class KqlQuery(BaseCfgModel):
    """Represents a KQL (Kibana Query Language) query configuration.

    KQL is the default query language in Kibana and provides a simplified syntax for filtering data.
    """

    kql: str = Field(...)
    """The Kibana Query Language (KQL) query string to apply."""


class LuceneQuery(BaseCfgModel):
    """Represents a Lucene query configuration.

    Lucene provides a more powerful and flexible, but less friendly, syntax for querying data compared to KQL.
    """

    lucene: str = Field(...)
    """The Lucene query string to apply."""


class ESQLQuery(BaseRootCfgModel):
    """Represents an ESQL (Elasticsearch Query Language) query configuration.

    ESQL is a powerful query language for Elasticsearch that provides a flexible syntax for filtering data.

    The query can be provided as either:
    - A string: The complete ESQL query
    - A list of strings: Query parts that will be concatenated with pipe characters (|)

    The list format supports YAML anchors for query reuse. When anchors reference arrays,
    they create nested lists which are automatically flattened before concatenation.

    Example with YAML anchors:
        .base: &base_query
          - FROM logs-*
          - WHERE @timestamp > NOW() - 1h

        query:
          - *base_query
          - STATS count = COUNT()

        # Results in: FROM logs-* | WHERE @timestamp > NOW() - 1h | STATS count = COUNT()
    """

    root: str = Field(...)

    @field_validator('root', mode='before')
    @classmethod
    def normalize_query(cls, value: QueryPart) -> str:
        """Normalize the query to a string by flattening and concatenating list elements with pipes."""
        if isinstance(value, list):
            flattened = _flatten_query_parts(value)
            return ' | '.join(flattened)
        return value


def _flatten_query_parts(parts: list[QueryPart]) -> list[str]:
    """Flatten a potentially nested list of query parts into a single list of strings.

    Args:
        parts: A list that may contain strings or nested lists of strings (arbitrarily deep).

    Returns:
        A flat list of strings.
    """
    result: list[str] = []
    for part in parts:
        if isinstance(part, list):
            result.extend(_flatten_query_parts(part))
        else:
            result.append(part)
    return result
