from typing import Literal, Self

from pydantic import Field, model_validator

from dashboard_compiler.panels.charts.base.config import BaseChart, ColorMapping
from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.dimensions.config import LensDimensionTypes
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes


class LensMetricChart(BaseChart):
    """Represents a Metric chart configuration within a Lens panel.

    Metric charts display a single value or a list of values, often representing
    key performance indicators.

    Examples:
        Minimal count metric:
        ```yaml
        lens:
          type: metric
          data_view: "logs-*"
          primary:
            aggregation: count
            label: "Total Requests"
        ```

        Formula-based error rate metric:
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

        Multi-field breakdown metric:
        ```yaml
        lens:
          type: metric
          data_view: "logs-*"
          primary:
            aggregation: count
          breakdown_by:
            - field: "service.name"
              type: values
            - field: "host.name"
              type: values
        ```
    """

    type: Literal['metric'] = Field(default='metric')
    """The type of chart, which is 'metric' for this visualization."""

    data_view: str = Field(default=...)
    """The data view that determines the data for the metric chart."""

    primary: LensMetricTypes = Field(default=...)
    """The primary metric to display in the chart. This is the main value shown in the metric visualization."""

    secondary: LensMetricTypes | None = Field(default=None)
    """An optional secondary metric to display alongside the primary metric."""

    maximum: LensMetricTypes | None = Field(default=None)
    """An optional maximum metric to display, often used for comparison or thresholds."""

    breakdown: LensDimensionTypes | None = Field(default=None)
    """An optional single breakdown dimension (deprecated: use breakdown_by for multi-field breakdowns)."""

    breakdown_by: list[LensDimensionTypes] | None = Field(default=None, min_length=1, max_length=4)
    """An optional list of breakdown dimensions (1-4 fields) for multi-field breakdowns."""

    color: ColorMapping | None = Field(default=None)
    """Formatting options for the chart color palette."""

    @model_validator(mode='after')
    def validate_breakdown_exclusivity(self) -> Self:
        """Validate that breakdown and breakdown_by are mutually exclusive.

        Raises:
            ValueError: If both breakdown and breakdown_by are specified.

        """
        if self.breakdown is not None and self.breakdown_by is not None:
            msg = "Cannot specify both 'breakdown' and 'breakdown_by'. Use 'breakdown_by' for multi-field breakdowns."
            raise ValueError(msg)
        return self


class ESQLMetricChart(BaseChart):
    """Represents a Metric chart configuration within an ESQL panel.

    ESQL metric charts reference columns from your ESQL query result.
    The query determines what metrics are available - each column in your
    STATS clause becomes a metric you can reference.

    Examples:
        Multi-metric ESQL example:
        ```yaml
        esql:
          type: metric
          query: |
            FROM logs-*
            | STATS
                total_requests = COUNT(*),
                avg_duration = AVG(event.duration),
                error_rate = COUNT(kql='event.outcome:failure') / COUNT(*) * 100
          primary:
            field: "total_requests"
          secondary:
            field: "avg_duration"
          maximum:
            field: "error_rate"
        ```

        Multi-field breakdown ESQL example:
        ```yaml
        esql:
          type: metric
          query: |
            FROM logs-*
            | STATS total = COUNT(*) BY service.name, host.name
          primary:
            field: "total"
          breakdown_by:
            - field: "service.name"
            - field: "host.name"
        ```
    """

    type: Literal['metric'] = Field(default='metric')
    """The type of chart, which is 'metric' for this visualization."""

    primary: ESQLMetricTypes = Field(default=...)
    """The primary metric to display in the chart. This is the main value shown in the metric visualization."""

    secondary: ESQLMetricTypes | None = Field(default=None)
    """An optional secondary metric to display alongside the primary metric."""

    maximum: ESQLMetricTypes | None = Field(default=None)
    """An optional maximum metric to display, often used for comparison or thresholds."""

    breakdown: ESQLDimensionTypes | None = Field(default=None)
    """An optional single breakdown dimension (deprecated: use breakdown_by for multi-field breakdowns)."""

    breakdown_by: list[ESQLDimensionTypes] | None = Field(default=None, min_length=1, max_length=4)
    """An optional list of breakdown dimensions (1-4 fields) for multi-field breakdowns."""

    color: ColorMapping | None = Field(default=None)
    """Formatting options for the chart color palette."""

    @model_validator(mode='after')
    def validate_breakdown_exclusivity(self) -> Self:
        """Validate that breakdown and breakdown_by are mutually exclusive.

        Raises:
            ValueError: If both breakdown and breakdown_by are specified.

        """
        if self.breakdown is not None and self.breakdown_by is not None:
            msg = "Cannot specify both 'breakdown' and 'breakdown_by'. Use 'breakdown_by' for multi-field breakdowns."
            raise ValueError(msg)
        return self
