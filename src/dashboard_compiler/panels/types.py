from typing import Annotated

from pydantic import Discriminator, Tag

from dashboard_compiler.panels.charts.config import LensPanel
from dashboard_compiler.panels.images import ImagePanel
from dashboard_compiler.panels.links import LinksPanel
from dashboard_compiler.panels.markdown import MarkdownPanel
from dashboard_compiler.panels.search import SearchPanel

__all__ = ['PanelTypes']


def get_panel_type(v: dict | object) -> str:
    """Extract panel type for discriminated union validation.

    Args:
        v: Either a dict (during validation) or a panel instance.

    Returns:
        str: The panel type identifier.

    """
    if isinstance(v, dict):
        return v.get('type', 'unknown')
    return getattr(v, 'type', 'unknown')


type PanelTypes = Annotated[
    Annotated[MarkdownPanel, Tag('markdown')]
    | Annotated[SearchPanel, Tag('search')]
    | Annotated[LinksPanel, Tag('links')]
    | Annotated[ImagePanel, Tag('image')]
    | Annotated[LensPanel, Tag('charts')],
    Discriminator(get_panel_type),
]
