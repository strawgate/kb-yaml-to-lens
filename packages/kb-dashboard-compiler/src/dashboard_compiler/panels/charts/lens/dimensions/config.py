"""Lens dimensions configuration for the Lens chart."""

from enum import StrEnum
from typing import Literal

from pydantic import Field

from dashboard_compiler.queries.types import LegacyQueryTypes
from dashboard_compiler.shared.config import BaseCfgModel, BaseIdentifiableModel, Sort

type LensDimensionTypes = (
    LensTermsDimension | LensMultiTermsDimension | LensDateHistogramDimension | LensFiltersDimension | LensIntervalsDimension
)


class BaseDimension(BaseIdentifiableModel):
    """Base model for dimensions."""


class CollapseAggregationEnum(StrEnum):
    """Collapse aggregation options."""

    SUM = 'sum'
    MIN = 'min'
    MAX = 'max'
    AVG = 'avg'


class BaseLensDimension(BaseDimension):
    """Base model for Lens dimensions."""

    label: str | None = Field(default=None)
    """Display label (inferred from field if not provided)."""


class LensFiltersDimensionFilter(BaseCfgModel):
    """A filter bucket in a filters dimension."""

    query: LegacyQueryTypes = Field(default=...)
    """The KQL/Lucene query for this bucket."""

    label: str | None = Field(default=None)
    """Display label (query string used if not provided)."""


class LensFiltersDimension(BaseLensDimension):
    """Filters dimension - buckets defined by KQL/Lucene queries."""

    type: Literal['filters'] = 'filters'

    filters: list[LensFiltersDimensionFilter] = Field(default=...)
    """Filter definitions for each bucket."""

    collapse: CollapseAggregationEnum | None = Field(default=None, strict=False)
    """Collapse function for stacked charts (sum, avg, min, max)."""


class LensIntervalsDimensionInterval(BaseCfgModel):
    """A single range in an intervals dimension."""

    from_value: int | None = Field(default=None, alias='from')
    """Interval start (inclusive)."""

    to_value: int | None = Field(default=None, alias='to')
    """Interval end (exclusive)."""

    label: str | None = Field(default=None)
    """Display label for this interval."""


class LensIntervalsDimension(BaseLensDimension):
    """Intervals dimension - numeric range buckets."""

    type: Literal['intervals'] = 'intervals'

    field: str = Field(default=...)
    """Field to create intervals from."""

    intervals: list[LensIntervalsDimensionInterval] | None = Field(default=None)
    """Custom intervals. If not provided, auto-generated based on granularity."""

    granularity: int | None = Field(default=None, ge=1, le=7)
    """Auto-interval granularity (1=coarse, 7=fine). Kibana defaults to 4."""

    collapse: CollapseAggregationEnum | None = Field(default=None, strict=False)
    """Collapse function for stacked charts (sum, avg, min, max)."""

    empty_bucket: bool | None = Field(default=None)
    """Show bucket for missing values. Defaults to false."""


class BaseLensTermsDimension(BaseLensDimension):
    """Base class for top values dimensions."""

    type: Literal['values'] = 'values'

    size: int | None = Field(default=None)
    """Number of top terms to display."""

    sort: Sort | None = Field(default=None)
    """Sort configuration."""

    other_bucket: bool | None = Field(default=None)
    """Show 'Other' bucket for remaining terms. Defaults to false."""

    missing_bucket: bool | None = Field(default=None)
    """Show bucket for missing values. Defaults to false."""

    include: list[str] | None = Field(default=None)
    """Terms to include (exact or regex)."""

    exclude: list[str] | None = Field(default=None)
    """Terms to exclude (exact or regex)."""

    include_is_regex: bool | None = Field(default=None)
    """Treat include values as regex. Defaults to false."""

    exclude_is_regex: bool | None = Field(default=None)
    """Treat exclude values as regex. Defaults to false."""

    collapse: CollapseAggregationEnum | None = Field(default=None, strict=False)
    """Collapse function for stacked charts (sum, avg, min, max)."""


class LensTermsDimension(BaseLensTermsDimension):
    """Top values dimension - single field."""

    field: str = Field(default=...)
    """Field to get top values from."""


class LensMultiTermsDimension(BaseLensTermsDimension):
    """Top values dimension - multiple fields (multi-terms aggregation)."""

    fields: list[str] = Field(default=..., min_length=2)
    """Fields for multi-term aggregation (minimum 2)."""


class LensDateHistogramDimension(BaseLensDimension):
    """Date histogram dimension - time-based buckets."""

    type: Literal['date_histogram'] = 'date_histogram'

    field: str = Field(default=...)
    """Date field to bucket."""

    minimum_interval: str | None = Field(default=None)
    """Minimum bucket interval (e.g., '1h', '1d'). Defaults to 'auto'."""

    partial_intervals: bool | None = Field(default=None)
    """Include partial time buckets. Kibana defaults to true."""

    collapse: CollapseAggregationEnum | None = Field(default=None, strict=False)
    """Collapse function for stacked charts (sum, avg, min, max)."""
