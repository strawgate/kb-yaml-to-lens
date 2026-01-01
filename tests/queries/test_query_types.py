"""Tests for query type discrimination utilities."""

from typing import Any, cast

import pytest

from dashboard_compiler.queries.config import ESQLQuery, KqlQuery, LuceneQuery
from dashboard_compiler.queries.types import get_query_type


class TestGetQueryTypeFromDict:
    """Tests for get_query_type with dictionary inputs."""

    def test_identifies_kql_query_from_dict(self) -> None:
        """Test that get_query_type identifies KQL query from dict."""
        query_dict = {'kql': 'status:200'}
        assert get_query_type(query_dict) == 'kql'

    def test_identifies_lucene_query_from_dict(self) -> None:
        """Test that get_query_type identifies Lucene query from dict."""
        query_dict = {'lucene': 'status:[200 TO 299]'}
        assert get_query_type(query_dict) == 'lucene'

    def test_identifies_esql_query_from_dict(self) -> None:
        """Test that get_query_type identifies ESQL query from dict with root key."""
        query_dict = {'root': ['FROM logs']}
        assert get_query_type(query_dict) == 'esql'

    def test_raises_value_error_for_unknown_dict_keys(self) -> None:
        """Test that get_query_type raises ValueError for unknown dict keys."""
        query_dict = {'unknown': 'value'}
        with pytest.raises(ValueError, match='Cannot determine query type from dict with keys'):
            _ = get_query_type(query_dict)

    def test_raises_value_error_for_empty_dict(self) -> None:
        """Test that get_query_type raises ValueError for empty dict."""
        query_dict: dict[str, object] = {}
        with pytest.raises(ValueError, match='Cannot determine query type from dict with keys'):
            _ = get_query_type(query_dict)


class TestGetQueryTypeFromObject:
    """Tests for get_query_type with object inputs."""

    def test_identifies_kql_query_from_object(self) -> None:
        """Test that get_query_type identifies KQL query from object."""
        query = KqlQuery(kql='status:200')
        assert get_query_type(query) == 'kql'

    def test_identifies_lucene_query_from_object(self) -> None:
        """Test that get_query_type identifies Lucene query from object."""
        query = LuceneQuery(lucene='status:[200 TO 299]')
        assert get_query_type(query) == 'lucene'

    def test_identifies_esql_query_from_object(self) -> None:
        """Test that get_query_type identifies ESQL query from object."""
        query = ESQLQuery(root=['FROM logs'])
        assert get_query_type(query) == 'esql'

    def test_raises_value_error_for_unknown_object_type(self) -> None:
        """Test that get_query_type raises ValueError for unknown object type."""

        class UnknownQuery:
            """An unknown query type for testing."""

            def __init__(self) -> None:
                """Initialize the unknown query."""
                self.value: str = 'test'

        query = UnknownQuery()
        with pytest.raises(ValueError, match='Cannot determine query type from object'):
            _ = get_query_type(query)

    def test_raises_value_error_for_string_input(self) -> None:
        """Test that get_query_type raises ValueError for string input."""
        with pytest.raises(ValueError, match='Cannot determine query type from object'):
            _ = get_query_type(cast('Any', 'not a query'))

    def test_raises_value_error_for_none_input(self) -> None:
        """Test that get_query_type raises ValueError for None input."""
        with pytest.raises(ValueError, match='Cannot determine query type from object'):
            _ = get_query_type(cast('Any', None))
