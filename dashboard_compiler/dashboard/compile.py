"""Compile a Dashboard into its Kibana view model representation."""

from dashboard_compiler.controls.compile import compile_control_group
from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard.view import KbnDashboard, KbnDashboardAttributes, KbnDashboardOptions
from dashboard_compiler.filters.compile import compile_filters
from dashboard_compiler.panels.compile import compile_dashboard_panels
from dashboard_compiler.panels.view import KbnSavedObjectMeta, KbnSearchSourceJSON
from dashboard_compiler.queries.compile import compile_nonesql_query
from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.shared.config import stable_id_generator
from dashboard_compiler.shared.view import KbnReference


def compile_dashboard_options() -> KbnDashboardOptions:
    """Compile the Kibana Dashboard Options view model.

    Returns:
        KbnDashboardOptions: The compiled Kibana dashboard options view model.

    """
    return KbnDashboardOptions(
        useMargins=True,
        syncColors=False,
        syncCursor=True,
        syncTooltips=False,
        hidePanelTitles=False,
    )


def compile_dashboard_attributes(dashboard: Dashboard) -> tuple[list[KbnReference], KbnDashboardAttributes]:
    """Compile the attributes of a Dashboard object into its Kibana view model representation.

    Args:
        dashboard (Dashboard): The Dashboard object to compile.

    Returns:
        KbnDashboardAttributes: The compiled Kibana dashboard attributes view model.

    """
    references, panels = compile_dashboard_panels(dashboard.panels)

    return references, KbnDashboardAttributes(
        title=dashboard.name,
        description=dashboard.description or '',
        panelsJSON=panels,
        kibanaSavedObjectMeta=KbnSavedObjectMeta(
            searchSourceJSON=KbnSearchSourceJSON(
                filter=compile_filters(filters=dashboard.filters),
                query=compile_nonesql_query(query=dashboard.query) if dashboard.query else KbnQuery(query='', language='kuery'),
            ),
        ),
        optionsJSON=compile_dashboard_options(),
        timeRestore=False,
        version=1,
        controlGroupInput=compile_control_group(control_settings=dashboard.settings.controls, controls=dashboard.controls),
    )


def compile_dashboard(dashboard: Dashboard) -> KbnDashboard:
    """Compile a Dashboard object into its Kibana view model representation.

    Args:
        dashboard (Dashboard): The Dashboard object to compile.

    Returns:
        KbnDashboard: The compiled Kibana dashboard view model.

    """
    kbn_dashboard_id = dashboard.id or stable_id_generator([dashboard.name])

    references, attributes = compile_dashboard_attributes(dashboard)

    # Create the KbnDashboard view model
    return KbnDashboard(
        attributes=attributes,
        coreMigrationVersion='8.8.0',
        created_at='2023-10-01T00:00:00Z',
        created_by='admin',
        id=kbn_dashboard_id,
        managed=False,
        references=references,
        type='dashboard',
        typeMigrationVersion='10.2.0',
        updated_at='2023-10-01T00:00:00Z',
        updated_by='admin',
        version='1',
    )
