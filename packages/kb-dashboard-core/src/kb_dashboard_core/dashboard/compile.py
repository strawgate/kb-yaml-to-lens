"""Compile a Dashboard into its Kibana view model representation."""

from kb_dashboard_core.controls.compile import compile_control_group
from kb_dashboard_core.dashboard.config import Dashboard, DashboardSettings
from kb_dashboard_core.dashboard.view import KbnDashboard, KbnDashboardAttributes, KbnDashboardOptions
from kb_dashboard_core.filters.compile import compile_filters
from kb_dashboard_core.panels.compile import compile_dashboard_panels
from kb_dashboard_core.panels.view import KbnSavedObjectMeta, KbnSearchSourceJSON
from kb_dashboard_core.queries.compile import compile_nonesql_query
from kb_dashboard_core.queries.view import KbnQuery
from kb_dashboard_core.shared.config import stable_id_generator
from kb_dashboard_core.shared.defaults import default_false, default_if_none, default_true
from kb_dashboard_core.shared.logging import log_compile
from kb_dashboard_core.shared.view import KbnReference

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
