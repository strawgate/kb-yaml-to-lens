"""Unit tests for shared compilation utility functions."""

from dashboard_compiler.shared.compile import return_unless


def test_return_unless_true() -> None:
    """Test return_unless when var is True."""
    assert return_unless(True, False) is True


def test_return_unless_false() -> None:
    """Test return_unless when var is False."""
    assert return_unless(False, True) is False


def test_return_unless_none_with_true_default() -> None:
    """Test return_unless when var is None and default is True."""
    assert return_unless(None, True) is True


def test_return_unless_none_with_false_default() -> None:
    """Test return_unless when var is None and default is False."""
    assert return_unless(None, False) is False
