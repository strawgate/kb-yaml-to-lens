#!/usr/bin/env python3
# pyright: reportAny=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportMissingTypeStubs=false
# Script receives untyped YAML data from file parsing
"""Remove redundant position properties from dashboard YAML files.

This script identifies dashboards where manually-specified positions match
what the auto-layout algorithm would produce, and removes those position
properties to simplify future maintenance.

Usage:
    python3 scripts/remove_redundant_positions.py [--dry-run] [path...]

Arguments:
    path     Optional paths to process. If not provided, processes all
             dashboards in inputs/crowdstrike/, inputs/crowdstrike-modern/,
             and inputs/elastic_agent/.

Options:
    --dry-run    Report which dashboards would be modified without making changes.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, get_args

from ruamel.yaml.comments import CommentedMap, CommentedSeq

from dashboard_compiler.panels.auto_layout import LayoutAlgorithm, create_layout_engine
from dashboard_compiler.panels.config import (
    GRID_WIDTH_EIGHTH,
    GRID_WIDTH_HALF,
    GRID_WIDTH_QUARTER,
    GRID_WIDTH_SIXTH,
    GRID_WIDTH_THIRD,
    GRID_WIDTH_WHOLE,
)
from dashboard_compiler.yaml_roundtrip import dump_roundtrip, load_roundtrip

logger = logging.getLogger(__name__)

# Default input directories relative to compiler/
DEFAULT_INPUT_DIRS = [
    'inputs/crowdstrike',
    'inputs/crowdstrike-modern',
    'inputs/elastic_agent',
]

# Map of semantic width values to grid units
SEMANTIC_WIDTHS = {
    'whole': GRID_WIDTH_WHOLE,
    'half': GRID_WIDTH_HALF,
    'third': GRID_WIDTH_THIRD,
    'quarter': GRID_WIDTH_QUARTER,
    'sixth': GRID_WIDTH_SIXTH,
    'eighth': GRID_WIDTH_EIGHTH,
}

DEFAULT_WIDTH = GRID_WIDTH_QUARTER  # 12
DEFAULT_HEIGHT = 8


def _safe_int(value: Any, default: int) -> int:
    """Safely convert a value to int, returning default on failure."""
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def resolve_width(w: Any) -> int:
    """Resolve a width value (int or semantic string) to grid units."""
    if isinstance(w, int):
        return w
    if isinstance(w, str) and w in SEMANTIC_WIDTHS:
        return SEMANTIC_WIDTHS[w]
    # Unexpected type or unknown semantic - could indicate config error
    logger.warning(f'Unexpected width value: {w!r} (type: {type(w).__name__}), using default {DEFAULT_WIDTH}')
    return DEFAULT_WIDTH


def extract_panel_size_from_yaml(panel: CommentedMap) -> tuple[int, int]:
    """Extract panel size (w, h) from YAML panel data.

    Handles both formats:
    - Expanded: size: {w: 12, h: 8}
    - Inline: grid: {x: 0, y: 0, w: 12, h: 8}

    Args:
        panel: The panel CommentedMap from YAML.

    Returns:
        Tuple of (width, height).
    """
    # Check for grid format (Elastic Agent style)
    grid = panel.get('grid')
    if isinstance(grid, CommentedMap):
        w = grid.get('w', DEFAULT_WIDTH)
        h = grid.get('h', DEFAULT_HEIGHT)
        return (resolve_width(w), _safe_int(h, DEFAULT_HEIGHT))

    # Check for size format (CrowdStrike style)
    size = panel.get('size')
    if isinstance(size, CommentedMap):
        w = size.get('w', DEFAULT_WIDTH)
        h = size.get('h', DEFAULT_HEIGHT)
        return (resolve_width(w), _safe_int(h, DEFAULT_HEIGHT))

    # Default size
    return (DEFAULT_WIDTH, DEFAULT_HEIGHT)


def extract_panel_position_from_yaml(panel: CommentedMap) -> tuple[int, int] | None:
    """Extract panel position (x, y) from YAML panel data if present.

    Handles both formats:
    - Expanded: position: {x: 0, y: 0}
    - Inline: grid: {x: 0, y: 0, w: 12, h: 8}

    Args:
        panel: The panel CommentedMap from YAML.

    Returns:
        Tuple of (x, y) if position is set, None otherwise.
    """
    # Check for grid format (Elastic Agent style)
    grid = panel.get('grid')
    if isinstance(grid, CommentedMap):
        x_val, y_val = grid.get('x'), grid.get('y')
        if x_val is not None and y_val is not None:
            return (int(x_val), int(y_val))

    # Check for position format (CrowdStrike style)
    position = panel.get('position')
    if isinstance(position, CommentedMap):
        x_val, y_val = position.get('x'), position.get('y')
        if x_val is not None and y_val is not None:
            return (int(x_val), int(y_val))

    return None


def compute_auto_positions_from_yaml(panels: CommentedSeq, algorithm: LayoutAlgorithm = 'up-left') -> dict[int, tuple[int, int]]:
    """Compute auto-layout positions for all panels based on their sizes.

    Args:
        panels: The panels CommentedSeq from YAML.
        algorithm: The layout algorithm to use.

    Returns:
        Dict mapping panel index to computed (x, y) position.
    """
    engine = create_layout_engine(algorithm)

    position_map: dict[int, tuple[int, int]] = {}
    for idx, panel in enumerate(panels):
        if not isinstance(panel, CommentedMap):
            continue
        w, h = extract_panel_size_from_yaml(panel)
        x, y = engine.add_panel(w, h)
        position_map[idx] = (x, y)

    return position_map


def _make_error_result(error: str, dashboard_name: str) -> dict[str, Any]:
    """Create an error result dict."""
    return {'can_remove': False, 'error': error, 'dashboard_name': dashboard_name}


def _get_layout_algorithm(dashboard: CommentedMap) -> LayoutAlgorithm:
    """Extract layout algorithm from dashboard settings."""
    valid_algorithms = get_args(LayoutAlgorithm)
    settings = dashboard.get('settings')
    if isinstance(settings, CommentedMap):
        algo = settings.get('layout_algorithm')
        if algo in valid_algorithms:
            return algo
    return 'up-left'


def _check_panel_positions(panels: CommentedSeq, auto_positions: dict[int, tuple[int, int]]) -> tuple[int, list[dict[str, Any]]]:
    """Check each panel for position mismatches."""
    mismatches: list[dict[str, Any]] = []
    positioned_count = 0

    for idx, panel in enumerate(panels):
        if not isinstance(panel, CommentedMap):
            continue

        manual_pos = extract_panel_position_from_yaml(panel)
        if manual_pos is None:
            continue

        positioned_count += 1
        auto_pos = auto_positions.get(idx)

        if auto_pos is None:
            mismatches.append(
                {
                    'index': idx,
                    'title': panel.get('title', f'Panel {idx}'),
                    'reason': 'Could not compute auto position',
                }
            )
        elif manual_pos != auto_pos:
            mismatches.append(
                {
                    'index': idx,
                    'title': panel.get('title', f'Panel {idx}'),
                    'manual': manual_pos,
                    'auto': auto_pos,
                    'delta': (manual_pos[0] - auto_pos[0], manual_pos[1] - auto_pos[1]),
                }
            )

    return positioned_count, mismatches


def check_dashboard_positions(yaml_path: str) -> dict[str, Any]:
    """Check if a dashboard's manual positions match auto-layout.

    Args:
        yaml_path: Path to the YAML dashboard file.

    Returns:
        Dict with can_remove, dashboard_name, total_panels, positioned_panels, mismatches.
    """
    file_name = Path(yaml_path).name

    try:
        document = load_roundtrip(yaml_path)
    except Exception as e:
        return _make_error_result(f'Failed to load: {e}', file_name)

    dashboards = document.get('dashboards')
    if dashboards is None or not isinstance(dashboards, CommentedSeq) or len(dashboards) == 0:
        return _make_error_result('No dashboards found', file_name)

    dashboard = dashboards[0]
    if not isinstance(dashboard, CommentedMap):
        return _make_error_result('Invalid dashboard structure', file_name)

    dashboard_name = dashboard.get('name', file_name)
    panels = dashboard.get('panels')
    if panels is None or not isinstance(panels, CommentedSeq):
        return _make_error_result('No panels found', dashboard_name)

    algorithm = _get_layout_algorithm(dashboard)
    auto_positions = compute_auto_positions_from_yaml(panels, algorithm)
    positioned_count, mismatches = _check_panel_positions(panels, auto_positions)

    return {
        'can_remove': len(mismatches) == 0 and positioned_count > 0,
        'dashboard_name': dashboard_name,
        'total_panels': len(panels),
        'positioned_panels': positioned_count,
        'mismatches': mismatches,
    }


def _has_grid_format(panel: CommentedMap) -> bool:
    """Check if panel uses grid format (combined x, y, w, h)."""
    return 'grid' in panel and 'position' not in panel


def _has_position_format(panel: CommentedMap) -> bool:
    """Check if panel uses separate position/size format."""
    return 'position' in panel


def _convert_grid_to_size(panel: CommentedMap) -> bool:
    """Convert grid: {x, y, w, h} to size: {w, h}. Returns True if modified."""
    grid = panel.get('grid')
    if not isinstance(grid, CommentedMap) or 'x' not in grid or 'y' not in grid:
        return False

    # Get fallback values from existing size if present
    existing_size = panel.get('size')
    fallback_w = existing_size.get('w', DEFAULT_WIDTH) if isinstance(existing_size, CommentedMap) else DEFAULT_WIDTH
    fallback_h = existing_size.get('h', DEFAULT_HEIGHT) if isinstance(existing_size, CommentedMap) else DEFAULT_HEIGHT

    new_size = CommentedMap()
    new_size['w'] = grid.get('w', fallback_w)
    new_size['h'] = grid.get('h', fallback_h)
    new_size.fa.set_flow_style()

    del panel['grid']
    panel['size'] = new_size
    return True


def remove_positions_from_yaml(yaml_path: str) -> dict[str, Any]:  # noqa: PLR0911
    """Remove position properties from a YAML dashboard file.

    Args:
        yaml_path: Path to the YAML dashboard file.

    Returns:
        Dict with success status and details.
    """
    try:
        document = load_roundtrip(yaml_path)
    except Exception as e:
        return {'success': False, 'error': f'Failed to load: {e}'}

    dashboards = document.get('dashboards')
    if dashboards is None or not isinstance(dashboards, CommentedSeq) or len(dashboards) == 0:
        return {'success': False, 'error': 'No dashboards found'}

    dashboard = dashboards[0]
    if not isinstance(dashboard, CommentedMap):
        return {'success': False, 'error': 'Invalid dashboard structure'}

    panels = dashboard.get('panels')
    if panels is None or not isinstance(panels, CommentedSeq) or len(panels) == 0:
        return {'success': False, 'error': 'No panels found'}

    modified_count = 0
    for panel in panels:
        if not isinstance(panel, CommentedMap):
            continue

        if _has_grid_format(panel) and _convert_grid_to_size(panel):
            modified_count += 1
        elif _has_position_format(panel):
            del panel['position']
            modified_count += 1

    if modified_count == 0:
        return {'success': True, 'message': 'No positions to remove', 'modified': 0}

    try:
        dump_roundtrip(document, yaml_path)
    except Exception as e:
        return {'success': False, 'error': f'Failed to save: {e}'}

    return {'success': True, 'modified': modified_count}


def find_dashboard_files(base_dir: Path, input_dirs: list[str]) -> list[Path]:
    """Find all YAML dashboard files in the specified directories."""
    files: list[Path] = []
    for dir_name in input_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            files.extend(sorted(dir_path.glob('*.yaml')))
    return files


def _categorize_results(
    files: list[Path],
) -> tuple[list[tuple[Path, dict[str, Any]]], list[tuple[Path, dict[str, Any]]], list[tuple[Path, dict[str, Any]]]]:
    """Categorize dashboard check results."""
    can_remove: list[tuple[Path, dict[str, Any]]] = []
    cannot_remove: list[tuple[Path, dict[str, Any]]] = []
    no_positions: list[tuple[Path, dict[str, Any]]] = []

    for file_path in files:
        result = check_dashboard_positions(str(file_path))

        if 'error' in result:
            cannot_remove.append((file_path, result))
        elif result['positioned_panels'] == 0:
            no_positions.append((file_path, result))
        elif result['can_remove']:
            can_remove.append((file_path, result))
        else:
            cannot_remove.append((file_path, result))

    return can_remove, cannot_remove, no_positions


def _print_mismatch(mismatch: dict[str, Any]) -> None:
    """Print a single mismatch entry."""
    title = mismatch.get('title', f'Panel {mismatch["index"]}')
    if 'delta' in mismatch:
        manual = mismatch['manual']
        auto = mismatch['auto']
        delta = mismatch['delta']
        print(f'    - {title}: manual={manual} vs auto={auto} (delta: {delta})')
    else:
        print(f'    - {title}: {mismatch.get("reason", "unknown")}')


def _print_results(
    can_remove: list[tuple[Path, dict[str, Any]]],
    cannot_remove: list[tuple[Path, dict[str, Any]]],
    no_positions: list[tuple[Path, dict[str, Any]]],
    total_files: int,
) -> None:
    """Print analysis results."""
    if no_positions:
        print(f'=== Already using auto-layout ({len(no_positions)} dashboards) ===')
        for file_path, result in no_positions:
            print(f'  {file_path.name}: {result.get("dashboard_name", "?")}')
        print()

    if can_remove:
        print(f'=== Can remove positions ({len(can_remove)} dashboards) ===')
        for file_path, result in can_remove:
            print(f'  {file_path.name}: {result.get("dashboard_name", "?")} ({result["positioned_panels"]} panels)')
        print()

    if cannot_remove:
        print(f'=== Cannot remove positions ({len(cannot_remove)} dashboards) ===')
        for file_path, result in cannot_remove:
            if 'error' in result:
                print(f'  {file_path.name}: ERROR - {result["error"]}')
            else:
                print(f'  {file_path.name}: {result.get("dashboard_name", "?")}')
                for mismatch in result.get('mismatches', []):
                    _print_mismatch(mismatch)
        print()

    print('=== Summary ===')
    print(f'  Total dashboards: {total_files}')
    print(f'  Already auto-layout: {len(no_positions)}')
    print(f'  Can remove positions: {len(can_remove)}')
    print(f'  Cannot remove (mismatches): {len(cannot_remove)}')
    print()


def _apply_changes(can_remove: list[tuple[Path, dict[str, Any]]]) -> int:
    """Apply position removal to qualifying dashboards. Returns error count."""
    print('Removing positions...')
    modified_count = 0
    error_count = 0

    for file_path, _check_result in can_remove:
        result = remove_positions_from_yaml(str(file_path))
        if result.get('success'):
            modified = result.get('modified', 0)
            if modified > 0:
                print(f'  {file_path.name}: Removed {modified} positions')
                modified_count += 1
        else:
            print(f'  {file_path.name}: ERROR - {result.get("error")}')
            error_count += 1

    print()
    print(f'Modified {modified_count} dashboards.')
    if error_count > 0:
        print(f'Errors: {error_count}')

    return error_count


def main() -> int:
    """Run the position removal script."""
    parser = argparse.ArgumentParser(
        description='Remove redundant position properties from dashboard YAML files.',
    )
    _ = parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Report which dashboards would be modified without making changes.',
    )
    _ = parser.add_argument(
        'paths',
        nargs='*',
        help='Specific YAML files to process. If not provided, processes default directories.',
    )

    args = parser.parse_args()

    # Determine base directory (compiler/)
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent

    # Find files to process
    files = [Path(p).resolve() for p in args.paths] if args.paths else find_dashboard_files(base_dir, DEFAULT_INPUT_DIRS)

    if not files:
        print('No dashboard files found.')
        return 1

    print(f'Analyzing {len(files)} dashboard files...')
    print()

    can_remove, cannot_remove, no_positions = _categorize_results(files)
    _print_results(can_remove, cannot_remove, no_positions, len(files))

    if args.dry_run:
        print('[DRY RUN] No changes made.')
        return 0

    if not can_remove:
        print('No dashboards to modify.')
        return 0

    error_count = _apply_changes(can_remove)
    return 1 if error_count > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
