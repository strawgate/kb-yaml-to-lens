"""View models for heatmap chart visualizations in Kibana Lens format."""

from typing import Annotated, Literal

from pydantic import Field

from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone


class KbnHeatmapGridConfig(BaseVwModel):
    """View model for heatmap grid configuration.

    Controls visibility of cell labels, axis labels, and axis titles in the heatmap.
    """

    type: Literal['heatmap_grid'] = 'heatmap_grid'
    """Type identifier for heatmap grid configuration."""

    isCellLabelVisible: bool = Field(default=False)
    """Whether to show labels inside heatmap cells. Defaults to false."""

    isXAxisLabelVisible: bool = Field(default=False)
    """Whether to show X-axis labels. Defaults to false."""

    isXAxisTitleVisible: bool = Field(default=False)
    """Whether to show X-axis title. Defaults to false."""

    isYAxisLabelVisible: bool = Field(default=False)
    """Whether to show Y-axis labels. Defaults to false."""

    isYAxisTitleVisible: bool = Field(default=False)
    """Whether to show Y-axis title. Defaults to false."""


class KbnHeatmapLegendConfig(BaseVwModel):
    """View model for heatmap legend configuration.

    Controls visibility and position of the color legend.
    """

    type: Literal['heatmap_legend'] = 'heatmap_legend'
    """Type identifier for heatmap legend configuration."""

    isVisible: bool = Field(default=True)
    """Whether to show the legend. Defaults to true."""

    position: Literal['top', 'right', 'bottom', 'left'] = Field(default='right')
    """Position of the legend relative to the chart. Defaults to 'right'."""


class KbnHeatmapVisualizationState(BaseVwModel):
    """View model for heatmap visualization state after compilation to Kibana Lens format.

    This model represents the complete visualization state for heatmap visualizations as stored
    in the Kibana saved object JSON structure. Heatmap visualizations display data as a matrix
    where cell colors represent metric values, typically used for visualizing patterns across
    two categorical dimensions.

    Unlike multi-layer chart types (pie, XY), heatmap visualizations use a flat structure where
    layer properties are directly on the visualization state object, not nested in a layers array.

    The visualization state is part of the larger Lens panel configuration and defines how
    the heatmap should be rendered in Kibana dashboards.

    See Also:
        Kibana type definition: `HeatmapVisualizationState` in Kibana source code.
    """

    layerId: str = Field(...)
    """Unique identifier for the layer within the visualization."""

    layerType: Literal['data'] = 'data'
    """Always 'data' for heatmap visualizations."""

    shape: Literal['heatmap'] = 'heatmap'
    """Always 'heatmap' for heatmap visualizations."""

    xAccessor: str = Field(...)
    """Field accessor ID for the X-axis dimension."""

    yAccessor: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Field accessor ID for the Y-axis dimension. Optional for 1D heatmaps."""

    valueAccessor: str = Field(...)
    """Field accessor ID for the metric that determines cell color intensity."""

    gridConfig: KbnHeatmapGridConfig = Field(default_factory=KbnHeatmapGridConfig)
    """Grid configuration controlling cell and axis label visibility. Always present with defaults."""

    legend: KbnHeatmapLegendConfig = Field(default_factory=KbnHeatmapLegendConfig)
    """Legend configuration controlling visibility and position. Always present with defaults."""
