"""Tests for KibanaClient."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest

from kb_dashboard_mcp.client import KibanaClient, KibanaClientConfig

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


class TestKibanaClientConfig:
    """Tests for KibanaClientConfig."""

    def test_config_with_api_key(self) -> None:
        """Test configuration with API key."""
        config = KibanaClientConfig(
            kibana_url='https://kibana.example.com:5601',
            api_key='test-api-key',
        )

        assert config.kibana_url == 'https://kibana.example.com:5601'
        assert config.api_key == 'test-api-key'
        assert config.username is None
        assert config.password is None
        assert config.verify_ssl is True

    def test_config_with_basic_auth(self) -> None:
        """Test configuration with basic auth."""
        config = KibanaClientConfig(
            kibana_url='https://kibana.example.com:5601',
            username='user',
            password='pass',
            verify_ssl=False,
        )

        assert config.username == 'user'
        assert config.password == 'pass'
        assert config.verify_ssl is False


class TestKibanaClient:
    """Tests for KibanaClient."""

    @pytest.fixture
    def client_with_api_key(self) -> KibanaClient:
        """Create a KibanaClient with API key auth."""
        config = KibanaClientConfig(
            kibana_url='https://kibana.example.com:5601',
            api_key='test-api-key',
            verify_ssl=False,
        )
        return KibanaClient(config)

    @pytest.fixture
    def client_with_basic_auth(self) -> KibanaClient:
        """Create a KibanaClient with basic auth."""
        config = KibanaClientConfig(
            kibana_url='https://kibana.example.com:5601',
            username='user',
            password='pass',
            verify_ssl=False,
        )
        return KibanaClient(config)

    async def test_ping_success(self, client_with_api_key: KibanaClient, httpx_mock: HTTPXMock) -> None:
        """Test successful ping."""
        httpx_mock.add_response(
            url='https://kibana.example.com:5601/api/status',
            status_code=200,
            json={'status': {'overall': {'level': 'available'}}},
        )

        result = await client_with_api_key.ping()

        assert result is True
        await client_with_api_key.close()

    async def test_ping_failure(self, client_with_api_key: KibanaClient, httpx_mock: HTTPXMock) -> None:
        """Test failed ping."""
        httpx_mock.add_response(
            url='https://kibana.example.com:5601/api/status',
            status_code=503,
        )

        result = await client_with_api_key.ping()

        assert result is False
        await client_with_api_key.close()

    async def test_ping_connection_error(self, client_with_api_key: KibanaClient, httpx_mock: HTTPXMock) -> None:
        """Test ping with connection error."""
        httpx_mock.add_exception(httpx.ConnectError('Connection refused'))

        result = await client_with_api_key.ping()

        assert result is False
        await client_with_api_key.close()

    async def test_esql_query(self, client_with_api_key: KibanaClient, httpx_mock: HTTPXMock) -> None:
        """Test ES|QL query execution."""
        expected_response = {
            'columns': [{'name': 'field', 'type': 'keyword'}],
            'values': [['value']],
        }
        httpx_mock.add_response(
            url=httpx.URL('https://kibana.example.com:5601/api/console/proxy', params={'path': '/_query?format=json', 'method': 'POST'}),
            json=expected_response,
        )

        result = await client_with_api_key.esql_query('FROM test | LIMIT 1')

        assert result == expected_response
        await client_with_api_key.close()

    async def test_esql_query_columnar(self, client_with_api_key: KibanaClient, httpx_mock: HTTPXMock) -> None:
        """Test ES|QL query with columnar format."""
        expected_response = {'columns': [], 'values': []}
        httpx_mock.add_response(
            url=httpx.URL('https://kibana.example.com:5601/api/console/proxy', params={'path': '/_query?format=json', 'method': 'POST'}),
            json=expected_response,
        )

        await client_with_api_key.esql_query('FROM test', columnar=True)

        request = httpx_mock.get_request()
        assert request is not None
        body = request.read()
        assert b'columnar' in body
        assert b'true' in body
        await client_with_api_key.close()

    async def test_get_data_streams(self, client_with_api_key: KibanaClient, httpx_mock: HTTPXMock) -> None:
        """Test getting data streams."""
        expected_response = {'data_streams': [{'name': 'test-stream'}]}
        httpx_mock.add_response(
            url=httpx.URL('https://kibana.example.com:5601/api/console/proxy', params={'path': '/_data_stream', 'method': 'GET'}),
            json=expected_response,
        )

        result = await client_with_api_key.get_data_streams()

        assert result == expected_response
        await client_with_api_key.close()

    async def test_get_data_streams_with_pattern(self, client_with_api_key: KibanaClient, httpx_mock: HTTPXMock) -> None:
        """Test getting data streams with pattern filter."""
        expected_response = {'data_streams': []}
        httpx_mock.add_response(
            url=httpx.URL('https://kibana.example.com:5601/api/console/proxy', params={'path': '/_data_stream/logs-*', 'method': 'GET'}),
            json=expected_response,
        )

        result = await client_with_api_key.get_data_streams(name='logs-*')

        assert result == expected_response
        await client_with_api_key.close()

    async def test_test_grok_pattern(self, client_with_api_key: KibanaClient, httpx_mock: HTTPXMock) -> None:
        """Test grok pattern testing."""
        expected_response = {'matches': [{'match': {'field': 'value'}}]}
        httpx_mock.add_response(
            url=httpx.URL(
                'https://kibana.example.com:5601/api/console/proxy',
                params={'path': '/_text_structure/test_grok_pattern', 'method': 'POST'},
            ),
            json=expected_response,
        )

        result = await client_with_api_key.test_grok_pattern(
            grok_pattern='%{WORD:field}',
            text=['value'],
        )

        assert result == expected_response
        await client_with_api_key.close()

    async def test_test_grok_pattern_with_custom_patterns(self, client_with_api_key: KibanaClient, httpx_mock: HTTPXMock) -> None:
        """Test grok pattern with custom pattern definitions."""
        expected_response = {'matches': []}
        httpx_mock.add_response(
            url=httpx.URL(
                'https://kibana.example.com:5601/api/console/proxy',
                params={'path': '/_text_structure/test_grok_pattern', 'method': 'POST'},
            ),
            json=expected_response,
        )

        await client_with_api_key.test_grok_pattern(
            grok_pattern='%{CUSTOM:field}',
            text=['value'],
            pattern_definitions={'CUSTOM': '[a-z]+'},
        )

        request = httpx_mock.get_request()
        assert request is not None
        body = request.read()
        assert b'pattern_definitions' in body
        await client_with_api_key.close()

    async def test_simulate_ingest(self, client_with_api_key: KibanaClient, httpx_mock: HTTPXMock) -> None:
        """Test ingest pipeline simulation."""
        expected_response = {'docs': [{'doc': {'_source': {'field': 'value'}}}]}
        httpx_mock.add_response(
            url=httpx.URL(
                'https://kibana.example.com:5601/api/console/proxy',
                params={'path': '/_ingest/pipeline/_simulate', 'method': 'POST'},
            ),
            json=expected_response,
        )

        result = await client_with_api_key.simulate_ingest(
            pipeline={'processors': []},
            docs=[{'_source': {'message': 'test'}}],
        )

        assert result == expected_response
        await client_with_api_key.close()

    async def test_api_key_auth_header(self, client_with_api_key: KibanaClient, httpx_mock: HTTPXMock) -> None:
        """Test that API key auth header is set correctly."""
        httpx_mock.add_response(
            url='https://kibana.example.com:5601/api/status',
            status_code=200,
            json={},
        )

        await client_with_api_key.ping()

        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers['Authorization'] == 'ApiKey test-api-key'
        assert request.headers['kbn-xsrf'] == 'true'
        await client_with_api_key.close()

    async def test_basic_auth_header(self, client_with_basic_auth: KibanaClient, httpx_mock: HTTPXMock) -> None:
        """Test that basic auth header is set correctly."""
        httpx_mock.add_response(
            url='https://kibana.example.com:5601/api/status',
            status_code=200,
            json={},
        )

        await client_with_basic_auth.ping()

        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers['Authorization'].startswith('Basic ')
        assert request.headers['kbn-xsrf'] == 'true'
        await client_with_basic_auth.close()

    async def test_close_client(self, client_with_api_key: KibanaClient, httpx_mock: HTTPXMock) -> None:
        """Test closing the client."""
        httpx_mock.add_response(
            url='https://kibana.example.com:5601/api/status',
            status_code=200,
            json={},
        )

        await client_with_api_key.ping()
        await client_with_api_key.close()

        assert client_with_api_key._client is None

    async def test_close_without_opening(self, client_with_api_key: KibanaClient) -> None:
        """Test closing client that was never opened."""
        await client_with_api_key.close()
