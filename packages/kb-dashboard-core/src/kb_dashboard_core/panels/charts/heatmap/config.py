"""Configuration models for heatmap chart visualizations."""

import warnings
from typing import Any, Literal, Self, cast

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

    @model_validator(mode='before')
    @classmethod
    def _translate_deprecated_appearance_fields(cls, data: object) -> object:  # noqa: PLR0912, PLR0915
        if not isinstance(data, dict):
            return data

        def as_dict(value: object) -> dict[str, Any]:
            return dict(cast('dict[str, Any]', value)) if isinstance(value, dict) else {}

        normalized_data: dict[str, Any] = dict(cast('dict[str, Any]', data))
        appearance = as_dict(cast('object', normalized_data.get('appearance')))

        if 'grid_config' in normalized_data:
            grid_config_raw = cast('object', normalized_data.get('grid_config'))
            if isinstance(grid_config_raw, dict):
                normalized_data.pop('grid_config')
                grid_config = as_dict(cast('object', grid_config_raw))
                values = as_dict(cast('object', appearance.get('values')))
                x_axis = as_dict(cast('object', appearance.get('x_axis')))
                y_axis = as_dict(cast('object', appearance.get('y_axis')))

                cells = grid_config.get('cells')
                if isinstance(cells, dict) and 'show_labels' in cells:
                    if 'visible' not in values:
                        values['visible'] = cells['show_labels']
                    else:
                        warnings.warn(
                            (
                                "Heatmap field 'grid_config.cells.show_labels' is ignored because "
                                "'appearance.values.visible' is already set."
                            ),
                            DeprecationWarning,
                            stacklevel=2,
                        )

                legacy_x_axis = as_dict(grid_config.get('x_axis'))
                if legacy_x_axis:
                    labels = as_dict(x_axis.get('labels'))
                    title = as_dict(x_axis.get('title'))
                    if 'show_labels' in legacy_x_axis:
                        if 'visible' not in labels:
                            labels['visible'] = legacy_x_axis['show_labels']
                        else:
                            warnings.warn(
                                (
                                    "Heatmap field 'grid_config.x_axis.show_labels' is ignored because "
                                    "'appearance.x_axis.labels.visible' is already set."
                                ),
                                DeprecationWarning,
                                stacklevel=2,
                            )
                    if 'show_title' in legacy_x_axis:
                        if 'visible' not in title:
                            title['visible'] = legacy_x_axis['show_title']
                        else:
                            warnings.warn(
                                (
                                    "Heatmap field 'grid_config.x_axis.show_title' is ignored because "
                                    "'appearance.x_axis.title.visible' is already set."
                                ),
                                DeprecationWarning,
                                stacklevel=2,
                            )
                    if labels:
                        x_axis['labels'] = labels
                    if title:
                        x_axis['title'] = title

                legacy_y_axis = as_dict(grid_config.get('y_axis'))
                if legacy_y_axis:
                    labels = as_dict(y_axis.get('labels'))
                    title = as_dict(y_axis.get('title'))
                    if 'show_labels' in legacy_y_axis:
                        if 'visible' not in labels:
                            labels['visible'] = legacy_y_axis['show_labels']
                        else:
                            warnings.warn(
                                (
                                    "Heatmap field 'grid_config.y_axis.show_labels' is ignored because "
                                    "'appearance.y_axis.labels.visible' is already set."
                                ),
                                DeprecationWarning,
                                stacklevel=2,
                            )
                    if 'show_title' in legacy_y_axis:
                        if 'visible' not in title:
                            title['visible'] = legacy_y_axis['show_title']
                        else:
                            warnings.warn(
                                (
                                    "Heatmap field 'grid_config.y_axis.show_title' is ignored because "
                                    "'appearance.y_axis.title.visible' is already set."
                                ),
                                DeprecationWarning,
                                stacklevel=2,
                            )
                    if labels:
                        y_axis['labels'] = labels
                    if title:
                        y_axis['title'] = title

                if values:
                    appearance['values'] = values
                if x_axis:
                    appearance['x_axis'] = x_axis
                if y_axis:
                    appearance['y_axis'] = y_axis
                warnings.warn(
                    "Heatmap field 'grid_config' is deprecated, use nested 'appearance.values/x_axis/y_axis' visibility fields instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )

        if 'legend' in normalized_data:
            legend_raw = cast('object', normalized_data.get('legend'))
            if isinstance(legend_raw, dict):
                normalized_data.pop('legend')
                legend = as_dict(cast('object', legend_raw))
                if 'legend' not in appearance:
                    appearance['legend'] = legend
                    warnings.warn(
                        "Heatmap field 'legend' is deprecated, use 'appearance.legend' instead.",
                        DeprecationWarning,
                        stacklevel=2,
                    )
                else:
                    warnings.warn(
                        "Heatmap field 'legend' is ignored because 'appearance.legend' is already set.",
                        DeprecationWarning,
                        stacklevel=2,
                    )

        if appearance:
            normalized_data['appearance'] = appearance

        return normalized_data


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
