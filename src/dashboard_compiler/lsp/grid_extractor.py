#!/usr/bin/env python3
"""Extract panel grid layout information from a YAML dashboard file.

This script reads a YAML dashboard file and extracts the grid layout information
for each panel, returning it as JSON for use by the VSCode extension.
"""

import json
import sys
from typing import Any

from dashboard_compiler.dashboard_compiler import load
from dashboard_compiler.lsp.utils import get_panel_type
from dashboard_compiler.panels.compile import compute_panel_positions


def extract_grid_layout(yaml_path: str, dashboard_index: int = 0) -> dict[str, Any]:
    """Extract grid layout information from a YAML dashboard file.

    Args:
        yaml_path: Path to the YAML dashboard file
        dashboard_index: Index of the dashboard to extract (default: 0)

    Returns:
        Dictionary containing dashboard metadata and panel grid information
    """
    dashboards = load(yaml_path)
    if len(dashboards) == 0:
        msg = 'No dashboards found in YAML file'
        raise ValueError(msg)

    if dashboard_index < 0 or dashboard_index >= len(dashboards):
        msg = f'Dashboard index {dashboard_index} out of range (0-{len(dashboards) - 1})'
        raise ValueError(msg)

    dashboard_config = dashboards[dashboard_index]

    # Compute positions for panels that need auto-layout
    position_map = compute_panel_positions(dashboard_config.panels, algorithm=dashboard_config.settings.layout_algorithm)

    # Extract panel information
    panels = []
    for index, panel in enumerate(dashboard_config.panels):
        panel_type = get_panel_type(panel)

        # Use computed position if available, otherwise use panel's position
        if index in position_map:
            x, y = position_map[index]
        elif panel.position.x is not None and panel.position.y is not None:
            x, y = panel.position.x, panel.position.y
        else:
            msg = f'Panel at index {index} has no position and auto-layout failed'
            raise ValueError(msg)

        panel_info = {
            'id': panel.id if (panel.id is not None and len(panel.id) > 0) else f'panel_{index}',
            'title': panel.title if (panel.title is not None and len(panel.title) > 0) else 'Untitled Panel',
            'type': panel_type,
            'grid': {
                'x': x,
                'y': y,
                'w': panel.size.w,
                'h': panel.size.h,
            },
        }
        panels.append(panel_info)

    title = dashboard_config.name if (dashboard_config.name is not None and len(dashboard_config.name) > 0) else 'Untitled Dashboard'
    description = (
        dashboard_config.description if (dashboard_config.description is not None and len(dashboard_config.description) > 0) else ''
    )

    return {
        'title': title,
        'description': description,
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
