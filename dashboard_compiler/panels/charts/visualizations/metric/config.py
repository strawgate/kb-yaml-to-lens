from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.charts.dimensions.config import ESQLDimensionTypes, LensDimensionTypes
from dashboard_compiler.panels.charts.metrics.config import ESQLMetricTypes, LensMetricTypes
from dashboard_compiler.shared.charts.config import ESQLChartMixin, LensChartMixin
from dashboard_compiler.shared.config import BaseCfgModel


class BaseMetricChart(BaseCfgModel):
    """Base model for defining a Metric chart object within a Lens panel."""

    type: Literal['metric'] = Field(default='metric')
    """The type of chart, which is 'metric' for this visualization."""


class LensMetricChart(BaseMetricChart, LensChartMixin):
    """Represents a Metric chart configuration within a Lens panel.

    Metric charts display a single value or a list of values, often representing
    key performance indicators.
    """

    primary: LensMetricTypes = Field(...)
    """The primary metric to display in the chart. This is the main value shown in the metric visualization."""

    secondary: LensMetricTypes | None = Field(default=None)
    """An optional secondary metric to display alongside the primary metric."""

    maximum: LensMetricTypes | None = Field(default=None)
    """An optional maximum metric to display, often used for comparison or thresholds."""

    breakdown: LensDimensionTypes | None = Field(default=None)
    """An optional breakdown metric to display, often used for comparison or thresholds."""


class ESQLMetricChart(BaseMetricChart, ESQLChartMixin):
    """Represents a Metric chart configuration within an ESQL panel."""

    primary: ESQLMetricTypes = Field(...)
    """The primary metric to display in the chart. This is the main value shown in the metric visualization."""

    secondary: ESQLMetricTypes | None = Field(default=None)
    """An optional secondary metric to display alongside the primary metric."""

    maximum: ESQLMetricTypes | None = Field(default=None)
    """An optional maximum metric to display, often used for comparison or thresholds."""

    breakdown: ESQLDimensionTypes | None = Field(default=None)
    """An optional breakdown metric to display, often used for comparison or thresholds."""
