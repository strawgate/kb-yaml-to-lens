"""Decompile Kibana image panels back to config models."""

from typing import Any

from dashboard_compiler.panels.config import Position, Size
from dashboard_compiler.panels.images.config import ImagePanel, ImagePanelConfig
from dashboard_compiler.shared.decompile_context import DecompileContext


def decompile_image_panel(
    kbn_panel: dict[str, Any],
    *,
    context: DecompileContext,  # noqa: ARG001
) -> ImagePanel:
    """Decompile a Kibana image panel to config model.

    Args:
        kbn_panel: The Kibana panel dict.
        context: Decompilation context for warnings.

    Returns:
        The decompiled ImagePanel config.

    """
    grid_data = kbn_panel.get('gridData', {})
    embeddable_config = kbn_panel.get('embeddableConfig', {})

    # Extract grid info
    size = Size(
        w=grid_data.get('w', 12),
        h=grid_data.get('h', 8),
    )
    position = Position(
        x=grid_data.get('x'),
        y=grid_data.get('y'),
    )

    # Extract image config
    image_config = embeddable_config.get('imageConfig', {})

    # Get the image source - could be URL or file reference
    src = image_config.get('src', {})
    url = src.get('url', '')

    # Alt text
    alt_text = image_config.get('altText', '')

    # Background color
    background_color = image_config.get('backgroundColor', '')

    # Sizing - only include if not default
    sizing_config = image_config.get('sizing', {})
    sizing = sizing_config.get('objectFit', 'contain')

    # Use model_validate with field aliases
    config = ImagePanelConfig.model_validate(
        {
            'from_url': url,
            'description': alt_text if len(alt_text) > 0 else None,
            'background_color': background_color if len(background_color) > 0 else None,
            'fit': sizing if sizing != 'contain' else None,
        }
    )

    # Extract panel metadata
    panel_id = kbn_panel.get('panelIndex')
    hide_title = embeddable_config.get('hidePanelTitles')

    return ImagePanel.model_validate(
        {
            'id': panel_id,
            'title': '',  # Image panels typically don't have titles
            'hide_title': hide_title if hide_title else None,
            'size': size.model_dump(),
            'position': position.model_dump(),
            'image': config.model_dump(exclude_none=True),
        }
    )
