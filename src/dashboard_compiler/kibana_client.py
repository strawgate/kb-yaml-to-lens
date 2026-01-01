"""Kibana client for uploading dashboards via the Saved Objects API."""

import asyncio
import logging
from pathlib import Path
from typing import Any, ClassVar, TypedDict

import aiohttp
import prison
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

HTTP_OK = 200
HTTP_SERVICE_UNAVAILABLE = 503


class _JobParamsLayout(TypedDict):
    id: str
    dimensions: dict[str, int]


class _JobParams(TypedDict):
    layout: _JobParamsLayout
    browserTimezone: str
    locatorParams: dict[str, Any]


class SavedObjectResult(BaseModel):
    """Represents a single saved object result from Kibana API."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    id: str
    destination_id: str | None = Field(default=None, validation_alias='destinationId')
    type: str


class SavedObjectError(BaseModel):
    """Represents an error from Kibana saved objects API."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow', populate_by_name=True)

    error: dict[str, Any] | None = None
    message: str | None = None
    status_code: int | None = Field(default=None, alias='statusCode')


class KibanaSavedObjectsResponse(BaseModel):
    """Response from Kibana saved objects import API."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow', populate_by_name=True)

    success: bool = Field(default=False, description='Whether the import was successful')
    success_count: int = Field(default=0, alias='successCount', description='Number of successfully imported objects')
    success_results: list[SavedObjectResult] = Field(
        default_factory=list, alias='successResults', description='List of successfully imported objects'
    )
    errors: list[SavedObjectError] = Field(default_factory=list, description='List of errors encountered during import')


class KibanaReportingJobResponse(BaseModel):
    """Response from Kibana reporting job creation API."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    path: str = Field(..., description='Path to poll for job completion')


class KibanaClient:
    """Client for interacting with Kibana's Saved Objects API."""

    url: str
    username: str | None
    password: str | None
    api_key: str | None
    ssl_verify: bool

    def __init__(
        self,
        url: str,
        *,
        username: str | None = None,
        password: str | None = None,
        api_key: str | None = None,
        ssl_verify: bool = True,
    ) -> None:
        """Initialize the Kibana client.

        Args:
            url: Base Kibana URL (e.g., http://localhost:5601)
            username: Basic auth username (optional)
            password: Basic auth password (optional)
            api_key: API key for authentication (optional)
            ssl_verify: Whether to verify SSL certificates (default: True). Set to False for self-signed certificates.

        """
        self.url = url.rstrip('/')
        self.username = username
        self.password = password
        self.api_key = api_key
        self.ssl_verify = ssl_verify

    def _get_auth_headers_and_auth(self) -> tuple[dict[str, str], aiohttp.BasicAuth | None]:
        """Get authentication headers and auth object for Kibana API requests.

        Returns:
            Tuple of (headers dict with kbn-xsrf and optional Authorization, BasicAuth or None)

        """
        headers = {'kbn-xsrf': 'true'}
        if self.api_key:
            headers['Authorization'] = f'ApiKey {self.api_key}'

        auth = None
        if self.username and self.password:
            auth = aiohttp.BasicAuth(self.username, self.password)

        return headers, auth

    async def upload_ndjson(
        self,
        ndjson_data: Path | str,
        overwrite: bool = True,
    ) -> KibanaSavedObjectsResponse:
        """Upload NDJSON data to Kibana using the Saved Objects Import API.

        Args:
            ndjson_data: Either a Path to an NDJSON file or a string containing NDJSON content
            overwrite: Whether to overwrite existing objects with the same IDs

        Returns:
            Pydantic model with parsed Kibana API response containing success status and results

        Raises:
            aiohttp.ClientError: If the request fails

        """
        endpoint = f'{self.url}/api/saved_objects/_import'
        if overwrite:
            endpoint += '?overwrite=true'

        headers, auth = self._get_auth_headers_and_auth()

        connector = aiohttp.TCPConnector(ssl=self.ssl_verify)
        async with aiohttp.ClientSession(connector=connector) as session:
            data = aiohttp.FormData()

            if isinstance(ndjson_data, Path):
                with ndjson_data.open('rb') as f:
                    content = f.read()
                data.add_field('file', content, filename=ndjson_data.name, content_type='application/ndjson')
            else:
                data.add_field('file', ndjson_data.encode('utf-8'), filename='dashboard.ndjson', content_type='application/ndjson')

            async with session.post(endpoint, data=data, headers=headers, auth=auth) as response:
                response.raise_for_status()
                json_response = await response.json()  # pyright: ignore[reportAny]
                return KibanaSavedObjectsResponse.model_validate(json_response)

    def get_dashboard_url(self, dashboard_id: str) -> str:
        """Get the URL for a specific dashboard.

        Args:
            dashboard_id: The ID of the dashboard

        Returns:
            Full URL to the dashboard in Kibana

        """
        return f'{self.url}/app/dashboards#/view/{dashboard_id}'

    async def generate_screenshot(  # noqa: PLR0913
        self,
        dashboard_id: str,
        time_from: str | None = None,
        time_to: str | None = None,
        width: int = 1920,
        height: int = 1080,
        browser_timezone: str = 'UTC',
    ) -> str:
        """Generate a PNG screenshot of a dashboard using Kibana Reporting API.

        Args:
            dashboard_id: The dashboard ID to screenshot
            time_from: Optional start time for the dashboard time range (ISO 8601 format)
            time_to: Optional end time for the dashboard time range (ISO 8601 format)
            width: Screenshot width in pixels (default: 1920)
            height: Screenshot height in pixels (default: 1080)
            browser_timezone: Timezone for the screenshot (default: UTC)

        Returns:
            Job path for downloading the screenshot

        Raises:
            aiohttp.ClientError: If the request fails

        """
        locator_params: dict[str, Any] = {
            'id': 'DASHBOARD_APP_LOCATOR',
            'params': {
                'dashboardId': dashboard_id,
                'useHash': False,
                'viewMode': 'view',
                'preserveSavedFilters': True,
            },
        }

        if time_from or time_to:
            locator_params['params']['timeRange'] = {
                'from': time_from or 'now-15m',
                'to': time_to or 'now',
            }

        job_params: _JobParams = {
            'layout': {
                'id': 'preserve_layout',
                'dimensions': {
                    'width': width,
                    'height': height,
                },
            },
            'browserTimezone': browser_timezone,
            'locatorParams': locator_params,
        }

        rison_result = prison.dumps(job_params)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        if not isinstance(rison_result, str):
            msg = f'prison.dumps() returned {type(rison_result).__name__}, expected str'  # pyright: ignore[reportUnknownArgumentType]
            raise TypeError(msg)

        endpoint = f'{self.url}/api/reporting/generate/pngV2'
        params: dict[str, str] = {'jobParams': rison_result}

        headers, auth = self._get_auth_headers_and_auth()

        connector = aiohttp.TCPConnector(ssl=self.ssl_verify)
        async with (
            aiohttp.ClientSession(connector=connector) as session,
            session.post(endpoint, params=params, headers=headers, auth=auth) as response,
        ):
            response.raise_for_status()
            json_response = await response.json()  # pyright: ignore[reportAny]
            job_response = KibanaReportingJobResponse.model_validate(json_response)
            return job_response.path

    async def wait_for_job_completion(
        self,
        job_path: str,
        timeout_seconds: int = 300,
        poll_interval: int = 2,
    ) -> bytes:
        """Poll a reporting job until completion and download the result.

        Args:
            job_path: The reporting job path returned from generate_screenshot
            timeout_seconds: Maximum seconds to wait (default: 300)
            poll_interval: Seconds between polls (default: 2)

        Returns:
            PNG screenshot data as bytes

        Raises:
            TimeoutError: If job doesn't complete within timeout
            aiohttp.ClientError: If the request fails

        """
        endpoint = f'{self.url}{job_path}'

        headers, auth = self._get_auth_headers_and_auth()

        try:
            async with asyncio.timeout(timeout_seconds):
                connector = aiohttp.TCPConnector(ssl=self.ssl_verify)
                async with aiohttp.ClientSession(connector=connector) as session:
                    while True:
                        async with session.get(endpoint, headers=headers, auth=auth) as response:
                            if response.status == HTTP_OK:
                                content_type = response.headers.get('Content-Type', '')
                                if 'image/png' in content_type:
                                    return await response.read()
                                body = await response.text()
                                msg = (
                                    f'Unexpected response from Kibana (status {response.status}, content-type {content_type}): {body[:200]}'
                                )
                                raise ValueError(msg)

                            if response.status == HTTP_SERVICE_UNAVAILABLE:
                                pass
                            else:
                                response.raise_for_status()

                        await asyncio.sleep(poll_interval)
        except TimeoutError as e:
            msg = f'Screenshot generation timed out after {timeout_seconds} seconds'
            raise TimeoutError(msg) from e

    async def download_screenshot(  # noqa: PLR0913
        self,
        dashboard_id: str,
        output_path: Path,
        time_from: str | None = None,
        time_to: str | None = None,
        width: int = 1920,
        height: int = 1080,
        browser_timezone: str = 'UTC',
        timeout_seconds: int = 300,
    ) -> None:
        """Generate and download a screenshot of a dashboard to a file.

        This is a convenience method that combines generate_screenshot and wait_for_job_completion.

        Args:
            dashboard_id: The dashboard ID to screenshot
            output_path: Local file path to save the PNG
            time_from: Optional start time for the dashboard time range (ISO 8601 format)
            time_to: Optional end time for the dashboard time range (ISO 8601 format)
            width: Screenshot width in pixels (default: 1920)
            height: Screenshot height in pixels (default: 1080)
            browser_timezone: Timezone for the screenshot (default: UTC)
            timeout_seconds: Maximum seconds to wait for screenshot generation (default: 300)

        Raises:
            aiohttp.ClientError: If the request fails
            TimeoutError: If screenshot generation times out

        """
        job_path = await self.generate_screenshot(
            dashboard_id=dashboard_id,
            time_from=time_from,
            time_to=time_to,
            width=width,
            height=height,
            browser_timezone=browser_timezone,
        )

        screenshot_data = await self.wait_for_job_completion(job_path, timeout_seconds=timeout_seconds)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open('wb') as f:
            _ = f.write(screenshot_data)
