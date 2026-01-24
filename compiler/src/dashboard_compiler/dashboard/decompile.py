"""Decompile a Kibana Dashboard view model back to config model.

This module provides the reverse transformation of compile.py, converting
Kibana dashboard JSON back into Dashboard configuration models.
"""

from dashboard_compiler.controls.decompile import decompile_control_group
from dashboard_compiler.dashboard.config import (
    Dashboard,
    DashboardSettings,
    DashboardSyncSettings,
    TimeRange,
)
from dashboard_compiler.dashboard.view import KbnDashboard, KbnDashboardOptions
from dashboard_compiler.filters.decompile import decompile_filters
from dashboard_compiler.panels.decompile import decompile_panels
from dashboard_compiler.queries.decompile import decompile_query
from dashboard_compiler.shared.decompile import ReferenceResolver
from dashboard_compiler.shared.decompile_context import DecompileContext
from dashboard_compiler.shared.logging import log_compile


def decompile_dashboard_options(options: KbnDashboardOptions) -> tuple[DashboardSyncSettings, bool | None, bool | None]:
    """Decompile KbnDashboardOptions to sync settings and margin/title settings.

    Args:
        options: The Kibana dashboard options.

    Returns:
        Tuple of (sync_settings, margins, titles).

    """
    sync = DashboardSyncSettings(
        cursor=options.syncCursor if options.syncCursor is not True else None,
        tooltips=options.syncTooltips if options.syncTooltips is not False else None,
        colors=options.syncColors if options.syncColors is not False else None,
    )

    # Convert from Kibana's useMargins to our margins (same semantics)
    margins = options.useMargins if options.useMargins is not True else None

    # Convert from Kibana's hidePanelTitles to our titles (inverted)
    titles = not options.hidePanelTitles if options.hidePanelTitles is not False else None

    return sync, margins, titles


def decompile_time_range(
    time_restore: bool,
    time_from: str | None,
    time_to: str | None,
) -> TimeRange | None:
    """Decompile time range settings.

    Args:
        time_restore: Whether time range is enabled.
        time_from: Start time.
        time_to: End time.

    Returns:
        TimeRange config or None if not set.

    """
    if not time_restore or time_from is None:
        return None

    # Don't include 'to' if it's the default 'now'
    to_time = time_to if time_to != 'now' else None

    # Use 'from' and 'to' as keyword arguments (field aliases)
    return TimeRange.model_validate({'from': time_from, 'to': to_time})


@log_compile
def decompile_dashboard(kbn_dashboard: KbnDashboard, context: DecompileContext) -> Dashboard:
    """Decompile a KbnDashboard view model back to Dashboard config model.

    Args:
        kbn_dashboard: The Kibana dashboard view model to decompile.
        context: Decompilation context for warnings and reference resolution.

    Returns:
        The decompiled Dashboard configuration model.

    """
    attrs = kbn_dashboard.attributes

    # Decompile options
    sync_settings, margins, titles = decompile_dashboard_options(attrs.optionsJSON)

    # Decompile control settings and controls
    control_settings, controls = decompile_control_group(
        attrs.controlGroupInput,
        context=context,
    )

    # Build dashboard settings
    settings = DashboardSettings(
        margins=margins,
        sync=sync_settings,
        controls=control_settings,
        titles=titles,
    )

    # Decompile time range
    time_range = decompile_time_range(
        attrs.timeRestore,
        attrs.timeFrom,
        attrs.timeTo,
    )

    # Decompile filters
    search_source = attrs.kibanaSavedObjectMeta.searchSourceJSON
    filters = decompile_filters(search_source.filter, context=context)

    # Decompile query
    query = decompile_query(search_source.query, context=context)

    # Create reference resolver for panel decompilation
    reference_resolver = ReferenceResolver(kbn_dashboard.references)

    # Decompile panels
    # panelsJSON may be a list of dicts or KbnBasePanel objects
    panels_data = attrs.panelsJSON
    if len(panels_data) > 0:
        # Convert to dicts if they're Pydantic models
        panel_dicts_raw = [p.model_dump() if hasattr(p, 'model_dump') else p for p in panels_data]
        # Cast to the expected type - we know these are all dicts at this point
        panel_dicts: list[dict[str, object]] = panel_dicts_raw  # pyright: ignore[reportAssignmentType]
        panels = decompile_panels(panel_dicts, context=context, reference_resolver=reference_resolver)
    else:
        panels = []

    return Dashboard(
        name=attrs.title,
        id=kbn_dashboard.id,
        description=attrs.description if len(attrs.description) > 0 else None,
        time_range=time_range,
        settings=settings,
        query=query,
        filters=filters,
        controls=controls,
        panels=panels,
    )
