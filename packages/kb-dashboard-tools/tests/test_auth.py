"""Tests for authentication utilities."""

from kb_dashboard_tools.auth import normalize_credentials, redact_url


def test_normalize_credentials() -> None:
    """Test normalize_credentials function."""
    assert normalize_credentials('my-key') == 'my-key'
    assert normalize_credentials('') is None
    assert normalize_credentials(None) is None


def test_redact_url() -> None:
    """Test redact_url function."""
    assert redact_url('https://user:pass@example.com:9200/path?q=1') == 'https://example.com:9200/path?q=1'
    assert redact_url('http://localhost:5601/app/kibana') == 'http://localhost:5601/app/kibana'
    assert redact_url('https://example.com') == 'https://example.com'
    # Test IPv6 address handling - brackets must be preserved
    assert redact_url('http://[::1]:9200/path') == 'http://[::1]:9200/path'
    assert redact_url('http://user:pass@[::1]:9200/path') == 'http://[::1]:9200/path'
