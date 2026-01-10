"""Fixture test utilities for comparing compiled output against Kibana fixtures.

This module provides utilities for loading Kibana-generated fixture files,
normalizing compiled output, and comparing them using deepdiff.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from deepdiff import DeepDiff

if TYPE_CHECKING:
    from collections.abc import Sequence


# Default version for fixtures
DEFAULT_FIXTURE_VERSION = 'v9.2.0'

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
    """
    fixture_path = _FIXTURE_OUTPUT_DIR / version / f'{fixture_name}.json'
    if not fixture_path.exists():
        msg = f'Fixture not found: {fixture_path}'
        raise FileNotFoundError(msg)

    with fixture_path.open() as f:
        return json.load(f)


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

    # Build the normalized structure to match fixture format
    normalized: dict[str, Any] = {
        'title': compiled_panel.get('title', ''),
        'visualizationType': config.get('attributes', {}).get('visualizationType', ''),
        'references': config.get('attributes', {}).get('references', []),
        'state': config.get('attributes', {}).get('state', {}),
    }

    return normalized


def normalize_for_comparison(data: dict[str, Any]) -> dict[str, Any]:
    """Normalize data for comparison by removing dynamic/unstable fields.

    Args:
        data: Dictionary to normalize.

    Returns:
        Normalized dictionary with dynamic fields removed or replaced.
    """
    # Deep copy to avoid modifying original
    import copy

    # Remove fields that vary between compilations but aren't semantically meaningful
    # These are typically auto-generated IDs or ordering details
    return copy.deepcopy(data)


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


def get_yaml_fixture_files() -> list[Path]:
    """Get all YAML test fixture files.

    Returns:
        List of Path objects for each YAML fixture file.
    """
    yaml_dir = Path(__file__).parent / 'yaml'
    if not yaml_dir.exists():
        return []
    return sorted(yaml_dir.glob('*.yaml'))
