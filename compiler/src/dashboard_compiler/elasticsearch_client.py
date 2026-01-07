"""Elasticsearch client for sample data operations."""

from elasticsearch import AsyncElasticsearch


class ElasticsearchClient:
    """Client for interacting with Elasticsearch."""

    url: str
    username: str | None
    password: str | None
    api_key: str | None
    ssl_verify: bool
    _client: AsyncElasticsearch | None

    def __init__(
        self,
        url: str,
        *,
        username: str | None = None,
        password: str | None = None,
        api_key: str | None = None,
        ssl_verify: bool = True,
    ) -> None:
        """Initialize the Elasticsearch client.

        Args:
            url: Elasticsearch base URL (e.g., http://localhost:9200)
            username: Basic auth username (optional)
            password: Basic auth password (optional)
            api_key: API key for authentication (optional)
            ssl_verify: Whether to verify SSL certificates (default: True)

        """
        self.url = url.rstrip('/')
        self.username = username
        self.password = password
        self.api_key = api_key
        self.ssl_verify = ssl_verify
        self._client = None

    def _create_client(self) -> AsyncElasticsearch:
        """Create and configure AsyncElasticsearch client.

        Returns:
            Configured AsyncElasticsearch client

        """
        if self.api_key is not None:
            return AsyncElasticsearch(self.url, api_key=self.api_key, verify_certs=self.ssl_verify)
        if self.username is not None and self.password is not None:
            return AsyncElasticsearch(
                self.url,
                basic_auth=(self.username, self.password),
                verify_certs=self.ssl_verify,
            )
        return AsyncElasticsearch(self.url, verify_certs=self.ssl_verify)

    @property
    def client(self) -> AsyncElasticsearch:
        """Get or create the Elasticsearch client.

        Returns:
            AsyncElasticsearch client instance

        """
        if self._client is None:
            self._client = self._create_client()
        return self._client

    async def close(self) -> None:
        """Close the Elasticsearch client and release resources."""
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def __aenter__(self) -> 'ElasticsearchClient':
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager and close client."""
        await self.close()
