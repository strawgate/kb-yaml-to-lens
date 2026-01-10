"""Compile Dashboard Panels to Kibana View Models."""

from collections.abc import Sequence

from dashboard_compiler.panels import ImagePanel, LinksPanel, MarkdownPanel, SearchPanel
from dashboard_compiler.panels.auto_layout import LayoutAlgorithm, create_layout_engine
from dashboard_compiler.panels.charts.compile import compile_charts_panel_config
from dashboard_compiler.panels.charts.config import ESQLPanel, LensPanel
from dashboard_compiler.panels.charts.view import KbnLensPanel
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.images.compile import compile_image_panel_config
from dashboard_compiler.panels.images.view import KbnImagePanel
from dashboard_compiler.panels.links.compile import compile_links_panel_config
from dashboard_compiler.panels.links.view import KbnLinksPanel
from dashboard_compiler.panels.markdown.compile import compile_markdown_panel_config
from dashboard_compiler.panels.markdown.view import KbnMarkdownPanel
from dashboard_compiler.panels.search.compile import compile_search_panel_config
from dashboard_compiler.panels.search.view import KbnSearchPanel
from dashboard_compiler.panels.types import PanelTypes
from dashboard_compiler.panels.view import KbnBasePanel, KbnGridData
from dashboard_compiler.shared.config import stable_id_generator
from dashboard_compiler.shared.view import KbnReference


def convert_to_panel_reference(kbn_reference: KbnReference, panel_index: str) -> KbnReference:
    """Convert a KbnReference object to a panel reference.

    Kibana requires panel references to be namespaced with the panel ID to avoid
    conflicts when multiple panels reference the same resource (e.g., data views).
    This transforms a reference like {type: 'index-pattern', id: 'abc', name: 'dataView'}
    into {type: 'index-pattern', id: 'abc', name: 'panel-123:dataView'}

    Args:
        kbn_reference (KbnReference): The KbnReference object to convert.
        panel_index (str): The index (id) of the panel to which the reference belongs.

    Returns:
        KbnReference: The converted panel reference.

    """
    return KbnReference(
        type=kbn_reference.type,
        id=kbn_reference.id,
        name=panel_index + ':' + kbn_reference.name,
    )


def get_panel_type_name(panel: PanelTypes) -> str:
    """Get the type name for a panel.

    Args:
        panel (PanelTypes): The panel object.

    Returns:
        str: The type name for the panel.

    """
    match panel:
        case MarkdownPanel():
            return 'markdown'
        case LinksPanel():
            return 'links'
        case ImagePanel():
            return 'image'
        case SearchPanel():
            return 'search'
        case LensPanel() | ESQLPanel():
            return 'charts'
        case _:  # pyright: ignore[reportUnnecessaryComparison]
            # This should never be reached if PanelTypes is exhaustive, but provides a clear error
            msg = f'Unknown panel type: {type(panel).__name__}'
            raise TypeError(msg)  # pyright: ignore[reportUnreachable]


def compute_panel_grid(panel: PanelTypes) -> Grid:
    """Compute the grid position for a panel based on its size and position.

    Args:
        panel (PanelTypes): The panel object.

    Returns:
        Grid: The computed grid with x, y, w, h.

    Raises:
        ValueError: If position is not set (should be set by auto-layout first).

    """
    if panel.position.x is None or panel.position.y is None:
        msg = f'Panel "{panel.title}" position is not set'
        raise ValueError(msg)

    return Grid(x=panel.position.x, y=panel.position.y, w=panel.size.width, h=panel.size.h)


def compile_panel_shared(panel: PanelTypes, grid: Grid) -> tuple[str, KbnGridData]:
    """Compile shared properties of a panel into its Kibana view model representation.

    Args:
        panel (PanelTypes): The panel object to compile.
        grid (Grid): The computed grid position for the panel.

    Returns:
        tuple[str, KbnGridData]: A tuple containing the panel index and the grid data.

    """
    panel_type = get_panel_type_name(panel)
    panel_index = panel.id or stable_id_generator(values=[panel_type, panel.title, str(grid)])

    grid_data = KbnGridData(x=grid.x, y=grid.y, w=grid.w, h=grid.h, i=panel_index)

    return panel_index, grid_data


def compile_dashboard_panel(panel: PanelTypes, grid: Grid) -> tuple[list[KbnReference], KbnBasePanel]:
    """Compile a single panel into its Kibana view model representation.

    Args:
        panel (PanelTypes): The panel object to compile.
        grid (Grid): The computed grid position for the panel.

    Returns:
        tuple: A tuple containing the compiled references and the Kibana panel view model.

    """
    panel_index, grid_data = compile_panel_shared(panel, grid)

    match panel:
        case MarkdownPanel():
            references, embeddable_config = compile_markdown_panel_config(panel)
            return references, KbnMarkdownPanel(panelIndex=panel_index, gridData=grid_data, embeddableConfig=embeddable_config)
        case LinksPanel():
            references, embeddable_config = compile_links_panel_config(panel)
            return references, KbnLinksPanel(panelIndex=panel_index, gridData=grid_data, embeddableConfig=embeddable_config)
        case ImagePanel():
            references, embeddable_config = compile_image_panel_config(panel)
            return references, KbnImagePanel(panelIndex=panel_index, gridData=grid_data, embeddableConfig=embeddable_config)
        case SearchPanel():
            references, embeddable_config = compile_search_panel_config(panel)
            return references, KbnSearchPanel(panelIndex=panel_index, gridData=grid_data, embeddableConfig=embeddable_config)
        case LensPanel() | ESQLPanel():
            references, kbn_panel = compile_charts_panel_config(panel)
            return references, KbnLensPanel(panelIndex=panel_index, gridData=grid_data, embeddableConfig=kbn_panel)
        case _:  # pyright: ignore[reportUnnecessaryComparison]
            # This should never be reached if PanelTypes is exhaustive, but provides a clear error
            msg = f'Unknown panel type: {type(panel).__name__}'
            raise TypeError(msg)  # pyright: ignore[reportUnreachable]


def compute_panel_positions(
    panels: Sequence[PanelTypes],
    algorithm: LayoutAlgorithm = 'up-left',
) -> dict[int, tuple[int, int]]:
    """Compute positions for panels that need auto-layout.

    Args:
        panels (Sequence[PanelTypes]): The sequence of panel objects.
        algorithm (LayoutAlgorithm): The layout algorithm to use. Defaults to 'up-left'.

    Returns:
        dict[int, tuple[int, int]]: Mapping of panel index to (x, y) position.

    """
    # Check if any panels need positioning
    any_needs_layout = any(p.position.x is None or p.position.y is None for p in panels)
    if any_needs_layout is False:
        return {}

    # Create stateful layout engine
    engine = create_layout_engine(algorithm)

    # Mark locked panels (those with explicit positions)
    for panel in panels:
        if panel.position.x is not None and panel.position.y is not None:
            engine.mark_locked_panel(panel.position.x, panel.position.y, panel.size.width, panel.size.h)

    # Add panels one at a time and get coordinates back immediately
    position_map: dict[int, tuple[int, int]] = {}
    for idx, panel in enumerate(panels):
        if panel.position.x is None or panel.position.y is None:
            x, y = engine.add_panel(panel.size.width, panel.size.h)
            position_map[idx] = (x, y)

    return position_map


def validate_no_overlapping_grids(grids: list[tuple[str, Grid]]) -> None:
    """Validate that no panels overlap on the grid.

    Args:
        grids (list[tuple[str, Grid]]): List of (panel_title, grid) tuples.

    Raises:
        ValueError: If any panels overlap.

    """
    for i, (title1, grid1) in enumerate(grids):
        for title2, grid2 in grids[i + 1 :]:
            if grid1.overlaps_with(grid2):
                msg = (
                    f'Panel "{title1}" at (x={grid1.x}, y={grid1.y}, '
                    f'w={grid1.w}, h={grid1.h}) overlaps with '
                    f'panel "{title2}" at (x={grid2.x}, y={grid2.y}, '
                    f'w={grid2.w}, h={grid2.h})'
                )
                raise ValueError(msg)


def compile_dashboard_panels(
    panels: Sequence[PanelTypes],
    layout_algorithm: LayoutAlgorithm = 'up-left',
) -> tuple[list[KbnReference], list[KbnBasePanel]]:
    """Compile the panels of a Dashboard object into their Kibana view model representation.

    Args:
        panels (Sequence[PanelTypes]): The sequence of panel objects to compile.
        layout_algorithm (LayoutAlgorithm): The layout algorithm to use. Defaults to 'up-left'.

    Returns:
        tuple[list[KbnReference], list[KbnBasePanel]]: The compiled references and panel view models.

    """
    # Compute positions for panels that need auto-layout
    position_map = compute_panel_positions(panels, algorithm=layout_algorithm)

    # Compute grid for each panel and validate
    grids: list[Grid] = []
    grid_titles: list[tuple[str, Grid]] = []

    for idx, panel in enumerate(panels):
        # Use computed position if available, otherwise use panel's position
        if idx in position_map:
            x, y = position_map[idx]
            grid = Grid(x=x, y=y, w=panel.size.width, h=panel.size.h)
        else:
            grid = compute_panel_grid(panel)

        grids.append(grid)
        panel_title = panel.title if len(panel.title) > 0 else 'Untitled Panel'
        grid_titles.append((panel_title, grid))

    # Validate no overlaps
    validate_no_overlapping_grids(grid_titles)

    # Compile panels
    kbn_panels: list[KbnBasePanel] = []
    kbn_references: list[KbnReference] = []

    for panel, grid in zip(panels, grids, strict=True):
        new_references, new_panel = compile_dashboard_panel(panel=panel, grid=grid)

        kbn_panels.append(new_panel)

        kbn_references.extend([convert_to_panel_reference(kbn_reference=ref, panel_index=new_panel.panelIndex) for ref in new_references])

    return kbn_references, kbn_panels
