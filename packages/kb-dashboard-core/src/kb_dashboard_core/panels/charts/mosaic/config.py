"""Mosaic chart configuration models for YAML schema definition.

Mosaic charts display multi-dimensional categorical data as proportional rectangles,
similar to treemaps but with a different visual arrangement. They are part of the
Kibana Lens partition chart family (pie, donut, treemap, waffle, mosaic).
"""

from typing import Any, Literal, cast

from pydantic import Field, model_validator

from kb_dashboard_core.panels.charts.base.config import BaseChart, BaseLegend, ColorValueMapping
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from kb_dashboard_core.panels.charts.lens.breakdowns.config import LensBreakdownTypes
from kb_dashboard_core.panels.charts.lens.dimensions.config import LensDimensionTypes
from kb_dashboard_core.panels.charts.lens.metrics.config import LensMetricTypes
from kb_dashboard_core.shared.config import BaseCfgModel


class MosaicLegend(BaseLegend):
    """Represents legend formatting options for mosaic charts."""

    truncate_labels: int | None = Field(default=None, ge=0, le=5)
    """Number of lines to truncate the legend labels to. Kibana defaults to 1 if not specified. Set to 0 to disable truncation."""

    nested: bool | None = Field(default=None)
    """Whether to show legend in nested format for multi-level mosaic charts. Kibana defaults to False if not specified."""

    show_single_series: bool | None = Field(default=None)
    """Whether to show legend when there is only one series. Kibana defaults to false if not specified."""


class MosaicValuesConfig(BaseCfgModel):
    """Formatting options for value labels."""

    format: Literal['percent', 'value', 'hide'] | None = Field(default=None)
    """Controls how values are displayed in the mosaic chart. Kibana defaults to 'percent' if not specified."""

    decimal_places: int | None = Field(default=None, ge=0, le=10)
    """Controls the number of decimal places for values in the mosaic chart. Kibana defaults to 2 if not specified."""


class MosaicAppearance(BaseCfgModel):
    """Formatting options for value labels."""

    values: MosaicValuesConfig | None = Field(default=None)
    """Formatting options for numeric values."""


class BaseMosaicChart(BaseChart):
    """Base model for defining Mosaic chart objects.

    Mosaic charts visualize multi-dimensional categorical data as nested rectangles,
    where the area of each rectangle is proportional to its value. They are ideal
    for showing hierarchical relationships and comparing proportions across categories.
    """

    type: Literal['mosaic'] = Field(default='mosaic')

    appearance: MosaicAppearance | None = Field(default=None)
    """Formatting options for the chart appearance."""

    legend: MosaicLegend | None = Field(default=None)
    """Formatting options for the chart legend."""

    color: ColorValueMapping | None = Field(default=None)
    """Formatting options for the chart color."""

    @model_validator(mode='before')
    @classmethod
    def _translate_legacy_value_fields(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data

        normalized_data: dict[str, Any] = dict(cast('dict[str, Any]', data))
        legacy_titles_and_text = normalized_data.pop('titles_and_text', None)
        if not isinstance(legacy_titles_and_text, dict):
            return normalized_data

        legacy_values: dict[str, Any] = {}
        if 'value_format' in legacy_titles_and_text:
            legacy_values['format'] = legacy_titles_and_text['value_format']
        if 'value_decimal_places' in legacy_titles_and_text:
            legacy_values['decimal_places'] = legacy_titles_and_text['value_decimal_places']
        if not legacy_values:
            return normalized_data

        appearance = normalized_data.get('appearance')
        if appearance is None:
            normalized_data['appearance'] = {'values': legacy_values}
            return normalized_data
        if not isinstance(appearance, dict):
            return normalized_data

        normalized_appearance = dict(cast('dict[str, Any]', appearance))
        appearance_values = normalized_appearance.get('values')
        if appearance_values is None:
            normalized_appearance['values'] = legacy_values
        elif isinstance(appearance_values, dict):
            normalized_appearance['values'] = {**legacy_values, **cast('dict[str, Any]', appearance_values)}
        normalized_data['appearance'] = normalized_appearance
        return normalized_data


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
        ```
    """

    data_view: str = Field(default=...)
    """The data view that determines the data for the mosaic chart."""

    metric: LensMetricTypes = Field(default=...)
    """Metric that determines the size of rectangles. Mosaic charts support only one metric."""

    dimension: LensDimensionTypes = Field(default=...)
    """Primary dimension for grouping data. Mosaic charts support only one dimension."""

    breakdown: LensBreakdownTypes | None = Field(default=None)
    """Optional secondary breakdown for splitting the mosaic into sub-groups."""


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
