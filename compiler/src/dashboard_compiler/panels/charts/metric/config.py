from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base.config import BaseChart, ColorMapping
from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.dimensions.config import LensDimensionTypes
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes


class LensMetricChart(BaseChart):
    """Represents a Metric chart configuration within a Lens panel.

    Metric charts display a single value or a list of values, often representing
    key performance indicators.
    """

    type: Literal['metric'] = Field(default='metric')
    """The type of chart, which is 'metric' for this visualization."""

    data_view: str = Field(default=...)
    """The data view that determines the data for the metric chart."""

    primary: LensMetricTypes = Field(...)
    """The primary metric to display in the chart. This is the main value shown in the metric visualization."""

    secondary: LensMetricTypes | None = Field(default=None)
    """An optional secondary metric to display alongside the primary metric."""

    maximum: LensMetricTypes | None = Field(default=None)
    """An optional maximum metric to display, often used for comparison or thresholds."""

    breakdown: LensDimensionTypes | None = Field(default=None)
    """An optional breakdown metric to display, often used for comparison or thresholds."""

    color: ColorMapping | None = Field(default=None)
    """Formatting options for the chart color palette."""


class ESQLMetricChart(BaseChart):
    """Represents a Metric chart configuration within an ESQL panel."""

    type: Literal['metric'] = Field(default='metric')
    """The type of chart, which is 'metric' for this visualization."""

    primary: ESQLMetricTypes = Field(...)
    """The primary metric to display in the chart. This is the main value shown in the metric visualization."""

    secondary: ESQLMetricTypes | None = Field(default=None)
    """An optional secondary metric to display alongside the primary metric."""

    maximum: ESQLMetricTypes | None = Field(default=None)
    """An optional maximum metric to display, often used for comparison or thresholds."""

    breakdown: ESQLDimensionTypes | None = Field(default=None)
    """An optional breakdown metric to display, often used for comparison or thresholds."""

    color: ColorMapping | None = Field(default=None)
    """Formatting options for the chart color palette."""
