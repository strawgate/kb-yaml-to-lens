"""Type guard utilities for validating untyped data structures.

This module provides runtime type validation helpers that narrow types from Any
to specific types with proper error handling. These utilities are particularly
useful when working with external data sources like YAML files or JSON APIs.
"""

# pyright: reportAny=false, reportUnknownVariableType=false

from typing import Any, TypeGuard


def ensure_dict(value: Any, context: str) -> dict[str, Any]:
    """Ensure a value is a dictionary.

    Args:
        value: The value to validate.
        context: Description of where this value came from (for error messages).

    Returns:
        The validated dictionary.

    Raises:
        TypeError: If the value is not a dictionary.

    """
    if not isinstance(value, dict):
        msg = f'{context} must be a dictionary, got {type(value).__name__}'
        raise TypeError(msg)
    return value


def ensure_str(value: Any, context: str) -> str:
    """Ensure a value is a string.

    Args:
        value: The value to validate.
        context: Description of where this value came from (for error messages).

    Returns:
        The validated string.

    Raises:
        TypeError: If the value is not a string.

    """
    if not isinstance(value, str):
        msg = f'{context} must be a string, got {type(value).__name__}'
        raise TypeError(msg)
    return value


def ensure_list(value: Any, context: str) -> list[Any]:
    """Ensure a value is a list.

    Args:
        value: The value to validate.
        context: Description of where this value came from (for error messages).

    Returns:
        The validated list.

    Raises:
        TypeError: If the value is not a list.

    """
    if not isinstance(value, list):
        msg = f'{context} must be a list, got {type(value).__name__}'
        raise TypeError(msg)
    return value


def is_str_dict(value: Any) -> TypeGuard[dict[str, Any]]:
    """Type guard that checks if a value is a dictionary with string keys.

    This is a TypeGuard that can be used with isinstance-style checking to
    narrow types. It verifies that all keys in the dictionary are strings.

    Args:
        value: The value to check.

    Returns:
        True if value is a dict with all string keys, False otherwise.

    """
    if not isinstance(value, dict):
        return False
    return all(isinstance(key, str) for key in value)
