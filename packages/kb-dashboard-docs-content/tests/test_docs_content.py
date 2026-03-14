"""Tests for kb_dashboard_docs_content module."""

import pytest

from kb_dashboard_docs_content import get_full_docs, get_guide, list_guides


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
    # Check that known guides exist
    assert 'otel-dashboard-guide' in guides
    assert 'esql-language-reference' in guides


def test_get_guide_returns_content() -> None:
    """Test that get_guide returns guide content."""
    content = get_guide('otel-dashboard-guide')
    assert isinstance(content, str)
    assert len(content) > 0


def test_get_guide_handles_md_extension() -> None:
    """Test that get_guide handles .md extension."""
    content = get_guide('otel-dashboard-guide.md')
    assert isinstance(content, str)
    assert len(content) > 0


def test_get_guide_not_found() -> None:
    """Test that get_guide raises FileNotFoundError for missing guide."""
    with pytest.raises(FileNotFoundError, match='nonexistent-guide') as exc_info:
        get_guide('nonexistent-guide')
    assert 'Available guides:' in str(exc_info.value)
