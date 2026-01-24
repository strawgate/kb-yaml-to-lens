"""Decompile Kibana links panels back to config models."""

from typing import Any

from dashboard_compiler.panels.config import Position, Size
from dashboard_compiler.panels.links.config import (
    DashboardLink,
    LinksPanel,
    LinksPanelConfig,
    LinkTypes,
    UrlLink,
)
from dashboard_compiler.shared.decompile import ReferenceResolver
from dashboard_compiler.shared.decompile_context import DecompileContext


def decompile_dashboard_link(
    kbn_link: dict[str, Any],
    *,
    reference_resolver: ReferenceResolver,
) -> DashboardLink:
    """Decompile a dashboard link."""
    # Resolve destination dashboard ID from reference
    ref_name = kbn_link.get('destinationRefName', '')
    ref = reference_resolver.resolve_by_name(ref_name)
    dashboard_id = ref.id if ref is not None else ''

    options = kbn_link.get('options', {})

    return DashboardLink.model_validate(
        {
            'id': kbn_link.get('id'),
            'label': kbn_link.get('label'),
            'dashboard': dashboard_id,
            'new_tab': options.get('openInNewTab') if options.get('openInNewTab') else None,
            'with_time': options.get('useCurrentDateRange') if options.get('useCurrentDateRange') is not True else None,
            'with_filters': options.get('useCurrentFilters') if options.get('useCurrentFilters') is not True else None,
        }
    )


def decompile_url_link(kbn_link: dict[str, Any]) -> UrlLink:
    """Decompile a URL/web link."""
    options = kbn_link.get('options', {})

    return UrlLink.model_validate(
        {
            'id': kbn_link.get('id'),
            'label': kbn_link.get('label'),
            'url': kbn_link.get('destination', ''),
            'encode': options.get('encodeUrl') if options.get('encodeUrl') is not True else None,
            'new_tab': options.get('openInNewTab') if options.get('openInNewTab') else None,
        }
    )


def decompile_link(
    kbn_link: dict[str, Any],
    *,
    context: DecompileContext,
    reference_resolver: ReferenceResolver,
) -> LinkTypes | None:
    """Decompile a single link."""
    link_type = kbn_link.get('type', '')

    if link_type == 'dashboardLink':
        return decompile_dashboard_link(kbn_link, reference_resolver=reference_resolver)
    if link_type == 'externalLink':
        return decompile_url_link(kbn_link)
    context.warn(f'Unknown link type: {link_type}')
    return None


def decompile_links_panel(
    kbn_panel: dict[str, Any],
    *,
    context: DecompileContext,
    reference_resolver: ReferenceResolver,
) -> LinksPanel:
    """Decompile a Kibana links panel to config model.

    Args:
        kbn_panel: The Kibana panel dict.
        context: Decompilation context for warnings.
        reference_resolver: Resolver for panel references.

    Returns:
        The decompiled LinksPanel config.

    """
    grid_data = kbn_panel.get('gridData', {})
    embeddable_config = kbn_panel.get('embeddableConfig', {})
    attributes = embeddable_config.get('attributes', {})

    # Extract grid info
    size = Size(
        w=grid_data.get('w', 12),
        h=grid_data.get('h', 8),
    )
    position = Position(
        x=grid_data.get('x'),
        y=grid_data.get('y'),
    )

    # Decompile links
    kbn_links = attributes.get('links', [])
    # Sort by order
    sorted_links = sorted(kbn_links, key=lambda x: x.get('order', 0))

    links: list[LinkTypes] = []
    for kbn_link in sorted_links:
        link = decompile_link(kbn_link, context=context, reference_resolver=reference_resolver)
        if link is not None:
            links.append(link)

    # Get layout, only include if not default
    layout = attributes.get('layout', 'horizontal')

    links_config = LinksPanelConfig.model_validate(
        {
            'layout': layout if layout != 'horizontal' else None,
            'items': links,
        }
    )

    # Extract panel metadata
    panel_id = kbn_panel.get('panelIndex')
    hide_title = embeddable_config.get('hidePanelTitles')

    return LinksPanel.model_validate(
        {
            'id': panel_id,
            'title': '',  # Links panels typically don't have titles
            'hide_title': hide_title if hide_title else None,
            'size': size.model_dump(),
            'position': position.model_dump(),
            'links': links_config.model_dump(exclude_none=True),
        }
    )
