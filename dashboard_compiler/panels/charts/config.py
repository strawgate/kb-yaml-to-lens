from typing import TYPE_CHECKING, Literal

from pydantic import Field

from dashboard_compiler.panels.charts.metric import ESQLMetricChart, LensMetricChart
from dashboard_compiler.panels.charts.pie import ESQLPieChart, LensPieChart
from dashboard_compiler.panels.config import BasePanel

if TYPE_CHECKING:
    from dashboard_compiler.filters.config import AllFilterTypes
    from dashboard_compiler.queries.config import KqlQuery, LuceneQuery

type AllChartTypes = LensChartTypes | ESQLChartTypes

type LensChartTypes = MultiLayerChartTypes | SingleLayerChartTypes

type MultiLayerChartTypes = LensPieChart

type SingleLayerChartTypes = LensMetricChart

type ESQLChartTypes = ESQLMetricChart | ESQLPieChart


class LensPanel(BasePanel):
    """Represents a Lens chart panel configuration."""

    type: Literal['charts'] = 'charts'

    filters: list['AllFilterTypes'] | None = Field(default=None)
    """A list of filters to apply to the panel."""

    query: 'KqlQuery | LuceneQuery | None' = Field(default=None)
    """The query to be executed. This is the core of the chart definition."""

    chart: 'LensChartTypes' = Field(default=...)


class LensMultiLayerPanel(BasePanel):
    """Represents a multi-layer Lens chart panel configuration."""

    type: Literal['charts'] = 'charts'

    layers: list['MultiLayerChartTypes'] = Field(default=...)


class ESQLPanel(BasePanel):
    """Represents an ESQL chart panel configuration."""

    type: Literal['charts'] = 'charts'

    esql: str = Field(...)

    chart: 'ESQLChartTypes' = Field(default=...)
