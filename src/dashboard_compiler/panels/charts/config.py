from typing import Any

from pydantic import ConfigDict, Field, TypeAdapter, model_validator

from dashboard_compiler.filters.config import FilterTypes
from dashboard_compiler.panels.base import BasePanel
from dashboard_compiler.panels.charts.metric import ESQLMetricChart, LensMetricChart
from dashboard_compiler.panels.charts.pie import ESQLPieChart, LensPieChart
from dashboard_compiler.panels.charts.tagcloud import ESQLTagcloudChart, LensTagcloudChart
from dashboard_compiler.panels.charts.xy.config import (
    ESQLAreaChart,
    ESQLBarChart,
    ESQLLineChart,
    LensAreaChart,
    LensBarChart,
    LensLineChart,
    LensReferenceLineLayer,
)
from dashboard_compiler.queries.types import ESQLQueryTypes, LegacyQueryTypes
from dashboard_compiler.shared.config import BaseCfgModel

type AllChartTypes = LensChartTypes | ESQLChartTypes

type LensChartTypes = MultiLayerChartTypes | SingleLayerChartTypes

type MultiLayerChartTypes = LensPieChart | LensLineChart | LensBarChart | LensAreaChart | LensTagcloudChart | LensReferenceLineLayer

type SingleLayerChartTypes = LensMetricChart

type ESQLChartTypes = ESQLMetricChart | ESQLPieChart | ESQLBarChart | ESQLAreaChart | ESQLLineChart | ESQLTagcloudChart


class LensPanelConfig(BaseCfgModel):
    """Configuration for a Lens chart panel (single or multi-layer).

    The base layer chart configuration fields (type, data_view, metrics, etc.)
    are specified directly in this object alongside panel-level fields.
    """

    model_config: ConfigDict = ConfigDict(extra='allow')

    # Panel-level configuration
    filters: list['FilterTypes'] | None = Field(default=None)
    """A list of filters to apply to the panel."""

    query: 'LegacyQueryTypes | None' = Field(default=None)
    """The query to be executed."""

    # Optional additional layers for multi-layer panels
    layers: list['MultiLayerChartTypes'] | None = Field(default=None)
    """Optional additional layers for multi-layer charts. The first layer is defined directly in this config."""

    # Internal fields to store parsed chart
    chart_config: 'LensChartTypes | None' = Field(default=None, exclude=True)
    """Internal field storing the parsed base chart configuration."""

    @model_validator(mode='before')
    @classmethod
    def parse_chart_fields(cls, data: Any) -> Any:
        """Parse and validate the base chart configuration from input data."""
        if not isinstance(data, dict):
            return data

        # Extract chart fields (everything except panel-level fields)
        panel_fields = {'filters', 'query', 'layers'}
        chart_data = {k: v for k, v in data.items() if k not in panel_fields}

        # Parse chart data into appropriate chart type using TypeAdapter
        if len(chart_data) > 0:
            adapter = TypeAdapter(LensChartTypes)
            try:
                chart = adapter.validate_python(chart_data)
                data['chart_config'] = chart
            except Exception as e:
                msg = f'Failed to parse Lens chart configuration: {e!s}'
                raise ValueError(msg) from e

        return data


class ESQLPanelConfig(BaseCfgModel):
    """Configuration for an ES|QL chart panel.

    The ES|QL query and chart configuration fields are specified directly in this object.
    ES|QL panels do not support multi-layer configurations.
    """

    model_config: ConfigDict = ConfigDict(extra='allow')

    query: 'ESQLQueryTypes' = Field(...)
    """The ES|QL query to execute."""

    # Internal field to store parsed chart
    chart_config: 'ESQLChartTypes | None' = Field(default=None, exclude=True)
    """Internal field storing the parsed chart configuration."""

    @model_validator(mode='before')
    @classmethod
    def parse_chart_fields(cls, data: Any) -> Any:
        """Parse and validate the chart configuration from input data."""
        if not isinstance(data, dict):
            return data

        # Extract chart fields (everything except query)
        chart_data = {k: v for k, v in data.items() if k != 'query'}

        # Parse chart data into appropriate chart type
        if len(chart_data) > 0:
            adapter = TypeAdapter(ESQLChartTypes)
            try:
                chart = adapter.validate_python(chart_data)
                data['chart_config'] = chart
            except Exception as e:
                msg = f'Failed to parse ES|QL chart configuration: {e!s}'
                raise ValueError(msg) from e

        return data


class LensPanel(BasePanel):
    """Represents a Lens chart panel (single or multi-layer)."""

    lens: LensPanelConfig = Field(...)
    """Lens panel configuration."""


class ESQLPanel(BasePanel):
    """Represents an ES|QL chart panel."""

    esql: ESQLPanelConfig = Field(...)
    """ES|QL panel configuration."""


# Backward compatibility - LensMultiLayerPanel is now handled by LensPanel with layers field
LensMultiLayerPanel = LensPanel
