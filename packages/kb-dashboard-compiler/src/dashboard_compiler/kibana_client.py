# pyright: reportMissingTypeStubs=false
# prison library lacks type stubs
"""Kibana client for uploading dashboards via the Saved Objects API."""

import asyncio
import logging
from pathlib import Path
from typing import Annotated, Any, ClassVar, Literal

import aiohttp
import prison
from pydantic import BaseModel, ConfigDict, Discriminator, Field, Tag, TypeAdapter

logger = logging.getLogger(__name__)

HTTP_OK = 200
HTTP_SERVICE_UNAVAILABLE = 503


# ============================================================================
# Error Response Models
# ============================================================================


class KibanaErrorDetail(BaseModel):
    """Structured error detail from Kibana API responses.

    Captures the known error structure returned by Kibana's Saved Objects API.
    Configured with extra='allow' to handle unexpected fields gracefully.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    message: str | None = None
    """Error message from Kibana."""
    type: str | None = None
    """Error type identifier."""


# ============================================================================
# Screenshot Job Parameter Models
# ============================================================================


class LayoutDimensions(BaseModel):
    """Screenshot layout dimensions."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    width: int
    """Screenshot width in pixels."""
    height: int
    """Screenshot height in pixels."""


class ScreenshotLayout(BaseModel):
    """Screenshot layout configuration."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    id: Literal['preserve_layout'] = 'preserve_layout'
    """Layout type identifier."""
    dimensions: LayoutDimensions
    """Layout dimensions."""


class ScreenshotTimeRange(BaseModel):
    """Time range for dashboard screenshot."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    from_time: str = Field(..., serialization_alias='from')
    """Start time (ISO 8601 or relative)."""
    to: str
    """End time (ISO 8601 or relative)."""


class DashboardLocatorParams(BaseModel):
    """Parameters for locating a specific dashboard view."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    dashboard_id: str = Field(..., serialization_alias='dashboardId')
    """Dashboard ID to screenshot."""
    use_hash: bool = Field(default=False, serialization_alias='useHash')
    """Whether to use hash routing."""
    view_mode: Literal['view', 'edit'] = Field(default='view', serialization_alias='viewMode')
    """Dashboard view mode."""
    preserve_saved_filters: bool = Field(default=True, serialization_alias='preserveSavedFilters')
    """Preserve saved filters."""
    time_range: ScreenshotTimeRange | None = Field(default=None, serialization_alias='timeRange')
    """Optional time range override."""


class LocatorParams(BaseModel):
    """Locator configuration for Kibana reporting."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    id: Literal['DASHBOARD_APP_LOCATOR'] = 'DASHBOARD_APP_LOCATOR'
    """Locator type identifier."""
    params: DashboardLocatorParams
    """Dashboard locator parameters."""


class JobParams(BaseModel):
    """Complete job parameters for Kibana screenshot generation."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')

    layout: ScreenshotLayout
    """Screenshot layout configuration."""
    browser_timezone: str = Field(..., serialization_alias='browserTimezone')
    """Browser timezone for rendering."""
    locator_params: LocatorParams = Field(..., serialization_alias='locatorParams')
    """Dashboard locator configuration."""


# ============================================================================
# Saved Object Response Models
# ============================================================================


class SavedObjectResult(BaseModel):
    """Represents a single saved object result from Kibana API."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    id: str
    """Saved object ID."""
    destination_id: str | None = Field(default=None, validation_alias='destinationId')
    """Destination ID if object was relocated."""
    type: str
    """Saved object type."""


class SavedObjectError(BaseModel):
    """Represents an error from Kibana saved objects API."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow', populate_by_name=True)

    error: KibanaErrorDetail | None = None
    """Structured error details from Kibana."""
    message: str | None = None
    """Top-level error message."""
    status_code: int | None = Field(default=None, alias='statusCode')
    """HTTP status code."""

    def get_error_message(self) -> str:
        """Extract the most descriptive error message available.

        Returns:
            Error message from nested error detail, top-level message, or 'Unknown error'.

        """
        if self.error is not None and self.error.message is not None:
            return self.error.message
        if self.message is not None:
            return self.message
        return 'Unknown error'


class KibanaSavedObjectsResponse(BaseModel):
    """Response from Kibana saved objects import API."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow', populate_by_name=True)

    success: bool = False
    """Whether the import was successful."""
    success_count: int = Field(default=0, alias='successCount')
    """Number of successfully imported objects."""
    success_results: list[SavedObjectResult] = Field(default_factory=list, alias='successResults')
    """List of successfully imported objects."""
    errors: list[SavedObjectError] = Field(default_factory=list)
    """List of errors encountered during import."""


class KibanaReportingJobResponse(BaseModel):
    """Response from Kibana reporting job creation API."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    path: str
    """Path to poll for job completion."""


class EsqlColumn(BaseModel):
    """Represents a column definition in ES|QL query results.

    Note: Uses pydantic.BaseModel directly (not shared.model.BaseModel) because this is
    a view model for API responses, requiring extra='allow' and mutable instances.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    name: str
    """Column name."""
    type: str
    """Column data type (e.g., keyword, long, date)."""


class EsqlResponse(BaseModel):
    """Response from ES|QL query execution via Kibana.

    This model represents the structured result of an ES|QL query,
    containing column definitions and row values.

    Note: Uses pydantic.BaseModel directly (not shared.model.BaseModel) because this is
    a view model for API responses, requiring extra='allow' and mutable instances.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    columns: list[EsqlColumn] = Field(default_factory=list)
    """Column definitions with name and type."""
    values: list[list[Any]] = Field(default_factory=list)
    """Row values as nested arrays."""
    took: int | None = None
    """Query execution time in milliseconds."""
    is_partial: bool = False
    """Whether results are partial."""

    @property
    def row_count(self) -> int:
        """Return the number of rows in the result."""
        return len(self.values)

    @property
    def column_count(self) -> int:
        """Return the number of columns in the result."""
        return len(self.columns)

    def to_dicts(self) -> list[dict[str, Any]]:
        """Convert results to a list of dictionaries with column names as keys.

        Returns:
            List of dictionaries, each representing a row with column names as keys.
        """
        # Values are dynamic JSON types from Elasticsearch; col.name is typed, val is Any from ES
        return [{col.name: val for col, val in zip(self.columns, row, strict=False)} for row in self.values]  # pyright: ignore[reportAny]


class EsqlRootCause(BaseModel):
    """Root cause detail in ES|QL error responses."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    type: str | None = None
    """Error type identifier."""
    reason: str | None = None
    """Human-readable error reason."""


class EsqlErrorDetail(BaseModel):
    """Structured error detail from ES|QL query responses."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    type: str | None = None
    """Error type identifier (e.g., 'verification_exception', 'parsing_exception')."""
    reason: str | None = None
    """Human-readable error reason."""
    root_cause: list[EsqlRootCause] = Field(default_factory=list)
    """List of root causes for the error."""


class EsqlErrorResponse(BaseModel):
    """Error response from ES|QL query execution.

    This model represents an error response from Elasticsearch when an ES|QL
    query fails (e.g., syntax error, verification error, unknown field).
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    error: EsqlErrorDetail
    """Structured error details."""
    status: int | None = None
    """HTTP status code."""

    def get_error_message(self) -> str:
        """Extract a user-friendly error message from the error response.

        Returns:
            The error reason, or a fallback message if not available.
        """
        if self.error.reason is not None:
            return self.error.reason
        if self.error.type is not None:
            return self.error.type
        return 'Unknown ES|QL error'


def _esql_response_discriminator(value: Any) -> str:  # pyright: ignore[reportAny]
    """Discriminator function for ES|QL API responses.

    Determines whether the response is an error or success based on the presence
    of the 'error' key in the response dict.

    Args:
        value: The raw response value (typically a dict).

    Returns:
        'error' if the response contains an error, 'success' otherwise.
    """
    if isinstance(value, dict):
        return 'error' if 'error' in value else 'success'
    return 'success'


EsqlApiResponse = Annotated[
    Annotated[EsqlErrorResponse, Tag('error')] | Annotated[EsqlResponse, Tag('success')],
    Discriminator(_esql_response_discriminator),
]
"""Union type for ES|QL API responses, discriminated by the presence of 'error' key."""

# TypeAdapter instance for parsing ES|QL API responses.
# Note: Explicit type annotation omitted to avoid beartype compatibility issues with complex generics.
_esql_response_adapter = TypeAdapter(  # pyright: ignore[reportUnknownVariableType]
    EsqlApiResponse
)


class KibanaClient:
    """Client for interacting with Kibana's Saved Objects API."""

    url: str
    username: str | None
    password: str | None
    api_key: str | None
    space_id: str | None
    ssl_verify: bool
    _session: aiohttp.ClientSession | None
    _connector: aiohttp.TCPConnector | None

    def __init__(  # noqa: PLR0913
        self,
        url: str,
        *,
        username: str | None = None,
        password: str | None = None,
        api_key: str | None = None,
        space_id: str | None = None,
        ssl_verify: bool = True,
    ) -> None:
        """Initialize the Kibana client.

        Args:
            url: Base Kibana URL (e.g., http://localhost:5601)
            username: Basic auth username (optional)
            password: Basic auth password (optional)
            api_key: API key for authentication (optional)
            space_id: Kibana space ID (optional). If not specified, uses the default space.
            ssl_verify: Whether to verify SSL certificates (default: True). Set to False for self-signed certificates.

        """
        self.url = url.rstrip('/')
        self.username = username
        self.password = password
        self.api_key = api_key
        self.space_id = space_id
        self.ssl_verify = ssl_verify
        self._session = None
        self._connector = None

    def _get_api_url(self, path: str) -> str:
        """Build API URL with space prefix if space_id is set.

        Args:
            path: API path starting with /api/ or /app/

        Returns:
            Full URL with optional space prefix

        """
        if self.space_id is not None and path.startswith(('/api/', '/app/')):
            # Insert /s/{space_id} before /api/ or /app/
            path = f'/s/{self.space_id}{path}'
        return f'{self.url}{path}'

    def _get_auth_headers_and_auth(self) -> tuple[dict[str, str], aiohttp.BasicAuth | None]:
        """Get authentication headers and auth object for Kibana API requests.

        Returns:
            Tuple of (headers dict with kbn-xsrf and optional Authorization, BasicAuth or None)

        """
        headers = {'kbn-xsrf': 'true'}
        if self.api_key is not None:
            headers['Authorization'] = f'ApiKey {self.api_key}'

        auth = None
        if self.username is not None and self.password is not None:
            auth = aiohttp.BasicAuth(self.username, self.password)

        return headers, auth

    def _get_session(self) -> aiohttp.ClientSession:
        """Get or create reusable HTTP session.

        Returns:
            aiohttp.ClientSession instance

        """
        if self._session is None or self._session.closed:
            self._connector = aiohttp.TCPConnector(ssl=self.ssl_verify)
            self._session = aiohttp.ClientSession(connector=self._connector)
        return self._session

    async def close(self) -> None:
        """Close HTTP session and connector, releasing resources."""
        if self._session is not None and not self._session.closed:
            await self._session.close()
        if self._connector is not None and not self._connector.closed:
            await self._connector.close()
        self._session = None
        self._connector = None

    async def __aenter__(self) -> 'KibanaClient':
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager and close client."""
        await self.close()

    async def _get(self, path: str, **kwargs: Any) -> aiohttp.ClientResponse:  # pyright: ignore[reportAny]
        """Make GET request to Kibana API.

        Args:
            path: API path (e.g., /api/saved_objects/_export)
            **kwargs: Additional arguments to pass to session.get()

        Returns:
            aiohttp.ClientResponse object

        """
        url = self._get_api_url(path)
        headers, auth = self._get_auth_headers_and_auth()
        session = self._get_session()
        return await session.get(url, headers=headers, auth=auth, **kwargs)  # pyright: ignore[reportAny]

    async def _post(self, path: str, **kwargs: Any) -> aiohttp.ClientResponse:  # pyright: ignore[reportAny]
        """Make POST request to Kibana API.

        Args:
            path: API path (e.g., /api/saved_objects/_import)
            **kwargs: Additional arguments to pass to session.post()

        Returns:
            aiohttp.ClientResponse object

        """
        url = self._get_api_url(path)
        headers, auth = self._get_auth_headers_and_auth()

        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))  # pyright: ignore[reportAny]

        session = self._get_session()
        return await session.post(url, headers=headers, auth=auth, **kwargs)  # pyright: ignore[reportAny]

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
        endpoint = '/api/saved_objects/_import'
        if overwrite is True:
            endpoint += '?overwrite=true'

        data = aiohttp.FormData()

        if isinstance(ndjson_data, Path):
            with ndjson_data.open('rb') as f:
                content = f.read()
            data.add_field('file', content, filename=ndjson_data.name, content_type='application/ndjson')
        else:
            data.add_field('file', ndjson_data.encode('utf-8'), filename='dashboard.ndjson', content_type='application/ndjson')

        async with await self._post(endpoint, data=data) as response:
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
        return self._get_api_url(f'/app/dashboards#/view/{dashboard_id}')

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
        time_range: ScreenshotTimeRange | None = None
        if time_from is not None or time_to is not None:
            time_range = ScreenshotTimeRange(
                from_time=time_from if time_from is not None else 'now-15m',
                to=time_to if time_to is not None else 'now',
            )

        dashboard_params = DashboardLocatorParams(
            dashboard_id=dashboard_id,
            time_range=time_range,
        )

        job_params = JobParams(
            layout=ScreenshotLayout(
                dimensions=LayoutDimensions(width=width, height=height),
            ),
            browser_timezone=browser_timezone,
            locator_params=LocatorParams(params=dashboard_params),
        )

        job_params_dict = job_params.model_dump(by_alias=True, exclude_none=True)
        rison_result = prison.dumps(job_params_dict)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        if not isinstance(rison_result, str):
            msg = f'prison.dumps() returned {type(rison_result).__name__}, expected str'  # pyright: ignore[reportUnknownArgumentType]
            raise TypeError(msg)

        endpoint = '/api/reporting/generate/pngV2'
        params: dict[str, str] = {'jobParams': rison_result}

        async with await self._post(endpoint, params=params) as response:
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
        session = self._get_session()
        headers, auth = self._get_auth_headers_and_auth()
        endpoint = f'{self.url}{job_path}'

        try:
            async with asyncio.timeout(timeout_seconds):
                while True:
                    async with session.get(endpoint, headers=headers, auth=auth) as response:
                        if response.status == HTTP_OK:
                            content_type = response.headers.get('Content-Type', '')
                            if 'image/png' in content_type:
                                return await response.read()
                            body = await response.text()
                            msg = f'Unexpected response from Kibana (status {response.status}, content-type {content_type}): {body[:200]}'
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

    async def export_dashboard(self, dashboard_id: str) -> str:
        """Export a dashboard from Kibana using the Saved Objects Export API.

        Args:
            dashboard_id: The ID of the dashboard to export

        Returns:
            NDJSON string containing the dashboard and all its dependent objects

        Raises:
            aiohttp.ClientError: If the request fails

        """
        endpoint = '/api/saved_objects/_export'

        request_body = {
            'objects': [
                {
                    'type': 'dashboard',
                    'id': dashboard_id,
                },
            ],
            'includeReferencesDeep': True,
        }

        async with await self._post(endpoint, json=request_body, headers={'Content-Type': 'application/json'}) as response:
            response.raise_for_status()
            return await response.text()

    async def execute_esql(self, query: str) -> EsqlResponse:
        """Execute an ES|QL query via Kibana's console proxy API.

        Args:
            query: The ES|QL query string to execute

        Returns:
            EsqlResponse with query results containing columns, values, and metadata

        Raises:
            aiohttp.ClientError: If the request fails due to network issues
            asyncio.TimeoutError: If the request times out
            ValueError: If the response contains an error message
            pydantic.ValidationError: If response validation fails

        """
        endpoint = '/api/console/proxy'
        params = {'path': '/_query', 'method': 'POST'}

        request_body = {
            'query': query,
        }

        logger.info('Executing ES|QL query via Kibana console proxy')

        timeout = aiohttp.ClientTimeout(total=30)
        async with await self._post(
            endpoint,
            params=params,
            json=request_body,
            headers={'Content-Type': 'application/json', 'x-elastic-internal-origin': 'kibana'},
            timeout=timeout,
        ) as response:
            if response.status != HTTP_OK:
                error_text = await response.text()
                logger.error('ES|QL query failed with status %s: %s', response.status, error_text[:500])
                msg = f'ES|QL query failed (HTTP {response.status}): {error_text[:200]}'
                raise ValueError(msg)

            result = await response.json()  # pyright: ignore[reportAny]

            # Parse response using TypeAdapter for automatic error/success discrimination
            parsed = _esql_response_adapter.validate_python(  # pyright: ignore[reportUnknownVariableType]
                result
            )

            # Handle response based on type (exhaustive type checking per CODE_STYLE.md)
            if isinstance(parsed, EsqlErrorResponse):
                error_msg = parsed.get_error_message()
                msg = f'ES|QL query error: {error_msg}'
                raise ValueError(msg)  # noqa: TRY004 - ValueError is correct for query errors, not TypeError
            if isinstance(parsed, EsqlResponse):
                return parsed

            msg = f'Unexpected ES|QL response type: {type(parsed).__name__}'  # pyright: ignore[reportUnknownArgumentType]
            raise TypeError(msg)
