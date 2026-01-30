"""Tests for default value helper utilities."""

from kb_dashboard_core.shared.defaults import (
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
