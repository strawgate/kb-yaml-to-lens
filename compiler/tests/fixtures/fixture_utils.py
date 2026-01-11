"""Fixture test utilities for comparing compiled output against Kibana fixtures.

This module provides utilities for normalizing compiled panel output and
comparing them against dynamically generated fixtures using DeepDiff.
"""

from __future__ import annotations

import copy
import re
from typing import TYPE_CHECKING, Any

from deepdiff import DeepDiff

if TYPE_CHECKING:
    from collections.abc import Sequence

# UUID pattern for matching dynamic layer IDs (case-insensitive)
UUID_PATTERN = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'

# Layer ID patterns
_UUID_REGEX = re.compile(rf'^{UUID_PATTERN}$')
_LAYER_N_REGEX = re.compile(r'^layer_\d+$')

# Patterns for normalizing paths in diff output (match UUIDs and layer_N with optional quotes)
_UUID_IN_PATH_REGEX = re.compile(rf"['\"]?{UUID_PATTERN}['\"]?")
_LAYER_N_IN_PATH_REGEX = re.compile(r"['\"]?layer_\d+['\"]?")


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

    # Build the normalized structure to match fixture format
    # Prefer title from embeddableConfig.attributes, fall back to panel-level title
    normalized: dict[str, Any] = {
        'title': attributes.get('title', compiled_panel.get('title', '')),
        'visualizationType': attributes.get('visualizationType', ''),
        'references': attributes.get('references', []),
        'state': attributes.get('state', {}),
    }

    return normalized


def _is_layer_id(value: str) -> bool:
    """Check if a string looks like a dynamic layer ID (UUID or layer_N)."""
    return bool(_UUID_REGEX.match(value) or _LAYER_N_REGEX.match(value))


def normalize_layer_ids(data: dict[str, Any], placeholder: str = '<LAYER>') -> dict[str, Any]:
    """Normalize dynamic layer IDs in a data structure for stable comparison.

    Replaces UUID-based layer IDs and layer_N patterns with a stable placeholder.
    This allows DeepDiff to match up corresponding layers between compiled
    output (uses UUIDs) and fixtures (use layer_N).

    Args:
        data: Panel configuration dictionary.
        placeholder: Placeholder to use for layer IDs.

    Returns:
        A deep copy with normalized layer IDs.
    """
    layer_mapping: dict[str, str] = {}

    def get_placeholder(layer_id: str) -> str:
        """Get or create a stable placeholder for a layer ID."""
        if layer_id not in layer_mapping:
            idx = len(layer_mapping)
            layer_mapping[layer_id] = f'{placeholder}_{idx}'
        return layer_mapping[layer_id]

    def normalize_value(value: Any) -> Any:
        """Recursively normalize values."""
        if isinstance(value, dict):
            return normalize_dict(value)
        if isinstance(value, list):
            return [normalize_value(item) for item in value]
        if isinstance(value, str) and _is_layer_id(value):
            return get_placeholder(value)
        return value

    def normalize_dict(d: dict[str, Any]) -> dict[str, Any]:
        """Normalize a dictionary, replacing layer ID keys and values."""
        result: dict[str, Any] = {}
        for key, value in sorted(d.items()):  # Sort for deterministic ordering
            # Check if key is a layer ID
            new_key = get_placeholder(key) if _is_layer_id(key) else key
            result[new_key] = normalize_value(value)
        return result

    return normalize_dict(copy.deepcopy(data))


def compare_with_deepdiff(
    compiled: dict[str, Any],
    fixture: dict[str, Any],
    exclude_regex_paths: Sequence[str] | None = None,
    normalize_layers: bool = True,
) -> DeepDiff:
    """Compare compiled output to fixture using DeepDiff with sensible defaults.

    Uses DeepDiff's built-in features for handling dynamic values:
    - ignore_order=True for list comparisons
    - verbose_level=2 for detailed output
    - Optional layer ID normalization for stable comparison

    Args:
        compiled: Compiled panel configuration.
        fixture: Generated fixture JSON.
        exclude_regex_paths: Optional regex patterns to exclude from comparison.
        normalize_layers: Whether to normalize layer IDs before comparison.

    Returns:
        A DeepDiff object containing the differences.
    """
    exclude_patterns = list(exclude_regex_paths) if exclude_regex_paths is not None else []

    # Optionally normalize layer IDs for stable comparison
    if normalize_layers:
        compiled = normalize_layer_ids(compiled)
        fixture = normalize_layer_ids(fixture)

    return DeepDiff(
        fixture,
        compiled,
        ignore_order=True,
        verbose_level=2,
        exclude_regex_paths=exclude_patterns,
    )


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

    def normalize_path(path: str) -> str:
        """Replace dynamic IDs in path with placeholders."""
        return _LAYER_N_IN_PATH_REGEX.sub('<LAYER>', _UUID_IN_PATH_REGEX.sub('<UUID>', path))

    result: dict[str, Any] = {}

    # Handle each type of diff
    if 'values_changed' in diff:
        values_changed: dict[str, dict[str, Any]] = {}
        for path, change in diff['values_changed'].items():
            normalized_path = normalize_path(path)
            values_changed[normalized_path] = {
                'old_value': change.get('old_value'),
                'new_value': change.get('new_value'),
            }
        result['values_changed'] = dict(sorted(values_changed.items()))

    if 'dictionary_item_added' in diff:
        added_items: dict[str, Any] = {}
        for path in diff['dictionary_item_added']:
            normalized_path = normalize_path(path)
            added_items[normalized_path] = diff['dictionary_item_added'][path]
        result['dictionary_item_added'] = dict(sorted(added_items.items()))

    if 'dictionary_item_removed' in diff:
        removed_items: dict[str, Any] = {}
        for path in diff['dictionary_item_removed']:
            normalized_path = normalize_path(path)
            removed_items[normalized_path] = diff['dictionary_item_removed'][path]
        result['dictionary_item_removed'] = dict(sorted(removed_items.items()))

    if 'iterable_item_added' in diff:
        iter_added: dict[str, Any] = {}
        for path, value in diff['iterable_item_added'].items():
            normalized_path = normalize_path(path)
            iter_added[normalized_path] = value
        result['iterable_item_added'] = dict(sorted(iter_added.items()))

    if 'iterable_item_removed' in diff:
        iter_removed: dict[str, Any] = {}
        for path, value in diff['iterable_item_removed'].items():
            normalized_path = normalize_path(path)
            iter_removed[normalized_path] = value
        result['iterable_item_removed'] = dict(sorted(iter_removed.items()))

    if 'type_changes' in diff:
        type_changes: dict[str, dict[str, str]] = {}
        for path, change in diff['type_changes'].items():
            normalized_path = normalize_path(path)
            type_changes[normalized_path] = {
                'old_type': str(change.get('old_type')),
                'new_type': str(change.get('new_type')),
            }
        result['type_changes'] = dict(sorted(type_changes.items()))

    return dict(sorted(result.items()))
