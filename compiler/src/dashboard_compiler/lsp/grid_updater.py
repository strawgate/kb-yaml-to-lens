#!/usr/bin/env python3
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
    dashboards = document.get('dashboards')
    if dashboards is None or not isinstance(dashboards, CommentedSeq):
        return None, 'No dashboards found in YAML file'

    if len(dashboards) == 0:
        return None, 'No dashboards found in YAML file'

    if dashboard_index < 0 or dashboard_index >= len(dashboards):
        return None, f'Dashboard index {dashboard_index} out of range (0-{len(dashboards) - 1})'

    dashboard = dashboards[dashboard_index]
    if not isinstance(dashboard, CommentedMap):
        return None, 'Invalid dashboard structure'

    panels = dashboard.get('panels')
    if panels is None or not isinstance(panels, CommentedSeq):
        return None, 'No panels found in dashboard'

    if panel_id.startswith('panel_'):
        try:
            panel_index = int(panel_id.split('_')[1])
        except (ValueError, IndexError) as e:
            return None, f'Invalid panel ID format: {e}'
        else:
            if panel_index < 0 or panel_index >= len(panels):
                return None, f'Panel index {panel_index} out of range (0-{len(panels) - 1})'
            panel = panels[panel_index]
            if not isinstance(panel, CommentedMap):
                return None, 'Invalid panel structure'
            return panel, None
    else:
        for panel in panels:
            if isinstance(panel, CommentedMap) and panel.get('id') == panel_id:
                return panel, None
        return None, f'Panel with ID {panel_id} not found'


def _update_grid_in_panel(panel: CommentedMap, new_grid: dict[str, Any]) -> None:
    """Update the grid coordinates in a panel dictionary.

    Args:
        panel: The panel's CommentedMap to modify.
        new_grid: New grid coordinates with keys: x, y, w, h.
    """
    position = panel.get('position')
    if isinstance(position, CommentedMap):
        position['x'] = new_grid['x']
        position['y'] = new_grid['y']
    else:
        panel['position'] = {'x': new_grid['x'], 'y': new_grid['y']}

    size = panel.get('size')
    if isinstance(size, CommentedMap):
        size['w'] = new_grid['w']
        size['h'] = new_grid['h']
    else:
        panel['size'] = {'w': new_grid['w'], 'h': new_grid['h']}


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
