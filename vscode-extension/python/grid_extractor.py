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
    # Add the parent directory to sys.path to import dashboard_compiler
    repo_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(repo_root / "src"))

    from dashboard_compiler.dashboard_compiler import load

    # Load the dashboard configuration
    dashboard_config = load(yaml_path)

    # Extract panel information
    panels = []
    for panel in dashboard_config.panels:
        panel_info = {
            "id": panel.id or f"panel_{len(panels)}",
            "title": panel.title or "Untitled Panel",
            "type": panel.__class__.__name__.replace("Panel", "").lower(),
            "grid": {
                "x": panel.grid.x,
                "y": panel.grid.y,
                "w": panel.grid.w,
                "h": panel.grid.h,
            }
        }
        panels.append(panel_info)

    # Return dashboard metadata and panels
    result = {
        "title": dashboard_config.name or "Untitled Dashboard",
        "description": dashboard_config.description or "",
        "panels": panels,
    }

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: grid_extractor.py <yaml_path>"}))
        sys.exit(1)

    yaml_path = sys.argv[1]

    try:
        result = extract_grid_layout(yaml_path)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
