#!/usr/bin/env python3
"""Extract panel grid layout information from a YAML dashboard file.

This script reads a YAML dashboard file and extracts the grid layout information
for each panel, returning it as JSON for use by the VSCode extension.
"""

import json
import sys
from pathlib import Path


def extract_grid_layout(yaml_path: str) -> dict:
    """Extract grid layout information from a YAML dashboard file.

    Args:
        yaml_path: Path to the YAML dashboard file

    Returns:
        Dictionary containing dashboard metadata and panel grid information
    """
    # Add the src directory to sys.path to import dashboard_compiler
    # This is necessary because the extension is not installed as a package
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

    # Load the dashboard configuration
    dashboard_configs = load(yaml_path)

    # Get the first dashboard (assuming single dashboard files for now)
    if isinstance(dashboard_configs, list) and len(dashboard_configs) > 0:
        dashboard_config = dashboard_configs[0]
    else:
        msg = f'Expected list of dashboards, got {type(dashboard_configs)}'
        raise ValueError(msg)

    # Extract panel information
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

    # Return dashboard metadata and panels
    return {
        'title': dashboard_config.name or 'Untitled Dashboard',
        'description': dashboard_config.description or '',
        'panels': panels,
    }


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(json.dumps({'error': 'Usage: grid_extractor.py <yaml_path>'}))
        sys.exit(1)

    yaml_path = sys.argv[1]

    try:
        result = extract_grid_layout(yaml_path)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({'error': str(e)}))
        sys.exit(1)
