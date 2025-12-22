"""Helper utilities for ID generation with stable hashing fallbacks."""

import uuid
from collections.abc import Sequence

from dashboard_compiler.shared.config import stable_id_generator


def generate_id(
    provided_id: str | None,
    stable_values: Sequence[str | int | float | None] | None = None,
    use_stable: bool = True,
) -> str:
    """Generate ID with fallback to UUID or stable hash.

    This helper standardizes ID generation across the codebase. It first checks
    for a user-provided ID, then falls back to stable ID generation (if enabled
    and values provided), and finally to a random UUID.

    Args:
        provided_id: User-provided ID (takes precedence if not None).
        stable_values: Values to hash for stable ID generation.
        use_stable: Whether to use stable ID or random UUID when no ID provided.

    Returns:
        A valid ID string.

    Examples:
        >>> generate_id("my-id")
        'my-id'
        >>> generate_id(None, ["panel", "title"], use_stable=True)  # doctest: +SKIP
        'a1b2c3d4-...'  # stable hash
        >>> generate_id(None, use_stable=False)  # doctest: +SKIP
        'f47ac10b-...'  # random UUID

    """
    if provided_id:
        return provided_id
    if use_stable and stable_values:
        return stable_id_generator(stable_values)
    return str(uuid.uuid4())
