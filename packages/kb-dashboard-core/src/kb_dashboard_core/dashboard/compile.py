"""Compile a Dashboard into its Kibana view model representation."""

from collections.abc import Sequence

from kb_dashboard_core.controls.compile import compile_control_group
from kb_dashboard_core.dashboard.config import Dashboard, DashboardSection, DashboardSettings
from kb_dashboard_core.dashboard.view import (
    KbnDashboard,
    KbnDashboardAttributes,
    KbnDashboardOptions,
    KbnDashboardSection,
    KbnDashboardSectionGridData,
)
from kb_dashboard_core.filters.compile import compile_filters
from kb_dashboard_core.panels.compile import compile_dashboard_panels
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


def _panel_display_title(panel: PanelTypes, idx: int) -> str:
    return panel.title if len(panel.title) > 0 else f'Panel #{idx + 1}'


def _validate_panel_section_usage_without_sections(source_panels: Sequence[PanelTypes]) -> None:
    for idx, panel in enumerate(source_panels):
        if panel.section is not None:
            msg = (
                f'Panel "{_panel_display_title(panel, idx)}" references section "{panel.section}", '
                'but dashboard.sections is empty.'
            )
            raise ValueError(msg)


def _build_section_entries(section_configs: Sequence[DashboardSection]) -> tuple[list[tuple[DashboardSection, str]], dict[str, str]]:
    section_entries: list[tuple[DashboardSection, str]] = []
    title_to_uid: dict[str, str] = {}
    explicit_id_to_uid: dict[str, str] = {}
    seen_compiled_uids: set[str] = set()

    for section in section_configs:
        section_uid = section.id or stable_id_generator(['section', section.title])

        if section_uid in seen_compiled_uids:
            msg = f'Duplicate compiled section id "{section_uid}". Section ids must be unique.'
            raise ValueError(msg)
        seen_compiled_uids.add(section_uid)

        if section.title in title_to_uid:
            msg = f'Duplicate section title "{section.title}". Section titles must be unique.'
            raise ValueError(msg)
        title_to_uid[section.title] = section_uid

        if section.id is not None:
            if section.id in explicit_id_to_uid:
                msg = f'Duplicate section id "{section.id}". Section ids must be unique.'
                raise ValueError(msg)
            if section.id in title_to_uid and title_to_uid[section.id] != section_uid:
                msg = (
                    f'Section id "{section.id}" conflicts with another section title. '
                    'Use unique ids/titles for unambiguous panel.section references.'
                )
                raise ValueError(msg)
            explicit_id_to_uid[section.id] = section_uid

        section_entries.append((section, section_uid))

    return section_entries, {**title_to_uid, **explicit_id_to_uid}


def _assign_sections_to_panels(
    source_panels: Sequence[PanelTypes],
    compiled_panels: Sequence[KbnBasePanel],
    section_lookup: dict[str, str],
    section_entries: Sequence[tuple[DashboardSection, str]],
) -> tuple[list[KbnBasePanel], dict[str, list[int]]]:
    section_panel_ys: dict[str, list[int]] = {section_uid: [] for _, section_uid in section_entries}
    resolved_panels: list[KbnBasePanel] = []

    for idx, (source_panel, compiled_panel) in enumerate(zip(source_panels, compiled_panels, strict=True)):
        if source_panel.section is None:
            resolved_panels.append(compiled_panel)
            continue

        section_uid = section_lookup.get(source_panel.section)
        if section_uid is None:
            msg = (
                f'Panel "{_panel_display_title(source_panel, idx)}" references unknown section "{source_panel.section}". '
                'Add this section to dashboard.sections.'
            )
            raise ValueError(msg)

        section_panel_ys[section_uid].append(compiled_panel.gridData.y)
        updated_grid_data = compiled_panel.gridData.model_copy(update={'sectionId': section_uid})
        resolved_panels.append(compiled_panel.model_copy(update={'gridData': updated_grid_data}))

    return resolved_panels, section_panel_ys


def _compile_sections(
    section_entries: Sequence[tuple[DashboardSection, str]],
    section_panel_ys: dict[str, list[int]],
) -> list[KbnDashboardSection]:
    compiled_sections: list[KbnDashboardSection] = []
    next_auto_y = 0

    for section, section_uid in section_entries:
        section_y_values = section_panel_ys[section_uid]
        section_y = section.y if section.y is not None else (min(section_y_values) if len(section_y_values) > 0 else next_auto_y)
        next_auto_y = max(next_auto_y, section_y + 1)
        compiled_sections.append(
            KbnDashboardSection(
                title=section.title,
                collapsed=section.collapsed,
                gridData=KbnDashboardSectionGridData(y=section_y, i=section_uid),
            )
        )

    return compiled_sections


@log_compile
def _resolve_sections(
    section_configs: Sequence[DashboardSection],
    source_panels: Sequence[PanelTypes],
    compiled_panels: Sequence[KbnBasePanel],
) -> tuple[list[KbnBasePanel], list[KbnDashboardSection] | None]:
    """Resolve section references for panels and compile dashboard sections."""
    if len(source_panels) != len(compiled_panels):
        msg = (
            f'Internal error: source and compiled panel counts differ '
            f'({len(source_panels)} != {len(compiled_panels)}).'
        )
        raise ValueError(msg)

    if len(section_configs) == 0:
        _validate_panel_section_usage_without_sections(source_panels)
        return list(compiled_panels), None

    section_entries, section_lookup = _build_section_entries(section_configs)
    resolved_panels, section_panel_ys = _assign_sections_to_panels(
        source_panels=source_panels,
        compiled_panels=compiled_panels,
        section_lookup=section_lookup,
        section_entries=section_entries,
    )
    compiled_sections = _compile_sections(
        section_entries=section_entries,
        section_panel_ys=section_panel_ys,
    )
    return resolved_panels, compiled_sections


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
    panels, sections = _resolve_sections(
        section_configs=dashboard.sections,
        source_panels=dashboard.panels,
        compiled_panels=panels,
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
