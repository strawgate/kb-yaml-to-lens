from enum import StrEnum
from typing import Literal

from pydantic import Field

from kb_dashboard_core.panels.charts.base.config import BaseChart, BaseLegend, ColorValueMapping
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from kb_dashboard_core.panels.charts.lens.breakdowns.config import LensBreakdownTypes
from kb_dashboard_core.panels.charts.lens.metrics.config import LensDataMetricTypes
from kb_dashboard_core.shared.config import BaseCfgModel


class PieLegend(BaseLegend):
    """Represents legend formatting options for pie charts."""

    truncate_labels: int | None = Field(default=None, ge=0, le=5)
    """Number of lines to truncate the legend labels to. Kibana defaults to 1 if not specified. Set to 0 to disable truncation."""

    nested: bool | None = Field(default=None)
    """Whether to show legend in nested format for multi-level pie charts. Kibana defaults to False if not specified."""

    show_single_series: bool | None = Field(default=None)
    """Whether to show legend when there is only one series. Kibana defaults to false if not specified."""


class PieSliceValuesEnum(StrEnum):
    """Represents the possible values for slice values in a pie chart."""

    HIDE = 'hide'
    """Hide the slice values."""

    INTEGER = 'integer'
    """Show the slice values as integers."""

    PERCENT = 'percent'
    """Show the slice values as percentages."""


class PieSliceLabelsEnum(StrEnum):
    """Represents the possible values for slice labels in a pie chart."""

    HIDE = 'hide'
    """Hide the slice labels."""

    INSIDE = 'inside'
    """Show the slice labels on the inside of the pie chart."""

    AUTO = 'auto'
    """Automatically determine the slice labels based on the data."""


class PieCategoriesConfig(BaseCfgModel):
    """Formatting options for category labels."""

    position: PieSliceLabelsEnum | None = Field(default=None, strict=False)
    """Controls the visibility of category labels in the pie chart. Kibana defaults to 'auto' if not specified."""


class PieValuesConfig(BaseCfgModel):
    """Formatting options for numeric values."""

    format: PieSliceValuesEnum | None = Field(default=None, strict=False)
    """Controls the display of values in the pie chart. Kibana defaults to percent if not specified."""

    decimal_places: int | None = Field(default=None, ge=0, le=10)
    """Controls the number of decimal places for values in the pie chart. Kibana defaults to 2 if not specified."""


class PieChartAppearance(BaseCfgModel):
    """Represents chart appearance formatting options for Pie charts."""

    donut: Literal['small', 'medium', 'large'] | None = Field(default=None)
    """Controls the size of the donut hole in the pie chart. Kibana defaults to 'medium' if not specified."""

    categories: PieCategoriesConfig | None = Field(default=None)
    """Formatting options for category labels."""

    values: PieValuesConfig | None = Field(default=None)
    """Formatting options for numeric values."""


class BasePieChart(BaseChart):
    """Base model for defining Pie chart objects."""

    type: Literal['pie'] = Field(default='pie')

    appearance: PieChartAppearance | None = Field(default=None)
    """Formatting options for the chart appearance, including donut size."""

    legend: PieLegend | None = Field(default=None)
    """Formatting options for the chart legend."""

    color: ColorValueMapping | None = Field(default=None)
    """Formatting options for the chart color."""


class LensPieChart(BasePieChart):
    """Represents a Pie chart configuration within a Lens panel.

    Pie charts are used to visualize the proportion of categories.

    Examples:
        Simple pie chart showing traffic sources:
        ```yaml
        lens:
          type: pie
          data_view: "logs-*"
          breakdowns:
            - field: "source.geo.country_name"
              type: values
          metrics:
            - aggregation: count
        ```

        Pie chart with custom colors:
        ```yaml
        lens:
          type: pie
          data_view: "metrics-*"
          breakdowns:
            - field: "resource.attributes.os.type"
              type: values
          metrics:
            - aggregation: unique_count
              field: resource.attributes.host.name
          color:
            palette: 'eui_amsterdam_color_blind'
            assignments:
              - values: ['linux']
                color: '#00BF6F'
              - values: ['windows']
                color: '#006BB4'
        ```
    """

    data_view: str = Field(default=...)
    """The data view that determines the data for the pie chart."""

    metrics: list[LensDataMetricTypes] = Field(default=..., min_length=1)
    """Metrics that determine the size of slices."""

    breakdowns: list[LensBreakdownTypes] = Field(default=...)
    """The breakdowns that determine the slices of the pie chart. First breakdown is primary, additional breakdowns are secondary."""


class ESQLPieChart(BasePieChart):
    """Represents a Pie chart configuration within an ES|QL panel.

    Examples:
        ES|QL pie chart with STATS query:
        ```yaml
        esql:
          type: pie
          query: |
            FROM logs-*
            | STATS count = COUNT(*) BY service.name
          metrics:
            - field: "count"
          breakdowns:
            - field: "service.name"
        ```
    """

    metrics: list[ESQLMetricTypes] = Field(default=..., min_length=1)
    """Metrics that determine the size of slices."""

    breakdowns: list[ESQLDimensionTypes] = Field(default=...)
    """The breakdowns that determine the slices of the pie chart. First breakdown is primary, additional breakdowns are secondary."""
