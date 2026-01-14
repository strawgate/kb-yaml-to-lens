"""View models for pie and donut chart visualizations in Kibana Lens format.

Fixture Examples:
    https://github.com/strawgate/kb-yaml-to-lens-fixtures
    - ES|QL: output/<version>/pie-chart-esql.json
    - Data View: output/<version>/pie-chart-dataview.json
"""

from typing import Annotated, Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base.view import KbnBaseStateVisualization, KbnBaseStateVisualizationLayer
from dashboard_compiler.shared.view import OmitIfNone


class KbnPieStateVisualizationLayer(KbnBaseStateVisualizationLayer):
    """View model for pie chart visualization layer configuration.

    Represents a data layer in a pie or donut chart visualization. Defines the metrics
    to display, grouping dimensions, legend configuration, and display options for the chart.

    This model represents the compiled structure sent to Kibana for configuring pie chart
    layers in Lens visualizations.

    See Also:
        Kibana type definition: Related layer types in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/pie/types.ts
    """

    layerType: Literal['data'] = 'data'
    """Always 'data' for pie chart layers."""

    primaryGroups: list[str]
    """List of field accessor IDs for primary grouping dimension (slice breakdown)."""

    secondaryGroups: Annotated[list[str] | None, OmitIfNone()] = Field(None)
    """List of field accessor IDs for secondary grouping dimension (nested slices)."""

    metrics: list[str]
    """List of field accessor IDs for metrics to display (slice sizes)."""

    allowMultipleMetrics: Annotated[bool | None, OmitIfNone()] = Field(None)
    """Whether to allow multiple metrics in a single pie chart."""

    collapseFns: Annotated[dict[str, str] | None, OmitIfNone()] = Field(None)
    """Aggregation functions for collapsing values by accessor ID."""

    numberDisplay: str
    """How to display numbers on slices ('percent', 'value', or 'hidden')."""

    categoryDisplay: str
    """How to display category labels ('default', 'inside', or 'hide')."""

    legendDisplay: str
    """Legend display mode ('default', 'show', 'hide')."""

    nestedLegend: bool
    """Whether to show nested legend for multi-level grouping."""

    emptySizeRatio: Annotated[float | None, OmitIfNone()] = Field(None)
    """Size ratio of the empty center hole in donut charts (0.0 to 1.0)."""

    legendSize: Annotated[str | None, OmitIfNone()] = Field(None)
    """Size of the legend ('small', 'medium', 'large', 'xlarge')."""

    truncateLegend: Annotated[bool | None, OmitIfNone()] = Field(None)
    """Whether to truncate long legend labels."""

    legendMaxLines: Annotated[int | None, OmitIfNone()] = Field(None)
    """Maximum number of lines to display in legend labels."""

    showSingleSeries: Annotated[bool | None, OmitIfNone()] = Field(None)
    """Whether to show legend when there is only one series."""


class KbnPieVisualizationState(KbnBaseStateVisualization):
    """View model for pie chart visualization state after compilation to Kibana Lens format.

    This model represents the complete visualization state for pie and donut charts as stored
    in the Kibana saved object JSON structure. It includes the chart shape and all data layers
    with their configuration.

    The visualization state is part of the larger Lens panel configuration and defines how
    the pie chart should be rendered in Kibana dashboards.

    See Also:
        Kibana type definition: `PieVisualizationState` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/pie/types.ts
    """

    shape: Literal['pie', 'donut']
    """Shape of the chart ('pie' for full circle, 'donut' for ring chart)."""

    layers: list[KbnPieStateVisualizationLayer] = Field(...)
    """List of data layers for the pie chart."""
