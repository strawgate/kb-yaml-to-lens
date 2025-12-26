#!/usr/bin/env python3
"""Extract panel grid layout information from a YAML dashboard file.

This script reads a YAML dashboard file and extracts the grid layout information
for each panel, returning it as JSON for use by the VSCode extension.
"""

import json
import sys
from pathlib import Path


def extract_grid_layout(yaml_path: str, dashboard_index: int = 0) -> dict:
    """Extract grid layout information from a YAML dashboard file.

    Args:
        yaml_path: Path to the YAML dashboard file
        dashboard_index: Index of the dashboard to extract (default: 0)

    Returns:
        Dictionary containing dashboard metadata and panel grid information
    """
    repo_root = Path(__file__).parent.parent.parent
    src_path = repo_root / 'src'
    if src_path.exists() and str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    try:
        from dashboard_compiler.dashboard_compiler import load
    except ImportError as e:
        msg = (
            f'Failed to import dashboard_compiler. Make sure the dashboard_compiler '
            f'package is installed or the src directory exists at {src_path}'
        )
        raise ImportError(msg) from e

    dashboards = load(yaml_path)
    if len(dashboards) == 0:
        msg = 'No dashboards found in YAML file'
        raise ValueError(msg)

    if dashboard_index < 0 or dashboard_index >= len(dashboards):
        msg = f'Dashboard index {dashboard_index} out of range (0-{len(dashboards) - 1})'
        raise ValueError(msg)

    dashboard_config = dashboards[dashboard_index]

    panels = []
    for index, panel in enumerate(dashboard_config.panels):
        panel_info = {
            'id': panel.id or f'panel_{index}',
            'title': panel.title or 'Untitled Panel',
            'type': panel.__class__.__name__.replace('Panel', '').lower(),
            'grid': {
                'x': panel.grid.x,
                'y': panel.grid.y,
                'w': panel.grid.w,
                'h': panel.grid.h,
            },
        }
        panels.append(panel_info)

    return {
        'title': dashboard_config.name or 'Untitled Dashboard',
        'description': dashboard_config.description or '',
        'panels': panels,
    }


if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(json.dumps({'error': 'Usage: grid_extractor.py <yaml_path> [dashboard_index]'}))
        sys.exit(1)

    yaml_path = sys.argv[1]
    dashboard_index = 0

    if len(sys.argv) == 3:
        try:
            dashboard_index = int(sys.argv[2])
        except ValueError:
            print(json.dumps({'error': 'Dashboard index must be an integer'}))
            sys.exit(1)

    try:
        result = extract_grid_layout(yaml_path, dashboard_index)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({'error': str(e)}))
        sys.exit(1)
