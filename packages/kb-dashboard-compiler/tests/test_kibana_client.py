"""Tests for the Kibana client."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from dashboard_compiler.kibana_client import (
    HTTP_SERVICE_UNAVAILABLE,
    DashboardLocatorParams,
    JobParams,
    KibanaClient,
    KibanaErrorDetail,
    KibanaSavedObjectsResponse,
    LayoutDimensions,
    LocatorParams,
    SavedObjectError,
    ScreenshotLayout,
    ScreenshotTimeRange,
)


@dataclass
class _FakeResponse:
    status: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    json_data: dict[str, Any] | None = None
    text_data: str = ''
    read_data: bytes = b''

    async def json(self) -> dict[str, Any]:
        return self.json_data or {}

    async def text(self) -> str:
        return self.text_data

    async def read(self) -> bytes:
        return self.read_data

    def raise_for_status(self) -> None:
        if self.status >= 400:
            msg = f'Request failed with status {self.status}'
            raise RuntimeError(msg)


@dataclass
class _FakeResponseContext:
    response: _FakeResponse

    async def __aenter__(self) -> _FakeResponse:
        return self.response

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


class _FakeSession:
    def __init__(self, responses: list[_FakeResponse]) -> None:
        self._responses = responses
        self.calls: list[tuple[str, dict[str, str], object]] = []

    def get(self, endpoint: str, headers: dict[str, str], auth: object) -> _FakeResponseContext:
        self.calls.append((endpoint, headers, auth))
        response = self._responses.pop(0)
        return _FakeResponseContext(response)


class TestKibanaClient:
    """Test the KibanaClient class."""

    def test_init_with_basic_auth(self) -> None:
        """Test KibanaClient initialization with basic auth."""
        client = KibanaClient(
            url='http://localhost:5601',
            username='admin',
            password='password',  # noqa: S106
        )
        assert client.url == 'http://localhost:5601'
        assert client.username == 'admin'
        assert client.password == 'password'  # noqa: S105
        assert client.api_key is None
        assert client.ssl_verify is True

    def test_init_with_api_key(self) -> None:
        """Test KibanaClient initialization with API key."""
        client = KibanaClient(
            url='http://localhost:5601',
            api_key='my-api-key',
        )
        assert client.url == 'http://localhost:5601'
        assert client.username is None
        assert client.password is None
        assert client.api_key == 'my-api-key'
        assert client.ssl_verify is True

    def test_init_strips_trailing_slash(self) -> None:
        """Test that trailing slashes are stripped from URL."""
        client = KibanaClient(url='http://localhost:5601/')
        assert client.url == 'http://localhost:5601'

    def test_init_with_ssl_verify_false(self) -> None:
        """Test KibanaClient initialization with SSL verification disabled."""
        client = KibanaClient(
            url='https://localhost:5601',
            ssl_verify=False,
        )
        assert client.ssl_verify is False

    def test_get_auth_headers_and_auth_with_api_key(self) -> None:
        """Test auth headers generation with API key."""
        client = KibanaClient(
            url='http://localhost:5601',
            api_key='my-api-key',
        )
        headers, auth = client._get_auth_headers_and_auth()
        assert headers == {
            'kbn-xsrf': 'true',
            'Authorization': 'ApiKey my-api-key',
        }
        assert auth is None

    def test_get_auth_headers_and_auth_with_basic_auth(self) -> None:
        """Test auth headers generation with basic auth."""
        client = KibanaClient(
            url='http://localhost:5601',
            username='admin',
            password='password',  # noqa: S106
        )
        headers, auth = client._get_auth_headers_and_auth()
        assert headers == {'kbn-xsrf': 'true'}
        assert auth is not None
        assert auth.login == 'admin'  # pyright: ignore[reportUnknownMemberType]
        assert auth.password == 'password'  # noqa: S105  # pyright: ignore[reportUnknownMemberType]

    def test_get_auth_headers_and_auth_no_auth(self) -> None:
        """Test auth headers generation without authentication."""
        client = KibanaClient(url='http://localhost:5601')
        headers, auth = client._get_auth_headers_and_auth()
        assert headers == {'kbn-xsrf': 'true'}
        assert auth is None

    def test_get_dashboard_url(self) -> None:
        """Test dashboard URL generation."""
        client = KibanaClient(url='http://localhost:5601')
        url = client.get_dashboard_url('my-dashboard-id')
        assert url == 'http://localhost:5601/app/dashboards#/view/my-dashboard-id'

    def test_init_with_space_id(self) -> None:
        """Test KibanaClient initialization with space ID."""
        client = KibanaClient(
            url='http://localhost:5601',
            space_id='my-space',
        )
        assert client.url == 'http://localhost:5601'
        assert client.space_id == 'my-space'

    def test_get_api_url_without_space(self) -> None:
        """Test API URL generation without space ID."""
        client = KibanaClient(url='http://localhost:5601')
        url = client._get_api_url('/api/saved_objects/_import')
        assert url == 'http://localhost:5601/api/saved_objects/_import'

    def test_get_api_url_with_space(self) -> None:
        """Test API URL generation with space ID."""
        client = KibanaClient(url='http://localhost:5601', space_id='my-space')
        url = client._get_api_url('/api/saved_objects/_import')
        assert url == 'http://localhost:5601/s/my-space/api/saved_objects/_import'

    def test_get_api_url_with_space_reporting_api(self) -> None:
        """Test API URL generation with space ID for reporting API."""
        client = KibanaClient(url='http://localhost:5601', space_id='production')
        url = client._get_api_url('/api/reporting/generate/pngV2')
        assert url == 'http://localhost:5601/s/production/api/reporting/generate/pngV2'

    def test_get_api_url_with_space_export_api(self) -> None:
        """Test API URL generation with space ID for export API."""
        client = KibanaClient(url='http://localhost:5601', space_id='staging')
        url = client._get_api_url('/api/saved_objects/_export')
        assert url == 'http://localhost:5601/s/staging/api/saved_objects/_export'

    def test_get_dashboard_url_with_space(self) -> None:
        """Test dashboard URL generation with space ID."""
        client = KibanaClient(url='http://localhost:5601', space_id='my-space')
        url = client.get_dashboard_url('my-dashboard-id')
        assert url == 'http://localhost:5601/s/my-space/app/dashboards#/view/my-dashboard-id'

    def test_get_api_url_non_api_path(self) -> None:
        """Test API URL generation with non-API path (no space prefix added)."""
        client = KibanaClient(url='http://localhost:5601', space_id='my-space')
        url = client._get_api_url('/some/other/path')
        assert url == 'http://localhost:5601/some/other/path'

    @pytest.mark.asyncio
    async def test_context_manager_closes_session(self) -> None:
        """Test that using KibanaClient as context manager closes session."""
        async with KibanaClient(url='http://localhost:5601') as client:
            session = client._get_session()
            connector = client._connector
            assert session is not None
            assert not session.closed

        # After exiting context, session should be closed
        assert session.closed
        assert connector is not None
        assert connector.closed

    @pytest.mark.asyncio
    async def test_upload_ndjson_string_payload(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test uploading NDJSON content from a string."""
        client = KibanaClient(url='http://localhost:5601')

        async def fake_post(endpoint: str, **kwargs: Any) -> _FakeResponseContext:
            assert endpoint == '/api/saved_objects/_import?overwrite=true'
            assert 'data' in kwargs
            return _FakeResponseContext(
                _FakeResponse(
                    json_data={
                        'success': True,
                        'successCount': 1,
                        'successResults': [],
                    }
                )
            )

        monkeypatch.setattr(client, '_post', fake_post)

        response = await client.upload_ndjson('{"type":"dashboard"}')
        assert response.success is True
        assert response.success_count == 1

    @pytest.mark.asyncio
    async def test_upload_ndjson_file_payload(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test uploading NDJSON content from a file."""
        client = KibanaClient(url='http://localhost:5601')
        ndjson_path = tmp_path / 'dashboard.ndjson'
        ndjson_path.write_text('{"type":"dashboard"}', encoding='utf-8')

        async def fake_post(endpoint: str, **kwargs: Any) -> _FakeResponseContext:
            assert endpoint == '/api/saved_objects/_import?overwrite=true'
            assert 'data' in kwargs
            return _FakeResponseContext(
                _FakeResponse(
                    json_data={
                        'success': True,
                        'successCount': 1,
                        'successResults': [],
                    }
                )
            )

        monkeypatch.setattr(client, '_post', fake_post)

        response = await client.upload_ndjson(ndjson_path)
        assert response.success is True
        assert response.success_count == 1

    @pytest.mark.asyncio
    async def test_generate_screenshot_returns_job_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test generating a screenshot returns the job path."""
        client = KibanaClient(url='http://localhost:5601')
        expected_path = '/api/reporting/jobs/download/123'

        async def fake_post(endpoint: str, **kwargs: Any) -> _FakeResponseContext:
            assert endpoint == '/api/reporting/generate/pngV2'
            assert 'params' in kwargs
            return _FakeResponseContext(_FakeResponse(json_data={'path': expected_path}))

        monkeypatch.setattr(client, '_post', fake_post)

        job_path = await client.generate_screenshot(
            dashboard_id='dashboard-1',
            time_from='now-1h',
            time_to='now',
            width=800,
            height=600,
            browser_timezone='UTC',
        )
        assert job_path == expected_path

    @pytest.mark.asyncio
    async def test_wait_for_job_completion_returns_png(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test waiting for a reporting job returns PNG bytes."""
        client = KibanaClient(url='http://localhost:5601')
        responses = [
            _FakeResponse(status=HTTP_SERVICE_UNAVAILABLE),
            _FakeResponse(status=200, headers={'Content-Type': 'image/png'}, read_data=b'png-data'),
        ]
        fake_session = _FakeSession(responses)

        monkeypatch.setattr(client, '_get_session', lambda: fake_session)

        result = await client.wait_for_job_completion('/api/reporting/jobs/download/123', poll_interval=0)
        assert result == b'png-data'

    @pytest.mark.asyncio
    async def test_wait_for_job_completion_unexpected_content_type(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test unexpected content type raises an error."""
        client = KibanaClient(url='http://localhost:5601')
        responses = [
            _FakeResponse(status=200, headers={'Content-Type': 'application/json'}, text_data='oops'),
        ]
        fake_session = _FakeSession(responses)

        monkeypatch.setattr(client, '_get_session', lambda: fake_session)

        with pytest.raises(ValueError, match='Unexpected response from Kibana'):
            await client.wait_for_job_completion('/api/reporting/jobs/download/123', poll_interval=0)

    @pytest.mark.asyncio
    async def test_download_screenshot_writes_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test download_screenshot writes the PNG to disk."""
        client = KibanaClient(url='http://localhost:5601')
        output_path = tmp_path / 'screenshots' / 'dashboard.png'

        async def fake_generate_screenshot(  # noqa: PLR0913
            dashboard_id: str,
            time_from: str | None = None,
            time_to: str | None = None,
            width: int = 1920,
            height: int = 1080,
            browser_timezone: str = 'UTC',
        ) -> str:
            _ = (time_from, time_to, width, height, browser_timezone)  # Mark as used
            assert dashboard_id == 'dashboard-1'
            return '/api/reporting/jobs/download/123'

        async def fake_wait_for_job_completion(job_path: str, timeout_seconds: int = 300) -> bytes:
            assert job_path == '/api/reporting/jobs/download/123'
            assert timeout_seconds == 300
            return b'png-data'

        monkeypatch.setattr(client, 'generate_screenshot', fake_generate_screenshot)
        monkeypatch.setattr(client, 'wait_for_job_completion', fake_wait_for_job_completion)

        await client.download_screenshot('dashboard-1', output_path)

        assert output_path.exists() is True
        assert output_path.read_bytes() == b'png-data'

    @pytest.mark.asyncio
    async def test_export_dashboard_returns_ndjson(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test exporting a dashboard returns NDJSON."""
        client = KibanaClient(url='http://localhost:5601')

        async def fake_post(endpoint: str, **kwargs: Any) -> _FakeResponseContext:
            assert endpoint == '/api/saved_objects/_export'
            assert kwargs['headers']['Content-Type'] == 'application/json'
            return _FakeResponseContext(_FakeResponse(text_data='{"type":"dashboard"}'))

        monkeypatch.setattr(client, '_post', fake_post)

        result = await client.export_dashboard('dashboard-1')
        assert result == '{"type":"dashboard"}'


class TestKibanaErrorDetail:
    """Test the KibanaErrorDetail model."""

    def test_parse_full_error(self) -> None:
        """Test parsing error with all known fields."""
        error = KibanaErrorDetail.model_validate({'message': 'Test error', 'type': 'validation_error'})
        assert error.message == 'Test error'
        assert error.type == 'validation_error'

    def test_parse_partial_error(self) -> None:
        """Test parsing error with only message."""
        error = KibanaErrorDetail.model_validate({'message': 'Test error'})
        assert error.message == 'Test error'
        assert error.type is None

    def test_parse_empty_error(self) -> None:
        """Test parsing empty error dict."""
        error = KibanaErrorDetail.model_validate({})
        assert error.message is None
        assert error.type is None

    def test_parse_unknown_fields_allowed(self) -> None:
        """Test that unknown fields are allowed (extra='allow')."""
        error = KibanaErrorDetail.model_validate(
            {
                'message': 'Test error',
                'type': 'conflict',
                'unexpected_field': 'some value',
            }
        )
        assert error.message == 'Test error'
        assert error.type == 'conflict'


class TestSavedObjectError:
    """Test the SavedObjectError model with KibanaErrorDetail."""

    def test_parse_error_with_nested_error_detail(self) -> None:
        """Test parsing error with nested KibanaErrorDetail."""
        error = SavedObjectError.model_validate(
            {
                'error': {'message': 'Conflict', 'type': 'conflict'},
                'message': 'Import failed',
                'statusCode': 409,
            }
        )
        assert error.error is not None
        assert error.error.message == 'Conflict'
        assert error.error.type == 'conflict'
        assert error.message == 'Import failed'
        assert error.status_code == 409

    def test_parse_error_without_nested_error(self) -> None:
        """Test parsing error without nested error detail."""
        error = SavedObjectError.model_validate(
            {
                'message': 'Import failed',
                'statusCode': 500,
            }
        )
        assert error.error is None
        assert error.message == 'Import failed'
        assert error.status_code == 500


class TestKibanaSavedObjectsResponse:
    """Test the KibanaSavedObjectsResponse model."""

    def test_parse_response_with_errors(self) -> None:
        """Test parsing response containing errors."""
        response = KibanaSavedObjectsResponse.model_validate(
            {
                'success': False,
                'successCount': 0,
                'successResults': [],
                'errors': [
                    {
                        'error': {'message': 'Object already exists', 'type': 'conflict'},
                        'message': 'Import conflict',
                        'statusCode': 409,
                    },
                ],
            }
        )
        assert response.success is False
        assert response.success_count == 0
        assert len(response.errors) == 1
        assert response.errors[0].error is not None
        assert response.errors[0].error.message == 'Object already exists'


class TestScreenshotJobParameterModels:
    """Test screenshot job parameter Pydantic models."""

    def test_layout_dimensions(self) -> None:
        """Test LayoutDimensions model."""
        dims = LayoutDimensions(width=1920, height=1080)
        assert dims.width == 1920
        assert dims.height == 1080

    def test_screenshot_layout(self) -> None:
        """Test ScreenshotLayout model with default id."""
        layout = ScreenshotLayout(dimensions=LayoutDimensions(width=800, height=600))
        assert layout.id == 'preserve_layout'
        assert layout.dimensions.width == 800
        assert layout.dimensions.height == 600

    def test_screenshot_time_range(self) -> None:
        """Test ScreenshotTimeRange model with alias."""
        time_range = ScreenshotTimeRange(from_time='now-1h', to='now')
        assert time_range.from_time == 'now-1h'
        assert time_range.to == 'now'

        # Test serialization produces correct alias
        serialized = time_range.model_dump(by_alias=True)
        assert serialized['from'] == 'now-1h'
        assert serialized['to'] == 'now'
        assert 'from_time' not in serialized

    def test_dashboard_locator_params(self) -> None:
        """Test DashboardLocatorParams model with defaults."""
        params = DashboardLocatorParams(dashboard_id='my-dashboard')
        assert params.dashboard_id == 'my-dashboard'
        assert params.use_hash is False
        assert params.view_mode == 'view'
        assert params.preserve_saved_filters is True
        assert params.time_range is None

    def test_dashboard_locator_params_with_time_range(self) -> None:
        """Test DashboardLocatorParams with time range."""
        time_range = ScreenshotTimeRange(from_time='now-7d', to='now')
        params = DashboardLocatorParams(dashboard_id='my-dashboard', time_range=time_range)
        assert params.time_range is not None
        assert params.time_range.from_time == 'now-7d'

    def test_dashboard_locator_params_serialization(self) -> None:
        """Test DashboardLocatorParams serializes with correct camelCase keys."""
        params = DashboardLocatorParams(dashboard_id='my-dashboard')
        serialized = params.model_dump(by_alias=True, exclude_none=True)
        assert serialized['dashboardId'] == 'my-dashboard'
        assert serialized['useHash'] is False
        assert serialized['viewMode'] == 'view'
        assert serialized['preserveSavedFilters'] is True
        assert 'dashboard_id' not in serialized
        assert 'use_hash' not in serialized

    def test_locator_params(self) -> None:
        """Test LocatorParams model."""
        dashboard_params = DashboardLocatorParams(dashboard_id='test-dash')
        locator = LocatorParams(params=dashboard_params)
        assert locator.id == 'DASHBOARD_APP_LOCATOR'
        assert locator.params.dashboard_id == 'test-dash'

    def test_job_params_full(self) -> None:
        """Test JobParams model with all components."""
        job_params = JobParams(
            layout=ScreenshotLayout(
                dimensions=LayoutDimensions(width=1920, height=1080),
            ),
            browser_timezone='America/New_York',
            locator_params=LocatorParams(
                params=DashboardLocatorParams(dashboard_id='my-dashboard'),
            ),
        )
        assert job_params.layout.dimensions.width == 1920
        assert job_params.browser_timezone == 'America/New_York'
        assert job_params.locator_params.params.dashboard_id == 'my-dashboard'

    def test_job_params_serialization_for_api(self) -> None:
        """Test JobParams serializes correctly for Kibana API."""
        time_range = ScreenshotTimeRange(from_time='now-1h', to='now')
        job_params = JobParams(
            layout=ScreenshotLayout(
                dimensions=LayoutDimensions(width=800, height=600),
            ),
            browser_timezone='UTC',
            locator_params=LocatorParams(
                params=DashboardLocatorParams(
                    dashboard_id='dashboard-1',
                    time_range=time_range,
                ),
            ),
        )

        serialized = job_params.model_dump(by_alias=True, exclude_none=True)

        # Check top-level structure
        assert 'layout' in serialized
        assert 'browserTimezone' in serialized
        assert 'locatorParams' in serialized
        assert 'browser_timezone' not in serialized
        assert 'locator_params' not in serialized

        # Check layout structure
        assert serialized['layout']['id'] == 'preserve_layout'
        assert serialized['layout']['dimensions']['width'] == 800
        assert serialized['layout']['dimensions']['height'] == 600

        # Check locatorParams structure
        assert serialized['locatorParams']['id'] == 'DASHBOARD_APP_LOCATOR'
        assert serialized['locatorParams']['params']['dashboardId'] == 'dashboard-1'
        assert serialized['locatorParams']['params']['timeRange']['from'] == 'now-1h'
        assert serialized['locatorParams']['params']['timeRange']['to'] == 'now'
