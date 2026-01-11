"""ID helper utilities."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dashboard_compiler.shared.config import IDMixin


def get_guaranteed_id(obj: 'IDMixin') -> str:
    """Get the ID from an IDMixin object, guaranteed to be non-None.

    IDMixin.model_post_init guarantees that id is always set after construction.
    This helper provides a type-safe way to access it without None checks.

    Args:
        obj: An object that inherits from IDMixin.

    Returns:
        The object's id, which is guaranteed to be a string.

    Raises:
        RuntimeError: If id is unexpectedly None (should never happen with IDMixin).
    """
    if obj.id is None:
        msg = f'{type(obj).__name__}.id is unexpectedly None - IDMixin should have set it'
        raise RuntimeError(msg)
    return obj.id
