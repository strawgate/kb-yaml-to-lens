"""Helper utilities for ID generation."""

import uuid


def generate_id(provided_id: str | None) -> str:
    """Generate ID with fallback to random UUID.

    This helper standardizes ID generation across the codebase. It returns
    the provided ID if given, otherwise generates a random UUID.

    Args:
        provided_id: User-provided ID (takes precedence if not None).

    Returns:
        A valid ID string.

    Examples:
        >>> generate_id("my-id")
        'my-id'
        >>> generate_id(None)  # doctest: +SKIP
        'f47ac10b-...'  # random UUID

    """
    if provided_id is not None:
        return provided_id
    return str(uuid.uuid4())
