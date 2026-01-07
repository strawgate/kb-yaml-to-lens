"""Tests for the Kibana client."""

from dashboard_compiler.kibana_client import KibanaClient


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
