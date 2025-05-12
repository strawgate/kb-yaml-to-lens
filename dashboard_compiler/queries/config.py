"""Configuration models for different types of queries used in Kibana dashboards."""

from pydantic import Field

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
    """

    root: str = Field(...)
