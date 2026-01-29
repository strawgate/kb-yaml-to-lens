"""Compilation functions for drilldowns."""

from kb_dashboard_core.panels.drilldowns.config import DashboardDrilldown, DrilldownTrigger, DrilldownTypes, UrlDrilldown
from kb_dashboard_core.panels.drilldowns.view import (
    DASHBOARD_TO_DASHBOARD_DRILLDOWN,
    URL_DRILLDOWN,
    KbnDashboardDrilldownConfig,
    KbnDrilldownAction,
    KbnDrilldownEvent,
    KbnDynamicActions,
    KbnEnhancements,
    KbnUrlDrilldownConfig,
)
from kb_dashboard_core.shared.config import stable_id_generator
from kb_dashboard_core.shared.view import KbnReference


def compile_trigger(trigger: DrilldownTrigger) -> str:
    """Convert a user-facing trigger type to Kibana trigger type.

    Args:
        trigger: User-facing trigger type.

    Returns:
        str: Kibana trigger type string.
    """
    match trigger:
        case DrilldownTrigger.click:
            return 'VALUE_CLICK_TRIGGER'
        case DrilldownTrigger.filter:
            return 'FILTER_TRIGGER'
        case DrilldownTrigger.range:
            return 'SELECT_RANGE_TRIGGER'
        case _:  # pyright: ignore[reportUnnecessaryComparison]
            msg = f'Unsupported drilldown trigger: {trigger!s}'  # pyright: ignore[reportUnreachable]
            raise ValueError(msg)


def compile_dashboard_drilldown(drilldown: DashboardDrilldown, order: int) -> tuple[KbnReference, KbnDrilldownEvent]:
    """Compile a dashboard drilldown into Kibana view models.

    Args:
        drilldown: Dashboard drilldown configuration.
        order: Position in the drilldown list (used for stable ID generation).

    Returns:
        tuple[KbnReference, KbnDrilldownEvent]: Dashboard reference and drilldown event.
    """
    event_id = drilldown.id if drilldown.id is not None else stable_id_generator([drilldown.name, str(order)])

    reference = KbnReference(
        type='dashboard',
        id=drilldown.dashboard,
        name=f'drilldown:{DASHBOARD_TO_DASHBOARD_DRILLDOWN}:{event_id}:dashboardId',
    )

    config = KbnDashboardDrilldownConfig(
        useCurrentFilters=drilldown.with_filters,
        useCurrentDateRange=drilldown.with_time,
    )

    event = KbnDrilldownEvent(
        eventId=event_id,
        triggers=[compile_trigger(t) for t in drilldown.triggers],
        action=KbnDrilldownAction(
            factoryId=DASHBOARD_TO_DASHBOARD_DRILLDOWN,
            name=drilldown.name,
            config=config.model_dump(by_alias=True),
        ),
    )

    return reference, event


def compile_url_drilldown(drilldown: UrlDrilldown, order: int) -> KbnDrilldownEvent:
    """Compile a URL drilldown into Kibana view model.

    Args:
        drilldown: URL drilldown configuration.
        order: Position in the drilldown list (used for stable ID generation).

    Returns:
        KbnDrilldownEvent: Drilldown event.
    """
    event_id = drilldown.id if drilldown.id is not None else stable_id_generator([drilldown.name, str(order)])

    config = KbnUrlDrilldownConfig(
        url={'template': drilldown.url},
        openInNewTab=drilldown.new_tab,
        encodeUrl=drilldown.encode_url,
    )

    return KbnDrilldownEvent(
        eventId=event_id,
        triggers=[compile_trigger(t) for t in drilldown.triggers],
        action=KbnDrilldownAction(
            factoryId=URL_DRILLDOWN,
            name=drilldown.name,
            config=config.model_dump(by_alias=True),
        ),
    )


def compile_drilldowns(drilldowns: list[DrilldownTypes]) -> tuple[list[KbnReference], KbnEnhancements]:
    """Compile a list of drilldowns into Kibana view models.

    Args:
        drilldowns: List of drilldown configurations.

    Returns:
        tuple[list[KbnReference], KbnEnhancements]: List of dashboard references and enhancements.
    """
    references: list[KbnReference] = []
    events: list[KbnDrilldownEvent] = []

    for i, drilldown in enumerate(drilldowns):
        if isinstance(drilldown, DashboardDrilldown):
            ref, event = compile_dashboard_drilldown(drilldown, order=i)
            references.append(ref)
            events.append(event)
            continue

        if isinstance(drilldown, UrlDrilldown):  # pyright: ignore[reportUnnecessaryIsInstance]
            event = compile_url_drilldown(drilldown, order=i)
            events.append(event)
            continue

        # Exhaustive check for unhandled types
        msg = f'Unknown drilldown type: {type(drilldown).__name__}'
        raise TypeError(msg)

    return references, KbnEnhancements(dynamicActions=KbnDynamicActions(events=events))
