from typing import Annotated

from pydantic import Discriminator, Tag

from dashboard_compiler.panels.charts.config import LensPanel
from dashboard_compiler.panels.images import ImagePanel
from dashboard_compiler.panels.links import LinksPanel
from dashboard_compiler.panels.markdown import MarkdownPanel
from dashboard_compiler.panels.search import SearchPanel

__all__ = ['PanelTypes', 'get_panel_type']


def get_panel_type(v: dict[str, object] | object) -> str:
    """Extract panel type for discriminated union validation.

    Args:
        v: Either a dict (during validation) or a panel instance.

    Returns:
        str: The panel type identifier ('markdown', 'search', 'links', 'image', 'charts').

    """
    if isinstance(v, dict):
        # Check for panel type discriminator keys in dict
        type_checks = [
            ('markdown', 'markdown'),
            ('search', 'search'),
            ('links', 'links'),
            ('image', 'image'),
        ]
        for key, panel_type in type_checks:
            if key in v:
                return panel_type
        # Charts can have multiple discriminator keys
        if 'charts' in v or 'chart' in v or 'esql' in v:
            return 'charts'
        msg = f'Cannot determine panel type from dict with keys: {list(v)}'  # pyright: ignore[reportUnknownArgumentType]
        raise ValueError(msg)

    # Check for panel type by object attributes
    attr_checks = [
        ('markdown', 'markdown'),
        ('search', 'search'),
        ('links_config', 'links'),
        ('image', 'image'),
    ]
    for attr, panel_type in attr_checks:
        if hasattr(v, attr):
            return panel_type
    # Charts can have multiple attribute variations
    if hasattr(v, 'chart') or hasattr(v, 'esql'):
        return 'charts'
    msg = f'Cannot determine panel type from object: {type(v).__name__}'
    raise ValueError(msg)


type PanelTypes = Annotated[
    Annotated[MarkdownPanel, Tag('markdown')]
    | Annotated[SearchPanel, Tag('search')]
    | Annotated[LinksPanel, Tag('links')]
    | Annotated[ImagePanel, Tag('image')]
    | Annotated[LensPanel, Tag('charts')],
    Discriminator(get_panel_type),
]
