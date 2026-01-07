"""Shared utilities for the LSP server and CLI tools."""

from typing import Any


def get_panel_type(panel: Any) -> str:  # pyright: ignore[reportAny]
    """Extract the panel type, including chart type for Lens/ESQL panels.

    Args:
        panel: The panel object to extract type from

    Returns:
        The panel type string (e.g., 'pie', 'bar', 'markdown', 'search')
    """
    class_name = panel.__class__.__name__

    if hasattr(panel, 'lens') and panel.lens is not None:
        return getattr(panel.lens, 'type', 'lens')

    if hasattr(panel, 'esql') and panel.esql is not None:
        return getattr(panel.esql, 'type', 'esql')

    return class_name.replace('Panel', '').lower()
