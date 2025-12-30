from typing import Annotated, Literal, cast

from pydantic import Discriminator, Tag

from dashboard_compiler.panels.charts.config import ESQLPanel, LensMultiLayerPanel, LensPanel
from dashboard_compiler.panels.images import ImagePanel
from dashboard_compiler.panels.links import LinksPanel
from dashboard_compiler.panels.markdown import MarkdownPanel
from dashboard_compiler.panels.search import SearchPanel

__all__ = ['PanelTypes']


def _panel_discriminator(v: object) -> Literal['markdown', 'search', 'links', 'image', 'lens', 'multi_layer', 'esql']:
    """Discriminate between panel types.

    Most panels can be discriminated by their 'type' field, but chart panels
    (LensPanel, LensMultiLayerPanel, ESQLPanel) all use type='charts', so we
    need to examine their fields to determine the specific type.

    Args:
        v: The raw panel data (dict) or an already-validated Panel object

    Returns:
        Literal tag indicating which panel type to use

    """
    # Handle already-validated panel objects - check their actual type
    if not isinstance(v, dict):
        # Get the class name and map to discriminator tag
        class_name = type(v).__name__
        type_map: dict[str, Literal['markdown', 'search', 'links', 'image', 'lens', 'multi_layer', 'esql']] = {
            'MarkdownPanel': 'markdown',
            'SearchPanel': 'search',
            'LinksPanel': 'links',
            'ImagePanel': 'image',
            'LensPanel': 'lens',
            'LensMultiLayerPanel': 'multi_layer',
            'ESQLPanel': 'esql',
        }
        if class_name in type_map:
            return type_map[class_name]
        msg = f'Unknown panel class: {class_name}'
        raise TypeError(msg)

    # Handle raw dict data during initial validation
    # Cast to dict[str, object] so we can safely access 'type' field
    v_dict = cast('dict[str, object]', v)
    panel_type = v_dict.get('type')

    # Most panel types can be discriminated by their 'type' field
    if panel_type in ('markdown', 'search', 'links', 'image'):
        return cast('Literal["markdown", "search", "links", "image"]', panel_type)

    # Chart panels all have type='charts', so discriminate by fields
    if panel_type == 'charts':
        if 'esql' in v_dict:
            return 'esql'
        if 'layers' in v_dict:
            return 'multi_layer'
        if 'chart' in v_dict:
            return 'lens'

    msg = f'Cannot determine panel type from data: type={panel_type}, keys={list(v_dict.keys())}'
    raise ValueError(msg)


# Main panel union with custom discriminator
type PanelTypes = Annotated[
    Annotated[MarkdownPanel, Tag('markdown')]
    | Annotated[SearchPanel, Tag('search')]
    | Annotated[LinksPanel, Tag('links')]
    | Annotated[ImagePanel, Tag('image')]
    | Annotated[LensPanel, Tag('lens')]
    | Annotated[LensMultiLayerPanel, Tag('multi_layer')]
    | Annotated[ESQLPanel, Tag('esql')],
    Discriminator(_panel_discriminator),
]
