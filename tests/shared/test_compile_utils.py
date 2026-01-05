"""Unit tests for shared compilation utility functions."""

from dashboard_compiler.shared.compile import (
    return_if,
    return_if_equals,
    return_unless,
    split_dimensions,
)


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


def test_return_if_true() -> None:
    """Test return_if when var is True."""
    assert return_if(True, 'false_val', 'true_val', 'default') == 'true_val'


def test_return_if_false() -> None:
    """Test return_if when var is False."""
    assert return_if(False, 'false_val', 'true_val', 'default') == 'false_val'


def test_return_if_none() -> None:
    """Test return_if when var is None."""
    assert return_if(None, 'false_val', 'true_val', 'default') == 'default'


def test_return_if_with_numbers() -> None:
    """Test return_if with numeric values."""
    assert return_if(True, 0, 100, 50) == 100
    assert return_if(False, 0, 100, 50) == 0
    assert return_if(None, 0, 100, 50) == 50


def test_return_if_equals_matching() -> None:
    """Test return_if_equals when var equals the comparison value."""
    assert return_if_equals('test', 'test', 'no', 'yes', 'none') == 'yes'


def test_return_if_equals_not_matching() -> None:
    """Test return_if_equals when var does not equal the comparison value."""
    assert return_if_equals('test', 'other', 'no', 'yes', 'none') == 'no'


def test_return_if_equals_none() -> None:
    """Test return_if_equals when var is None."""
    assert return_if_equals(None, 'test', 'no', 'yes', 'none') == 'none'


def test_return_if_equals_with_numbers() -> None:
    """Test return_if_equals with numeric values."""
    assert return_if_equals(42, 42, 0, 100, -1) == 100
    assert return_if_equals(42, 99, 0, 100, -1) == 0
    assert return_if_equals(None, 42, 0, 100, -1) == -1


def test_return_if_equals_with_zero() -> None:
    """Test return_if_equals with zero value to ensure it's not treated as falsy."""
    assert return_if_equals(0, 0, 'not_zero', 'is_zero', 'is_none') == 'is_zero'
    assert return_if_equals(0, 1, 'not_zero', 'is_zero', 'is_none') == 'not_zero'


def test_return_if_equals_with_empty_string() -> None:
    """Test return_if_equals with empty string to ensure it's not treated as falsy."""
    assert return_if_equals('', '', 'not_empty', 'is_empty', 'is_none') == 'is_empty'
    assert return_if_equals('', 'text', 'not_empty', 'is_empty', 'is_none') == 'not_empty'


def test_split_dimensions_with_multiple() -> None:
    """Test splitting dimensions into primary and secondary."""
    all_dims = ['dim1', 'dim2', 'dim3']
    primary, secondary = split_dimensions(all_dims)
    assert primary == ['dim1']
    assert secondary == ['dim2', 'dim3']


def test_split_dimensions_with_single() -> None:
    """Test splitting with single dimension."""
    all_dims = ['dim1']
    primary, secondary = split_dimensions(all_dims)
    assert primary == ['dim1']
    assert secondary is None


def test_split_dimensions_with_empty() -> None:
    """Test splitting with empty list."""
    all_dims: list[str] = []
    primary, secondary = split_dimensions(all_dims)
    assert primary == []
    assert secondary is None
