"""ES|QL query executor using Kibana's console proxy API."""

import logging
from typing import Any
from urllib.parse import urlencode

import aiohttp

logger = logging.getLogger(__name__)

HTTP_OK = 200


class EsqlExecutor:
    """Execute ES|QL queries via Kibana's console proxy API."""

    kibana_url: str
    username: str | None
    password: str | None
    api_key: str | None
    ssl_verify: bool

    def __init__(
        self,
        kibana_url: str,
        *,
        username: str | None = None,
        password: str | None = None,
        api_key: str | None = None,
        ssl_verify: bool = True,
    ) -> None:
        """Initialize the ES|QL executor.

        Args:
            kibana_url: Base Kibana URL (e.g., http://localhost:5601)
            username: Basic auth username (optional)
            password: Basic auth password (optional)
            api_key: API key for authentication (optional)
            ssl_verify: Whether to verify SSL certificates (default: True)

        """
        self.kibana_url = kibana_url.rstrip('/')
        self.username = username
        self.password = password
        self.api_key = api_key
        self.ssl_verify = ssl_verify

    def _get_auth_headers_and_auth(self) -> tuple[dict[str, str], aiohttp.BasicAuth | None]:
        """Get authentication headers and auth object for Kibana API requests.

        Returns:
            Tuple of (headers dict with kbn-xsrf and optional Authorization, BasicAuth or None)

        """
        headers = {
            'kbn-xsrf': 'true',
            'Content-Type': 'application/json',
        }
        if self.api_key is not None and len(self.api_key) > 0:
            headers['Authorization'] = f'ApiKey {self.api_key}'

        auth = None
        if self.username is not None and len(self.username) > 0 and self.password is not None and len(self.password) > 0:
            auth = aiohttp.BasicAuth(self.username, self.password)

        return headers, auth

    async def execute(self, query: str) -> dict[str, Any]:
        """Execute an ES|QL query via Kibana's console proxy API.

        Args:
            query: The ES|QL query string to execute

        Returns:
            Dictionary with query results:
                - columns: List of column definitions [{name, type}, ...]
                - values: List of row values [[val1, val2, ...], ...]
                - took: Query execution time in milliseconds (if available)

        Raises:
            aiohttp.ClientError: If the request fails
            ValueError: If the response is not valid

        """
        # Build the proxy URL for ES|QL queries
        # Kibana's console proxy forwards requests to Elasticsearch
        proxy_params = urlencode({'path': '/_query', 'method': 'POST'})
        url = f'{self.kibana_url}/api/console/proxy?{proxy_params}'

        headers, auth = self._get_auth_headers_and_auth()

        # Build the ES|QL request body
        request_body = {
            'query': query,
            'format': 'json',
        }

        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(ssl=self.ssl_verify)
        async with (
            aiohttp.ClientSession(connector=connector, timeout=timeout) as session,
            session.post(url, headers=headers, auth=auth, json=request_body) as response,
        ):
            if response.status != HTTP_OK:
                error_text = await response.text()
                logger.error(f'ES|QL query failed with status {response.status}: {error_text[:500]}')
                msg = f'ES|QL query failed (HTTP {response.status}): {error_text[:200]}'
                raise ValueError(msg)

            result = await response.json()  # pyright: ignore[reportAny]

            # Handle ES|QL response format
            # ES|QL returns: {columns: [{name, type}], values: [[...]]}
            if 'error' in result:
                error_info = result['error']  # pyright: ignore[reportAny]
                error_msg = (
                    error_info.get('reason', str(error_info))  # pyright: ignore[reportAny]
                    if isinstance(error_info, dict)
                    else str(error_info)
                )
                msg = f'ES|QL query error: {error_msg}'
                raise ValueError(msg)

            return {
                'columns': result.get('columns', []),  # pyright: ignore[reportAny]
                'values': result.get('values', []),  # pyright: ignore[reportAny]
                'took': result.get('took'),  # pyright: ignore[reportAny]
                'is_partial': result.get('is_partial', False),  # pyright: ignore[reportAny]
            }
