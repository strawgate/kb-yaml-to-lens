from enum import StrEnum
from typing import Literal

from pydantic import Field, field_validator

from kb_dashboard_core.panels.charts.base.config import BaseChart, ColorValueMapping
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from kb_dashboard_core.panels.charts.lens.breakdowns.config import LensBreakdownTypes
from kb_dashboard_core.panels.charts.lens.metrics.config import LensMetricTypes
from kb_dashboard_core.panels.charts.pie.config import PieLegend, PieSliceValuesEnum
from kb_dashboard_core.shared.config import BaseCfgModel

type ESQLTreemapBreakdownTypes = ESQLDimensionTypes


class TreemapSliceLabelsEnum(StrEnum):
    """Represents the possible values for treemap slice labels."""

    HIDE = 'hide'
    """Hide category labels."""

    SHOW = 'show'
    """Show category labels."""


class TreemapLegend(PieLegend):
    """Represents legend formatting options for treemap charts."""


class TreemapCategoriesConfig(BaseCfgModel):
    """Formatting options for category labels."""

    position: TreemapSliceLabelsEnum | None = Field(default=None, strict=False)
    """Controls the visibility of category labels. Defaults to show when not specified."""


class TreemapValuesConfig(BaseCfgModel):
    """Formatting options for numeric values."""

    format: PieSliceValuesEnum | None = Field(default=None, strict=False)
    """Controls the display of values in treemap rectangles. Defaults to percent."""

    decimal_places: int | None = Field(default=None, ge=0, le=10)
    """Controls the number of decimal places for values."""


class TreemapAppearance(BaseCfgModel):
    """Formatting options for treemap appearance."""

    categories: TreemapCategoriesConfig | None = Field(default=None)
    """Formatting options for category labels."""

    values: TreemapValuesConfig | None = Field(default=None)
    """Formatting options for numeric values."""


class BaseTreemapChart(BaseChart):
    """Base model for defining Treemap chart objects."""

    type: Literal['treemap'] = Field(default='treemap')
    """The type of chart, which is 'treemap' for this visualization."""

    appearance: TreemapAppearance | None = Field(default=None)
    """Formatting options for the chart appearance."""

    legend: TreemapLegend | None = Field(default=None)
    """Formatting options for the chart legend."""

    color: ColorValueMapping | None = Field(default=None)
    """Formatting options for the chart color."""


class LensTreemapChart(BaseTreemapChart):
    """Represents a Treemap chart configuration within a Lens panel."""

    data_view: str = Field(default=...)
    """The data view that determines the data for the treemap chart."""

    metric: LensMetricTypes = Field(default=...)
    """Metric that determines the rectangle sizes. Treemap supports only one metric."""

    breakdowns: list[LensBreakdownTypes] = Field(default=..., max_length=2)
    """Breakdowns that determine treemap grouping levels. Maximum 2 breakdowns supported."""

    @field_validator('breakdowns')
    @classmethod
    def validate_breakdowns_count(cls, v: list[LensBreakdownTypes]) -> list[LensBreakdownTypes]:
        """Validate that treemap has at least one breakdown."""
        if len(v) == 0:
            msg = 'Treemap must have at least one breakdown'
            raise ValueError(msg)
        return v


class ESQLTreemapChart(BaseTreemapChart):
    """Represents a Treemap chart configuration within an ES|QL panel."""

    metric: ESQLMetricTypes = Field(default=...)
    """Metric that determines the rectangle sizes. Treemap supports only one metric."""

    breakdowns: list[ESQLTreemapBreakdownTypes] = Field(default=..., max_length=2)
    """Breakdowns that determine treemap grouping levels. Maximum 2 breakdowns supported."""

    @field_validator('breakdowns')
    @classmethod
    def validate_breakdowns_count(cls, v: list[ESQLTreemapBreakdownTypes]) -> list[ESQLTreemapBreakdownTypes]:
        """Validate that treemap has at least one breakdown."""
        if len(v) == 0:
            msg = 'Treemap must have at least one breakdown'
            raise ValueError(msg)
        return v
