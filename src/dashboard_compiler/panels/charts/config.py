from typing import Literal

from pydantic import Field
from pydantic.functional_validators import field_validator

from dashboard_compiler.filters.config import FilterTypes
from dashboard_compiler.panels.base import BasePanel
from dashboard_compiler.panels.charts.gauge import ESQLGaugeChart, LensGaugeChart
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

type AllChartTypes = LensChartTypes | ESQLChartTypes

type LensChartTypes = MultiLayerChartTypes | SingleLayerChartTypes

type MultiLayerChartTypes = LensPieChart | LensLineChart | LensBarChart | LensAreaChart | LensTagcloudChart | LensReferenceLineLayer

type SingleLayerChartTypes = LensMetricChart | LensGaugeChart

type ESQLChartTypes = ESQLMetricChart | ESQLGaugeChart | ESQLPieChart | ESQLBarChart | ESQLAreaChart | ESQLLineChart | ESQLTagcloudChart


class LensPanel(BasePanel):
    """Represents a Lens chart panel configuration."""

    type: Literal['charts'] = 'charts'

    filters: list['FilterTypes'] | None = Field(default=None)
    """A list of filters to apply to the panel."""

    query: 'LegacyQueryTypes | None' = Field(default=None)
    """The query to be executed. This is the core of the chart definition."""

    chart: 'LensChartTypes' = Field(default=...)


class LensMultiLayerPanel(BasePanel):
    """Represents a multi-layer Lens chart panel configuration."""

    type: Literal['multi_layer_charts'] = 'multi_layer_charts'

    layers: list['MultiLayerChartTypes'] = Field(default=..., min_length=1)

    @field_validator('layers', mode='after')
    @classmethod
    def validate_layers(cls, layers: list['MultiLayerChartTypes']) -> list['MultiLayerChartTypes']:
        """Validate that the multi-layer panel does not start with a reference line layer.

        Args:
            layers: The list of layers to validate.

        Returns:
            The list of layers.
        """
        if isinstance(layers[0], LensReferenceLineLayer):
            msg = 'Multi-layer panel cannot start with a reference line layer'
            raise TypeError(msg)

        # Check if reference lines are used with compatible charts
        has_ref_line = any(isinstance(layer, LensReferenceLineLayer) for layer in layers)
        if has_ref_line:
            # The last non-reference-line layer determines the visualization type
            # We know there is at least one non-reference-line layer because layers[0] is not a reference line layer
            last_main_layer = next(layer for layer in reversed(layers) if not isinstance(layer, LensReferenceLineLayer))

            if not isinstance(last_main_layer, (LensLineChart, LensBarChart, LensAreaChart)):
                msg = 'Reference line layers can only be used with XY chart visualizations'
                raise ValueError(msg)

        return layers


class ESQLPanel(BasePanel):
    """Represents an ESQL chart panel configuration."""

    type: Literal['charts'] = 'charts'

    esql: 'ESQLQueryTypes' = Field(...)

    chart: 'ESQLChartTypes' = Field(default=...)
