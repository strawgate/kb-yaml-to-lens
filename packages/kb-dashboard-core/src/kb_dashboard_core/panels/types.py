from typing import Annotated

from pydantic import Discriminator, Tag

from kb_dashboard_core.panels.charts.config import ESQLPanel, LensPanel
from kb_dashboard_core.panels.images import ImagePanel
from kb_dashboard_core.panels.links import LinksPanel
from kb_dashboard_core.panels.markdown import MarkdownPanel
from kb_dashboard_core.panels.search import SearchPanel
from kb_dashboard_core.panels.vega import VegaPanel

__all__ = ['PanelTypes', 'get_panel_type']


def get_panel_type(v: dict[str, object] | object) -> str:
    """Extract panel type for discriminated union validation.

    Args:
        v: Either a dict (during validation) or a panel instance.

    Returns:
        str: The panel type identifier.

    """
    simple_types = {'markdown': 'markdown', 'search': 'search', 'links': 'links', 'image': 'image', 'vega': 'vega'}
    simple_attrs = {'markdown': 'markdown', 'search': 'search', 'links_config': 'links', 'image': 'image', 'vega': 'vega'}

    if isinstance(v, dict):
        for key, panel_type in simple_types.items():
            if key in v:
                return panel_type
        if 'lens' in v:
            return 'lens'
        if 'esql' in v:
            return 'esql'
    else:
        for attr, panel_type in simple_attrs.items():
            if hasattr(v, attr):
                return panel_type
        if hasattr(v, 'lens'):
            return 'lens'
        if hasattr(v, 'esql'):
            return 'esql'

    if isinstance(v, dict):
        keys = list(v)  # pyright: ignore[reportUnknownArgumentType]
        msg = (
            f'Cannot determine panel type from dict with keys: {keys}. '
            'Each panel must have exactly one type discriminator key: '
            "'markdown', 'search', 'links', 'image', 'lens', 'esql', or 'vega'."
        )
    else:
        msg = f'Cannot determine panel type from object: {type(v).__name__}'
    raise ValueError(msg)


type PanelTypes = Annotated[
    Annotated[MarkdownPanel, Tag('markdown')]
    | Annotated[SearchPanel, Tag('search')]
    | Annotated[LinksPanel, Tag('links')]
    | Annotated[ImagePanel, Tag('image')]
    | Annotated[LensPanel, Tag('lens')]
    | Annotated[ESQLPanel, Tag('esql')]
    | Annotated[VegaPanel, Tag('vega')],
    Discriminator(get_panel_type),
]
