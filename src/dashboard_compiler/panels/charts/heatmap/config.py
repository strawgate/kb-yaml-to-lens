"""Configuration models for heatmap chart visualizations."""

from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.charts.base.config import BaseChart
from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from dashboard_compiler.panels.charts.lens.dimensions.config import LensDimensionTypes
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes
from dashboard_compiler.shared.config import BaseCfgModel


class HeatmapGridConfig(BaseCfgModel):
    """Grid configuration for heatmap visualizations.

    Controls the visibility of cell labels, axis labels, and axis titles.
    """

    is_cell_label_visible: bool | None = Field(default=None)
    """Whether to show labels inside heatmap cells."""

    is_x_axis_label_visible: bool | None = Field(default=None)
    """Whether to show X-axis labels."""

    is_x_axis_title_visible: bool | None = Field(default=None)
    """Whether to show X-axis title."""

    is_y_axis_label_visible: bool | None = Field(default=None)
    """Whether to show Y-axis labels."""

    is_y_axis_title_visible: bool | None = Field(default=None)
    """Whether to show Y-axis title."""


class HeatmapLegendConfig(BaseCfgModel):
    """Legend configuration for heatmap visualizations.

    Controls the visibility and position of the color legend.
    """

    is_visible: bool | None = Field(default=None)
    """Whether to show the legend."""

    position: Literal['top', 'right', 'bottom', 'left'] | None = Field(default=None)
    """Position of the legend relative to the chart."""


class BaseHeatmapChart(BaseCfgModel):
    """Base configuration for heatmap chart visualizations.

    Provides common fields shared between Lens and ESQL heatmap chart configurations.
    Heatmap charts display data as a matrix where values are represented by color intensity.
    """

    type: Literal['heatmap'] = Field(default='heatmap')
    """The type of chart, which is 'heatmap' for this visualization."""

    grid_config: HeatmapGridConfig | None = Field(default=None)
    """Configuration for grid elements (cell labels, axis labels, titles)."""

    legend: HeatmapLegendConfig | None = Field(default=None)
    """Configuration for the color legend."""


class LensHeatmapChart(BaseChart, BaseHeatmapChart):
    """Represents a Heatmap chart configuration within a Lens panel.

    Heatmap charts display data as a matrix where cell colors represent metric values,
    typically used for visualizing patterns across two categorical dimensions.
    """

    data_view: str = Field(default=...)
    """The data view that determines the data for the heatmap chart."""

    x_axis: LensDimensionTypes = Field(...)
    """The dimension to display on the X-axis (horizontal)."""

    y_axis: LensDimensionTypes | None = Field(default=None)
    """The dimension to display on the Y-axis (vertical). Optional for 1D heatmaps."""

    value: LensMetricTypes = Field(...)
    """The metric that determines cell color intensity."""


class ESQLHeatmapChart(BaseChart, BaseHeatmapChart):
    """Represents a Heatmap chart configuration within an ESQL panel.

    Heatmap charts display data as a matrix where cell colors represent metric values,
    typically used for visualizing patterns across two categorical dimensions.
    """

    x_axis: ESQLDimensionTypes = Field(...)
    """The dimension to display on the X-axis (horizontal)."""

    y_axis: ESQLDimensionTypes | None = Field(default=None)
    """The dimension to display on the Y-axis (vertical). Optional for 1D heatmaps."""

    value: ESQLMetricTypes = Field(...)
    """The metric that determines cell color intensity."""
