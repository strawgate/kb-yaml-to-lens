"""Lens dimensions configuration for the Lens chart."""

from enum import StrEnum
from typing import Literal

from pydantic import Field

from dashboard_compiler.queries.types import LegacyQueryTypes
from dashboard_compiler.shared.config import BaseCfgModel, Sort

type LensDimensionTypes = (
    LensTermsDimension | LensMultiTermsDimension | LensDateHistogramDimension | LensFiltersDimension | LensIntervalsDimension
)


class BaseDimension(BaseCfgModel):
    """Base model for defining dimensions."""

    id: str | None = Field(default=None)
    """A unique identifier for the dimension. If not provided, one may be generated during compilation."""

    # color: ColorMapping | None = Field(default=None)


class CollapseAggregationEnum(StrEnum):
    """The aggregation to use for the dimension."""

    SUM = 'sum'
    MIN = 'min'
    MAX = 'max'
    AVG = 'avg'


class BaseLensDimension(BaseDimension):
    """Base model for defining dimensions within a Lens chart."""

    label: str | None = Field(default=None)
    """The display label for the dimension. If not provided, a label may be inferred from the field and type."""


class LensFiltersDimensionFilter(BaseCfgModel):
    """A filter for a filters dimension."""

    query: LegacyQueryTypes = Field(default=...)
    """The query to use for the dimension."""

    label: str | None = Field(default=None)
    """The display label for the filter. If not provided, the query will be used as the label."""


class LensFiltersDimension(BaseLensDimension):
    """Represents a filters dimension configuration within a Lens chart.

    Filters dimensions are used for filtering data based on a field.
    """

    type: Literal['filters'] = 'filters'

    filters: list[LensFiltersDimensionFilter] = Field(default=...)
    """The filters to use for the dimension."""

    collapse: CollapseAggregationEnum | None = Field(default=None, strict=False)
    """The collapse function to apply to this dimension (sum, avg, min, max)."""


class LensIntervalsDimensionInterval(BaseCfgModel):
    """A single interval for an intervals dimension."""

    from_value: int | None = Field(default=None, alias='from')
    """The start of the interval."""

    to_value: int | None = Field(default=None, alias='to')
    """The end of the interval."""

    label: str | None = Field(default=None)
    """The label for the interval."""


class LensIntervalsDimension(BaseLensDimension):
    """Represents an intervals dimension configuration within a Lens chart.

    Intervals dimensions are used for aggregating data based on numeric ranges.
    """

    type: Literal['intervals'] = 'intervals'

    field: str = Field(default=...)
    """The name of the field in the data view that this dimension is based on."""

    intervals: list[LensIntervalsDimensionInterval] | None = Field(default=None)
    """The intervals to use for the dimension. If not provided, intervals will be automatically picked."""

    granularity: int | None = Field(default=None, ge=1, le=7)
    """Interval granularity divides the field into evenly spaced intervals based on the minimum and maximum values for the field.
    Kibana defaults to 4 if not specified."""

    collapse: CollapseAggregationEnum | None = Field(default=None, strict=False)
    """The collapse function to apply to this dimension (sum, avg, min, max)."""

    empty_bucket: bool | None = Field(default=None)
    """If `true`, show a bucket for documents with a missing value for the field. Defaults to `false`."""


class BaseLensTermsDimension(BaseLensDimension):
    """Base class for top values dimensions (single and multi-field).

    Contains all common configuration fields for terms-based dimensions.
    """

    type: Literal['values'] = 'values'

    size: int | None = Field(default=None)
    """The number of top terms to display."""

    sort: Sort | None = Field(default=None)
    """The sort configuration for the terms."""

    other_bucket: bool | None = Field(default=None)
    """If `true`, show a bucket for terms not included in the top size. Defaults to `false`."""

    missing_bucket: bool | None = Field(default=None)
    """If `true`, show a bucket for documents with a missing value for the field. Defaults to `false`."""

    include: list[str] | None = Field(default=None)
    """A list of terms to include. Can be used with or without `include_is_regex`."""

    exclude: list[str] | None = Field(default=None)
    """A list of terms to exclude. Can be used with or without `exclude_is_regex`."""

    include_is_regex: bool | None = Field(default=None)
    """If `true`, treat the values in the `include` list as regular expressions. Defaults to `false`."""

    exclude_is_regex: bool | None = Field(default=None)
    """If `true`, treat the values in the `exclude` list as regular expressions. Defaults to `false`."""

    collapse: CollapseAggregationEnum | None = Field(default=None, strict=False)
    """The collapse function to apply to this dimension (sum, avg, min, max)."""


class LensTermsDimension(BaseLensTermsDimension):
    """Represents a single-field top values dimension configuration within a Lens chart.

    Terms dimensions are used for aggregating data based on unique values of a single field.
    """

    field: str = Field(default=...)
    """The name of the field in the data view that this dimension is based on."""


class LensMultiTermsDimension(BaseLensTermsDimension):
    """Represents a multi-field top values dimension configuration within a Lens chart.

    Multi-terms dimensions are used for aggregating data based on unique combinations
    of values across multiple fields.
    """

    fields: list[str] = Field(default=..., min_length=2)
    """List of field names for multi-field aggregation. Requires at least 2 fields."""


class LensDateHistogramDimension(BaseLensDimension):
    """Represents a histogram dimension configuration within a Lens chart.

    Date histogram dimensions are used for aggregating data into buckets based on numeric ranges.
    """

    type: Literal['date_histogram'] = 'date_histogram'

    field: str = Field(default=...)
    """The name of the field in the data view that this dimension is based on."""

    minimum_interval: str | None = Field(default=None)
    """The numeric interval for the histogram buckets. Defaults to `auto` if not specified."""

    partial_intervals: bool | None = Field(default=None)
    """If `true`, show partial intervals. Kibana defaults to `true` if not specified."""

    collapse: CollapseAggregationEnum | None = Field(default=None, strict=False)
    """The collapse function to apply to this dimension (sum, avg, min, max)."""
