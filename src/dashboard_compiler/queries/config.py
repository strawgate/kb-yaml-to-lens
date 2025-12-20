"""Configuration models for different types of queries used in Kibana dashboards."""

from pydantic import Field, field_validator

from dashboard_compiler.shared.config import BaseCfgModel
from dashboard_compiler.shared.model import BaseRootCfgModel


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

    This enables using YAML anchors to share parts of ESQL queries across panels.
    """

    root: str = Field(...)

    @field_validator('root', mode='before')
    @classmethod
    def normalize_query(cls, value: str | list[str]) -> str:
        """Normalize the query to a string by concatenating list elements with pipes."""
        if isinstance(value, list):
            # Join array elements with " | "
            return ' | '.join(value)
        return value
