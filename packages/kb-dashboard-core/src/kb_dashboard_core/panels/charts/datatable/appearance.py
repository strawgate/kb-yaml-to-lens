from enum import StrEnum
from typing import Literal

from pydantic import Field

from kb_dashboard_core.panels.charts.base.config import ColorRangeMapping, ColorThreshold
from kb_dashboard_core.shared.config import BaseCfgModel


class DatatableAlignmentEnum(StrEnum):
    """Alignment options for datatable columns."""

    LEFT = 'left'
    RIGHT = 'right'
    CENTER = 'center'


class DatatableColorModeEnum(StrEnum):
    """Color mode options for datatable columns."""

    NONE = 'none'
    CELL = 'cell'
    TEXT = 'text'


class DatatableSummaryRowEnum(StrEnum):
    """Summary row options for datatable columns."""

    NONE = 'none'
    SUM = 'sum'
    AVG = 'avg'
    COUNT = 'count'
    MIN = 'min'
    MAX = 'max'


class DatatableColumnAppearance(BaseCfgModel):
    """Appearance options shared by datatable metric and dimension columns."""

    width: int | None = Field(default=None)
    """Column width in pixels."""

    hidden: bool = Field(default=False)
    """Whether to hide this column."""

    one_click_filter: bool = Field(default=False)
    """Enable one-click filtering for this column."""

    alignment: DatatableAlignmentEnum | None = Field(default=None, strict=False)
    """Text alignment for the column."""


class DatatableMetricColor(BaseCfgModel):
    """Color settings for datatable metric appearance."""

    apply_to: DatatableColorModeEnum | None = Field(default=None, strict=False)
    """How to apply colors to the metric column."""

    range_type: Literal['number', 'percent'] = Field(default='number')
    """How threshold values are interpreted by Kibana."""

    range_min: float | None = Field(default=0)
    """Optional lower bound for the palette domain."""

    range_max: float | None = Field(default=None)
    """Optional upper bound for the palette domain."""

    thresholds: list[ColorThreshold] | None = Field(default=None, min_length=1)
    """Ordered threshold bands used to build datatable palettes."""

    def to_range_mapping(self) -> ColorRangeMapping | None:
        """Convert to ColorRangeMapping when thresholds are provided."""
        if self.thresholds is None:
            return None
        return ColorRangeMapping(
            range_type=self.range_type,
            range_min=self.range_min,
            range_max=self.range_max,
            thresholds=self.thresholds,
        )


class DatatableMetricAppearance(DatatableColumnAppearance):
    """Appearance options specific to datatable metric columns."""

    summary_row: DatatableSummaryRowEnum | None = Field(default=None, strict=False)
    """Summary function to display at the bottom of the metric column."""

    summary_label: str | None = Field(default=None)
    """Custom label for the summary row."""

    color: DatatableMetricColor | None = Field(default=None)
    """Color display mode and optional range mapping."""


class DatatableColumnAppearanceMixin(BaseCfgModel):
    """Mixin that nests dimension appearance."""

    appearance: DatatableColumnAppearance | None = Field(default=None)
    """Presentation options for this dimension."""


class DatatableMetricAppearanceMixin(BaseCfgModel):
    """Mixin that nests metric appearance."""

    appearance: DatatableMetricAppearance | None = Field(default=None)
    """Presentation options for this metric."""
