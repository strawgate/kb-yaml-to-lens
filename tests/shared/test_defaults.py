"""Tests for default value helper utilities."""

from dashboard_compiler.shared.defaults import (
    default_empty_list,
    default_empty_str,
    default_false,
    default_if_none,
    default_true,
)


class TestDefaultIfNone:
    """Tests for default_if_none helper."""

    def test_returns_value_when_not_none(self) -> None:
        """Test that value is returned when not None."""
        assert default_if_none(5, 10) == 5
        assert default_if_none('hello', 'world') == 'hello'
        assert default_if_none([], ['default']) == []
        assert default_if_none(False, True) is False

    def test_returns_default_when_none(self) -> None:
        """Test that default is returned when value is None."""
        assert default_if_none(None, 10) == 10
        assert default_if_none(None, 'default') == 'default'
        assert default_if_none(None, [1, 2, 3]) == [1, 2, 3]


class TestDefaultFalse:
    """Tests for default_false helper."""

    def test_returns_value_when_true(self) -> None:
        """Test that True is returned when value is True."""
        assert default_false(True) is True

    def test_returns_false_when_false(self) -> None:
        """Test that False is returned when value is False."""
        assert default_false(False) is False

    def test_returns_false_when_none(self) -> None:
        """Test that False is returned when value is None."""
        assert default_false(None) is False


class TestDefaultTrue:
    """Tests for default_true helper."""

    def test_returns_value_when_false(self) -> None:
        """Test that False is returned when value is False."""
        assert default_true(False) is False

    def test_returns_true_when_true(self) -> None:
        """Test that True is returned when value is True."""
        assert default_true(True) is True

    def test_returns_true_when_none(self) -> None:
        """Test that True is returned when value is None."""
        assert default_true(None) is True


class TestDefaultEmptyList:
    """Tests for default_empty_list helper."""

    def test_returns_list_when_not_none(self) -> None:
        """Test that list is returned when not None."""
        test_list = [1, 2, 3]
        assert default_empty_list(test_list) == test_list
        assert default_empty_list(['a', 'b']) == ['a', 'b']

    def test_returns_empty_list_when_none(self) -> None:
        """Test that empty list is returned when value is None."""
        result = default_empty_list(None)
        assert result == []
        assert isinstance(result, list)

    def test_returns_same_list_when_empty(self) -> None:
        """Test that empty list is returned when value is empty list."""
        assert default_empty_list([]) == []


class TestDefaultEmptyStr:
    """Tests for default_empty_str helper."""

    def test_returns_string_when_not_none(self) -> None:
        """Test that string is returned when not None."""
        assert default_empty_str('hello') == 'hello'
        assert default_empty_str('world') == 'world'

    def test_returns_empty_string_when_none(self) -> None:
        """Test that empty string is returned when value is None."""
        result = default_empty_str(None)
        assert result == ''
        assert isinstance(result, str)

    def test_returns_same_string_when_empty(self) -> None:
        """Test that empty string is returned when value is empty string."""
        assert default_empty_str('') == ''
