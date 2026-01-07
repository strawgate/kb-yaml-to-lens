"""Helper utilities for filter compilation."""

from dashboard_compiler.filters.view import KbnFilterState


def create_filter_state(nested: bool) -> KbnFilterState | None:
    """Create filter state if not nested.

    This helper standardizes the pattern of creating filter state objects
    only when filters are not nested within other filters.

    Args:
        nested: Whether the filter is nested within another filter.

    Returns:
        A KbnFilterState object if not nested, otherwise None.

    Examples:
        >>> state = create_filter_state(nested=False)
        >>> state is not None
        True
        >>> create_filter_state(nested=True) is None
        True

    """
    return KbnFilterState() if not nested else None
