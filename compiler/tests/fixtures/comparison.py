"""DeepDiff comparison utilities for fixture testing.

This module provides utilities for comparing compiled output against Kibana JSON fixtures
with appropriate normalization for dynamic values.

Usage Pattern:
    Individual tests use inline snapshots with dirty-equals matchers for acceptable differences.
    DeepDiff is used to identify structural differences between compiled and fixture JSON.

Example:
    from tests.fixtures.comparison import compare_visualization_state, normalize_layer_ids

    fixture = load_fixture_by_name('metric-basic-esql')
    fixture_viz = extract_visualization_state(fixture)

    # Compile from YAML
    compiled_viz = compile_metric_chart(config)

    # Compare (returns diff dict)
    diff = compare_visualization_state(compiled_viz, fixture_viz)

    # Snapshot the diff for tracking over time
    assert diff == snapshot({})  # Empty dict means perfect match
"""

import re
from typing import Any

from deepdiff import DeepDiff

# Regex patterns for dynamic values that should be normalized
UUID_PATTERN = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$')
LAYER_ID_PATTERN = re.compile(r'^layer_\d+$')
COLUMN_ID_PATTERN = re.compile(r'^(metric_formula_accessor|x_metric_formula_accessor)\d*(_breakdown_\d+)?$')

# Paths to exclude from comparison (these are expected to differ)
EXCLUDE_PATHS = [
    # Layer IDs are generated differently
    "root['layerId']",
    "root['layers'][*]['layerId']",
]

# Regex paths to exclude (for patterns)
EXCLUDE_REGEX_PATHS = [
    # Column/accessor IDs that contain generated UUIDs or sequential numbers
    r"root\['[^']*[Aa]ccessor[^']*'\]",
    r"root\['layers'\]\[\d+\]\['[^']*[Aa]ccessor[^']*'\]",
]


def is_uuid(value: Any) -> bool:
    """Check if a value is a UUID string."""
    if not isinstance(value, str):
        return False
    return UUID_PATTERN.match(value) is not None


def is_layer_id(value: Any) -> bool:
    """Check if a value is a layer ID like 'layer_0'."""
    if not isinstance(value, str):
        return False
    return LAYER_ID_PATTERN.match(value) is not None


def normalize_ids(data: Any, placeholder: str = 'NORMALIZED_ID') -> Any:
    """Recursively normalize UUIDs and generated IDs in a data structure.

    This is useful for comparing structures where the IDs themselves don't matter,
    only the structure and other values.

    Args:
        data: Data structure to normalize (dict, list, or scalar)
        placeholder: Placeholder string to use for normalized IDs

    Returns:
        New data structure with IDs normalized
    """
    if isinstance(data, dict):
        return {k: normalize_ids(v, placeholder) for k, v in data.items()}
    if isinstance(data, list):
        return [normalize_ids(item, placeholder) for item in data]
    if is_uuid(data):
        return placeholder
    if is_layer_id(data):
        return placeholder
    return data


def compare_visualization_state(
    compiled: dict[str, Any],
    fixture: dict[str, Any],
    *,
    ignore_order: bool = True,
    normalize: bool = False,
) -> dict[str, Any]:
    """Compare compiled visualization state against a fixture.

    Args:
        compiled: Compiled visualization state from the compiler
        fixture: Expected visualization state from the Kibana fixture
        ignore_order: Whether to ignore order in lists/dicts
        normalize: Whether to normalize IDs before comparison

    Returns:
        DeepDiff result as a dictionary. Empty dict means no differences.
    """
    if normalize:
        compiled = normalize_ids(compiled)
        fixture = normalize_ids(fixture)

    diff = DeepDiff(
        fixture,  # t1 = expected (fixture)
        compiled,  # t2 = actual (compiled)
        ignore_order=ignore_order,
        exclude_paths=EXCLUDE_PATHS,
        exclude_regex_paths=EXCLUDE_REGEX_PATHS,
        verbose_level=2,
    )

    # Convert to plain dict for snapshot compatibility
    return dict(diff) if diff else {}


def compare_layer(
    compiled_layer: dict[str, Any],
    fixture_layer: dict[str, Any],
    *,
    ignore_order: bool = True,
) -> dict[str, Any]:
    """Compare a single compiled layer against a fixture layer.

    Args:
        compiled_layer: Compiled layer from the compiler
        fixture_layer: Expected layer from the Kibana fixture
        ignore_order: Whether to ignore order in lists/dicts

    Returns:
        DeepDiff result as a dictionary
    """
    # Exclude layerId as it's always generated
    exclude_paths = ["root['layerId']"]

    # Also exclude accessor-related keys since IDs differ
    exclude_regex = [r"root\['[^']*[Aa]ccessor[^']*'\]"]

    diff = DeepDiff(
        fixture_layer,
        compiled_layer,
        ignore_order=ignore_order,
        exclude_paths=exclude_paths,
        exclude_regex_paths=exclude_regex,
        verbose_level=2,
    )

    return dict(diff) if diff else {}


def format_diff_for_snapshot(diff: dict[str, Any]) -> dict[str, Any]:
    """Format a DeepDiff result for cleaner snapshot output.

    Simplifies the diff structure to be more readable in inline snapshots.

    Args:
        diff: DeepDiff result dictionary

    Returns:
        Simplified diff dictionary
    """
    if not diff:
        return {}

    result: dict[str, Any] = {}

    # Values changed
    if 'values_changed' in diff:
        result['changed'] = {path: {'from': v['old_value'], 'to': v['new_value']} for path, v in diff['values_changed'].items()}

    # Items added (in compiled but not in fixture)
    if 'dictionary_item_added' in diff:
        result['added'] = list(diff['dictionary_item_added'].keys())

    # Items removed (in fixture but not in compiled)
    if 'dictionary_item_removed' in diff:
        result['missing'] = list(diff['dictionary_item_removed'].keys())

    # Type changes
    if 'type_changes' in diff:
        result['type_changed'] = {path: {'from': str(v['old_type']), 'to': str(v['new_type'])} for path, v in diff['type_changes'].items()}

    return result
