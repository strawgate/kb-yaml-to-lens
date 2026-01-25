"""Tests for the Kibana client."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from dashboard_compiler.kibana_client import (
    HTTP_SERVICE_UNAVAILABLE,
    BulkItemError,
    BulkItemResult,
    BulkResponse,
    DashboardLocatorParams,
    EsqlErrorDetail,
    EsqlErrorResponse,
    EsqlResponse,
    IndexTemplateResponse,
    JobParams,
    KibanaClient,
    KibanaErrorDetail,
    LayoutDimensions,
    LocatorParams,
    ScreenshotLayout,
    ScreenshotTimeRange,
    _esql_response_adapter,
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

    @pytest.mark.asyncio
    async def test_proxy_bulk_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test bulk indexing through Kibana console proxy."""
        client = KibanaClient(url='http://localhost:5601')

        async def fake_post(endpoint: str, **kwargs: Any) -> _FakeResponseContext:
            assert endpoint == '/api/console/proxy'
            assert kwargs['params'] == {'path': '/_bulk', 'method': 'POST'}
            assert kwargs['headers']['Content-Type'] == 'application/x-ndjson'
            assert kwargs['headers']['x-elastic-internal-origin'] == 'kibana'
            return _FakeResponseContext(
                _FakeResponse(
                    json_data={
                        'took': 30,
                        'errors': False,
                        'items': [
                            {'index': {'_index': 'logs-sample', 'status': 201}},
                            {'index': {'_index': 'logs-sample', 'status': 201}},
                        ],
                    }
                )
            )

        monkeypatch.setattr(client, '_post', fake_post)

        actions = [
            {'_index': 'logs-sample', '_source': {'message': 'test1'}, 'pipeline': '_none'},
            {'_index': 'logs-sample', '_source': {'message': 'test2'}, 'pipeline': '_none'},
        ]
        result = await client.proxy_bulk(actions)

        assert isinstance(result, BulkResponse)
        assert result.took == 30
        assert result.errors is False
        assert result.get_success_count() == 2
        assert len(result.get_failed_items()) == 0

    @pytest.mark.asyncio
    async def test_proxy_bulk_with_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test bulk indexing with some failures through Kibana console proxy."""
        client = KibanaClient(url='http://localhost:5601')

        async def fake_post(_endpoint: str, **_kwargs: Any) -> _FakeResponseContext:
            return _FakeResponseContext(
                _FakeResponse(
                    json_data={
                        'took': 30,
                        'errors': True,
                        'items': [
                            {'index': {'_index': 'logs-sample', 'status': 201}},
                            {
                                'index': {
                                    '_index': 'logs-sample',
                                    'status': 400,
                                    'error': {'type': 'mapper_parsing_exception', 'reason': 'failed to parse'},
                                }
                            },
                        ],
                    }
                )
            )

        monkeypatch.setattr(client, '_post', fake_post)

        actions = [
            {'_index': 'logs-sample', '_source': {'message': 'test1'}},
            {'_index': 'logs-sample', '_source': {'bad': 'data'}},
        ]
        result = await client.proxy_bulk(actions)

        assert isinstance(result, BulkResponse)
        assert result.errors is True
        assert result.get_success_count() == 1
        failed_items = result.get_failed_items()
        assert len(failed_items) == 1
        assert failed_items[0].error is not None
        assert failed_items[0].error.type == 'mapper_parsing_exception'
        assert failed_items[0].error.reason == 'failed to parse'

    @pytest.mark.asyncio
    async def test_proxy_bulk_http_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test bulk indexing with HTTP error through Kibana console proxy."""
        client = KibanaClient(url='http://localhost:5601')

        async def fake_post(_endpoint: str, **_kwargs: Any) -> _FakeResponseContext:
            return _FakeResponseContext(_FakeResponse(status=500, text_data='Internal Server Error'))

        monkeypatch.setattr(client, '_post', fake_post)

        actions = [{'_index': 'logs-sample', '_source': {'message': 'test'}}]

        with pytest.raises(ValueError, match='Bulk indexing failed'):
            await client.proxy_bulk(actions)

    @pytest.mark.asyncio
    async def test_proxy_put_index_template_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test creating index template through Kibana console proxy."""
        client = KibanaClient(url='http://localhost:5601')

        async def fake_post(endpoint: str, **kwargs: Any) -> _FakeResponseContext:
            assert endpoint == '/api/console/proxy'
            assert kwargs['params'] == {'path': '/_index_template/my-template', 'method': 'PUT'}
            assert kwargs['headers']['Content-Type'] == 'application/json'
            assert kwargs['headers']['x-elastic-internal-origin'] == 'kibana'
            return _FakeResponseContext(_FakeResponse(json_data={'acknowledged': True}))

        monkeypatch.setattr(client, '_post', fake_post)

        result = await client.proxy_put_index_template(
            name='my-template',
            index_patterns=['logs-*'],
            template={'mappings': {'properties': {'@timestamp': {'type': 'date'}}}},
        )

        assert isinstance(result, IndexTemplateResponse)
        assert result.acknowledged is True

    @pytest.mark.asyncio
    async def test_proxy_put_index_template_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test creating index template with error through Kibana console proxy."""
        client = KibanaClient(url='http://localhost:5601')

        async def fake_post(_endpoint: str, **_kwargs: Any) -> _FakeResponseContext:
            return _FakeResponseContext(
                _FakeResponse(
                    json_data={
                        'error': {'type': 'resource_already_exists_exception', 'reason': 'template already exists'},
                    }
                )
            )

        monkeypatch.setattr(client, '_post', fake_post)

        with pytest.raises(ValueError, match='Index template creation error'):
            await client.proxy_put_index_template(
                name='my-template',
                index_patterns=['logs-*'],
                template={},
            )

    @pytest.mark.asyncio
    async def test_proxy_put_index_template_http_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test creating index template with HTTP error through Kibana console proxy."""
        client = KibanaClient(url='http://localhost:5601')

        async def fake_post(_endpoint: str, **_kwargs: Any) -> _FakeResponseContext:
            return _FakeResponseContext(_FakeResponse(status=403, text_data='Forbidden'))

        monkeypatch.setattr(client, '_post', fake_post)

        with pytest.raises(ValueError, match='Index template creation failed'):
            await client.proxy_put_index_template(
                name='my-template',
                index_patterns=['logs-*'],
                template={},
            )


class TestKibanaErrorDetail:
    """Test the KibanaErrorDetail model for Saved Objects API errors."""

    def test_parses_typical_conflict_error(self) -> None:
        """Test parsing a typical conflict error from Kibana."""
        error = KibanaErrorDetail.model_validate(
            {
                'message': 'Saved object [dashboard/abc-123] conflict',
                'type': 'conflict',
            }
        )
        assert error.message == 'Saved object [dashboard/abc-123] conflict'
        assert error.type == 'conflict'

    def test_allows_extra_fields_for_api_compatibility(self) -> None:
        """Test that unknown fields from the API are preserved, not rejected."""
        error = KibanaErrorDetail.model_validate(
            {
                'message': 'Error',
                'type': 'validation',
                'meta': {'index': 0},
                'statusCode': 409,
            }
        )
        assert error.message == 'Error'
        assert error.type == 'validation'
        # Verify extra fields are preserved in model_dump() output
        dumped = error.model_dump()
        assert dumped.get('meta') == {'index': 0}
        assert dumped.get('statusCode') == 409


class TestEsqlResponseModels:
    """Test ES|QL response models and TypeAdapter discrimination."""

    def test_parses_success_response_with_results(self) -> None:
        """Test parsing a successful ES|QL query response with data."""
        response_data = {
            'columns': [
                {'name': 'host.name', 'type': 'keyword'},
                {'name': 'cpu.usage', 'type': 'double'},
            ],
            'values': [
                ['server-1', 0.75],
                ['server-2', 0.42],
            ],
            'took': 15,
        }
        result = _esql_response_adapter.validate_python(response_data)
        assert isinstance(result, EsqlResponse)
        assert result.row_count == 2
        assert result.column_count == 2
        assert result.took == 15

    def test_parses_empty_success_response(self) -> None:
        """Test parsing a successful ES|QL response with no results."""
        response_data = {'columns': [], 'values': []}
        result = _esql_response_adapter.validate_python(response_data)
        assert isinstance(result, EsqlResponse)
        assert result.row_count == 0

    def test_parses_error_response_with_reason(self) -> None:
        """Test parsing an ES|QL error response (e.g., syntax error)."""
        response_data = {
            'error': {
                'type': 'verification_exception',
                'reason': 'Unknown column [nonexistent_field]',
                'root_cause': [
                    {'type': 'verification_exception', 'reason': 'Unknown column [nonexistent_field]'},
                ],
            },
            'status': 400,
        }
        result = _esql_response_adapter.validate_python(response_data)
        assert isinstance(result, EsqlErrorResponse)
        assert result.error.type == 'verification_exception'
        assert result.error.reason == 'Unknown column [nonexistent_field]'
        assert result.status == 400

    def test_error_response_get_error_message_returns_reason(self) -> None:
        """Test that get_error_message extracts the reason field."""
        error = EsqlErrorResponse(
            error=EsqlErrorDetail(type='parsing_exception', reason='Invalid query syntax'),
            status=400,
        )
        assert error.get_error_message() == 'Invalid query syntax'

    def test_error_response_get_error_message_falls_back_to_type(self) -> None:
        """Test that get_error_message falls back to type if reason is missing."""
        error = EsqlErrorResponse(
            error=EsqlErrorDetail(type='internal_error'),
            status=500,
        )
        assert error.get_error_message() == 'internal_error'

    def test_error_response_get_error_message_unknown_fallback(self) -> None:
        """Test that get_error_message returns fallback when no details available."""
        error = EsqlErrorResponse(error=EsqlErrorDetail())
        assert error.get_error_message() == 'Unknown ES|QL error'

    def test_esql_response_to_dicts(self) -> None:
        """Test converting ES|QL results to list of dicts."""
        from dashboard_compiler.kibana_client import EsqlColumn

        response = EsqlResponse(
            columns=[
                EsqlColumn(name='host', type='keyword'),
                EsqlColumn(name='count', type='long'),
            ],
            values=[
                ['server-1', 100],
                ['server-2', 200],
            ],
        )
        dicts = response.to_dicts()
        assert dicts == [
            {'host': 'server-1', 'count': 100},
            {'host': 'server-2', 'count': 200},
        ]

    @pytest.mark.asyncio
    async def test_execute_esql_returns_success_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test execute_esql returns EsqlResponse on success."""
        client = KibanaClient(url='http://localhost:5601')

        async def fake_post(_endpoint: str, **_kwargs: Any) -> _FakeResponseContext:
            return _FakeResponseContext(
                _FakeResponse(
                    json_data={
                        'columns': [{'name': 'count', 'type': 'long'}],
                        'values': [[42]],
                        'took': 5,
                    }
                )
            )

        monkeypatch.setattr(client, '_post', fake_post)

        result = await client.execute_esql('FROM logs | STATS count()')
        assert isinstance(result, EsqlResponse)
        assert result.row_count == 1
        assert result.values[0][0] == 42

    @pytest.mark.asyncio
    async def test_execute_esql_raises_on_error_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test execute_esql raises ValueError with error message from ES|QL error response."""
        client = KibanaClient(url='http://localhost:5601')

        async def fake_post(_endpoint: str, **_kwargs: Any) -> _FakeResponseContext:
            return _FakeResponseContext(
                _FakeResponse(
                    json_data={
                        'error': {
                            'type': 'verification_exception',
                            'reason': 'Unknown column [bad_field]',
                        },
                        'status': 400,
                    }
                )
            )

        monkeypatch.setattr(client, '_post', fake_post)

        with pytest.raises(ValueError, match='Unknown column \\[bad_field\\]'):
            await client.execute_esql('FROM logs | KEEP bad_field')


class TestScreenshotJobParameterModels:
    """Test screenshot job parameter serialization for Kibana API compatibility.

    These tests verify the serialization aliases are correct for the Kibana Reporting API.
    The API expects specific camelCase keys, not snake_case Python attributes.
    """

    def test_time_range_serializes_from_as_api_expects(self) -> None:
        """Test ScreenshotTimeRange serializes 'from_time' as 'from' for Kibana API."""
        time_range = ScreenshotTimeRange(from_time='now-1h', to='now')
        serialized = time_range.model_dump(by_alias=True)
        assert serialized == {'from': 'now-1h', 'to': 'now'}

    def test_job_params_full_structure_matches_api_spec(self) -> None:
        """Test JobParams serializes to the exact structure Kibana expects."""
        job_params = JobParams(
            layout=ScreenshotLayout(
                dimensions=LayoutDimensions(width=1920, height=1080),
            ),
            browser_timezone='America/New_York',
            locator_params=LocatorParams(
                params=DashboardLocatorParams(
                    dashboard_id='abc-123',
                    time_range=ScreenshotTimeRange(from_time='2024-01-01', to='2024-01-02'),
                ),
            ),
        )

        serialized = job_params.model_dump(by_alias=True, exclude_none=True)

        # Verify the exact structure Kibana expects
        assert serialized == {
            'layout': {
                'id': 'preserve_layout',
                'dimensions': {'width': 1920, 'height': 1080},
            },
            'browserTimezone': 'America/New_York',
            'locatorParams': {
                'id': 'DASHBOARD_APP_LOCATOR',
                'params': {
                    'dashboardId': 'abc-123',
                    'useHash': False,
                    'viewMode': 'view',
                    'preserveSavedFilters': True,
                    'timeRange': {'from': '2024-01-01', 'to': '2024-01-02'},
                },
            },
        }


class TestBulkResponseModels:
    """Test Bulk API response models."""

    def test_bulk_item_error_get_error_message_with_both_fields(self) -> None:
        """Test BulkItemError.get_error_message with type and reason."""
        error = BulkItemError(type='mapper_parsing_exception', reason='failed to parse')
        assert error.get_error_message() == 'mapper_parsing_exception: failed to parse'

    def test_bulk_item_error_get_error_message_reason_only(self) -> None:
        """Test BulkItemError.get_error_message with reason only."""
        error = BulkItemError(reason='some error')
        assert error.get_error_message() == 'some error'

    def test_bulk_item_error_get_error_message_type_only(self) -> None:
        """Test BulkItemError.get_error_message with type only."""
        error = BulkItemError(type='unknown_exception')
        assert error.get_error_message() == 'unknown_exception'

    def test_bulk_item_error_get_error_message_fallback(self) -> None:
        """Test BulkItemError.get_error_message with no fields."""
        error = BulkItemError()
        assert error.get_error_message() == 'Unknown bulk error'

    def test_bulk_item_result_success_property(self) -> None:
        """Test BulkItemResult.success property for various status codes."""
        assert BulkItemResult(index='test', status=200).success is True
        assert BulkItemResult(index='test', status=201).success is True
        assert BulkItemResult(index='test', status=299).success is True
        assert BulkItemResult(index='test', status=400).success is False
        assert BulkItemResult(index='test', status=500).success is False

    def test_bulk_response_parses_from_json(self) -> None:
        """Test BulkResponse parses typical Elasticsearch bulk response."""
        response_data = {
            'took': 30,
            'errors': True,
            'items': [
                {'index': {'_index': 'logs-sample', 'status': 201}},
                {
                    'index': {
                        '_index': 'logs-sample',
                        'status': 400,
                        'error': {'type': 'mapper_parsing_exception', 'reason': 'failed to parse'},
                    }
                },
            ],
        }
        response = BulkResponse.model_validate(response_data)

        assert response.took == 30
        assert response.errors is True
        assert len(response.items) == 2
        assert response.get_success_count() == 1
        assert len(response.get_failed_items()) == 1

    def test_bulk_response_get_failed_items_returns_failed_only(self) -> None:
        """Test get_failed_items returns only items with non-2xx status."""
        response = BulkResponse(
            took=10,
            errors=True,
            items=[
                {'index': BulkItemResult(index='test', status=201)},
                {'index': BulkItemResult(index='test', status=400, error=BulkItemError(type='error1'))},
                {'index': BulkItemResult(index='test', status=200)},
                {'index': BulkItemResult(index='test', status=500, error=BulkItemError(type='error2'))},
            ],
        )

        failed = response.get_failed_items()
        assert len(failed) == 2
        assert failed[0].status == 400
        assert failed[1].status == 500

    def test_bulk_response_empty_items(self) -> None:
        """Test BulkResponse with empty items list."""
        response = BulkResponse(took=5, errors=False, items=[])
        assert response.get_success_count() == 0
        assert len(response.get_failed_items()) == 0


class TestIndexTemplateResponseModel:
    """Test Index Template response model."""

    def test_parses_acknowledged_response(self) -> None:
        """Test IndexTemplateResponse parses acknowledged response."""
        response = IndexTemplateResponse.model_validate({'acknowledged': True})
        assert response.acknowledged is True

    def test_parses_not_acknowledged_response(self) -> None:
        """Test IndexTemplateResponse handles non-acknowledged response."""
        response = IndexTemplateResponse.model_validate({'acknowledged': False})
        assert response.acknowledged is False

    def test_allows_extra_fields(self) -> None:
        """Test IndexTemplateResponse allows extra fields for API compatibility."""
        response = IndexTemplateResponse.model_validate(
            {
                'acknowledged': True,
                'shards_acknowledged': True,
                'index': 'test-index',
            }
        )
        assert response.acknowledged is True
        dumped = response.model_dump()
        assert dumped.get('shards_acknowledged') is True
