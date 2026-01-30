"""Configuration models for heatmap chart visualizations."""

from typing import Literal, Self

from pydantic import Field, model_validator

from kb_dashboard_core.panels.charts.base.config import BaseChart, LegendVisibleEnum
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from kb_dashboard_core.panels.charts.lens.dimensions.config import LensDimensionTypes
from kb_dashboard_core.panels.charts.lens.metrics.config import LensMetricTypes
from kb_dashboard_core.shared.config import BaseCfgModel


class HeatmapAxisConfig(BaseCfgModel):
    """Configuration for a heatmap axis.

    Controls visibility of axis labels and title.
    """

    show_labels: bool | None = Field(default=None)
    """Whether to show axis labels."""

    show_title: bool | None = Field(default=None)
    """Whether to show axis title."""


class HeatmapCellsConfig(BaseCfgModel):
    """Configuration for heatmap cells.

    Controls visibility of cell labels.
    """

    show_labels: bool | None = Field(default=None)
    """Whether to show labels inside heatmap cells."""


class HeatmapGridConfig(BaseCfgModel):
    """Grid configuration for heatmap visualizations.

    Controls the visibility of cell labels and axis configuration.
    """

    cells: HeatmapCellsConfig | None = Field(default=None)
    """Configuration for cell labels."""

    x_axis: HeatmapAxisConfig | None = Field(default=None)
    """Configuration for the X-axis."""

    y_axis: HeatmapAxisConfig | None = Field(default=None)
    """Configuration for the Y-axis."""


class HeatmapLegendConfig(BaseCfgModel):
    """Legend configuration for heatmap visualizations.

    Controls the visibility and position of the color legend.
    Note: Heatmaps only support 'show' and 'hide' visibility options (not 'auto').
    """

    visible: LegendVisibleEnum | None = Field(
        default=None,
        strict=False,  # Allow string coercion from YAML config (e.g., 'show' -> LegendVisibleEnum.SHOW)
    )
    """Visibility of the legend (show or hide). Kibana defaults to show if not specified."""

    position: Literal['top', 'right', 'bottom', 'left'] | None = Field(default=None)
    """Position of the legend relative to the chart."""

    @model_validator(mode='after')
    def validate_visible_not_auto(self) -> Self:
        """Validate that visible is not 'auto' for heatmaps.

        Heatmaps only support 'show' and 'hide' visibility options.
        """
        if self.visible == LegendVisibleEnum.AUTO:
            msg = "Heatmap legend does not support 'auto' visibility. Use 'show' or 'hide'."
            raise ValueError(msg)
        return self


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
