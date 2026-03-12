"""Dashboard Panels."""

from .collapsible import CollapsiblePanel
from .drilldowns import DashboardDrilldown, DrilldownTrigger, DrilldownTypes, UrlDrilldown
from .images import ImagePanel
from .links import LinksPanel
from .markdown import MarkdownPanel
from .search import SearchPanel
from .vega import VegaPanel

__all__ = [
    'CollapsiblePanel',
    'DashboardDrilldown',
    'DrilldownTrigger',
    'DrilldownTypes',
    'ImagePanel',
    'LinksPanel',
    'MarkdownPanel',
    'SearchPanel',
    'UrlDrilldown',
    'VegaPanel',
]
