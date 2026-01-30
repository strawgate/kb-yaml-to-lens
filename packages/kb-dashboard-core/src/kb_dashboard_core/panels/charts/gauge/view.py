"""View models for gauge chart visualizations in Kibana Lens format.

Fixture Examples:
    https://github.com/strawgate/kb-yaml-to-lens-fixtures
    - ES|QL: output/<version>/gauge-esql.json
    - Data View: output/<version>/gauge-dataview.json
"""

from typing import Annotated, Literal

from pydantic import Field

from kb_dashboard_core.shared.view import BaseVwModel, OmitIfNone


class KbnGaugeVisualizationState(BaseVwModel):
    """View model for gauge visualization state after compilation to Kibana Lens format.

    This model represents the complete visualization state for gauge visualizations as stored
    in the Kibana saved object JSON structure. Gauge visualizations display a single metric
    value with optional min/max ranges and goal indicators, typically used for KPIs and
    progress tracking.

    Unlike multi-layer chart types (pie, XY), gauge visualizations use a flat structure where
    layer properties are directly on the visualization state object, not nested in a layers array.

    The visualization state is part of the larger Lens panel configuration and defines how
    the gauge should be rendered in Kibana dashboards.

    See Also:
        Kibana type definition: `GaugeVisualizationState` in
        https://github.com/elastic/kibana/blob/main/src/platform/packages/shared/kbn-lens-common/visualizations/gauge/types.ts
    """

    layerId: str = Field(...)
    """Unique identifier for the layer within the visualization."""

    layerType: Literal['data'] = 'data'
    """Always 'data' for gauge visualizations."""

    metricAccessor: str = Field(...)
    """Field accessor ID for the primary metric value to display."""

    minAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Field accessor ID for the minimum value metric (defines gauge range start)."""

    maxAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Field accessor ID for the maximum value metric (defines gauge range end)."""

    goalAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Field accessor ID for the goal/target metric (shown as reference line)."""

    shape: Literal['horizontalBullet', 'verticalBullet', 'arc', 'circle'] = Field(default='arc')
    """The shape of the gauge visualization. Defaults to 'arc'."""

    ticksPosition: Literal['auto', 'bands', 'hidden'] = Field(default='auto')
    """Position of tick marks on the gauge. Defaults to 'auto'."""

    labelMajor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Major label text to display on the gauge."""

    labelMinor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Minor label text to display on the gauge."""

    labelMajorMode: Annotated[Literal['auto', 'custom', 'none'] | None, OmitIfNone()] = Field(default=None)
    """Mode for the major label (auto-generated, custom, or hidden)."""

    colorMode: Annotated[Literal['none', 'palette'] | None, OmitIfNone()] = Field(default=None)
    """Color mode for the gauge visualization."""
