"""Configuration for a Lens and ESQL Metric."""

from typing import Literal

from pydantic import Field

from dashboard_compiler.queries.types import LegacyQueryTypes
from dashboard_compiler.shared.config import BaseCfgModel


class BaseMetric(BaseCfgModel):
    """Base class for metric configurations in Lens charts."""

    id: str | None = Field(default=None)
    """A unique identifier for the metric. If not provided, one may be generated during compilation."""


class LensStaticValue(BaseMetric):
    """Represents a static numeric value metric in Lens charts.

    Used to display a fixed numeric value rather than aggregating from data.
    Commonly used for gauge min/max/goal values or reference lines.
    """

    value: int | float = Field(...)
    """The static numeric value to display."""

    label: str | None = Field(default=None)
    """Optional label for the static value."""


type LensMetricTypes = LensFormulaMetric | LensAggregatedMetricTypes | LensStaticValue

type LensMetricFormatTypes = LensMetricFormat | LensCustomMetricFormat


class LensMetricFormat(BaseCfgModel):
    """Standard format configuration for displaying metric values.

    Supports common numeric formats with optional suffix, compact notation, and custom patterns.
    """

    type: Literal['number', 'bytes', 'bits', 'percent', 'duration']
    """The format type for the metric value.

    Available formats:
    - **number**: Plain numeric value with optional decimal places
    - **bytes**: Byte size formatting (B, KB, MB, GB, TB)
    - **bits**: Bit size formatting (b, Kb, Mb, Gb, Tb)
    - **percent**: Percentage formatting with % symbol
    - **duration**: Time duration formatting (ms, s, m, h, d)
    """

    suffix: str | None = Field(default=None)
    """Optional suffix to display after the formatted number (e.g., " requests", " users")."""

    compact: bool | None = Field(default=None)
    """Whether to use compact notation (e.g., 1.2K instead of 1200). Defaults to Kibana's behavior."""

    pattern: str | None = Field(default=None)
    """Custom numeral.js format pattern (e.g., "0.00" for 2 decimal places, "0,0" for thousands separator)."""


class LensCustomMetricFormat(BaseCfgModel):
    """Custom format configuration for metrics using numeral.js patterns.

    Use this for complete control over numeric formatting with numeral.js syntax.
    """

    type: Literal['custom'] = 'custom'
    """Format type identifier. Must be 'custom' for custom formats."""

    pattern: str = Field(...)
    """numeral.js format pattern (e.g., "0,0.00" for comma-separated numbers with 2 decimals)."""


class BaseLensMetric(BaseMetric):
    """Base class for metric configurations in Lens charts."""

    label: str | None = Field(None)
    """The display label for the metric. If not provided, a label may be inferred from the type and field."""

    format: LensMetricFormatTypes | None = Field(default=None)
    """The format of the metric."""

    filter: LegacyQueryTypes | None = Field(default=None)
    """A KQL filter applied before determining the metric value."""


type LensAggregatedMetricTypes = (
    LensOtherAggregatedMetric
    | LensLastValueAggregatedMetric
    | LensCountAggregatedMetric
    | LensSumAggregatedMetric
    | LensPercentileRankAggregatedMetric
    | LensPercentileAggregatedMetric
)


class LensCountAggregatedMetric(BaseLensMetric):
    """Represents a count metric configuration within a Lens chart.

    Count metrics are used to count the number of documents in a data view.
    """

    aggregation: Literal['count', 'unique_count'] = 'count'

    field: str | None = Field(default=None)
    """The field to count. If not provided, the count will be of all documents in the data view."""

    exclude_zeros: bool | None = Field(default=None)
    """Whether to exclude zero values from the count. Kibana defaults to true if not specified."""


class LensSumAggregatedMetric(BaseLensMetric):
    """Represents a sum metric configuration within a Lens chart.

    Sum metrics are used to sum the values of a field.
    """

    aggregation: Literal['sum'] = 'sum'

    field: str = Field(...)

    exclude_zeros: bool | None = Field(default=None)
    """Whether to exclude zero values from the count. Kibana defaults to true if not specified."""


class LensOtherAggregatedMetric(BaseLensMetric):
    """Represents various aggregated metric configurations within a Lens chart."""

    aggregation: Literal['min', 'max', 'median', 'average'] = Field(...)
    """The aggregation type for the metric (e.g., 'min', 'max', 'median', 'average')."""

    field: str = Field(...)


class LensLastValueAggregatedMetric(BaseLensMetric):
    """Represents a last value metric configuration within a Lens chart.

    Last value metrics are used to retrieve the most recent value of a field based on a specified sort order.
    """

    aggregation: Literal['last_value'] = 'last_value'

    field: str = Field(...)

    date_field: str | None = Field(default=None)
    """The field used to determine the 'last' value."""

    # filter: str | None = Field(default=None)
    # """A KQL filter applied before determining the last value."""


class LensPercentileRankAggregatedMetric(BaseLensMetric):
    """Represents a percentile rank metric configuration within a Lens chart.

    Percentile rank metrics are used to determine the rank of a value in a data set.
    """

    aggregation: Literal['percentile_rank'] = 'percentile_rank'

    field: str = Field(...)

    rank: int = Field(...)


class LensPercentileAggregatedMetric(BaseLensMetric):
    """Represents a percentile metric configuration within a Lens chart.

    Percentile metrics are used to determine the value at a specific percentile in a data set.
    """

    aggregation: Literal['percentile'] = 'percentile'

    field: str = Field(...)

    percentile: int = Field(...)


class LensFormulaMetric(BaseLensMetric):
    """Represents a formula metric configuration within a Lens chart.

    Formula metrics allow for custom calculations using Kibana's formula syntax.
    The formula string is passed directly to Kibana, which handles parsing and
    AST generation internally.

    Example formulas:
    - Simple arithmetic: "count() / 100"
    - Field aggregations: "(max(field='response.time') - min(field='response.time')) / average(field='response.time')"
    - With filters: "count(kql='status:error') / count() * 100"
    """

    formula: str = Field(...)
    """The formula string to be evaluated for this metric."""
