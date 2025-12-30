from pydantic import Field

from dashboard_compiler.panels.charts.lens.dimensions.config import CollapseAggregationEnum
from dashboard_compiler.shared.config import BaseCfgModel

type ESQLColumnTypes = ESQLDimension | ESQLMetric | ESQLStaticValue

type ESQLDimensionTypes = ESQLDimension

type ESQLMetricTypes = ESQLMetric | ESQLStaticValue


class BaseESQLColumn(BaseCfgModel):
    """A base class for ESQL columns."""

    id: str | None = Field(default=None)
    """A unique identifier for the column. If not provided, one may be generated during compilation."""


class ESQLDimension(BaseESQLColumn):
    """A dimension that is defined in the ESQL query."""

    id: str | None = Field(default=None)
    """A unique identifier for the dimension. If not provided, one may be generated during compilation."""

    field: str = Field(default=...)
    """The field to use for the dimension."""

    collapse: CollapseAggregationEnum | None = Field(default=None, strict=False)
    """The collapse function to apply to this dimension (sum, avg, min, max)."""


class ESQLMetric(BaseESQLColumn):
    """A metric that is defined in the ESQL query."""

    field: str = Field(default=...)
    """The field in the data view that this metric is based on."""


class ESQLStaticValue(BaseESQLColumn):
    """A static numeric value metric for ESQL charts.

    Used to display a fixed numeric value rather than querying from data.
    Commonly used for gauge min/max/goal values or reference lines.
    """

    value: int | float = Field(...)
    """The static numeric value to display."""

    label: str | None = Field(default=None)
    """Optional label for the static value."""
