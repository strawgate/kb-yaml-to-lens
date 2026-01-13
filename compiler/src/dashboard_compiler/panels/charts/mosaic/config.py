"""Mosaic chart configuration models for YAML schema definition.

Mosaic charts display multi-dimensional categorical data as proportional rectangles,
similar to treemaps but with a different visual arrangement. They are part of the
Kibana Lens partition chart family (pie, donut, treemap, waffle, mosaic).
"""

from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base.config import BaseChart, ColorMapping, LegendVisibleEnum, LegendWidthEnum
from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.dimensions.config import LensDimensionTypes
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes
from dashboard_compiler.shared.config import BaseCfgModel


class MosaicLegend(BaseCfgModel):
    """Represents legend formatting options for mosaic charts."""

    visible: LegendVisibleEnum | None = Field(default=None, strict=False)
    """Visibility of the legend in the mosaic chart. Kibana defaults to 'auto' if not specified."""

    position: Literal['top', 'right', 'bottom', 'left'] | None = Field(default=None)
    """Position of the legend. Kibana defaults to 'right' if not specified."""

    width: LegendWidthEnum | None = Field(default=None, strict=False)
    """Width of the legend in the mosaic chart. Kibana defaults to 'medium' if not specified."""

    truncate_labels: int | None = Field(default=None, ge=0, le=5)
    """Number of lines to truncate the legend labels to. Kibana defaults to 1 if not specified. Set to 0 to disable truncation."""

    nested: bool | None = Field(default=None)
    """Whether to show legend in nested format for multi-level mosaic charts. Kibana defaults to False if not specified."""

    show_single_series: bool | None = Field(default=None)
    """Whether to show legend when there is only one series. Kibana defaults to false if not specified."""


class MosaicTitlesAndText(BaseCfgModel):
    """Represents titles and text formatting options for mosaic charts."""

    value_format: Literal['percent', 'value', 'hidden'] | None = Field(default=None)
    """Controls how values are displayed in the mosaic chart. Kibana defaults to 'percent' if not specified."""

    value_decimal_places: int | None = Field(default=None, ge=0, le=10)
    """Controls the number of decimal places for values in the mosaic chart. Kibana defaults to 2 if not specified."""


class BaseMosaicChart(BaseChart):
    """Base model for defining Mosaic chart objects.

    Mosaic charts visualize multi-dimensional categorical data as nested rectangles,
    where the area of each rectangle is proportional to its value. They are ideal
    for showing hierarchical relationships and comparing proportions across categories.
    """

    type: Literal['mosaic'] = Field(default='mosaic')

    titles_and_text: MosaicTitlesAndText | None = Field(default=None)
    """Formatting options for the chart titles and text."""

    legend: MosaicLegend | None = Field(default=None)
    """Formatting options for the chart legend."""

    color: ColorMapping | None = Field(default=None)
    """Formatting options for the chart color."""


class LensMosaicChart(BaseMosaicChart):
    """Represents a Mosaic chart configuration within a Lens panel.

    Mosaic charts visualize categorical data as proportional rectangles,
    where each rectangle's area represents its proportion of the whole.
    Mosaic charts support exactly one metric, one dimension, and an optional breakdown.

    Examples:
        Simple mosaic chart showing request distribution:
        ```yaml
        lens:
          type: mosaic
          data_view: "logs-*"
          dimension:
            field: "http.request.method"
            type: values
          metric:
            aggregation: count
        ```

        Mosaic chart with breakdown:
        ```yaml
        lens:
          type: mosaic
          data_view: "logs-*"
          dimension:
            field: "http.request.method"
            type: values
          breakdown:
            field: "service.name"
            type: values
          metric:
            aggregation: count
        ```

        Mosaic chart with custom colors:
        ```yaml
        lens:
          type: mosaic
          data_view: "metrics-*"
          dimension:
            field: "service.name"
            type: values
          metric:
            aggregation: count
          color:
            palette: 'eui_amsterdam_color_blind'
            assignments:
              - values: ['api-gateway']
                color: '#00BF6F'
              - values: ['database']
                color: '#006BB4'
        ```

        Mosaic chart with legend options:
        ```yaml
        lens:
          type: mosaic
          data_view: "logs-*"
          dimension:
            field: "http.request.method"
            type: values
          metric:
            aggregation: count
          legend:
            visible: show
            position: bottom
            width: medium
        ```
    """

    data_view: str = Field(default=...)
    """The data view that determines the data for the mosaic chart."""

    metric: LensMetricTypes = Field(default=...)
    """Metric that determines the size of rectangles. Mosaic charts support only one metric."""

    dimension: LensDimensionTypes = Field(default=...)
    """Primary dimension for grouping data. Mosaic charts support only one dimension."""

    breakdown: LensDimensionTypes | None = Field(default=None)
    """Optional secondary dimension for breaking down the mosaic into sub-groups."""


class ESQLMosaicChart(BaseMosaicChart):
    """Represents a Mosaic chart configuration within an ES|QL panel.

    Mosaic charts visualize categorical data as proportional rectangles,
    using ES|QL queries to aggregate and group the data.
    Mosaic charts support exactly one metric, one dimension, and an optional breakdown.

    Examples:
        ES|QL mosaic chart with STATS query:
        ```yaml
        esql:
          type: mosaic
          query: |
            FROM logs-*
            | STATS count = COUNT(*) BY http.request.method
          metric:
            field: "count"
          dimension:
            field: "http.request.method"
        ```

        ES|QL mosaic chart with breakdown:
        ```yaml
        esql:
          type: mosaic
          query: |
            FROM logs-*
            | STATS count = COUNT(*) BY http.request.method, service.name
          metric:
            field: "count"
          dimension:
            field: "http.request.method"
          breakdown:
            field: "service.name"
        ```
    """

    metric: ESQLMetricTypes = Field(default=...)
    """Metric that determines the size of rectangles. Mosaic charts support only one metric."""

    dimension: ESQLDimensionTypes = Field(default=...)
    """Primary dimension for grouping data. Mosaic charts support only one dimension."""

    breakdown: ESQLDimensionTypes | None = Field(default=None)
    """Optional secondary dimension for breaking down the mosaic into sub-groups."""
