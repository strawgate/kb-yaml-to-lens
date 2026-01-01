from typing import TypeVar

T = TypeVar('T')


def return_unless(var: bool | None, is_none: bool) -> bool:
    """Return `var` unless it's none, and then return the value passed for `is_none`.

    A simple helper that replaces `var if var is not None else default`

    Args:
        var: The variable to evaluate.
        is_none: The value to return if var is None.

    Returns:
        True if var is True, False if var is False, or is_none if var is None.

    """
    return var if var is not None else is_none
