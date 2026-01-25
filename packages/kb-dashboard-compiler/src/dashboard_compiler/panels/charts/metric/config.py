from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base.config import BaseChart, ColorMapping
from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.dimensions.config import LensDimensionTypes
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes


class LensMetricChart(BaseChart):
    """Lens metric chart configuration.

    Examples:
        ```yaml
        lens:
          type: metric
          data_view: "logs-*"
          primary:
            aggregation: count
            label: "Total Requests"
        ```

        ```yaml
        lens:
          type: metric
          data_view: "logs-*"
          primary:
            formula: "count(kql='status:error') / count() * 100"
            label: "Error Rate %"
            format:
              type: percent
        ```
    """

    type: Literal['metric'] = Field(default='metric')

    data_view: str = Field(default=...)
    """Data view for the chart."""

    primary: LensMetricTypes = Field(default=...)
    """Primary metric (main displayed value)."""

    secondary: LensMetricTypes | None = Field(default=None)
    """Secondary metric displayed alongside primary."""

    maximum: LensMetricTypes | None = Field(default=None)
    """Maximum value for gauge-style display."""

    breakdown: LensDimensionTypes | None = Field(default=None)
    """Dimension to split the metric by."""

    color: ColorMapping | None = Field(default=None)
    """Color palette configuration."""


class ESQLMetricChart(BaseChart):
    """ES|QL metric chart configuration.

    Metrics reference columns from your query's STATS clause.

    Examples:
        ```yaml
        esql:
          type: metric
          query: |
            FROM logs-*
            | STATS
                total_requests = COUNT(*),
                avg_duration = AVG(event.duration)
          primary:
            field: "total_requests"
          secondary:
            field: "avg_duration"
        ```
    """

    type: Literal['metric'] = Field(default='metric')

    primary: ESQLMetricTypes = Field(default=...)
    """Primary metric (main displayed value)."""

    secondary: ESQLMetricTypes | None = Field(default=None)
    """Secondary metric displayed alongside primary."""

    maximum: ESQLMetricTypes | None = Field(default=None)
    """Maximum value for gauge-style display."""

    breakdown: ESQLDimensionTypes | None = Field(default=None)
    """Dimension to split the metric by."""

    color: ColorMapping | None = Field(default=None)
    """Color palette configuration."""
