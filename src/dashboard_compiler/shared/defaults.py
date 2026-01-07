"""Helper utilities for handling default values in optional fields."""

from typing import TypeVar

T = TypeVar('T')


def default_if_none(value: T | None, default: T) -> T:
    """Return value if not None, otherwise return default.

    Args:
        value: The value to check.
        default: The default value to return if value is None.

    Returns:
        The value if not None, otherwise the default.

    Examples:
        >>> default_if_none(5, 10)
        5
        >>> default_if_none(None, 10)
        10

    """
    return value if value is not None else default


def default_false(value: bool | None) -> bool:
    """Return value or False if None.

    Args:
        value: The boolean value to check.

    Returns:
        The value if not None, otherwise False.

    Examples:
        >>> default_false(True)
        True
        >>> default_false(None)
        False

    """
    return value if value is not None else False


def default_true(value: bool | None) -> bool:
    """Return value or True if None.

    Args:
        value: The boolean value to check.

    Returns:
        The value if not None, otherwise True.

    Examples:
        >>> default_true(False)
        False
        >>> default_true(None)
        True

    """
    return value if value is not None else True


def default_none[T](value: T | None) -> T | None:
    """Return value or None if None.

    This helper provides clarity and consistency with default_true/default_false
    when working with optional fields, particularly in Pydantic models with
    OmitIfNone metadata.

    Args:
        value: The value to check.

    Returns:
        The value if not None, otherwise None.

    Examples:
        >>> default_none("hello")
        'hello'
        >>> default_none(5)
        5
        >>> default_none(None)
        None

    """
    return value if value is not None else None
