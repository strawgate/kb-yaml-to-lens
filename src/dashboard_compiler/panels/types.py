from typing import Annotated

from pydantic import Field

from dashboard_compiler.panels.charts.config import LensPanel
from dashboard_compiler.panels.images import ImagePanel
from dashboard_compiler.panels.links import LinksPanel
from dashboard_compiler.panels.markdown import MarkdownPanel
from dashboard_compiler.panels.search import SearchPanel

__all__ = ['PanelTypes']


type PanelTypes = Annotated[
    MarkdownPanel | SearchPanel | LinksPanel | ImagePanel | LensPanel,
    Field(discriminator='type'),
]
