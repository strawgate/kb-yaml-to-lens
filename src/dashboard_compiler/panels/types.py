from typing import Annotated

from pydantic import Discriminator, Tag

from dashboard_compiler.panels.charts.config import ESQLPanel, LensMultiLayerPanel, LensPanel
from dashboard_compiler.panels.images import ImagePanel
from dashboard_compiler.panels.links import LinksPanel
from dashboard_compiler.panels.markdown import MarkdownPanel
from dashboard_compiler.panels.search import SearchPanel

__all__ = ['PanelTypes', 'get_panel_type']


def get_panel_type(v: dict[str, object] | object) -> str:  # noqa: PLR0911, PLR0912
    """Extract panel type for discriminated union validation.

    Args:
        v: Either a dict (during validation) or a panel instance.

    Returns:
        str: The panel type identifier.

    """
    simple_types = {'markdown': 'markdown', 'search': 'search', 'links': 'links', 'image': 'image'}
    simple_attrs = {'markdown': 'markdown', 'search': 'search', 'links_config': 'links', 'image': 'image'}

    if isinstance(v, dict):
        for key, panel_type in simple_types.items():
            if key in v:
                return panel_type
        if ('type' in v and v['type'] == 'multi_layer_charts') or 'layers' in v:
            return 'multi_layer_charts'
        if 'esql' in v:
            return 'esql_charts'
        if 'chart' in v:
            return 'lens_charts'
    else:
        for attr, panel_type in simple_attrs.items():
            if hasattr(v, attr):
                return panel_type
        if (hasattr(v, 'type') and v.type == 'multi_layer_charts') or hasattr(v, 'layers'):  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
            return 'multi_layer_charts'
        if hasattr(v, 'esql'):
            return 'esql_charts'
        if hasattr(v, 'chart'):
            return 'lens_charts'

    if isinstance(v, dict):
        msg = f'Cannot determine panel type from dict with keys: {list(v)}'  # pyright: ignore[reportUnknownArgumentType]
    else:
        msg = f'Cannot determine panel type from object: {type(v).__name__}'
    raise ValueError(msg)


type PanelTypes = Annotated[
    Annotated[MarkdownPanel, Tag('markdown')]
    | Annotated[SearchPanel, Tag('search')]
    | Annotated[LinksPanel, Tag('links')]
    | Annotated[ImagePanel, Tag('image')]
    | Annotated[ESQLPanel, Tag('esql_charts')]
    | Annotated[LensPanel, Tag('lens_charts')]
    | Annotated[LensMultiLayerPanel, Tag('multi_layer_charts')],
    Discriminator(get_panel_type),
]
