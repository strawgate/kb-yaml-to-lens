from typing import Annotated, Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base import KbnBaseStateVisualization, KbnBaseStateVisualizationLayer
from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone


class KbnMetricStateVisualizationLayer(KbnBaseStateVisualizationLayer):
    """View model for metric visualization layer configuration.

    Represents a data layer in a metric visualization, which displays key performance indicators
    (KPIs) as large numbers with optional sparklines and comparison values. Defines which metrics
    to display, breakdowns, and visualization options.

    This model represents the compiled structure sent to Kibana for configuring metric
    visualization layers.

    See Also:
        Kibana type definition: Related layer types in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/metric/types.ts
    """

    layerType: Literal['data'] = 'data'
    """Always 'data' for metric layers."""

    metricAccessor: str = Field(...)
    """Field accessor ID for the primary metric value to display."""

    maxAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Field accessor ID for the maximum value metric (used for sparkline scale)."""

    showBar: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    """Whether to display a sparkline bar chart below the metric."""

    secondaryMetricAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Field accessor ID for a secondary comparison metric."""

    breakdownByAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Field accessor ID for breaking down the metric into multiple values."""


class KbnMetricVisualizationState(KbnBaseStateVisualization):
    """View model for metric visualization state after compilation to Kibana Lens format.

    This model represents the complete visualization state for metric visualizations as stored
    in the Kibana saved object JSON structure. Metric visualizations display key performance
    indicators (KPIs) as prominent numbers with optional sparklines and breakdowns.

    The visualization state is part of the larger Lens panel configuration and defines how
    the metric should be rendered in Kibana dashboards.

    See Also:
        Kibana type definition: `MetricVisualizationState` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/metric/types.ts
    """


class KbnESQLMetricVisualizationState(BaseVwModel):
    """View model for ES|QL metric visualization state.

    ES|QL metric visualizations use a flat structure without layers array or colorMapping,
    unlike Lens-based metrics which wrap everything in a layers array.

    This model represents the structure used when the datasource is textBased (ES|QL queries).

    See Also:
        Kibana type definition: `MetricVisualizationState` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/metric/types.ts
    """

    layerId: str = Field(...)
    """The ID of the layer containing the metric data."""

    layerType: Literal['data'] = 'data'
    """Always 'data' for metric layers."""

    metricAccessor: str = Field(...)
    """Field accessor ID for the primary metric value to display."""

    showBar: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    """Whether to display a sparkline bar chart below the metric."""

    secondaryMetricAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Field accessor ID for a secondary comparison metric."""

    breakdownByAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Field accessor ID for breaking down the metric into multiple values."""
