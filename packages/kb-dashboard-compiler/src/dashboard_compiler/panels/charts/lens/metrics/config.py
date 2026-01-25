"""Configuration for a Lens and ESQL Metric."""

from typing import Literal

from pydantic import Field

from dashboard_compiler.queries.types import LegacyQueryTypes
from dashboard_compiler.shared.config import BaseCfgModel, BaseIdentifiableModel


class BaseMetric(BaseIdentifiableModel):
    """Base class for metrics."""


class LensStaticValue(BaseMetric):
    """Static numeric value (for gauge min/max/goal or reference lines)."""

    value: int | float = Field(...)
    """The static value."""

    label: str | None = Field(default=None)
    """Display label."""


type LensMetricTypes = LensFormulaMetric | LensAggregatedMetricTypes | LensStaticValue

type LensMetricFormatTypes = LensMetricFormat | LensCustomMetricFormat


class LensMetricFormat(BaseCfgModel):
    """Metric format configuration.

    Format types: number, bytes, bits, percent, duration.
    """

    type: Literal['number', 'bytes', 'bits', 'percent', 'duration']
    """Format type."""

    decimals: int | None = Field(default=None, ge=0)
    """Decimal places. Defaults: 2 for number/bytes/percent, 0 for bits/duration."""

    suffix: str | None = Field(default=None)
    """Text appended to formatted value (e.g., ' req/s')."""

    compact: bool | None = Field(default=None)
    """Compact notation (e.g., 1.2K instead of 1200)."""

    pattern: str | None = Field(default=None)
    """numeral.js format pattern (e.g., '0,0.00')."""


class LensCustomMetricFormat(BaseCfgModel):
    """Custom format using numeral.js pattern."""

    type: Literal['custom'] = 'custom'

    decimals: int | None = Field(default=None, ge=0)
    """Decimal places. Defaults to 0."""

    pattern: str = Field(...)
    """numeral.js format pattern (e.g., '0,0.00')."""


class BaseLensMetric(BaseMetric):
    """Base class for Lens metrics."""

    label: str | None = Field(None)
    """Display label (inferred from aggregation/field if not provided)."""

    format: LensMetricFormatTypes | None = Field(default=None)
    """Value formatting."""

    filter: LegacyQueryTypes | None = Field(default=None)
    """KQL/Lucene filter applied before aggregation."""


type LensAggregatedMetricTypes = (
    LensOtherAggregatedMetric
    | LensLastValueAggregatedMetric
    | LensCountAggregatedMetric
    | LensSumAggregatedMetric
    | LensPercentileRankAggregatedMetric
    | LensPercentileAggregatedMetric
)


class LensCountAggregatedMetric(BaseLensMetric):
    """Count or unique count metric."""

    aggregation: Literal['count', 'unique_count'] = 'count'

    field: str | None = Field(default=None)
    """Field to count. If not provided, counts all documents."""

    exclude_zeros: bool | None = Field(default=None)
    """Exclude zero values. Kibana defaults to true."""


class LensSumAggregatedMetric(BaseLensMetric):
    """Sum metric."""

    aggregation: Literal['sum'] = 'sum'

    field: str = Field(...)

    exclude_zeros: bool | None = Field(default=None)
    """Exclude zero values. Kibana defaults to true."""


class LensOtherAggregatedMetric(BaseLensMetric):
    """Min, max, median, or average metric."""

    aggregation: Literal['min', 'max', 'median', 'average'] = Field(...)

    field: str = Field(...)


class LensLastValueAggregatedMetric(BaseLensMetric):
    """Last value metric (most recent by date)."""

    aggregation: Literal['last_value'] = 'last_value'

    field: str = Field(...)

    date_field: str | None = Field(default=None)
    """Date field for ordering. Defaults to @timestamp."""


class LensPercentileRankAggregatedMetric(BaseLensMetric):
    """Percentile rank metric (what % of values are below a given value)."""

    aggregation: Literal['percentile_rank'] = 'percentile_rank'

    field: str = Field(...)

    rank: int = Field(...)
    """The value to find the rank of."""


class LensPercentileAggregatedMetric(BaseLensMetric):
    """Percentile metric (value at a given percentile)."""

    aggregation: Literal['percentile'] = 'percentile'

    field: str = Field(...)

    percentile: int = Field(...)
    """Percentile to calculate (e.g., 95 for p95)."""


class LensFormulaMetric(BaseLensMetric):
    """Formula metric using Kibana formula syntax.

    Examples:
    - count() / 100
    - count(kql='status:error') / count() * 100
    - max(response.time) - min(response.time)
    """

    formula: str = Field(...)
    """The formula expression."""
