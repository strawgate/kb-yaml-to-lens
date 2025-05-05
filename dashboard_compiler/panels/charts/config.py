
from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.charts.visualizations.config import ESQLChartTypes, LensChartTypes
from dashboard_compiler.panels.config import BasePanel


class LensPanel(BasePanel):
    """Represents a Lens panel configuration.

    Lens panels are used to display rich text content using Markdown syntax.
    """

    type: Literal['lens'] = 'lens'

    chart: LensChartTypes = Field(...)


class ESQLPanel(BasePanel):
    """Represents an ESQL panel configuration.

    ESQL panels are used to display rich text content using Markdown syntax.
    """

    type: Literal['esql'] = 'esql'

    query: str = Field(...)

    chart: ESQLChartTypes = Field(...)
