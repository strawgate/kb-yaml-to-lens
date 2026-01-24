#!/usr/bin/env python3
# pyright: reportAny=false
# Grid updater receives untyped JSON data from CLI arguments
"""Update panel grid coordinates in a YAML dashboard file.

This script updates the grid coordinates for a specific panel in a YAML dashboard file
using round-trip YAML loading to preserve comments and formatting.
"""

import json
import sys
from typing import Any

from ruamel.yaml.comments import CommentedMap, CommentedSeq

from dashboard_compiler.yaml_roundtrip import dump_roundtrip, load_roundtrip


def _find_panel_in_document(document: CommentedMap, panel_id: str, dashboard_index: int) -> tuple[CommentedMap | None, str | None]:
    """Find a panel in the YAML document by ID or index.

    Args:
        document: The loaded YAML document.
        panel_id: ID of the panel to find (or 'panel_N' for index-based lookup).
        dashboard_index: Index of the dashboard to search in.

    Returns:
        Tuple of (panel_dict, error_message). If found, error_message is None.
    """
    dashboards = document.get('dashboards')  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
    if dashboards is None or not isinstance(dashboards, CommentedSeq):
        return None, 'No dashboards found in YAML file'

    if len(dashboards) == 0:
        return None, 'No dashboards found in YAML file'

    if dashboard_index < 0 or dashboard_index >= len(dashboards):
        return None, f'Dashboard index {dashboard_index} out of range (0-{len(dashboards) - 1})'

    dashboard = dashboards[dashboard_index]  # pyright: ignore[reportUnknownVariableType]
    if not isinstance(dashboard, CommentedMap):
        return None, 'Invalid dashboard structure'

    panels = dashboard.get('panels')  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
    if panels is None or not isinstance(panels, CommentedSeq):
        return None, 'No panels found in dashboard'

    if panel_id.startswith('panel_'):
        suffix = panel_id.removeprefix('panel_')
        if suffix.isdigit():
            panel_index = int(suffix)
            if panel_index < 0 or panel_index >= len(panels):
                return None, f'Panel index {panel_index} out of range (0-{len(panels) - 1})'
            panel = panels[panel_index]  # pyright: ignore[reportUnknownVariableType]
            if not isinstance(panel, CommentedMap):
                return None, 'Invalid panel structure'
            return panel, None
    for panel in panels:  # pyright: ignore[reportUnknownVariableType]
        if isinstance(panel, CommentedMap) and panel.get('id') == panel_id:  # pyright: ignore[reportUnknownMemberType]
            return panel, None
    return None, f'Panel with ID {panel_id} not found'


def _is_alias(value: CommentedMap) -> bool:
    """Check if a CommentedMap is an alias reference.

    A value is considered an alias if it has an anchor attribute with a value,
    indicating it was defined elsewhere and referenced via alias.

    Args:
        value: The CommentedMap to check.

    Returns:
        True if the value appears to be an alias reference.
    """
    anchor = getattr(value, 'anchor', None)
    return anchor is not None and anchor.value is not None


def _update_grid_in_panel(panel: CommentedMap, new_grid: dict[str, Any]) -> None:
    """Update the grid coordinates in a panel dictionary.

    When the existing position/size is an alias, replaces with a new CommentedMap
    to avoid mutating the shared anchor value.

    Args:
        panel: The panel's CommentedMap to modify.
        new_grid: New grid coordinates with keys: x, y, w, h.
    """
    position = panel.get('position')  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
    if isinstance(position, CommentedMap) and not _is_alias(position):
        position['x'] = new_grid['x']
        position['y'] = new_grid['y']
    else:
        new_position = CommentedMap()
        new_position['x'] = new_grid['x']
        new_position['y'] = new_grid['y']
        if isinstance(position, CommentedMap):
            new_position.fa.set_flow_style()  # pyright: ignore[reportUnknownMemberType]
        panel['position'] = new_position

    size = panel.get('size')  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
    if isinstance(size, CommentedMap) and not _is_alias(size):
        size['w'] = new_grid['w']
        size['h'] = new_grid['h']
    else:
        new_size = CommentedMap()
        new_size['w'] = new_grid['w']
        new_size['h'] = new_grid['h']
        if isinstance(size, CommentedMap):
            new_size.fa.set_flow_style()  # pyright: ignore[reportUnknownMemberType]
        panel['size'] = new_size


def update_panel_grid(yaml_path: str, panel_id: str, new_grid: dict[str, Any], dashboard_index: int = 0) -> dict[str, Any]:
    """Update grid coordinates for a specific panel in a YAML file.

    Uses round-trip YAML loading to preserve comments and formatting.

    Args:
        yaml_path: Path to the YAML dashboard file
        panel_id: ID of the panel to update (or 'panel_N' for index-based update)
        new_grid: New grid coordinates with keys: x, y, w, h
        dashboard_index: Index of the dashboard to update (default: 0)

    Returns:
        Dictionary with success status and message
    """
    required_keys = {'x', 'y', 'w', 'h'}
    if not all(key in new_grid for key in required_keys):
        return {'success': False, 'error': f'Invalid grid coordinates: missing required keys {required_keys}'}

    if not all(isinstance(new_grid[key], int) and new_grid[key] >= 0 for key in required_keys):
        return {'success': False, 'error': 'Invalid grid coordinates: all values must be non-negative integers'}

    try:
        document = load_roundtrip(yaml_path)
    except Exception as e:
        return {'success': False, 'error': f'Failed to load dashboard: {e}'}

    panel, error = _find_panel_in_document(document, panel_id, dashboard_index)
    if error is not None:
        return {'success': False, 'error': error}

    if panel is None:
        return {'success': False, 'error': f'Panel with ID {panel_id} not found'}

    try:
        _update_grid_in_panel(panel, new_grid)
    except Exception as e:
        return {'success': False, 'error': f'Failed to update panel: {e}'}

    try:
        dump_roundtrip(document, yaml_path)
    except Exception as e:
        return {'success': False, 'error': f'Failed to save dashboard: {e}'}
    else:
        return {'success': True, 'message': f'Updated grid for {panel_id}'}


if __name__ == '__main__':
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print(json.dumps({'error': 'Usage: grid_updater.py <yaml_path> <panel_id> <grid_json> [dashboard_index]'}))
        sys.exit(1)

    yaml_path = sys.argv[1]
    panel_id = sys.argv[2]
    grid_json = sys.argv[3]
    dashboard_index = 0

    if len(sys.argv) == 5:
        try:
            dashboard_index = int(sys.argv[4])
        except ValueError:
            print(json.dumps({'error': 'Dashboard index must be an integer'}))
            sys.exit(1)

    try:
        new_grid = json.loads(grid_json)
        result = update_panel_grid(yaml_path, panel_id, new_grid, dashboard_index)
        print(json.dumps(result))
        if result.get('success') is not True:
            sys.exit(1)
    except json.JSONDecodeError as e:
        print(json.dumps({'error': f'Invalid grid JSON: {e}'}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({'error': str(e)}))
        sys.exit(1)
