"""Dashboard Panels."""

from .config import PanelTypes
from .images import ImagePanel
from .links import LinksPanel
from .markdown import MarkdownPanel
from .search import SearchPanel

__all__ = [
    'ImagePanel',
    'LinksPanel',
    'MarkdownPanel',
    'PanelTypes',
    'SearchPanel',
]
