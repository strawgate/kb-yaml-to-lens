"""View models for gauge chart visualizations in Kibana Lens format."""

from typing import Annotated, Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base import KbnBaseStateVisualization, KbnBaseStateVisualizationLayer
from dashboard_compiler.shared.view import OmitIfNone


class KbnGaugeStateVisualizationLayer(KbnBaseStateVisualizationLayer):
    """View model for gauge visualization layer configuration.

    Represents a data layer in a gauge visualization, which displays a single metric value
    with optional min/max ranges and goal indicators. Defines which metric to display and
    visualization options like shape, ticks, and labels.

    This model represents the compiled structure sent to Kibana for configuring gauge
    visualization layers.

    See Also:
        Kibana type definition: Related layer types in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/gauge/types.ts
    """

    layerType: Literal['data'] = 'data'
    """Always 'data' for gauge layers."""

    metricAccessor: str = Field(...)
    """Field accessor ID for the primary metric value to display."""

    minAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Field accessor ID for the minimum value metric (defines gauge range start)."""

    maxAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Field accessor ID for the maximum value metric (defines gauge range end)."""

    goalAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Field accessor ID for the goal/target metric (shown as reference line)."""

    shape: Annotated[Literal['horizontalBullet', 'verticalBullet', 'arc', 'circle'] | None, OmitIfNone()] = Field(default=None)
    """The shape of the gauge visualization."""

    ticksPosition: Annotated[Literal['auto', 'bands', 'hidden'] | None, OmitIfNone()] = Field(default=None)
    """Position of tick marks on the gauge."""

    labelMajor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Major label text to display on the gauge."""

    labelMinor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Minor label text to display on the gauge."""

    labelMajorMode: Annotated[Literal['auto', 'custom', 'none'] | None, OmitIfNone()] = Field(default=None)
    """Mode for the major label (auto-generated, custom, or hidden)."""

    colorMode: Annotated[Literal['none', 'palette'] | None, OmitIfNone()] = Field(default=None)
    """Color mode for the gauge visualization."""


class KbnGaugeVisualizationState(KbnBaseStateVisualization):
    """View model for gauge visualization state after compilation to Kibana Lens format.

    This model represents the complete visualization state for gauge visualizations as stored
    in the Kibana saved object JSON structure. Gauge visualizations display a single metric
    value with optional min/max ranges and goal indicators, typically used for KPIs and
    progress tracking.

    The visualization state is part of the larger Lens panel configuration and defines how
    the gauge should be rendered in Kibana dashboards.

    See Also:
        Kibana type definition: `GaugeVisualizationState` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/gauge/types.ts
    """
