"""Tests for filter helper utilities."""

from dashboard_compiler.filters.view import KbnFilterState
from dashboard_compiler.shared.filter_utils import create_filter_state


class TestCreateFilterState:
    """Tests for create_filter_state helper."""

    def test_creates_state_when_not_nested(self) -> None:
        """Test that filter state is created when nested is False."""
        result = create_filter_state(nested=False)
        assert result is not None
        assert isinstance(result, KbnFilterState)

    def test_returns_none_when_nested(self) -> None:
        """Test that None is returned when nested is True."""
        result = create_filter_state(nested=True)
        assert result is None

    def test_creates_new_state_each_time(self) -> None:
        """Test that a new state object is created each time."""
        state1 = create_filter_state(nested=False)
        state2 = create_filter_state(nested=False)
        assert state1 is not state2
