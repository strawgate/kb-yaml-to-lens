"""Fixture test utilities for comparing compiled output against Kibana fixtures.

This module provides utilities for comparing compiled panel output
against dynamically generated fixtures using DeepDiff.
"""

from __future__ import annotations

import re
from typing import Any

from deepdiff import DeepDiff
from deepdiff.operator import BaseOperator

# UUID pattern for matching dynamic layer IDs
UUID_PATTERN = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
_UUID_REGEX = re.compile(rf'^{UUID_PATTERN}$')
_LAYER_N_REGEX = re.compile(r'^layer_\d+$')

# Patterns for normalizing paths in diff output
_UUID_IN_PATH_REGEX = re.compile(rf"['\"]?{UUID_PATTERN}['\"]?")
_LAYER_N_IN_PATH_REGEX = re.compile(r"['\"]?layer_\d+['\"]?")


def _is_layer_id(value: str) -> bool:
    """Check if a string looks like a dynamic layer ID (UUID or layer_N)."""
    return bool(_UUID_REGEX.match(value) or _LAYER_N_REGEX.match(value))


class LayerIdOperator(BaseOperator):
    """DeepDiff operator that treats layer IDs (UUIDs and layer_N) as equivalent.

    This allows comparing structures where one uses UUIDs and the other uses
    sequential layer_N identifiers without heavy-handed normalization.
    """

    def match(self, level: Any) -> bool:
        """Match when comparing two layer ID strings."""
        t1, t2 = level.t1, level.t2
        return isinstance(t1, str) and isinstance(t2, str) and _is_layer_id(t1) and _is_layer_id(t2)

    def give_up_diffing(self, level: Any, diff_instance: Any) -> bool:  # noqa: ARG002
        """Consider layer IDs equivalent regardless of format."""
        return True


def normalize_compiled_panel(compiled_panel: dict[str, Any]) -> dict[str, Any]:
    """Normalize a compiled panel's embeddableConfig for fixture comparison.

    Extracts the embeddableConfig from a compiled panel and normalizes it
    to match the fixture format.

    Args:
        compiled_panel: A panel from the compiled dashboard's panelsJSON.

    Returns:
        Normalized embeddableConfig dictionary.
    """
    config = compiled_panel.get('embeddableConfig', {})
    attributes = config.get('attributes', {})

    return {
        'title': attributes.get('title', compiled_panel.get('title', '')),
        'visualizationType': attributes.get('visualizationType', ''),
        'references': attributes.get('references', []),
        'state': attributes.get('state', {}),
    }


def compare_with_deepdiff(
    compiled: dict[str, Any],
    fixture: dict[str, Any],
) -> DeepDiff:
    """Compare compiled output to fixture using DeepDiff.

    Uses a custom operator to treat layer IDs (UUIDs vs layer_N) as equivalent,
    avoiding the need for heavy-handed normalization.

    Args:
        compiled: Compiled panel configuration.
        fixture: Generated fixture JSON.

    Returns:
        A DeepDiff object containing the differences.
    """
    return DeepDiff(
        fixture,
        compiled,
        ignore_order=True,
        verbose_level=2,
        custom_operators=[LayerIdOperator()],
    )


def _normalize_path(path: str) -> str:
    """Replace dynamic IDs in path with stable placeholders."""
    path = _UUID_IN_PATH_REGEX.sub('<LAYER>', path)
    return _LAYER_N_IN_PATH_REGEX.sub('<LAYER>', path)


def normalize_diff_paths(diff: DeepDiff) -> dict[str, Any]:  # noqa: PLR0912
    """Convert DeepDiff result to a dict with normalized paths for stable snapshots.

    Replaces dynamic values (UUIDs, layer_N patterns) in paths with stable
    placeholders so snapshots remain consistent across runs.

    Args:
        diff: The DeepDiff result to normalize.

    Returns:
        A dictionary with normalized paths, suitable for inline_snapshot.
    """
    if len(diff) == 0:
        return {}

    result: dict[str, Any] = {}

    if 'values_changed' in diff:
        values_changed: dict[str, dict[str, Any]] = {}
        for path, change in diff['values_changed'].items():  # pyright: ignore[reportUnknownMemberType]
            values_changed[_normalize_path(path)] = {
                'old_value': change.get('old_value'),  # pyright: ignore[reportUnknownMemberType]
                'new_value': change.get('new_value'),  # pyright: ignore[reportUnknownMemberType]
            }
        result['values_changed'] = dict(sorted(values_changed.items()))

    if 'dictionary_item_added' in diff:
        added: dict[str, Any] = {}
        for path in diff['dictionary_item_added']:
            added[_normalize_path(path)] = diff['dictionary_item_added'][path]
        result['dictionary_item_added'] = dict(sorted(added.items()))

    if 'dictionary_item_removed' in diff:
        removed: dict[str, Any] = {}
        for path in diff['dictionary_item_removed']:
            removed[_normalize_path(path)] = diff['dictionary_item_removed'][path]
        result['dictionary_item_removed'] = dict(sorted(removed.items()))

    if 'iterable_item_added' in diff:
        iter_added: dict[str, Any] = {}
        for path, value in diff['iterable_item_added'].items():  # pyright: ignore[reportUnknownMemberType]
            iter_added[_normalize_path(path)] = value
        result['iterable_item_added'] = dict(sorted(iter_added.items()))

    if 'iterable_item_removed' in diff:
        iter_removed: dict[str, Any] = {}
        for path, value in diff['iterable_item_removed'].items():  # pyright: ignore[reportUnknownMemberType]
            iter_removed[_normalize_path(path)] = value
        result['iterable_item_removed'] = dict(sorted(iter_removed.items()))

    if 'type_changes' in diff:
        type_changes: dict[str, dict[str, str]] = {}
        for path, change in diff['type_changes'].items():  # pyright: ignore[reportUnknownMemberType]
            type_changes[_normalize_path(path)] = {
                'old_type': str(change.get('old_type')),  # pyright: ignore[reportUnknownMemberType]
                'new_type': str(change.get('new_type')),  # pyright: ignore[reportUnknownMemberType]
            }
        result['type_changes'] = dict(sorted(type_changes.items()))

    return dict(sorted(result.items()))
