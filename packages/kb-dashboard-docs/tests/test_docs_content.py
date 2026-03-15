"""Tests for kb_dashboard_docs module."""

import pytest

from kb_dashboard_docs import get_full_docs, get_guide, list_guides


@pytest.fixture(autouse=True)
def skip_without_vendored_content(requires_vendored_content_fixture: None) -> None:
    """Auto-use fixture to skip all tests if vendored content is not available."""


def test_get_full_docs_returns_string() -> None:
    """Test that get_full_docs returns non-empty documentation."""
    content = get_full_docs()
    assert isinstance(content, str)
    assert len(content) > 0
    assert 'Dashboard Compiler' in content


def test_list_guides_returns_list() -> None:
    """Test that list_guides returns a sorted list of guide names."""
    guides = list_guides()
    assert isinstance(guides, list)
    assert len(guides) > 0
    assert guides == sorted(guides)
    # Check that known guides exist
    assert 'breaking-changes' in guides
    assert 'otel-dashboard-guide' in guides
    assert 'esql-language-reference' in guides


def test_get_guide_returns_content() -> None:
    """Test that get_guide returns guide content."""
    content = get_guide('otel-dashboard-guide')
    assert isinstance(content, str)
    assert len(content) > 0


def test_get_guide_handles_md_extension() -> None:
    """Test that get_guide handles .md extension and returns identical content."""
    content_without_ext = get_guide('otel-dashboard-guide')
    content_with_ext = get_guide('otel-dashboard-guide.md')
    assert content_with_ext == content_without_ext


def test_get_guide_not_found() -> None:
    """Test that get_guide raises FileNotFoundError for missing guide."""
    with pytest.raises(FileNotFoundError, match='nonexistent-guide') as exc_info:
        get_guide('nonexistent-guide')
    assert 'Available guides:' in str(exc_info.value)
