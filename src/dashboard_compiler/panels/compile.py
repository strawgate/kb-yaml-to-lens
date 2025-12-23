"""Compile Dashboard Panels to Kibana View Models."""

from collections.abc import Sequence

from dashboard_compiler.panels import LinksPanel, MarkdownPanel
from dashboard_compiler.panels.charts.compile import compile_charts_panel_config
from dashboard_compiler.panels.charts.config import ESQLPanel, LensPanel
from dashboard_compiler.panels.charts.view import KbnLensPanel
from dashboard_compiler.panels.links.compile import compile_links_panel_config
from dashboard_compiler.panels.links.view import KbnLinksPanel
from dashboard_compiler.panels.markdown.compile import compile_markdown_panel_config
from dashboard_compiler.panels.markdown.view import KbnMarkdownPanel
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


def compile_panel_shared(panel: PanelTypes) -> tuple[str, KbnGridData]:
    """Compile shared properties of a panel into its Kibana view model representation.

    Args:
        panel (LensPanel | ESQLPanel): The panel object to compile.

    Returns:
        tuple[str, KbnGridData]: A tuple containing the panel index and the grid data.

    """
    panel_index = panel.id or stable_id_generator(values=[panel.type, panel.title, str(panel.grid)])

    grid_data = KbnGridData(x=panel.grid.x, y=panel.grid.y, w=panel.grid.w, h=panel.grid.h, i=panel_index)

    return panel_index, grid_data


def compile_dashboard_panel(panel: PanelTypes) -> tuple[list[KbnReference], KbnBasePanel]:
    """Compile a single panel into its Kibana view model representation.

    Args:
        panel (PanelTypes): The panel object to compile.

    Returns:
        tuple: A tuple containing the compiled references and the Kibana panel view model.

    """
    panel_index, grid_data = compile_panel_shared(panel)

    if isinstance(panel, MarkdownPanel):
        references, embeddable_config = compile_markdown_panel_config(panel)
        return references, KbnMarkdownPanel(panelIndex=panel_index, gridData=grid_data, embeddableConfig=embeddable_config)

    if isinstance(panel, LinksPanel):
        references, embeddable_config = compile_links_panel_config(panel)
        return references, KbnLinksPanel(panelIndex=panel_index, gridData=grid_data, embeddableConfig=embeddable_config)

    if isinstance(panel, LensPanel | ESQLPanel):
        references, kbn_panel = compile_charts_panel_config(panel)
        return references, KbnLensPanel(panelIndex=panel_index, gridData=grid_data, embeddableConfig=kbn_panel)

    # if isinstance(panel, ESQLPanel):
    #     return compile_esql_panel(panel)

    msg = f'Panel type {type(panel)} is not supported in the dashboard compilation.'
    raise NotImplementedError(msg)


def compile_dashboard_panels(panels: Sequence[PanelTypes]) -> tuple[list[KbnReference], list[KbnBasePanel]]:
    """Compile the panels of a Dashboard object into their Kibana view model representation.

    Args:
        panels (Sequence[PanelTypes]): The sequence of panel objects to compile.

    Returns:
        tuple[list[KbnReference], list[KbnBasePanel]]: The compiled references and panel view models.

    """
    kbn_panels: list[KbnBasePanel] = []
    kbn_references: list[KbnReference] = []

    for panel in panels:
        new_references, new_panel = compile_dashboard_panel(panel=panel)

        kbn_panels.append(new_panel)

        kbn_references.extend([convert_to_panel_reference(kbn_reference=ref, panel_index=new_panel.panelIndex) for ref in new_references])

    return kbn_references, kbn_panels
