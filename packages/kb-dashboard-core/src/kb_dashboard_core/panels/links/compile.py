"""Compile links for a dashboard into their Kibana view models."""

from collections.abc import Sequence

from kb_dashboard_core.panels.links.config import BaseLink, DashboardLink, LinksPanel, LinkTypes, UrlLink
from kb_dashboard_core.panels.links.view import (
    KbnDashboardLink,
    KbnDashboardLinkOptions,
    KbnLinksPanelAttributes,
    KbnLinksPanelEmbeddableConfig,
    KbnLinkTypes,
    KbnWebLink,
    KbnWebLinkOptions,
)
from kb_dashboard_core.shared.config import stable_id_generator
from kb_dashboard_core.shared.defaults import default_false, default_true
from kb_dashboard_core.shared.view import KbnReference


def compile_dashboard_link(order: int, *, link: DashboardLink) -> tuple[KbnReference, KbnDashboardLink]:
    """Compile a DashboardLink into its Kibana view model representation.

    Args:
        order (int): The order of the link in the list.
        link (DashboardLink): The DashboardLink object to convert.

    Returns:
        Tuple[KbnReference, KbnDashboardLink]: A tuple containing the KbnReference and KbnDashboardLink objects.

    """
    link_id = link.id or stable_id_generator([link.label, str(order)])

    link_ref_id = f'link_{link_id}_dashboard'

    has_options: bool = link.new_tab is not None or link.with_time is not None or link.with_filters is not None

    options: KbnDashboardLinkOptions | None = (
        KbnDashboardLinkOptions(
            openInNewTab=default_false(link.new_tab),
            useCurrentDateRange=default_true(link.with_time),
            useCurrentFilters=default_true(link.with_filters),
        )
        if has_options
        else None
    )

    kbn_link = KbnDashboardLink(
        id=link_id,
        label=link.label,
        order=order,
        destinationRefName=link_ref_id,
        options=options,
    )

    # The id of the reference is supposed to be the target dashboard id,
    # the name of the reference is the link id
    kbn_reference = KbnReference(
        type='dashboard',
        id=link.dashboard,
        name=link_ref_id,
    )

    return kbn_reference, kbn_link


def compile_url_link(order: int, *, link: UrlLink) -> KbnWebLink:
    """Compile a UrlLink into its Kibana view model representation.

    Args:
        order (int): The order of the link in the list.
        link (UrlLink): The UrlLink object to convert.

    Returns:
        KbnWebLink: The compiled KbnWebLink object.

    """
    link_id = stable_id_generator([link.label, str(order)])

    has_options: bool = link.encode is not None or link.new_tab is not None

    options: KbnWebLinkOptions | None = (
        KbnWebLinkOptions(
            openInNewTab=default_false(link.new_tab),
            encodeUrl=default_true(link.encode),
        )
        if has_options
        else None
    )

    return KbnWebLink(
        destination=link.url,
        id=link_id,
        label=link.label or '',
        order=order,
        options=options,
    )


def compile_link(*, link: BaseLink, order: int) -> tuple[KbnReference | None, KbnLinkTypes]:
    """Compile a single link into its Kibana view model representation.

    Args:
        link (BaseLink): The link object to compile.
        order (int): The order of the link in the list.

    Returns:
        KbnLinkTypes: The compiled Kibana link view model.

    """
    if isinstance(link, DashboardLink):
        return compile_dashboard_link(order, link=link)

    if isinstance(link, UrlLink):
        return None, compile_url_link(order, link=link)

    msg = f'Link type {type(link)} is not supported for compilation.'
    raise NotImplementedError(msg)


def compile_links(links: Sequence[LinkTypes]) -> tuple[list[KbnReference], list[KbnLinkTypes]]:
    """Convert a sequence of KbnLink objects to lists of KbnReference and KbnLink objects.

    Args:
        links (Sequence[LinkTypes]): The sequence of link objects to convert.

    Returns:
        tuple[list[KbnReference], list[KbnLinkTypes]]: The converted references and link objects.

    """
    kbn_references: list[KbnReference] = []
    kbn_links: list[KbnLinkTypes] = []

    for i, link in enumerate(links):
        kbn_reference, kbn_link = compile_link(link=link, order=i)

        if kbn_reference is not None:
            kbn_references.append(kbn_reference)

        kbn_links.append(kbn_link)

    return kbn_references, kbn_links


def compile_links_panel_config(links_panel: LinksPanel) -> tuple[list[KbnReference], KbnLinksPanelEmbeddableConfig]:
    """Compile a LinksPanel into its Kibana embeddable configuration.

    Args:
        links_panel (LinksPanel): The Links panel to compile.

    Returns:
        tuple: A tuple containing the compiled references and the Kibana embeddable configuration.

    """
    kbn_references, kbn_links = compile_links(links_panel.links_config.items)

    return kbn_references, KbnLinksPanelEmbeddableConfig(
        hidePanelTitles=links_panel.hide_title,
        attributes=KbnLinksPanelAttributes(
            layout=links_panel.links_config.layout or 'horizontal',
            links=kbn_links,
        ),
        enhancements={},
    )
