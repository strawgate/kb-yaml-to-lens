"""Treemap chart configuration models for YAML schema definition."""

from enum import StrEnum
from typing import Literal

from pydantic import Field

from kb_dashboard_core.panels.charts.base.config import BaseChart, ColorValueMapping
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from kb_dashboard_core.panels.charts.lens.dimensions.config import LensDimensionTypes
from kb_dashboard_core.panels.charts.lens.metrics.config import LensMetricTypes
from kb_dashboard_core.panels.charts.pie.config import PieLegend, PieSliceValuesEnum
from kb_dashboard_core.shared.config import BaseCfgModel


class TreemapSliceLabelsEnum(StrEnum):
    """Represents the possible values for treemap slice labels."""

    HIDE = 'hide'
    """Hide category labels."""

    SHOW = 'show'
    """Show category labels."""


class TreeMapLegend(PieLegend):
    """Represents legend formatting options for treemap charts."""


class TreemapTitlesAndText(BaseCfgModel):
    """Represents titles and text formatting options for treemap charts."""

    slice_labels: TreemapSliceLabelsEnum | None = Field(default=None, strict=False)
    """Controls the visibility of category labels. Defaults to show when not specified."""

    slice_values: PieSliceValuesEnum | None = Field(default=None, strict=False)
    """Controls the display of values in treemap rectangles. Defaults to percent."""

    value_decimal_places: int | None = Field(default=None, ge=0, le=10)
    """Controls the number of decimal places for values."""


class BaseTreemapChart(BaseChart):
    """Base model for defining Treemap chart objects."""

    type: Literal['treemap'] = Field(default='treemap')

    titles_and_text: TreemapTitlesAndText | None = Field(default=None)
    """Formatting options for chart labels and values."""

    legend: TreeMapLegend | None = Field(default=None)
    """Formatting options for the chart legend."""

    color: ColorValueMapping | None = Field(default=None)
    """Formatting options for the chart color."""


class LensTreemapChart(BaseTreemapChart):
    """Represents a Treemap chart configuration within a Lens panel."""

    data_view: str = Field(default=...)
    """The data view that determines the data for the treemap chart."""

    metrics: list[LensMetricTypes] = Field(default=..., min_length=1)
    """Metrics that determine the rectangle sizes."""

    dimensions: list[LensDimensionTypes] = Field(default=...)
    """Dimensions that determine treemap grouping levels."""


class ESQLTreemapChart(BaseTreemapChart):
    """Represents a Treemap chart configuration within an ES|QL panel."""

    metrics: list[ESQLMetricTypes] = Field(default=..., min_length=1)
    """Metrics that determine the rectangle sizes."""

    dimensions: list[ESQLDimensionTypes] = Field(default=...)
    """Dimensions that determine treemap grouping levels."""
