from dashboard_compiler.compile.panels.base import compile_panel_shared
from dashboard_compiler.compile.utils import stable_id_generator
from dashboard_compiler.models.config.panels.links import BaseLink, DashboardLink, LinksPanel, UrlLink
from dashboard_compiler.models.views.panels.lens import KbnReference
from dashboard_compiler.models.views.panels.links import KbnLink, KbnLinksPanel, KbnLinksPanelAttributes, KbnLinksPanelEmbeddableConfig


def compile_dashboard_link(link: DashboardLink, link_index: int) -> tuple[KbnReference, KbnLink]:
    """
    Convert a dashboard link object to a KbnLink object and a KbnReference object.

    Args:
        link (DashboardLink): The DashboardLink object to convert.
        link_index (int): The index of the link in the panel.

    Returns:
        Tuple[KbnReference, KbnLink]: The converted KbnReference and KbnLink objects.
    """

    stable_id = stable_id_generator([link.label, str(link_index)])

    link_id = f"link_{stable_id}_dashboard"

    kbn_link = KbnLink(
        type="dashboardLink",
        id=stable_id,
        label=link.label,
        order=link_index,
        destinationRefName=link_id,
    )

    # The id of the reference is supposed to be the target dashboard id,
    # the name of the reference is the link id
    kbn_reference = KbnReference(
        type="dashboard",
        id=link.dashboard,
        name=link_id,
    )

    return kbn_reference, kbn_link


def compile_url_link(link: UrlLink, link_index: int) -> KbnLink:
    """
    Convert a web url link object to a KbnLink object.

    Args:
        link (UrlLink): The UrlLink object to convert.
        panel_index (str): The index of the panel to which this link belongs.

    Returns:
        KbnLink: The converted KbnLink object.
    """
    id = stable_id_generator([link.label, str(link_index)])
    return KbnLink(
        type="externalLink",
        destination=link.url,
        id=id,
        label=link.label,
        order=link_index,
    )


def compile_links(links: list[BaseLink]) -> tuple[list[KbnReference], list[KbnLink]]:
    """
    Convert a list of KbnLink objects to a list of KbnReference objects.

    Args:
        links (list[KbnLink]): The list of KbnLink objects to convert.
        panel_index (str): The index of the panel to which these links belong.

    Returns:
        list[KbnReference]: The converted list of KbnReference objects.
    """

    kbn_references = []
    kbn_links = []
    for i, link in enumerate(links):
        if isinstance(link, DashboardLink):
            kbn_reference, kbn_link = compile_dashboard_link(link, i)
            kbn_references.append(kbn_reference)
            kbn_links.append(kbn_link)
        elif isinstance(link, UrlLink):
            kbn_links.append(compile_url_link(link, i))
        else:
            raise ValueError(f"Unsupported link type: {link.type}")

    return kbn_references, kbn_links


def compile_links_panel(panel: LinksPanel) -> tuple[list[KbnReference], KbnLinksPanel]:
    """
    Compile a LinksPanel into its Kibana view model representation.

    Args:
        panel (LinksPanel): The Links panel to compile.

    Returns:
        KbnLinksPanel: The compiled Kibana Links panel view model.
    """
    panel_index, grid_data = compile_panel_shared(panel)

    kbn_references, kbn_links = compile_links(panel.links)

    return kbn_references, KbnLinksPanel(
        panelIndex=panel_index,
        gridData=grid_data,
        embeddableConfig=KbnLinksPanelEmbeddableConfig(
            hidePanelTitles=panel.hide_title,
            attributes=KbnLinksPanelAttributes(
                layout=panel.layout,
                links=kbn_links,
            ),
            enhancements={},
        ),
    )
