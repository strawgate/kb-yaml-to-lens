"""Utility functions for compiling dashboard components."""
from typing import Any, TypeVar

T = TypeVar('T')


def return_if(var: bool | None, is_false: T, is_true: T, default: T) -> T:  # noqa: FBT001
    """Evaluate var and return a corresponding value.

    Args:
        var: The variable to evaluate.
        is_false: The value to return if var is False.
        is_true: The value to return if var is True.
        default: The value to return if var is None.

    Returns:
        The value corresponding to the evaluation of var.

    """
    return default if var is None else (is_true if var else is_false)


def return_if_equals(var: Any, equals: Any, is_false: T, is_true: T, is_none: T) -> T:  # noqa: ANN401
    """Evaluate var against a value and return a corresponding value.

    Args:
        var: The variable to evaluate.
        equals: The value to compare against.
        is_false: The value to return if var does not equal equals.
        is_true: The value to return if var equals equals.
        is_none: The value to return if var is None.

    Returns:
        The value corresponding to the evaluation of var.

    """
    if var is None:
        return is_none
    return is_true if var == equals else is_false
