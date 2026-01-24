"""CLI context for sharing configuration across Click commands."""

from dataclasses import dataclass, field

from elasticsearch import AsyncElasticsearch

from dashboard_compiler.kibana_client import KibanaClient


@dataclass
class CliContext:
    """Context object for sharing clients across CLI commands.

    This dataclass holds optional pre-configured clients that are populated
    by the CLI option decorators. Each command uses only the clients it needs.
    """

    kibana_client: KibanaClient | None = field(default=None)
    """Pre-configured Kibana client, populated by @kibana_options decorator."""

    es_client: AsyncElasticsearch | None = field(default=None)
    """Pre-configured Elasticsearch client, populated by @elasticsearch_options decorator."""
