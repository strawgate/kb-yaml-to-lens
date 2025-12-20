"""Kibana client for uploading dashboards via the Saved Objects API."""

import logging
from pathlib import Path
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


class KibanaClient:
    """Client for interacting with Kibana's Saved Objects API."""

    def __init__(
        self,
        url: str,
        username: str | None = None,
        password: str | None = None,
        api_key: str | None = None,
    ) -> None:
        """Initialize the Kibana client.

        Args:
            url: Base Kibana URL (e.g., http://localhost:5601)
            username: Basic auth username (optional)
            password: Basic auth password (optional)
            api_key: API key for authentication (optional)

        """
        self.url = url.rstrip('/')
        self.username = username
        self.password = password
        self.api_key = api_key

    async def upload_ndjson(
        self,
        ndjson_path: Path,
        overwrite: bool = True,
    ) -> dict[str, Any]:
        """Upload an NDJSON file to Kibana using the Saved Objects Import API.

        Args:
            ndjson_path: Path to the NDJSON file containing saved objects
            overwrite: Whether to overwrite existing objects with the same IDs

        Returns:
            Response dict from Kibana API containing success status and results

        Raises:
            aiohttp.ClientError: If the request fails

        """
        endpoint = f'{self.url}/api/saved_objects/_import'
        if overwrite:
            endpoint += '?overwrite=true'

        headers = {'kbn-xsrf': 'true'}
        if self.api_key:
            headers['Authorization'] = f'ApiKey {self.api_key}'

        auth = None
        if self.username and self.password:
            auth = aiohttp.BasicAuth(self.username, self.password)

        async with aiohttp.ClientSession() as session:
            with ndjson_path.open('rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename=ndjson_path.name, content_type='application/ndjson')

                async with session.post(endpoint, data=data, headers=headers, auth=auth) as response:
                    response.raise_for_status()
                    return await response.json()

    def get_dashboard_url(self, dashboard_id: str) -> str:
        """Get the URL for a specific dashboard.

        Args:
            dashboard_id: The ID of the dashboard

        Returns:
            Full URL to the dashboard in Kibana

        """
        return f'{self.url}/app/dashboards#{dashboard_id}'
