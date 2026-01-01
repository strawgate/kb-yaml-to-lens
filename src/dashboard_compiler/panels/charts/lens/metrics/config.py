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
    """The format of the metric."""

    type: Literal['number', 'bytes', 'bits', 'percent', 'duration']

    suffix: str | None = Field(default=None)
    """The suffix to display after the number."""

    compact: bool | None = Field(default=None)
    """Whether to display the number in a compact format."""

    pattern: str | None = Field(default=None)
    """The pattern to display the number in."""


class LensCustomMetricFormat(BaseCfgModel):
    """The format of the metric."""

    type: Literal['custom'] = 'custom'

    pattern: str = Field(...)
    """The pattern to display the number in."""


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


class LensFormulaAggregation(BaseCfgModel):
    """Parameters for an aggregation used in a Lens formula."""

    field: str | None = Field(default=None)
    """The field to aggregate. Optional for count aggregations."""

    filter: LegacyQueryTypes | None = Field(default=None)
    """A KQL/Lucene filter applied to the aggregation."""


class LensFormulaCountAgg(BaseCfgModel):
    """Represents a `count()` aggregation in a Lens formula."""

    count: LensFormulaAggregation = Field(default_factory=LensFormulaAggregation)
    """Parameters for the count aggregation."""


class LensFormulaUniqueCountAgg(BaseCfgModel):
    """Represents a `unique_count()` aggregation in a Lens formula.

    The field parameter is required for unique_count aggregations.
    """

    unique_count: LensFormulaAggregation = Field(...)
    """Parameters for the unique_count aggregation (field is required)."""


class LensFormulaSumAgg(BaseCfgModel):
    """Represents a `sum()` aggregation in a Lens formula."""

    sum: LensFormulaAggregation = Field(...)
    """Parameters for the sum aggregation."""


class LensFormulaAverageAgg(BaseCfgModel):
    """Represents an `average()` aggregation in a Lens formula."""

    average: LensFormulaAggregation = Field(...)
    """Parameters for the average aggregation."""


class LensFormulaMinAgg(BaseCfgModel):
    """Represents a `min()` aggregation in a Lens formula."""

    min: LensFormulaAggregation = Field(...)
    """Parameters for the min aggregation."""


class LensFormulaMaxAgg(BaseCfgModel):
    """Represents a `max()` aggregation in a Lens formula."""

    max: LensFormulaAggregation = Field(...)
    """Parameters for the max aggregation."""


class LensFormulaMedianAgg(BaseCfgModel):
    """Represents a `median()` aggregation in a Lens formula."""

    median: LensFormulaAggregation = Field(...)
    """Parameters for the median aggregation."""


type LensFormulaAggregations = (
    LensFormulaCountAgg
    | LensFormulaUniqueCountAgg
    | LensFormulaSumAgg
    | LensFormulaAverageAgg
    | LensFormulaMinAgg
    | LensFormulaMaxAgg
    | LensFormulaMedianAgg
)


class LensFormulaLeftRightOperation(BaseCfgModel):
    """Represents a binary formula operation with `left` and `right` operands."""

    left: 'LensFormulaOperations | LensFormulaAggregations' = Field(...)
    """The left operand of the operation."""

    right: 'LensFormulaOperations | LensFormulaAggregations' = Field(...)
    """The right operand of the operation."""


class LensFormulaAdd(BaseCfgModel):
    """Lens formula for adding two operands."""

    add: LensFormulaLeftRightOperation = Field(...)
    """Parameters for addition operation."""


class LensFormulaSubtract(BaseCfgModel):
    """Lens formula for subtracting two operands."""

    subtract: LensFormulaLeftRightOperation = Field(...)
    """Parameters for subtraction operation."""


class LensFormulaMultiply(BaseCfgModel):
    """Lens formula for multiplying two operands."""

    multiply: LensFormulaLeftRightOperation = Field(...)
    """Parameters for multiplication operation."""


class LensFormulaDivide(BaseCfgModel):
    """Lens formula for dividing two operands."""

    divide: LensFormulaLeftRightOperation = Field(...)
    """Parameters for division operation."""


type LensFormulaOperations = LensFormulaAdd | LensFormulaSubtract | LensFormulaMultiply | LensFormulaDivide | int | float


class LensFormulaMetric(BaseLensMetric):
    """Represents a formula metric configuration within a Lens chart.

    Formula metrics allow custom calculations using a custom domain-specific language (DSL).
    The DSL uses a structure similar to the filter DSL, making it easy to express formulas in YAML.
    """

    operation: LensFormulaOperations | LensFormulaAggregations = Field(..., alias='formula')
    """The root operation or aggregation of the formula."""
