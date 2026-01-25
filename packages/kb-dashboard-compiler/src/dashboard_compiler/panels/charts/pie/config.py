from enum import StrEnum
from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base.config import BaseChart, ColorMapping, LegendVisibleEnum, LegendWidthEnum
from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.dimensions.config import LensDimensionTypes
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes
from dashboard_compiler.shared.config import BaseCfgModel


class PieLegend(BaseCfgModel):
    """Legend options for pie charts."""

    visible: LegendVisibleEnum | None = Field(default=None, strict=False)  # Turn off strict for enums
    """Legend visibility. Kibana defaults to 'auto'."""

    width: LegendWidthEnum | None = Field(default=None, strict=False)  # Turn off strict for enums
    """Legend width. Kibana defaults to 'medium'."""

    truncate_labels: int | None = Field(default=None, ge=0, le=5)
    """Lines before label truncation (0 disables). Kibana defaults to 1."""

    nested: bool | None = Field(default=None)
    """Nested format for multi-level pies. Kibana defaults to false."""

    show_single_series: bool | None = Field(default=None)
    """Show legend with single series. Kibana defaults to false."""


class PieSliceValuesEnum(StrEnum):
    """Slice value display options."""

    HIDE = 'hide'
    INTEGER = 'integer'
    PERCENT = 'percent'


class PieSliceLabelsEnum(StrEnum):
    """Slice label display options."""

    HIDE = 'hide'
    INSIDE = 'inside'
    AUTO = 'auto'


class PieTitlesAndText(BaseCfgModel):
    """Text formatting options for pie charts."""

    slice_labels: PieSliceLabelsEnum | None = Field(default=None, strict=False)  # Turn off strict for enums
    """Slice label visibility. Kibana defaults to 'auto'."""

    slice_values: PieSliceValuesEnum | None = Field(default=None, strict=False)  # Turn off strict for enums
    """Slice value display. Kibana defaults to 'percent'."""

    value_decimal_places: int | None = Field(default=None, ge=0, le=10)
    """Decimal places for slice values. Kibana defaults to 2."""


class PieChartAppearance(BaseCfgModel):
    """Appearance options for pie charts."""

    donut: Literal['small', 'medium', 'large'] | None = Field(default=None)
    """Donut hole size. Kibana defaults to no hole (pie, not donut)."""


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
    """Lens pie chart configuration.

    Examples:
        Simple pie chart showing traffic sources:
        ```yaml
        lens:
          type: pie
          data_view: "logs-*"
          dimensions:
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
          dimensions:
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
    """Data view for the chart."""

    metrics: list[LensMetricTypes] = Field(default=..., min_length=1)
    """Metrics determining slice size."""

    dimensions: list[LensDimensionTypes] = Field(default=...)
    """Dimensions determining slices. First is primary, additional are nested."""


class ESQLPieChart(BasePieChart):
    """ES|QL pie chart configuration.

    Examples:
        ```yaml
        esql:
          type: pie
          query: |
            FROM logs-*
            | STATS count = COUNT(*) BY service.name
          metrics:
            - field: "count"
          dimensions:
            - field: "service.name"
        ```
    """

    metrics: list[ESQLMetricTypes] = Field(default=..., min_length=1)
    """Metrics determining slice size."""

    dimensions: list[ESQLDimensionTypes] = Field(default=...)
    """Dimensions determining slices. First is primary, additional are nested."""
