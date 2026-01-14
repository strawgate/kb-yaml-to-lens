"""Compile a Dashboard into its Kibana view model representation."""

from dashboard_compiler.controls.compile import compile_control_group
from dashboard_compiler.dashboard.config import Dashboard, DashboardSettings
from dashboard_compiler.dashboard.view import KbnDashboard, KbnDashboardAttributes, KbnDashboardOptions
from dashboard_compiler.filters.compile import compile_filters
from dashboard_compiler.panels.compile import compile_dashboard_panel, compile_dashboard_panels, convert_to_panel_reference
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.view import KbnBasePanel, KbnGridData, KbnSavedObjectMeta, KbnSearchSourceJSON
from dashboard_compiler.queries.compile import compile_nonesql_query
from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.sections.compile import compile_section
from dashboard_compiler.sections.config import Section
from dashboard_compiler.sections.view import KbnSection
from dashboard_compiler.shared.config import stable_id_generator
from dashboard_compiler.shared.defaults import default_false, default_true
from dashboard_compiler.shared.logging import log_compile
from dashboard_compiler.shared.view import KbnReference

CORE_MIGRATION_VERSION: str = '8.8.0'
TYPE_MIGRATION_VERSION: str = '10.2.0'


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
def compile_dashboard_sections(
    sections: list[Section],
    start_y: int = 0,
) -> tuple[list[KbnReference], list[KbnBasePanel], list[KbnSection]]:
    """Compile dashboard sections and their panels.

    Args:
        sections: The list of sections to compile.
        start_y: The starting y position for the first section.

    Returns:
        tuple: References, panels (with sectionId), and section view models.

    """
    kbn_sections: list[KbnSection] = []
    kbn_panels: list[KbnBasePanel] = []
    kbn_references: list[KbnReference] = []

    current_y = start_y

    for section in sections:
        # Use explicit y position if provided, otherwise use calculated position
        section_y = section.y if section.y is not None else current_y

        # Generate section ID
        section_id = section.id or stable_id_generator(values=['section', section.title])

        # Compile the section
        kbn_section = compile_section(section, section_y)
        kbn_sections.append(kbn_section)

        # Compile panels within the section
        for panel in section.panels:
            # Panels need explicit positions within sections
            if panel.position.x is None or panel.position.y is None:
                msg = f'Panel "{panel.title}" in section "{section.title}" must have explicit position'
                raise ValueError(msg)

            grid = Grid(x=panel.position.x, y=panel.position.y, w=panel.size.width, h=panel.size.h)
            new_references, new_panel = compile_dashboard_panel(panel=panel, grid=grid)

            # Add sectionId to the panel's gridData
            grid_with_section = KbnGridData(
                x=new_panel.gridData.x,
                y=new_panel.gridData.y,
                w=new_panel.gridData.w,
                h=new_panel.gridData.h,
                i=new_panel.gridData.i,
                section_id=section_id,
            )
            updated_panel = new_panel.model_copy(update={'gridData': grid_with_section})

            kbn_panels.append(updated_panel)
            kbn_references.extend(
                [convert_to_panel_reference(kbn_reference=ref, panel_index=new_panel.panelIndex) for ref in new_references]
            )

        # Update current_y for the next section (section header + max panel height)
        if len(section.panels) > 0:
            max_panel_bottom = max(p.position.y + p.size.h for p in section.panels if p.position.y is not None)
            current_y = section_y + max_panel_bottom + 1
        else:
            current_y = section_y + 1

    return kbn_references, kbn_panels, kbn_sections


@log_compile
def compile_dashboard_attributes(dashboard: Dashboard) -> tuple[list[KbnReference], KbnDashboardAttributes]:
    """Compile the attributes of a Dashboard object into its Kibana view model representation.

    Args:
        dashboard (Dashboard): The Dashboard object to compile.

    Returns:
        tuple: A tuple containing the list of references and the compiled dashboard attributes.

    """
    panel_references, panels = compile_dashboard_panels(
        dashboard.panels,
        layout_algorithm=dashboard.settings.layout_algorithm,
    )

    # Compile sections and their panels
    kbn_sections: list[KbnSection] | None = None
    if len(dashboard.sections) > 0:
        # Calculate starting y for sections (after global panels)
        start_y = 0
        if len(panels) > 0:
            start_y = max(p.gridData.y + p.gridData.h for p in panels)

        section_references, section_panels, kbn_sections = compile_dashboard_sections(
            dashboard.sections,
            start_y=start_y,
        )
        panels.extend(section_panels)
        panel_references.extend(section_references)

    control_group_input, control_references = compile_control_group(
        control_settings=dashboard.settings.controls, controls=dashboard.controls
    )

    # Merge panel and control references
    all_references = panel_references + control_references

    return all_references, KbnDashboardAttributes(
        title=dashboard.name,
        description=dashboard.description or '',
        panelsJSON=panels,
        kibanaSavedObjectMeta=KbnSavedObjectMeta(
            searchSourceJSON=KbnSearchSourceJSON(
                filter=compile_filters(filters=dashboard.filters),
                query=compile_nonesql_query(query=dashboard.query) if dashboard.query else KbnQuery(query='', language='kuery'),
            ),
        ),
        optionsJSON=compile_dashboard_options(settings=dashboard.settings),
        timeRestore=False,
        version=1,
        controlGroupInput=control_group_input,
        sections=kbn_sections,
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
