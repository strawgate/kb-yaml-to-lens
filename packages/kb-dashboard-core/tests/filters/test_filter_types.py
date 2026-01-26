"""Tests for filter type discrimination utilities and filter validation."""

from typing import Any, cast

import pytest

from kb_dashboard_core.filters.config import (
    AndFilter,
    CustomFilter,
    ExistsFilter,
    NegateFilter,
    OrFilter,
    PhraseFilter,
    PhrasesFilter,
    RangeFilter,
    get_filter_type,
)


class TestGetFilterTypeFromObject:
    """Tests for get_filter_type with object inputs."""

    def test_identifies_exists_filter_from_object(self) -> None:
        """Test that get_filter_type identifies ExistsFilter from object."""
        filter_obj = ExistsFilter(exists='field_name')
        assert get_filter_type(filter_obj) == 'exists'

    def test_identifies_phrase_filter_from_object(self) -> None:
        """Test that get_filter_type identifies PhraseFilter from object."""
        filter_obj = PhraseFilter(field='status', equals='active')
        assert get_filter_type(filter_obj) == 'phrase'

    def test_identifies_phrases_filter_from_object(self) -> None:
        """Test that get_filter_type identifies PhrasesFilter from object."""
        filter_obj = PhrasesFilter(field='status', **{'in': ['active', 'pending']})
        assert get_filter_type(filter_obj) == 'phrases'

    def test_identifies_range_filter_from_object(self) -> None:
        """Test that get_filter_type identifies RangeFilter from object."""
        filter_obj = RangeFilter(field='age', gte='18')
        assert get_filter_type(filter_obj) == 'range'

    def test_identifies_custom_filter_from_object(self) -> None:
        """Test that get_filter_type identifies CustomFilter from object."""
        filter_obj = CustomFilter(dsl={'term': {'status': 'active'}})
        assert get_filter_type(filter_obj) == 'custom'

    def test_identifies_and_filter_from_object(self) -> None:
        """Test that get_filter_type identifies AndFilter from object."""
        filter_obj = AndFilter(
            **{
                'and': [
                    ExistsFilter(exists='field1'),
                    ExistsFilter(exists='field2'),
                ]
            }
        )
        assert get_filter_type(filter_obj) == 'and'

    def test_identifies_or_filter_from_object(self) -> None:
        """Test that get_filter_type identifies OrFilter from object."""
        filter_obj = OrFilter(
            **{
                'or': [
                    ExistsFilter(exists='field1'),
                    ExistsFilter(exists='field2'),
                ]
            }
        )
        assert get_filter_type(filter_obj) == 'or'

    def test_identifies_not_filter_from_object(self) -> None:
        """Test that get_filter_type identifies NegateFilter from object."""
        filter_obj = NegateFilter(**{'not': ExistsFilter(exists='field1')})
        assert get_filter_type(filter_obj) == 'not'

    def test_raises_error_for_unknown_object(self) -> None:
        """Test that get_filter_type raises ValueError for unknown object."""

        class UnknownFilter:
            """Unknown filter type for testing."""

            def __init__(self) -> None:
                """Initialize unknown filter."""
                self.value: str = 'test'

        filter_obj = UnknownFilter()
        with pytest.raises(ValueError, match='Cannot determine filter type from object'):
            _ = get_filter_type(filter_obj)

    def test_raises_error_for_string_input(self) -> None:
        """Test that get_filter_type raises ValueError for string input."""
        with pytest.raises(ValueError, match='Cannot determine filter type from object'):
            _ = get_filter_type(cast('Any', 'not a filter'))


class TestGetFilterTypeFromDict:
    """Tests for get_filter_type with dict inputs."""

    def test_raises_error_for_unknown_dict_keys(self) -> None:
        """Test that get_filter_type raises ValueError for unknown dict keys."""
        filter_dict = {'unknown_key': 'value'}
        with pytest.raises(ValueError, match='Cannot determine filter type from dict with keys'):
            _ = get_filter_type(filter_dict)

    def test_raises_error_for_empty_dict(self) -> None:
        """Test that get_filter_type raises ValueError for empty dict."""
        filter_dict: dict[str, object] = {}
        with pytest.raises(ValueError, match='Cannot determine filter type from dict with keys'):
            _ = get_filter_type(filter_dict)


class TestRangeFilterValidation:
    """Tests for RangeFilter validation."""

    def test_range_filter_accepts_gte(self) -> None:
        """Test that RangeFilter accepts gte value."""
        filter_obj = RangeFilter(field='age', gte='18')
        assert filter_obj.gte == '18'

    def test_range_filter_accepts_lte(self) -> None:
        """Test that RangeFilter accepts lte value."""
        filter_obj = RangeFilter(field='age', lte='65')
        assert filter_obj.lte == '65'

    def test_range_filter_accepts_gt(self) -> None:
        """Test that RangeFilter accepts gt value."""
        filter_obj = RangeFilter(field='age', gt='17')
        assert filter_obj.gt == '17'

    def test_range_filter_accepts_lt(self) -> None:
        """Test that RangeFilter accepts lt value."""
        filter_obj = RangeFilter(field='age', lt='66')
        assert filter_obj.lt == '66'

    def test_range_filter_accepts_multiple_values(self) -> None:
        """Test that RangeFilter accepts multiple range values."""
        filter_obj = RangeFilter(field='age', gte='18', lte='65')
        assert filter_obj.gte == '18'
        assert filter_obj.lte == '65'

    def test_range_filter_raises_error_when_no_values_provided(self) -> None:
        """Test that RangeFilter raises ValueError when no range values are provided."""
        with pytest.raises(ValueError, match="At least one of 'gte', 'lte', 'gt', or 'lt' must be provided"):
            _ = RangeFilter(field='age')
