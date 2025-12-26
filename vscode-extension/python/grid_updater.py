#!/usr/bin/env python3
"""Update panel grid coordinates in a YAML dashboard file.

This script updates the grid coordinates for a specific panel in a YAML dashboard file,
preserving the file's formatting and comments as much as possible.
"""

import json
import re
import sys
from pathlib import Path


def _validate_panel_id(panel_id: str) -> bool:
    """Validate that panel_id contains only safe characters.

    Args:
        panel_id: The panel ID to validate

    Returns:
        True if valid, False otherwise
    """
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', panel_id))


def _validate_grid_coords(grid: dict) -> bool:
    """Validate grid coordinates are within valid bounds.

    Args:
        grid: Dictionary with x, y, w, h coordinates

    Returns:
        True if valid, False otherwise
    """
    required_keys = {'x', 'y', 'w', 'h'}
    if not all(key in grid for key in required_keys):
        return False

    return all(isinstance(grid[key], int) and grid[key] >= 0 for key in required_keys)


def update_panel_grid(yaml_path: str, panel_id: str, new_grid: dict, dashboard_index: int = 0) -> dict:  # noqa: PLR0912, PLR0915
    """Update grid coordinates for a specific panel in a YAML file.

    Args:
        yaml_path: Path to the YAML dashboard file
        panel_id: ID of the panel to update
        new_grid: New grid coordinates with keys: x, y, w, h
        dashboard_index: Index of the dashboard to update (default: 0)

    Returns:
        Dictionary with success status and message
    """
    if not _validate_panel_id(panel_id):
        return {'success': False, 'error': f'Invalid panel ID: {panel_id}. Only alphanumeric, underscore, and hyphen allowed.'}

    if not _validate_grid_coords(new_grid):
        return {'success': False, 'error': f'Invalid grid coordinates: {new_grid}'}

    yaml_file = Path(yaml_path)
    if not yaml_file.exists():
        return {'success': False, 'error': f'File not found: {yaml_path}'}

    content = yaml_file.read_text()

    if 'dashboards:' in content:
        dashboard_pattern = r'^dashboards:\s*$'
        dashboards_match = re.search(dashboard_pattern, content, re.MULTILINE)
        if dashboards_match is None:
            return {'success': False, 'error': 'Could not find dashboards section'}

        dashboard_starts = list(re.finditer(r'^- (?:title:|name:|panels:)', content[dashboards_match.end() :], re.MULTILINE))
        if dashboard_index >= len(dashboard_starts):
            return {'success': False, 'error': f'Dashboard index {dashboard_index} out of range (0-{len(dashboard_starts) - 1})'}

        dashboard_start = dashboards_match.end() + dashboard_starts[dashboard_index].start()
        if dashboard_index + 1 < len(dashboard_starts):
            dashboard_end = dashboards_match.end() + dashboard_starts[dashboard_index + 1].start()
        else:
            dashboard_end = len(content)

        search_content = content[dashboard_start:dashboard_end]
        content_offset = dashboard_start
    else:
        search_content = content
        content_offset = 0

    if panel_id.startswith('panel_'):
        try:
            panel_index = int(panel_id.split('_')[1])
            panel_blocks = list(re.finditer(r'^\s*- (?:title:|id:|type:|grid:)', search_content, re.MULTILINE))
            if panel_index < len(panel_blocks):
                panel_start = panel_blocks[panel_index].start()
                panel_end = panel_blocks[panel_index + 1].start() if panel_index + 1 < len(panel_blocks) else len(search_content)
                panel_content = search_content[panel_start:panel_end]

                new_grid_str = f'grid: {{ x: {new_grid["x"]}, y: {new_grid["y"]}, w: {new_grid["w"]}, h: {new_grid["h"]} }}'

                inline_pattern = r'grid:\s*\{[^}]+\}'
                multiline_pattern = r'grid:\s*\n\s+x:.*?\n\s+h:.*?(?=\n\s+\w+:|\n[^\s]|$)'

                updated_panel = re.sub(inline_pattern, new_grid_str, panel_content, count=1)
                if updated_panel == panel_content:
                    updated_panel = re.sub(multiline_pattern, new_grid_str, panel_content, count=1, flags=re.DOTALL)

                abs_panel_start = content_offset + panel_start
                abs_panel_end = content_offset + panel_end
                updated_content = content[:abs_panel_start] + updated_panel + content[abs_panel_end:]
                yaml_file.write_text(updated_content)
                return {'success': True, 'message': f'Updated grid for {panel_id}'}
        except (ValueError, IndexError) as e:
            return {'success': False, 'error': f'Invalid panel ID format: {e}'}
    else:
        id_pattern = rf'id:\s+{re.escape(panel_id)}'
        id_match = re.search(id_pattern, search_content)
        if id_match is None:
            return {'success': False, 'error': f'Panel with ID {panel_id} not found'}

        panel_markers = list(re.finditer(r'\n\s*- (?:title:|id:|type:|grid:)', search_content[: id_match.start()]))
        panel_start = panel_markers[-1].start() if panel_markers else 0

        next_panel_match = re.search(r'\n\s*- (?:title:|id:|type:|grid:)', search_content[id_match.end() :])
        panel_end = id_match.end() + next_panel_match.start() if next_panel_match else len(search_content)

        panel_content = search_content[panel_start:panel_end]

        new_grid_str = f'grid: {{ x: {new_grid["x"]}, y: {new_grid["y"]}, w: {new_grid["w"]}, h: {new_grid["h"]} }}'

        inline_pattern = r'grid:\s*\{[^}]+\}'
        updated_panel = re.sub(inline_pattern, new_grid_str, panel_content, count=1)

        abs_panel_start = content_offset + panel_start
        abs_panel_end = content_offset + panel_end
        updated_content = content[:abs_panel_start] + updated_panel + content[abs_panel_end:]
        yaml_file.write_text(updated_content)
        return {'success': True, 'message': f'Updated grid for panel {panel_id}'}

    return {'success': False, 'error': 'Failed to update grid'}


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
        if not result.get('success'):
            sys.exit(1)
    except json.JSONDecodeError as e:
        print(json.dumps({'error': f'Invalid grid JSON: {e}'}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({'error': str(e)}))
        sys.exit(1)
