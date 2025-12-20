"""Configuration for a Lens and ESQL Metric."""

from typing import Literal

from pydantic import Field

from dashboard_compiler.queries.types import LegacyQueryTypes
from dashboard_compiler.shared.config import BaseCfgModel


class BaseMetric(BaseCfgModel):
    """Base class for metric configurations in Lens charts."""

    id: str | None = Field(default=None)
    """A unique identifier for the metric. If not provided, one may be generated during compilation."""


# class BaseMetricFormat(BaseCfgModel):
#     """Base class for metric format configurations in Lens charts."""


type LensMetricTypes = LensFormulaMetric | LensAggregatedMetricTypes

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

    aggregation: Literal['count', 'unique_count']

    field: str | None = Field(default=None)
    """The field to count. If not provided, the count will be of all documents in the data view."""

    exclude_zeros: bool | None = Field(default=None)
    """Whether to exclude zero values from the count. Kibana defaults to true if not specified."""


class LensSumAggregatedMetric(BaseLensMetric):
    """Represents a sum metric configuration within a Lens chart.

    Sum metrics are used to sum the values of a field.
    """

    aggregation: Literal['sum']

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


type LensFormulaAggregations = LensFormulaMinAgg | LensFormulaMaxAgg | LensFormulaSumAgg

type LensFormulaOperations = LensFormulaSubtract | LensFormulaAdd | LensFormulaDivide | LensFormulaMultiply | int | float


class LensFormulaMetric(BaseLensMetric):
    """Represents a formula metric configuration within a Lens chart.

    Formula metrics allow for custom calculations based on other fields or metrics.
    """

    formula: str = Field(...)
    """The formula string to be evaluated for this metric."""


class LensFormulaLeftRightOperation(BaseCfgModel):
    """Represents a binary formula operation with `left` and `right` operands."""

    left: LensFormulaOperations | LensFormulaAggregations = Field(...)
    right: LensFormulaOperations | LensFormulaAggregations = Field(...)


class LensFormulaAggregation(BaseCfgModel):
    """Represents an aggregation used as an operand in a Lens formula."""

    field: str = Field(...)
    kql: str | None = Field(...)
    lucene: str | None = Field(...)


class LensFormulaMinAgg(BaseCfgModel):
    """Represents a `min()` aggregation in a Lens formula."""

    min: LensFormulaAggregation = Field(...)


class LensFormulaMaxAgg(BaseCfgModel):
    """Represents a `max()` aggregation in a Lens formula."""

    max: LensFormulaAggregation = Field(...)


class LensFormulaSumAgg(BaseCfgModel):
    """Represents a `sum()` aggregation in a Lens formula."""

    sum: LensFormulaAggregation = Field(...)


class LensFormulaCountAgg(BaseCfgModel):
    """Represents a `count()` aggregation in a Lens formula."""

    count: LensFormulaAggregation = Field(...)


class LensFormulaUniqueCountAgg(BaseCfgModel):
    """Represents a `unique_count()` aggregation in a Lens formula."""

    unique_count: LensFormulaAggregation = Field(...)


class LensFormulaAverageAgg(BaseCfgModel):
    """Represents an `average()` aggregation in a Lens formula."""

    average: LensFormulaAggregation = Field(...)


class LensFormulaLastCountAgg(BaseCfgModel):
    """Represents a `last_count()` aggregation in a Lens formula."""

    last_count: LensFormulaAggregation = Field(...)


class LensFormulaSubtract(BaseCfgModel):
    """Lens formula for subtracting two operands."""

    subtract: LensFormulaLeftRightOperation = Field(...)


class LensFormulaAdd(BaseCfgModel):
    """Lens formula for adding two operands."""

    add: LensFormulaLeftRightOperation = Field(...)


class LensFormulaMultiply(BaseCfgModel):
    """Lens formula for multiplying two operands."""

    multiply: LensFormulaLeftRightOperation = Field(...)


class LensFormulaDivide(BaseCfgModel):
    """Lens formula for dividing two operands."""

    divide: LensFormulaLeftRightOperation = Field(...)
