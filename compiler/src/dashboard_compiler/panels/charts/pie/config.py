from enum import StrEnum
from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base.config import BaseChart, ColorMapping, LegendVisibleEnum, LegendWidthEnum
from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.dimensions.config import LensDimensionTypes
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes
from dashboard_compiler.shared.config import BaseCfgModel


class PieLegend(BaseCfgModel):
    """Represents legend formatting options for pie charts."""

    visible: LegendVisibleEnum | None = Field(default=None, strict=False)  # Turn off strict for enums
    """Visibility of the legend in the pie chart. Kibana defaults to 'auto' if not specified."""

    width: LegendWidthEnum | None = Field(default=None, strict=False)  # Turn off strict for enums
    """Width of the legend in the pie chart. Kibana defaults to 'medium' if not specified."""

    truncate_labels: int | None = Field(default=None, ge=0, le=5)
    """Number of lines to truncate the legend labels to. Kibana defaults to 1 if not specified. Set to 0 to disable truncation."""

    nested: bool | None = Field(default=None)
    """Whether to show legend in nested format for multi-level pie charts. Kibana defaults to False if not specified."""


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


class PieTitlesAndText(BaseCfgModel):
    """Represents titles and text formatting options for pie charts."""

    slice_labels: PieSliceLabelsEnum | None = Field(default=None, strict=False)  # Turn off strict for enums
    """Controls the visibility of slice labels in the pie chart. Kibana defaults to 'auto' if not specified."""

    slice_values: PieSliceValuesEnum | None = Field(default=None, strict=False)  # Turn off strict for enums
    """Controls the display of slice values in the pie chart. Kibana defaults to PERCENT if not specified."""

    value_decimal_places: int | None = Field(default=None, ge=0, le=10)
    """Controls the number of decimal places for slice values in the pie chart. Kibana defaults to 2, if not specified."""


class PieChartAppearance(BaseCfgModel):
    """Represents chart appearance formatting options for Pie charts."""

    donut: Literal['small', 'medium', 'large'] | None = Field(default=None)
    """Controls the size of the donut hole in the pie chart. Kibana defaults to 'medium' if not specified."""


class BasePieChart(BaseChart):
    """Base model for defining Pie chart objects."""

    type: Literal['pie'] = Field(default='pie')

    appearance: PieChartAppearance | None = Field(default=None)
    """Formatting options for the chart appearance, including donut size."""

    titles_and_text: PieTitlesAndText | None = Field(default=None)
    """Formatting options for the chart titles and text."""

    legend: PieLegend | None = Field(default=None)
    """Formatting options for the chart legend."""

    color: ColorMapping | None = Field(default=None)
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
          slice_by:
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
          slice_by:
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

    metrics: list[LensMetricTypes] = Field(default=..., min_length=1)
    """Metrics that determine the size of slices."""

    slice_by: list[LensDimensionTypes] = Field(default=...)
    """The dimensions that determine the slices of the pie chart. First dimension is primary, additional dimensions are secondary."""


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
          slice_by:
            - field: "service.name"
        ```
    """

    metrics: list[ESQLMetricTypes] = Field(default=..., min_length=1)
    """Metrics that determine the size of slices."""

    slice_by: list[ESQLDimensionTypes] = Field(default=...)
    """The dimensions that determine the slices of the pie chart. First dimension is primary, additional dimensions are secondary."""
