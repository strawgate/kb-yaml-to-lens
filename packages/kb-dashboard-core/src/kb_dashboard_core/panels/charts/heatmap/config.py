"""Configuration models for heatmap chart visualizations."""

from typing import Literal, Self

from pydantic import Field, model_validator

from kb_dashboard_core.panels.charts.base.config import BaseChart, BaseLegend, ColorRangeMapping, LegendVisibleEnum
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from kb_dashboard_core.panels.charts.lens.dimensions.config import LensDimensionTypes
from kb_dashboard_core.panels.charts.lens.metrics.config import LensMetricTypes
from kb_dashboard_core.shared.config import BaseCfgModel


class HeatmapAxisLabelsConfig(BaseCfgModel):
    """Configuration for heatmap axis tick labels."""

    visible: bool | None = Field(default=None)
    """Whether to show tick labels on the axis."""


class HeatmapAxisTitleConfig(BaseCfgModel):
    """Configuration for heatmap axis titles."""

    visible: bool | None = Field(default=None)
    """Whether to show the axis title."""


class HeatmapAxisAppearance(BaseCfgModel):
    """Appearance configuration for a heatmap axis."""

    labels: HeatmapAxisLabelsConfig | None = Field(default=None)
    """Configuration for axis tick labels."""

    title: HeatmapAxisTitleConfig | None = Field(default=None)
    """Configuration for axis title visibility."""


class HeatmapValuesConfig(BaseCfgModel):
    """Configuration for heatmap numeric values."""

    visible: bool | None = Field(default=None)
    """Whether to show numeric values inside heatmap cells."""


class HeatmapLegendConfig(BaseLegend):
    """Legend configuration for heatmap visualizations.

    Controls the visibility and position of the color legend.
    Note: Heatmaps only support 'show' and 'hide' visibility options (not 'auto').
    """

    @model_validator(mode='after')
    def validate_visible_not_auto(self) -> Self:
        """Validate that visible is not 'auto' for heatmaps.

        Heatmaps only support 'show' and 'hide' visibility options.
        """
        if self.visible == LegendVisibleEnum.AUTO:
            msg = "Heatmap legend does not support 'auto' visibility. Use 'show' or 'hide'."
            raise ValueError(msg)
        return self


class HeatmapAppearance(BaseCfgModel):
    """Formatting options for the chart appearance."""

    values: HeatmapValuesConfig | None = Field(default=None)
    """Configuration for numeric values shown in heatmap cells."""

    x_axis: HeatmapAxisAppearance | None = Field(default=None)
    """Configuration for the X-axis labels and title."""

    y_axis: HeatmapAxisAppearance | None = Field(default=None)
    """Configuration for the Y-axis labels and title."""

    legend: HeatmapLegendConfig | None = Field(default=None)
    """Configuration for the color legend."""


class BaseHeatmapChart(BaseCfgModel):
    """Base configuration for heatmap chart visualizations.

    Provides common fields shared between Lens and ESQL heatmap chart configurations.
    Heatmap charts display data as a matrix where values are represented by color intensity.
    """

    type: Literal['heatmap'] = Field(default='heatmap')
    """The type of chart, which is 'heatmap' for this visualization."""

    appearance: HeatmapAppearance | None = Field(default=None)
    """Formatting options for the chart appearance."""

    color: ColorRangeMapping | None = Field(default=None)
    """Optional range-based palette configuration for heatmap cell coloring."""


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

    metric: LensMetricTypes = Field(...)
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

    metric: ESQLMetricTypes = Field(...)
    """The metric that determines cell color intensity."""
