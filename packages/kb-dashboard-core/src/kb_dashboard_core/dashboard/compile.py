"""Compile a Dashboard into its Kibana view model representation."""

from collections.abc import Sequence

from kb_dashboard_core.controls.compile import compile_control_group
from kb_dashboard_core.dashboard.config import Dashboard, DashboardPanelTypes, DashboardSettings
from kb_dashboard_core.dashboard.view import (
    KbnDashboard,
    KbnDashboardAttributes,
    KbnDashboardOptions,
    KbnDashboardSection,
    KbnDashboardSectionGridData,
)
from kb_dashboard_core.filters.compile import compile_filters
from kb_dashboard_core.panels.auto_layout import LayoutAlgorithm
from kb_dashboard_core.panels.collapsible import CollapsiblePanel
from kb_dashboard_core.panels.compile import compile_dashboard_panels
from kb_dashboard_core.panels.config import GRID_WIDTH_WHOLE, Position, Size
from kb_dashboard_core.panels.markdown import MarkdownPanel
from kb_dashboard_core.panels.markdown.config import MarkdownPanelConfig
from kb_dashboard_core.panels.types import PanelTypes
from kb_dashboard_core.panels.view import KbnBasePanel, KbnSavedObjectMeta, KbnSearchSourceJSON
from kb_dashboard_core.queries.compile import compile_nonesql_query
from kb_dashboard_core.queries.view import KbnQuery
from kb_dashboard_core.shared.config import stable_id_generator
from kb_dashboard_core.shared.defaults import default_false, default_if_none, default_true
from kb_dashboard_core.shared.logging import log_compile
from kb_dashboard_core.shared.view import KbnReference

CORE_MIGRATION_VERSION: str = '8.8.0'
TYPE_MIGRATION_VERSION: str = '10.2.0'


@log_compile
def _prepare_panels_for_compilation(
    panels: Sequence[DashboardPanelTypes],
) -> tuple[list[PanelTypes], dict[int, CollapsiblePanel]]:
    """Separate collapsible panels, creating placeholder panels for autogrid."""
    flat_panels: list[PanelTypes] = []
    collapsible_map: dict[int, CollapsiblePanel] = {}

    for idx, panel in enumerate(panels):
        if isinstance(panel, CollapsiblePanel):
            collapsible_map[idx] = panel
            placeholder = MarkdownPanel(
                id=f'__section_placeholder_{idx}',
                title=panel.title,
                position=Position(x=panel.position.x, y=panel.position.y),
                size=Size(w=GRID_WIDTH_WHOLE, h=1),
                markdown=MarkdownPanelConfig(content=''),
            )
            flat_panels.append(placeholder)
        else:
            flat_panels.append(panel)

    return flat_panels, collapsible_map


@log_compile
def _compile_collapsible_panels(
    compiled_panels: list[KbnBasePanel],
    collapsible_map: dict[int, CollapsiblePanel],
    layout_algorithm: LayoutAlgorithm,
) -> tuple[list[KbnBasePanel], list[KbnDashboardSection], list[KbnReference]]:
    """Replace placeholder panels with section entries and compiled inner panels."""
    final_panels: list[KbnBasePanel] = []
    sections: list[KbnDashboardSection] = []
    section_references: list[KbnReference] = []

    for idx, compiled_panel in enumerate(compiled_panels):
        if idx not in collapsible_map:
            final_panels.append(compiled_panel)
            continue

        cp = collapsible_map[idx]
        section_y = compiled_panel.gridData.y
        section_id = cp.id or stable_id_generator(['section', cp.title])

        # Compile inner panels with independent autogrid
        inner_refs, inner_panels = compile_dashboard_panels(
            cp.section.panels,
            layout_algorithm=layout_algorithm,
        )

        # Add sectionId to inner panels' gridData
        for inner_panel in inner_panels:
            updated_gd = inner_panel.gridData.model_copy(update={'sectionId': section_id})
            final_panels.append(inner_panel.model_copy(update={'gridData': updated_gd}))

        section_references.extend(inner_refs)

        sections.append(
            KbnDashboardSection(
                title=cp.title,
                collapsed=cp.section.collapsed,
                gridData=KbnDashboardSectionGridData(y=section_y, i=section_id),
            )
        )

    return final_panels, sections, section_references


@log_compile
def compile_dashboard_options(settings: DashboardSettings) -> KbnDashboardOptions:
    """Compile the Kibana Dashboard Options view model.

    Args:
        settings: The dashboard settings containing option configuration.

    Returns:
        KbnDashboardOptions: The compiled Kibana dashboard options view model.

    """
    return KbnDashboardOptions(
        useMargins=default_true(settings.margins),
        syncColors=default_false(settings.sync.colors),
        syncCursor=default_true(settings.sync.cursor),
        syncTooltips=default_false(settings.sync.tooltips),
        hidePanelTitles=not default_true(settings.titles),
    )


@log_compile
def compile_dashboard_attributes(dashboard: Dashboard) -> tuple[list[KbnReference], KbnDashboardAttributes]:
    """Compile the attributes of a Dashboard object into its Kibana view model representation.

    Args:
        dashboard (Dashboard): The Dashboard object to compile.

    Returns:
        tuple: A tuple containing the list of references and the compiled dashboard attributes.

    """
    flat_panels, collapsible_map = _prepare_panels_for_compilation(dashboard.panels)

    panel_references, compiled_panels = compile_dashboard_panels(
        flat_panels,
        layout_algorithm=dashboard.settings.layout_algorithm,
    )

    if collapsible_map:
        panels, sections, section_references = _compile_collapsible_panels(
            compiled_panels=compiled_panels,
            collapsible_map=collapsible_map,
            layout_algorithm=dashboard.settings.layout_algorithm,
        )
        panel_references = panel_references + section_references
    else:
        panels = compiled_panels
        sections = None

    control_group_input, control_references = compile_control_group(
        control_settings=dashboard.settings.controls, controls=dashboard.controls
    )

    # Merge panel and control references
    all_references = panel_references + control_references

    # Time range configuration
    time_restore = dashboard.time_range is not None
    time_from = dashboard.time_range.from_time if dashboard.time_range is not None else None
    time_to = default_if_none(dashboard.time_range.to_time, 'now') if dashboard.time_range is not None else None

    return all_references, KbnDashboardAttributes(
        title=dashboard.name,
        description=dashboard.description or '',
        panelsJSON=panels,
        sections=sections,
        kibanaSavedObjectMeta=KbnSavedObjectMeta(
            searchSourceJSON=KbnSearchSourceJSON(
                filter=compile_filters(filters=dashboard.filters),
                query=compile_nonesql_query(query=dashboard.query) if dashboard.query else KbnQuery(query='', language='kuery'),
            ),
        ),
        optionsJSON=compile_dashboard_options(settings=dashboard.settings),
        timeRestore=time_restore,
        timeFrom=time_from,
        timeTo=time_to,
        version=1,
        controlGroupInput=control_group_input,
    )


@log_compile
def compile_dashboard(dashboard: Dashboard) -> KbnDashboard:
    """Compile a Dashboard object into its Kibana view model representation.

    Args:
        dashboard (Dashboard): The Dashboard object to compile.

    Returns:
        KbnDashboard: The compiled Kibana dashboard view model.

    """
    kbn_dashboard_id = dashboard.id or stable_id_generator([dashboard.name])

    references, attributes = compile_dashboard_attributes(dashboard)

    return KbnDashboard(
        attributes=attributes,
        coreMigrationVersion=CORE_MIGRATION_VERSION,
        created_at='2023-10-01T00:00:00Z',
        created_by='admin',
        id=kbn_dashboard_id,
        managed=False,
        references=references,
        type='dashboard',
        typeMigrationVersion=TYPE_MIGRATION_VERSION,
        updated_at='2023-10-01T00:00:00Z',
        updated_by='admin',
        version='1',
    )
