#!/usr/bin/env python3
# pyright: reportUnknownMemberType=false, reportUnnecessaryComparison=false
# Grid extractor handles panel types with dynamic attributes
"""Extract panel grid layout information from a YAML dashboard file.

This script reads a YAML dashboard file and extracts the grid layout information
for each panel, returning it as a typed Pydantic model for use by the LSP server.
"""

import json
import sys

from kb_dashboard_core.dashboard_compiler import load
from kb_dashboard_core.panels.collapsible import CollapsiblePanel
from kb_dashboard_core.panels.compile import compute_panel_positions
from kb_dashboard_core.panels.config import GRID_WIDTH_WHOLE, resolve_semantic_width

from dashboard_compiler.lsp.models import DashboardGridInfo, Grid, PanelGridInfo
from dashboard_compiler.lsp.utils import get_panel_type


def _extract_inner_panels(section_panel: CollapsiblePanel) -> list[PanelGridInfo]:
    """Extract inner panels from a CollapsiblePanel section with auto-layout."""
    inner_source = section_panel.section.panels
    if not inner_source:
        return []

    # Filter out nested CollapsiblePanels (not supported) for layout
    layout_panels = [p for p in inner_source if not isinstance(p, CollapsiblePanel)]
    position_map = compute_panel_positions(layout_panels)

    result: list[PanelGridInfo] = []
    layout_idx = 0
    for inner in inner_source:
        if isinstance(inner, CollapsiblePanel):
            continue

        if layout_idx in position_map:
            ix, iy = position_map[layout_idx]
            pinned = False
        elif inner.position.x is not None and inner.position.y is not None:
            ix, iy = inner.position.x, inner.position.y
            pinned = True
        else:
            layout_idx += 1
            continue

        result.append(
            PanelGridInfo(
                id=inner.id if (inner.id is not None and len(inner.id) > 0) else f'inner_{layout_idx}',
                title=inner.title if (inner.title is not None and len(inner.title) > 0) else 'Untitled Panel',
                type=get_panel_type(inner),
                grid=Grid(x=ix, y=iy, w=resolve_semantic_width(inner.size.w), h=inner.size.h),
                is_pinned=pinned,
            )
        )
        layout_idx += 1

    return result


def extract_grid_layout(yaml_path: str, dashboard_index: int = 0) -> DashboardGridInfo:
    """Extract grid layout information from a YAML dashboard file.

    Args:
        yaml_path: Path to the YAML dashboard file
        dashboard_index: Index of the dashboard to extract (default: 0)

    Returns:
        DashboardGridInfo containing dashboard metadata and panel grid information
    """
    dashboards = load(yaml_path)
    if len(dashboards) == 0:
        msg = 'No dashboards found in YAML file'
        raise ValueError(msg)

    if dashboard_index < 0 or dashboard_index >= len(dashboards):
        msg = f'Dashboard index {dashboard_index} out of range (0-{len(dashboards) - 1})'
        raise ValueError(msg)

    dashboard_config = dashboards[dashboard_index]

    # Filter out CollapsiblePanels for auto-layout (they are full-width section headers)
    layout_panels = [p for p in dashboard_config.panels if not isinstance(p, CollapsiblePanel)]
    position_map = compute_panel_positions(layout_panels, algorithm=dashboard_config.settings.layout_algorithm)

    # Extract panel information
    panels: list[PanelGridInfo] = []
    layout_index = 0
    for panel in dashboard_config.panels:
        if isinstance(panel, CollapsiblePanel):
            # Section headers are full-width, 1 row tall; position from the panel itself
            x = panel.position.x if panel.position.x is not None else 0
            y = panel.position.y if panel.position.y is not None else 0

            # Extract inner panels with their own auto-layout
            inner_panels = _extract_inner_panels(panel)

            panel_info = PanelGridInfo(
                id=panel.id if (panel.id is not None and len(panel.id) > 0) else f'section_{panel.title or "Untitled Section"}',
                title=panel.title if (panel.title is not None and len(panel.title) > 0) else 'Untitled Section',
                type='section',
                grid=Grid(x=x, y=y, w=GRID_WIDTH_WHOLE, h=1),
                is_pinned=panel.position.x is not None and panel.position.y is not None,
                panels=inner_panels,
            )
            panels.append(panel_info)
            continue

        # Use computed position if available, otherwise use panel's position
        # A panel is "pinned" if it has explicit position coordinates (not auto-positioned)
        if layout_index in position_map:
            x, y = position_map[layout_index]
            is_pinned = False
        elif panel.position.x is not None and panel.position.y is not None:
            x, y = panel.position.x, panel.position.y
            is_pinned = True
        else:
            msg = f'Panel "{panel.title}" has no position and auto-layout failed'
            raise ValueError(msg)

        panel_info = PanelGridInfo(
            id=panel.id if (panel.id is not None and len(panel.id) > 0) else f'panel_{layout_index}',
            title=panel.title if (panel.title is not None and len(panel.title) > 0) else 'Untitled Panel',
            type=get_panel_type(panel),
            grid=Grid(x=x, y=y, w=resolve_semantic_width(panel.size.w), h=panel.size.h),
            is_pinned=is_pinned,
        )
        panels.append(panel_info)
        layout_index += 1

    title = dashboard_config.name if (dashboard_config.name is not None and len(dashboard_config.name) > 0) else 'Untitled Dashboard'
    description = (
        dashboard_config.description if (dashboard_config.description is not None and len(dashboard_config.description) > 0) else ''
    )

    return DashboardGridInfo(
        title=title,
        description=description,
        panels=panels,
    )


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
        print(result.model_dump_json())
    except Exception as e:
        print(json.dumps({'error': str(e)}))
        sys.exit(1)
