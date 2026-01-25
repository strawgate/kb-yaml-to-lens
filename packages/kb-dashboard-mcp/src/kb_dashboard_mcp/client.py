"""Kibana client for proxying Elasticsearch requests."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, Field

HTTP_OK = 200


class KibanaClientConfig(BaseModel):
    """Configuration for KibanaClient."""

    kibana_url: str = Field(description='Kibana server URL (e.g., https://kibana.example.com:5601)')
    api_key: str | None = Field(default=None, description='API key for authentication')
    username: str | None = Field(default=None, description='Username for basic authentication')
    password: str | None = Field(default=None, description='Password for basic authentication')
    verify_ssl: bool = Field(default=True, description='Whether to verify SSL certificates')


class KibanaClient:
    """Async client for Elasticsearch operations through Kibana's proxy API.

    This client routes all Elasticsearch requests through Kibana's /api/console/proxy
    endpoint, which enables additional functionality like dashboard screenshots and
    simplifies authentication by leveraging Kibana's auth layer.
    """

    _config: KibanaClientConfig
    _base_url: str
    _client: httpx.AsyncClient | None

    def __init__(self, config: KibanaClientConfig) -> None:
        """Initialize the Kibana client.

        Args:
            config: Client configuration including URL and credentials.
        """
        self._config = config
        self._base_url = config.kibana_url.rstrip('/')
        self._client = None

    def _get_auth_headers(self) -> dict[str, str]:
        """Build authentication headers."""
        headers: dict[str, str] = {
            'kbn-xsrf': 'true',
            'Content-Type': 'application/json',
        }

        if self._config.api_key is not None:
            headers['Authorization'] = f'ApiKey {self._config.api_key}'
        elif self._config.username is not None and self._config.password is not None:
            import base64

            credentials = f'{self._config.username}:{self._config.password}'
            encoded = base64.b64encode(credentials.encode()).decode()
            headers['Authorization'] = f'Basic {encoded}'

        return headers

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the httpx client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                verify=self._config.verify_ssl,
                timeout=httpx.Timeout(30.0),
                headers=self._get_auth_headers(),
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def ping(self) -> bool:
        """Check connectivity to Kibana.

        Returns:
            True if Kibana is reachable, False otherwise.
        """
        client = await self._get_client()
        try:
            response = await client.get(f'{self._base_url}/api/status')
        except httpx.HTTPError:
            return False
        else:
            return response.status_code == HTTP_OK

    async def _es_request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an Elasticsearch request through Kibana's proxy.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            path: Elasticsearch API path (e.g., /_search, /index/_doc/id).
            body: Optional request body.

        Returns:
            Response from Elasticsearch.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        client = await self._get_client()

        proxy_url = f'{self._base_url}/api/console/proxy'
        params = {
            'path': path,
            'method': method,
        }

        if body is not None:
            response = await client.post(proxy_url, params=params, json=body)
        else:
            response = await client.post(proxy_url, params=params)

        response.raise_for_status()
        return response.json()

    async def esql_query(
        self,
        query: str,
        format_type: str = 'json',
        columnar: bool = False,
    ) -> dict[str, Any]:
        """Execute an ES|QL query.

        Args:
            query: The ES|QL query string.
            format_type: Response format (default: json).
            columnar: Whether to return results in columnar format.

        Returns:
            Query results with columns and values.
        """
        body: dict[str, Any] = {'query': query}
        if columnar:
            body['columnar'] = True

        return await self._es_request('POST', f'/_query?format={format_type}', body)

    async def get_data_streams(self, name: str | None = None) -> dict[str, Any]:
        """Get data stream information.

        Args:
            name: Optional name pattern to filter data streams.

        Returns:
            Data stream information.
        """
        path = '/_data_stream'
        if name is not None:
            path = f'/_data_stream/{name}'

        return await self._es_request('GET', path)

    async def test_grok_pattern(
        self,
        grok_pattern: str,
        text: list[str],
        pattern_definitions: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Test a grok pattern against sample text.

        Args:
            grok_pattern: The grok pattern to test.
            text: Sample text lines to match against.
            pattern_definitions: Optional custom pattern definitions.

        Returns:
            Match results.
        """
        body: dict[str, Any] = {
            'grok_pattern': grok_pattern,
            'text': text,
        }
        if pattern_definitions is not None:
            body['pattern_definitions'] = pattern_definitions

        return await self._es_request('POST', '/_text_structure/test_grok_pattern', body)

    async def simulate_ingest(
        self,
        pipeline: dict[str, Any],
        docs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Simulate an ingest pipeline.

        Args:
            pipeline: The pipeline configuration.
            docs: Documents to simulate.

        Returns:
            Simulation results.
        """
        body = {
            'pipeline': pipeline,
            'docs': docs,
        }
        return await self._es_request('POST', '/_ingest/pipeline/_simulate', body)
