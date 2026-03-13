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
from kb_dashboard_core.panels.config import GRID_WIDTH_WHOLE, Size, resolve_semantic_width

from dashboard_compiler.lsp.models import DashboardGridInfo, Grid, PanelGridInfo
from dashboard_compiler.lsp.utils import get_panel_type


def _extract_inner_panels(section_panel: CollapsiblePanel) -> tuple[list[PanelGridInfo], int]:
    """Extract inner panels from a CollapsiblePanel section with auto-layout.

    Inner panels use a **relative** coordinate space — their (x, y) positions
    start at (0, 0) within the section body, independent of the section's
    absolute position in the outer dashboard grid.

    Returns:
        Tuple of (inner panel grid infos, content height in grid rows).
    """
    inner_source = section_panel.section.panels
    if not inner_source:
        return [], 0

    # Filter out nested CollapsiblePanels (not supported) for layout
    layout_panels = [p for p in inner_source if not isinstance(p, CollapsiblePanel)]
    position_map = compute_panel_positions(layout_panels)

    result: list[PanelGridInfo] = []
    max_bottom = 0
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

        bottom = iy + inner.size.h
        max_bottom = max(max_bottom, bottom)

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

    return result, max_bottom


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

    # First pass: extract inner panels for each section and compute effective heights.
    #
    # Sections have h=1 (header bar) in the output, but their visual footprint in the
    # preview is header + inner panel content. We create height-inflated copies for layout
    # computation so the auto-layout engine reserves the right amount of vertical space,
    # preventing panels after a section from overlapping its inner content.
    # The inflated copies are only used for position computation — the output always
    # emits h=1 for sections.
    all_panels = list(dashboard_config.panels)
    section_data: dict[int, tuple[list[PanelGridInfo], int]] = {}
    layout_panels = []
    for idx, panel in enumerate(all_panels):
        if isinstance(panel, CollapsiblePanel):
            inner_panels, content_h = _extract_inner_panels(panel)
            section_data[idx] = (inner_panels, content_h)
            # Create a copy with effective height (header + content) for layout only
            effective_h = 1 + content_h
            adjusted = panel.model_copy(update={'size': Size(w=GRID_WIDTH_WHOLE, h=effective_h)})
            layout_panels.append(adjusted)
        else:
            layout_panels.append(panel)

    position_map = compute_panel_positions(layout_panels, algorithm=dashboard_config.settings.layout_algorithm)

    # Second pass: build output with correct positions but original section h=1
    panels: list[PanelGridInfo] = []
    for idx, panel in enumerate(all_panels):
        # Use computed position if available, otherwise use panel's position
        if idx in position_map:
            x, y = position_map[idx]
            is_pinned = False
        elif panel.position.x is not None and panel.position.y is not None:
            x, y = panel.position.x, panel.position.y
            is_pinned = True
        else:
            msg = f'Panel "{panel.title}" has no position and auto-layout failed'
            raise ValueError(msg)

        if isinstance(panel, CollapsiblePanel):
            inner_panels, _content_h = section_data[idx]

            panel_info = PanelGridInfo(
                id=panel.id if (panel.id is not None and len(panel.id) > 0) else f'section_{panel.title or "Untitled Section"}',
                title=panel.title if (panel.title is not None and len(panel.title) > 0) else 'Untitled Section',
                type='section',
                grid=Grid(x=x, y=y, w=GRID_WIDTH_WHOLE, h=1),
                is_pinned=is_pinned,
                panels=inner_panels,
            )
        else:
            panel_info = PanelGridInfo(
                id=panel.id if (panel.id is not None and len(panel.id) > 0) else f'panel_{idx}',
                title=panel.title if (panel.title is not None and len(panel.title) > 0) else 'Untitled Panel',
                type=get_panel_type(panel),
                grid=Grid(x=x, y=y, w=resolve_semantic_width(panel.size.w), h=panel.size.h),
                is_pinned=is_pinned,
            )
        panels.append(panel_info)

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
