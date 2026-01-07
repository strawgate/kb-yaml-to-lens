"""CLI context for sharing configuration across Click commands."""

from elasticsearch import AsyncElasticsearch

from dashboard_compiler.kibana_client import KibanaClient


class CliContext:
    """Context object for sharing client configuration across CLI commands."""

    kibana_url: str | None
    kibana_username: str | None
    kibana_password: str | None
    kibana_api_key: str | None
    kibana_space_id: str | None
    kibana_ssl_verify: bool
    es_url: str | None
    es_username: str | None
    es_password: str | None
    es_api_key: str | None
    es_ssl_verify: bool

    def __init__(self) -> None:
        """Initialize empty context."""
        self.kibana_url = None
        self.kibana_username = None
        self.kibana_password = None
        self.kibana_api_key = None
        self.kibana_space_id = None
        self.kibana_ssl_verify = True
        self.es_url = None
        self.es_username = None
        self.es_password = None
        self.es_api_key = None
        self.es_ssl_verify = True

    def create_kibana_client(self) -> KibanaClient:
        """Create a KibanaClient from stored configuration.

        Returns:
            Configured KibanaClient instance

        Raises:
            ValueError: If required Kibana configuration is missing

        """
        if self.kibana_url is None:
            msg = 'Kibana URL is required'
            raise ValueError(msg)

        return KibanaClient(
            url=self.kibana_url,
            username=self.kibana_username,
            password=self.kibana_password,
            api_key=self.kibana_api_key,
            space_id=self.kibana_space_id,
            ssl_verify=self.kibana_ssl_verify,
        )

    def create_elasticsearch_client(self) -> AsyncElasticsearch:
        """Create an AsyncElasticsearch client from stored configuration.

        Returns:
            Configured AsyncElasticsearch instance

        Raises:
            ValueError: If required Elasticsearch configuration is missing

        """
        if self.es_url is None:
            msg = 'Elasticsearch URL is required'
            raise ValueError(msg)

        # API key takes priority
        if self.es_api_key is not None:
            return AsyncElasticsearch(self.es_url, api_key=self.es_api_key, verify_certs=self.es_ssl_verify)

        # Basic auth
        if self.es_username is not None and self.es_password is not None:
            return AsyncElasticsearch(
                self.es_url,
                basic_auth=(self.es_username, self.es_password),
                verify_certs=self.es_ssl_verify,
            )

        # No auth
        return AsyncElasticsearch(self.es_url, verify_certs=self.es_ssl_verify)
