"""Waffle chart configuration models for YAML schema definition.

Waffle charts display categorical data as a grid of colored squares, where each
square represents a proportion of the whole. They are part of the Kibana Lens
partition chart family (pie, donut, treemap, waffle, mosaic).
"""

import warnings
from typing import Any, Literal, cast

from pydantic import Field, model_validator

from kb_dashboard_core.panels.charts.base.config import BaseChart, BaseLegend, ColorValueMapping
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from kb_dashboard_core.panels.charts.lens.breakdowns.config import LensBreakdownTypes
from kb_dashboard_core.panels.charts.lens.metrics.config import LensMetricTypes
from kb_dashboard_core.shared.config import BaseCfgModel


class WaffleLegend(BaseLegend):
    """Represents legend formatting options for waffle charts."""

    truncate_labels: int | None = Field(default=None, ge=0, le=5)
    """Number of lines to truncate the legend labels to. Kibana defaults to 1 if not specified. Set to 0 to disable truncation."""

    nested: bool | None = Field(default=None)
    """Whether to show legend in nested format for multi-level waffle charts. Kibana defaults to False if not specified."""

    show_single_series: bool | None = Field(default=None)
    """Whether to show legend when there is only one series. Kibana defaults to false if not specified."""


class WaffleValuesConfig(BaseCfgModel):
    """Formatting options for value labels."""

    format: Literal['percent', 'value', 'hide'] | None = Field(default=None)
    """Controls how values are displayed in the waffle chart. Kibana defaults to 'percent' if not specified."""

    decimal_places: int | None = Field(default=None, ge=0, le=10)
    """Controls the number of decimal places for values in the waffle chart. Kibana defaults to 2 if not specified."""


class WaffleAppearance(BaseCfgModel):
    """Formatting options for value labels."""

    values: WaffleValuesConfig | None = Field(default=None)
    """Formatting options for numeric values."""


class BaseWaffleChart(BaseChart):
    """Base model for defining Waffle chart objects.

    Waffle charts visualize categorical data as a grid of colored squares,
    where each square represents a unit or proportion of the whole. They are ideal
    for showing part-to-whole relationships with discrete visual elements.
    """

    type: Literal['waffle'] = Field(default='waffle')

    appearance: WaffleAppearance | None = Field(default=None)
    """Formatting options for the chart appearance."""

    legend: WaffleLegend | None = Field(default=None)
    """Formatting options for the chart legend."""

    color: ColorValueMapping | None = Field(default=None)
    """Formatting options for the chart color."""

    @model_validator(mode='before')
    @classmethod
    def _translate_deprecated_titles_and_text(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data

        def as_dict(value: object) -> dict[str, Any]:
            return dict(cast('dict[str, Any]', value)) if isinstance(value, dict) else {}

        normalized_data: dict[str, Any] = dict(cast('dict[str, Any]', data))
        legacy_raw = cast('object', normalized_data.get('titles_and_text'))
        if legacy_raw is None:
            return normalized_data
        if not isinstance(legacy_raw, dict):
            return normalized_data
        legacy_titles_and_text = as_dict(cast('object', legacy_raw))
        normalized_data.pop('titles_and_text')

        appearance = as_dict(cast('object', normalized_data.get('appearance')))
        values = as_dict(cast('object', appearance.get('values')))

        if 'value_format' in legacy_titles_and_text:
            mapped_format = cast('object', legacy_titles_and_text['value_format'])
            if mapped_format == 'hidden':
                mapped_format = 'hide'
            if 'format' not in values:
                values['format'] = mapped_format
            else:
                warnings.warn(
                    "Waffle chart field 'titles_and_text.value_format' is ignored because 'appearance.values.format' is already set.",
                    DeprecationWarning,
                    stacklevel=2,
                )

        if 'value_decimal_places' in legacy_titles_and_text:
            if 'decimal_places' not in values:
                values['decimal_places'] = legacy_titles_and_text['value_decimal_places']
            else:
                warnings.warn(
                    (
                        "Waffle chart field 'titles_and_text.value_decimal_places' is ignored because "
                        "'appearance.values.decimal_places' is already set."
                    ),
                    DeprecationWarning,
                    stacklevel=2,
                )

        if values:
            appearance['values'] = values
            normalized_data['appearance'] = appearance

        warnings.warn(
            "Waffle chart field 'titles_and_text' is deprecated, use 'appearance.values' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return normalized_data


class LensWaffleChart(BaseWaffleChart):
    """Represents a Waffle chart configuration within a Lens panel.

    Waffle charts visualize categorical data as a grid of colored squares,
    where each square represents a proportion of the whole.
    Waffle charts support exactly one metric and an optional breakdown.

    Examples:
        Simple waffle chart showing request distribution:
        ```yaml
        lens:
          type: waffle
          data_view: "logs-*"
          breakdown:
            field: "http.request.method"
            type: values
          metric:
            aggregation: count
        ```

        Waffle chart with custom colors:
        ```yaml
        lens:
          type: waffle
          data_view: "metrics-*"
          breakdown:
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

        Waffle chart with legend options:
        ```yaml
        lens:
          type: waffle
          data_view: "logs-*"
          breakdown:
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
    """The data view that determines the data for the waffle chart."""

    metric: LensMetricTypes = Field(default=...)
    """Metric that determines the size of squares. Waffle charts support only one metric."""

    breakdown: LensBreakdownTypes | None = Field(default=None)
    """Optional breakdown for grouping data. Waffle charts support only one breakdown."""

    @model_validator(mode='before')
    @classmethod
    def _warn_deprecated_fields(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        normalized_data: dict[str, Any] = dict(cast('dict[str, Any]', data))
        if 'dimension' in normalized_data and 'breakdown' not in normalized_data:
            warnings.warn(
                "Waffle chart field 'dimension' is deprecated, use 'breakdown' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            normalized_data['breakdown'] = normalized_data.pop('dimension')
        elif 'dimension' in normalized_data and 'breakdown' in normalized_data:
            warnings.warn(
                "Waffle chart field 'dimension' is ignored because 'breakdown' is already set.",
                DeprecationWarning,
                stacklevel=2,
            )
            normalized_data.pop('dimension')
        return normalized_data


class ESQLWaffleChart(BaseWaffleChart):
    """Represents a Waffle chart configuration within an ES|QL panel.

    Waffle charts visualize categorical data as a grid of colored squares,
    using ES|QL queries to aggregate and group the data.
    Waffle charts support exactly one metric and an optional breakdown.

    Examples:
        ES|QL waffle chart with STATS query:
        ```yaml
        esql:
          type: waffle
          query: |
            FROM logs-*
            | STATS count = COUNT(*) BY http.request.method
          metric:
            field: "count"
          breakdown:
            field: "http.request.method"
        ```

    """

    metric: ESQLMetricTypes = Field(default=...)
    """Metric that determines the size of squares. Waffle charts support only one metric."""

    breakdown: ESQLDimensionTypes | None = Field(default=None)
    """Optional breakdown for grouping data. Waffle charts support only one breakdown."""

    @model_validator(mode='before')
    @classmethod
    def _warn_deprecated_fields(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        normalized_data: dict[str, Any] = dict(cast('dict[str, Any]', data))
        if 'dimension' in normalized_data and 'breakdown' not in normalized_data:
            warnings.warn(
                "Waffle chart field 'dimension' is deprecated, use 'breakdown' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            normalized_data['breakdown'] = normalized_data.pop('dimension')
        elif 'dimension' in normalized_data and 'breakdown' in normalized_data:
            warnings.warn(
                "Waffle chart field 'dimension' is ignored because 'breakdown' is already set.",
                DeprecationWarning,
                stacklevel=2,
            )
            normalized_data.pop('dimension')
        return normalized_data
