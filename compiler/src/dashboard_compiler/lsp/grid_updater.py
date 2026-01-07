#!/usr/bin/env python3
"""Update panel grid coordinates in a YAML dashboard file.

This script updates the grid coordinates for a specific panel in a YAML dashboard file
by loading the dashboard, modifying the grid, and re-exporting it using the compiler.
"""

import json
import sys
from typing import Any

from dashboard_compiler.dashboard_compiler import dump, load


def update_panel_grid(yaml_path: str, panel_id: str, new_grid: dict[str, Any], dashboard_index: int = 0) -> dict[str, Any]:
    """Update grid coordinates for a specific panel in a YAML file.

    Args:
        yaml_path: Path to the YAML dashboard file
        panel_id: ID of the panel to update (or 'panel_N' for index-based update)
        new_grid: New grid coordinates with keys: x, y, w, h
        dashboard_index: Index of the dashboard to update (default: 0)

    Returns:
        Dictionary with success status and message
    """
    # Validate grid coordinates
    required_keys = {'x', 'y', 'w', 'h'}
    if not all(key in new_grid for key in required_keys):
        return {'success': False, 'error': f'Invalid grid coordinates: missing required keys {required_keys}'}

    if not all(isinstance(new_grid[key], int) and new_grid[key] >= 0 for key in required_keys):
        return {'success': False, 'error': 'Invalid grid coordinates: all values must be non-negative integers'}

    # Load dashboards
    try:
        dashboards = load(yaml_path)
    except Exception as e:
        return {'success': False, 'error': f'Failed to load dashboard: {e}'}

    if len(dashboards) == 0:
        return {'success': False, 'error': 'No dashboards found in YAML file'}

    if dashboard_index < 0 or dashboard_index >= len(dashboards):
        return {'success': False, 'error': f'Dashboard index {dashboard_index} out of range (0-{len(dashboards) - 1})'}

    dashboard = dashboards[dashboard_index]

    # Find the panel
    found_panel = None
    if panel_id.startswith('panel_'):
        # Index-based lookup
        try:
            panel_index = int(panel_id.split('_')[1])
            if panel_index < 0 or panel_index >= len(dashboard.panels):
                return {'success': False, 'error': f'Panel index {panel_index} out of range (0-{len(dashboard.panels) - 1})'}

            found_panel = dashboard.panels[panel_index]
        except (ValueError, IndexError) as e:
            return {'success': False, 'error': f'Invalid panel ID format: {e}'}
    else:
        # ID-based lookup
        for panel in dashboard.panels:
            if panel.id == panel_id:
                found_panel = panel
                break

    if found_panel is None:
        return {'success': False, 'error': f'Panel with ID {panel_id} not found'}

    # Update position and size (config model uses frozen, so we need to use model_copy)
    try:
        updated_panel = found_panel.model_copy(
            update={
                'position': {'x': new_grid['x'], 'y': new_grid['y']},
                'size': {'w': new_grid['w'], 'h': new_grid['h']},
            }
        )

        # Replace the panel in the dashboard's panel list
        for idx, panel in enumerate(dashboard.panels):
            if panel is found_panel:
                dashboard.panels[idx] = updated_panel
                break
    except Exception as e:
        return {'success': False, 'error': f'Failed to update panel: {e}'}

    # Save the updated dashboard
    try:
        dump(dashboards, yaml_path)
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
