"""Fixture test utilities for comparing compiled output against Kibana fixtures.

This module provides utilities for loading Kibana-generated fixture files,
normalizing compiled output, and comparing them using deepdiff.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

from deepdiff import DeepDiff

if TYPE_CHECKING:
    from collections.abc import Sequence


# Default version for fixtures
DEFAULT_FIXTURE_VERSION = 'v9.2.0'

# Shared UUID pattern for consistent matching across the module (case-insensitive)
_UUID_PATTERN_STR = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'

# Project paths
_TESTS_DIR = Path(__file__).parent.parent
_COMPILER_DIR = _TESTS_DIR.parent
_PROJECT_ROOT = _COMPILER_DIR.parent
_FIXTURE_OUTPUT_DIR = _PROJECT_ROOT / 'fixture-generator' / 'output'


def load_fixture(fixture_name: str, version: str = DEFAULT_FIXTURE_VERSION) -> dict[str, Any]:
    """Load a fixture JSON file from fixture-generator/output/.

    Args:
        fixture_name: Name of the fixture file without .json extension.
        version: Fixture version directory (default: v9.2.0).

    Returns:
        The parsed fixture JSON as a dictionary.

    Raises:
        FileNotFoundError: If the fixture file doesn't exist.
        ValueError: If the fixture JSON is invalid.
    """
    fixture_path = _FIXTURE_OUTPUT_DIR / version / f'{fixture_name}.json'
    if not fixture_path.exists():
        msg = f'Fixture not found: {fixture_path}'
        raise FileNotFoundError(msg)

    try:
        with fixture_path.open(encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        msg = f'Invalid JSON fixture: {fixture_path} ({e})'
        raise ValueError(msg) from e


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


def normalize_layer_ids(data: dict[str, Any], layer_id_placeholder: str = '<LAYER_ID>') -> dict[str, Any]:
    """Normalize dynamic layer IDs in a panel configuration for stable comparison.

    Replaces UUID-based layer IDs and layer_N patterns with a stable placeholder
    throughout the structure.

    Args:
        data: Panel configuration dictionary.
        layer_id_placeholder: Placeholder to use for layer IDs.

    Returns:
        Normalized dictionary with stable layer IDs.
    """
    uuid_pattern = re.compile(rf'^{_UUID_PATTERN_STR}$')
    layer_n_pattern = re.compile(r'^layer_\d+$')

    def is_uuid(value: str) -> bool:
        return uuid_pattern.match(value) is not None

    def is_layer_id_key(value: str) -> bool:
        return uuid_pattern.match(value) is not None or layer_n_pattern.match(value) is not None

    # First pass: collect all layer IDs used as keys in the 'layers' dict
    def collect_layer_ids(d: Any, layer_mapping: dict[str, str]) -> None:
        if isinstance(d, dict):
            for key, value in d.items():
                if key == 'layers' and isinstance(value, dict):
                    for layer_key in value:
                        if is_layer_id_key(layer_key) and layer_key not in layer_mapping:
                            layer_mapping[layer_key] = f'{layer_id_placeholder}_{len(layer_mapping)}'
                collect_layer_ids(value, layer_mapping)
        elif isinstance(d, list):
            for item in d:
                collect_layer_ids(item, layer_mapping)

    def normalize_value(value: Any, layer_mapping: dict[str, str]) -> Any:
        if isinstance(value, dict):
            return normalize_dict(value, layer_mapping)
        if isinstance(value, list):
            return [normalize_value(item, layer_mapping) for item in value]
        if isinstance(value, str):
            # Check if value is a known layer ID
            if value in layer_mapping:
                return layer_mapping[value]
            # Also normalize UUID values that might be layer IDs not yet in mapping
            if is_uuid(value):
                if value not in layer_mapping:
                    layer_mapping[value] = f'{layer_id_placeholder}_{len(layer_mapping)}'
                return layer_mapping[value]
        return value

    def normalize_dict(d: dict[str, Any], layer_mapping: dict[str, str]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in d.items():
            # Check if key is a layer ID (UUID or layer_N pattern)
            if is_layer_id_key(key):
                if key not in layer_mapping:
                    layer_mapping[key] = f'{layer_id_placeholder}_{len(layer_mapping)}'
                new_key = layer_mapping[key]
            else:
                new_key = key
            result[new_key] = normalize_value(value, layer_mapping)
        return result

    layer_mapping: dict[str, str] = {}
    data_copy = copy.deepcopy(data)

    # First pass: collect layer IDs from 'layers' dicts
    collect_layer_ids(data_copy, layer_mapping)

    # Second pass: normalize all references
    return normalize_dict(data_copy, layer_mapping)


def compare_to_fixture(
    compiled: dict[str, Any],
    fixture: dict[str, Any],
    ignore_paths: Sequence[str] | None = None,
) -> tuple[bool, DeepDiff]:
    """Compare compiled output to fixture using deepdiff.

    Args:
        compiled: Normalized compiled panel configuration.
        fixture: Loaded fixture JSON.
        ignore_paths: Optional list of paths to ignore in comparison.

    Returns:
        A tuple of (matches: bool, diff: DeepDiff).
        matches is True if there are no differences.
    """
    exclude_regex_paths = list(ignore_paths) if ignore_paths is not None else []

    diff = DeepDiff(
        fixture,
        compiled,
        ignore_order=True,
        exclude_regex_paths=exclude_regex_paths,
        verbose_level=2,
    )

    matches = len(diff) == 0
    return matches, diff


def diff_to_dict(diff: DeepDiff) -> dict[str, Any]:  # noqa: PLR0912
    """Convert a DeepDiff result to a stable, serializable dictionary.

    This function converts the DeepDiff result into a plain dictionary
    that can be used with inline_snapshot for explicit assertions.

    Args:
        diff: The DeepDiff result to convert.

    Returns:
        A dictionary with sorted keys containing the differences.
    """

    def normalize_path(path: str) -> str:
        """Normalize path by replacing UUIDs with placeholder."""
        uuid_pattern = rf"['\"]?{_UUID_PATTERN_STR}['\"]?"
        return re.sub(uuid_pattern, '<UUID>', path)

    if len(diff) == 0:
        return {}

    result: dict[str, Any] = {}

    if 'values_changed' in diff:
        values_changed: dict[str, dict[str, Any]] = {}
        for path, change in diff['values_changed'].items():  # pyright: ignore[reportUnknownMemberType]
            normalized_path = normalize_path(path)
            values_changed[normalized_path] = {
                'old_value': change.get('old_value'),  # pyright: ignore[reportUnknownMemberType]
                'new_value': change.get('new_value'),  # pyright: ignore[reportUnknownMemberType]
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
        for path, value in diff['iterable_item_added'].items():  # pyright: ignore[reportUnknownMemberType]
            normalized_path = normalize_path(path)
            iter_added[normalized_path] = value
        result['iterable_item_added'] = dict(sorted(iter_added.items()))

    if 'iterable_item_removed' in diff:
        iter_removed: dict[str, Any] = {}
        for path, value in diff['iterable_item_removed'].items():  # pyright: ignore[reportUnknownMemberType]
            normalized_path = normalize_path(path)
            iter_removed[normalized_path] = value
        result['iterable_item_removed'] = dict(sorted(iter_removed.items()))

    if 'type_changes' in diff:
        type_changes: dict[str, dict[str, str]] = {}
        for path, change in diff['type_changes'].items():  # pyright: ignore[reportUnknownMemberType]
            normalized_path = normalize_path(path)
            type_changes[normalized_path] = {
                'old_type': str(change.get('old_type')),  # pyright: ignore[reportUnknownMemberType]
                'new_type': str(change.get('new_type')),  # pyright: ignore[reportUnknownMemberType]
            }
        result['type_changes'] = dict(sorted(type_changes.items()))

    return dict(sorted(result.items()))


def format_diff_report(diff: DeepDiff) -> str:
    """Format a DeepDiff result into a human-readable report.

    Args:
        diff: The DeepDiff result to format.

    Returns:
        A formatted string describing the differences.
    """
    if len(diff) == 0:
        return 'No differences found.'

    lines: list[str] = ['Differences found:']

    if 'values_changed' in diff:
        lines.append('\n=== Values Changed ===')
        for path, change in diff['values_changed'].items():  # pyright: ignore[reportUnknownMemberType]
            lines.append(f'  {path}:')
            lines.append(f'    fixture: {change.get("old_value")!r}')  # pyright: ignore[reportUnknownMemberType]
            lines.append(f'    compiled: {change.get("new_value")!r}')  # pyright: ignore[reportUnknownMemberType]

    if 'dictionary_item_added' in diff:
        lines.append('\n=== Added in Compiled (not in fixture) ===')
        lines.extend(f'  {path}' for path in diff['dictionary_item_added'])

    if 'dictionary_item_removed' in diff:
        lines.append('\n=== Missing in Compiled (present in fixture) ===')
        lines.extend(f'  {path}' for path in diff['dictionary_item_removed'])

    if 'iterable_item_added' in diff:
        lines.append('\n=== Items Added to Lists ===')
        for path, value in diff['iterable_item_added'].items():  # pyright: ignore[reportUnknownMemberType]
            lines.append(f'  {path}: {value!r}')

    if 'iterable_item_removed' in diff:
        lines.append('\n=== Items Removed from Lists ===')
        for path, value in diff['iterable_item_removed'].items():  # pyright: ignore[reportUnknownMemberType]
            lines.append(f'  {path}: {value!r}')

    if 'type_changes' in diff:
        lines.append('\n=== Type Changes ===')
        for path, change in diff['type_changes'].items():  # pyright: ignore[reportUnknownMemberType]
            lines.append(f'  {path}:')
            lines.append(f'    fixture type: {change.get("old_type")}')  # pyright: ignore[reportUnknownMemberType]
            lines.append(f'    compiled type: {change.get("new_type")}')  # pyright: ignore[reportUnknownMemberType]

    return '\n'.join(lines)


def get_fixture_files(version: str = DEFAULT_FIXTURE_VERSION) -> list[Path]:
    """Get all fixture JSON files for a given version.

    Args:
        version: Fixture version directory (default: v9.2.0).

    Returns:
        List of Path objects for each fixture file.
    """
    fixture_dir = _FIXTURE_OUTPUT_DIR / version
    if not fixture_dir.exists():
        return []
    return sorted(fixture_dir.glob('*.json'))
