"""Configuration models for different types of queries used in Kibana dashboards."""

from pydantic import Field

from dashboard_compiler.shared.config import BaseCfgModel

type QueryTypes = KqlQuery | LuceneQuery


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
