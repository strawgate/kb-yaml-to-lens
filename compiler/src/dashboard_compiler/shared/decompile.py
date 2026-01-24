"""Shared decompilation utilities."""

import json
from typing import Any

from dashboard_compiler.shared.view import KbnReference


def parse_stringified_json(field: str | dict[str, Any] | list[Any] | None) -> dict[str, Any] | list[Any] | None:
    """Parse a field that may be stringified JSON or already parsed.

    Kibana stores some fields as stringified JSON (panelsJSON, optionsJSON, etc.).
    This handles both string and already-parsed inputs.

    Args:
        field: The field to parse (may be a JSON string, dict, list, or None).

    Returns:
        Parsed dict/list or None if the input was None.

    Raises:
        TypeError: If field is not a supported type.

    """
    if field is None:
        return None
    if isinstance(field, str):
        return json.loads(field)  # pyright: ignore[reportAny]
    if isinstance(field, (dict, list)):  # pyright: ignore[reportUnnecessaryIsInstance]
        return field
    msg = f'Unsupported field type: {type(field).__name__}'
    raise TypeError(msg)


class ReferenceResolver:
    """Resolve Kibana references from the dashboard references array.

    Kibana namespaces panel references like 'panel-123:dataView'.
    This class builds a lookup map to resolve them back to IDs.
    """

    def __init__(self, references: list[KbnReference]) -> None:
        """Initialize with dashboard references.

        Args:
            references: List of Kibana reference objects from the dashboard.

        """
        self._by_name: dict[str, KbnReference] = {ref.name: ref for ref in references}
        self._by_type_and_id: dict[tuple[str, str], KbnReference] = {(ref.type, ref.id): ref for ref in references}

    def resolve_by_name(self, name: str) -> KbnReference | None:
        """Resolve a reference by its name.

        Args:
            name: The reference name to look up.

        Returns:
            The resolved KbnReference object, or None if not found.

        """
        return self._by_name.get(name)

    def resolve_panel_reference(self, panel_id: str, ref_suffix: str) -> str | None:
        """Resolve a panel-namespaced reference to get the target ID.

        Args:
            panel_id: The panel's ID (e.g., '123').
            ref_suffix: The reference suffix (e.g., 'dataView').

        Returns:
            The resolved reference ID, or None if not found.

        """
        name = f'{panel_id}:{ref_suffix}'
        ref = self._by_name.get(name)
        return ref.id if ref is not None else None

    def get_data_view_id(self, panel_id: str) -> str | None:
        """Get the data view ID for a panel.

        Args:
            panel_id: The panel's ID.

        Returns:
            The data view ID, or None if not found.

        """
        return self.resolve_panel_reference(panel_id, 'indexpattern-datasource-layer-layer')
