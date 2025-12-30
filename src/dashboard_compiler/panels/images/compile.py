"""Compile Image panels into their Kibana representations."""

from dashboard_compiler.panels.images.config import ImagePanel
from dashboard_compiler.panels.images.view import (
    KbnImageConfig,
    KbnImageEmbeddableConfig,
    KbnUrlImageInfoSrc,
    KbnUrlImageSizing,
)
from dashboard_compiler.shared.view import KbnReference


def compile_image_panel_config(image_panel: ImagePanel) -> tuple[list[KbnReference], KbnImageEmbeddableConfig]:
    """Compile an ImagePanel into its Kibana view model representation.

    Args:
        image_panel (ImagePanel): The Image panel to compile.

    Returns:
        tuple[list[KbnReference], KbnImageEmbeddableConfig]: The compiled Kibana Image panel view model and references.

    """
    image_config = KbnImageConfig(
        src=KbnUrlImageInfoSrc(url=image_panel.image.from_url),
        altText=image_panel.image.description or '',
        backgroundColor=image_panel.image.background_color or '',
        sizing=KbnUrlImageSizing(
            objectFit=image_panel.image.fit or 'contain',
        ),
    )

    embeddable_config = KbnImageEmbeddableConfig(
        hidePanelTitles=image_panel.hide_title,
        enhancements={'dynamicActions': {'events': []}},
        imageConfig=image_config,
    )

    return [], embeddable_config
