"""View models for mosaic chart visualization state in Kibana JSON format.

Mosaic charts in Kibana use the lnsPie visualization type with shape: 'mosaic'.
These models represent the compiled structure sent to Kibana for configuring
mosaic chart layers in Lens visualizations.

Fixture Examples:
    https://github.com/strawgate/kb-yaml-to-lens-fixtures
    - ES|QL: output/<version>/mosaic-esql.json
    - Data View: output/<version>/mosaic-dataview.json
"""

from typing import Annotated, Literal

from pydantic import Field

from kb_dashboard_core.panels.charts.base.view import KbnBaseStateVisualization, KbnBaseStateVisualizationLayer
from kb_dashboard_core.shared.view import OmitIfNone

LegendPositionType = Literal['top', 'right', 'bottom', 'left']


class KbnMosaicStateVisualizationLayer(KbnBaseStateVisualizationLayer):
    """View model for mosaic chart visualization layer configuration.

    Represents a data layer in a mosaic chart visualization. Defines the metrics
    to display, grouping dimensions, legend configuration, and display options.

    This model represents the compiled structure sent to Kibana for configuring
    mosaic chart layers in Lens visualizations.

    See Also:
        Kibana type definition: Related layer types in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/pie/types.ts
    """

    layerType: Literal['data'] = 'data'
    """Always 'data' for mosaic chart layers."""

    primaryGroups: list[str]
    """List of field accessor IDs for the primary grouping dimension."""

    secondaryGroups: Annotated[list[str] | None, OmitIfNone()] = Field(None)
    """List of field accessor IDs for the secondary grouping (breakdown) dimension."""

    metrics: list[str]
    """List of field accessor IDs for metrics to display (rectangle sizes)."""

    allowMultipleMetrics: Annotated[bool | None, OmitIfNone()] = Field(None)
    """Whether to allow multiple metrics. Should be False for mosaic charts; omitted when None."""

    collapseFns: Annotated[dict[str, str] | None, OmitIfNone()] = Field(None)
    """Aggregation functions for collapsing values by accessor ID."""

    numberDisplay: str
    """How to display numbers ('percent', 'value', or 'hidden')."""

    categoryDisplay: str
    """How to display category labels ('default', 'inside', or 'hide')."""

    legendDisplay: str
    """Legend display mode ('default', 'show', 'hide')."""

    nestedLegend: bool
    """Whether to show nested legend for multi-level grouping."""

    legendPosition: LegendPositionType = Field(default='right')
    """Position of the legend ('top', 'right', 'bottom', 'left'). Defaults to 'right'."""

    legendSize: Annotated[str | None, OmitIfNone()] = Field(None)
    """Size of the legend ('small', 'medium', 'large', 'xlarge')."""

    truncateLegend: Annotated[bool | None, OmitIfNone()] = Field(None)
    """Whether to truncate long legend labels."""

    legendMaxLines: Annotated[int | None, OmitIfNone()] = Field(None)
    """Maximum number of lines to display in legend labels."""

    showSingleSeries: Annotated[bool | None, OmitIfNone()] = Field(None)
    """Whether to show legend when there is only one series."""

    percentDecimals: Annotated[int | None, OmitIfNone()] = Field(None)
    """Number of decimal places for percent display values."""


class KbnMosaicVisualizationState(KbnBaseStateVisualization):
    """View model for mosaic chart visualization state after compilation to Kibana Lens format.

    This model represents the complete visualization state for mosaic charts as stored
    in the Kibana saved object JSON structure. Mosaic charts use the lnsPie visualization
    type with shape set to 'mosaic'.

    The visualization state is part of the larger Lens panel configuration and defines how
    the mosaic chart should be rendered in Kibana dashboards.

    See Also:
        Kibana type definition: `PieVisualizationState` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/pie/types.ts
    """

    shape: Literal['mosaic'] = 'mosaic'
    """Shape of the chart. Always 'mosaic' for mosaic charts."""

    layers: list[KbnMosaicStateVisualizationLayer] = Field(...)
    """List of data layers for the mosaic chart."""
