"""Lens breakdown types for use in chart breakdowns fields.

Breakdowns slice data into categories (pie slices, treemap hierarchy,
waffle sections, datatable row groupings). Unlike plain dimensions, breakdowns
support the ``collapse`` aggregation which merges multiple dimension values
into a single bucket using a summary function.
"""

from pydantic import Field

from kb_dashboard_core.panels.charts.lens.dimensions.config import (
    CollapseAggregationEnum,
    LensDateHistogramDimension,
    LensFiltersDimension,
    LensIntervalsDimension,
    LensMultiTermsDimension,
    LensTermsDimension,
)

type LensBreakdownTypes = (
    LensTermsBreakdown | LensMultiTermsBreakdown | LensDateHistogramBreakdown | LensFiltersBreakdown | LensIntervalsBreakdown
)


class LensTermsBreakdown(LensTermsDimension):
    """Top-values breakdown with optional collapse aggregation."""

    collapse: CollapseAggregationEnum | None = Field(default=None, strict=False)
    """Aggregate all breakdown values into a single bucket using this function (sum, avg, min, max)."""


class LensMultiTermsBreakdown(LensMultiTermsDimension):
    """Multi-field top-values breakdown with optional collapse aggregation."""

    collapse: CollapseAggregationEnum | None = Field(default=None, strict=False)
    """Aggregate all breakdown values into a single bucket using this function (sum, avg, min, max)."""


class LensDateHistogramBreakdown(LensDateHistogramDimension):
    """Date histogram breakdown with optional collapse aggregation."""

    collapse: CollapseAggregationEnum | None = Field(default=None, strict=False)
    """Aggregate all breakdown values into a single bucket using this function (sum, avg, min, max)."""


class LensFiltersBreakdown(LensFiltersDimension):
    """Filters breakdown with optional collapse aggregation."""

    collapse: CollapseAggregationEnum | None = Field(default=None, strict=False)
    """Aggregate all breakdown values into a single bucket using this function (sum, avg, min, max)."""


class LensIntervalsBreakdown(LensIntervalsDimension):
    """Intervals breakdown with optional collapse aggregation."""

    collapse: CollapseAggregationEnum | None = Field(default=None, strict=False)
    """Aggregate all breakdown values into a single bucket using this function (sum, avg, min, max)."""
