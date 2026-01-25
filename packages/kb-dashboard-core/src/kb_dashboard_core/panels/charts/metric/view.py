"""View models for metric chart visualizations in Kibana Lens format.

Fixture Examples:
    https://github.com/strawgate/kb-yaml-to-lens-fixtures
    - ES|QL: output/<version>/metric-basic-esql.json
    - Data View: output/<version>/metric-basic-dataview.json
"""

from typing import Annotated, Literal

from pydantic import Field

from kb_dashboard_core.shared.view import BaseVwModel, OmitIfNone


class KbnSecondaryTrendNone(BaseVwModel):
    """View model for a secondary trend configuration with no trend display.

    See Also:
        Kibana type definition: Part of `SecondaryTrend` union in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/metric/types.ts
    """

    type: Literal['none'] = 'none'
    """Type indicating no trend should be displayed."""


class KbnMetricVisualizationState(BaseVwModel):
    """View model for metric visualization state after compilation to Kibana Lens format.

    This model represents the complete visualization state for metric visualizations as stored
    in the Kibana saved object JSON structure. Metric visualizations display key performance
    indicators (KPIs) as prominent numbers with optional sparklines and breakdowns.

    Metric visualizations use a flat structure without layers array, matching the structure
    used by ES|QL metrics.

    The visualization state is part of the larger Lens panel configuration and defines how
    the metric should be rendered in Kibana dashboards.

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

    secondaryTrend: Annotated[KbnSecondaryTrendNone | None, OmitIfNone()] = Field(default=None)
    """Configuration for secondary trend visualization (e.g., sparklines, comparison indicators)."""

    secondaryLabelPosition: Annotated[Literal['before', 'after'] | None, OmitIfNone()] = Field(default=None)
    """Position of secondary label relative to the metric value."""

    showBar: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    """Whether to display a sparkline bar chart below the metric."""

    secondaryMetricAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Field accessor ID for a secondary comparison metric."""

    breakdownByAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Field accessor ID for breaking down the metric into multiple values."""

    maxAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Field accessor ID for the maximum value metric (used for sparkline scale)."""


class KbnESQLMetricVisualizationState(BaseVwModel):
    """View model for ES|QL metric visualization state.

    ES|QL metric visualizations use a flat structure without layers array or colorMapping,
    similar to standard Lens metrics.

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
