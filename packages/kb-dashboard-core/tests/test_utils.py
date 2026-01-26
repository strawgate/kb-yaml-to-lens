"""Tests for utility functions."""

import pytest

from kb_dashboard_core.utils import extract_dashboard_id_from_url


class TestExtractDashboardIdFromUrl:
    """Tests for extract_dashboard_id_from_url function."""

    def test_extract_from_standard_url(self) -> None:
        """Test extraction from standard Kibana dashboard URL."""
        url = 'https://kibana.example.com/app/dashboards#/view/my-dashboard-id'
        assert extract_dashboard_id_from_url(url) == 'my-dashboard-id'

    def test_extract_from_url_with_space(self) -> None:
        """Test extraction from URL with space ID."""
        url = 'https://kibana.example.com/s/myspace/app/dashboards#/view/my-dashboard-id'
        assert extract_dashboard_id_from_url(url) == 'my-dashboard-id'

    def test_extract_from_url_with_query_params(self) -> None:
        """Test extraction from URL with query parameters."""
        url = 'https://kibana.example.com/app/dashboards#/view/my-dashboard-id?_g=(time:(from:now-15m,to:now))'
        assert extract_dashboard_id_from_url(url) == 'my-dashboard-id'

    def test_extract_from_url_with_anchor_params(self) -> None:
        """Test extraction from URL with additional anchor parameters."""
        url = 'https://kibana.example.com/app/dashboards#/view/my-dashboard-id&_a=(filters:!())'
        assert extract_dashboard_id_from_url(url) == 'my-dashboard-id'

    def test_extract_uuid_format_id(self) -> None:
        """Test extraction of UUID-format dashboard ID."""
        url = 'https://kibana.example.com/app/dashboards#/view/12345678-1234-1234-1234-123456789abc'
        assert extract_dashboard_id_from_url(url) == '12345678-1234-1234-1234-123456789abc'

    def test_extract_url_encoded_id(self) -> None:
        """Test extraction of URL-encoded dashboard ID."""
        url = 'https://kibana.example.com/app/dashboards#/view/my%20dashboard%20id'
        assert extract_dashboard_id_from_url(url) == 'my dashboard id'

    def test_plain_id_passthrough(self) -> None:
        """Test that plain dashboard IDs are returned unchanged."""
        dashboard_id = 'my-dashboard-id'
        assert extract_dashboard_id_from_url(dashboard_id) == 'my-dashboard-id'

    def test_plain_uuid_passthrough(self) -> None:
        """Test that plain UUID dashboard IDs are returned unchanged."""
        dashboard_id = '12345678-1234-1234-1234-123456789abc'
        assert extract_dashboard_id_from_url(dashboard_id) == '12345678-1234-1234-1234-123456789abc'

    def test_plain_id_with_special_chars(self) -> None:
        """Test that plain IDs with special characters are returned unchanged."""
        dashboard_id = 'my-dashboard_id.v2'
        assert extract_dashboard_id_from_url(dashboard_id) == 'my-dashboard_id.v2'

    def test_invalid_url_format(self) -> None:
        """Test that invalid URL format raises ValueError."""
        url = 'https://kibana.example.com/app/management/kibana/objects'
        with pytest.raises(ValueError, match='Invalid Kibana dashboard URL format'):
            extract_dashboard_id_from_url(url)

    def test_malformed_url_with_protocol(self) -> None:
        """Test that malformed URL with protocol raises ValueError."""
        url = 'https://kibana.example.com/random/path'
        with pytest.raises(ValueError, match='Invalid Kibana dashboard URL format'):
            extract_dashboard_id_from_url(url)

    def test_url_without_hash(self) -> None:
        """Test extraction from URL without hash symbol."""
        url = 'https://kibana.example.com/app/dashboards/view/my-dashboard-id'
        assert extract_dashboard_id_from_url(url) == 'my-dashboard-id'
