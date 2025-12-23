from pydantic import Field

from dashboard_compiler.panels.charts.lens.dimensions.config import CollapseAggregationEnum
from dashboard_compiler.shared.config import BaseIdentifiableComponent

type ESQLColumnTypes = ESQLDimension | ESQLMetric

type ESQLDimensionTypes = ESQLDimension

type ESQLMetricTypes = ESQLMetric


class BaseESQLColumn(BaseIdentifiableComponent):
    """A base class for ESQL columns."""


class ESQLDimension(BaseESQLColumn):
    """A dimension that is defined in the ESQL query."""

    field: str = Field(default=...)
    """The field to use for the dimension."""

    collapse: CollapseAggregationEnum | None = Field(default=None, strict=False)
    """The collapse function to apply to this dimension (sum, avg, min, max)."""


class ESQLMetric(BaseESQLColumn):
    """A metric that is defined in the ESQL query."""

    field: str = Field(default=...)
    """The field in the data view that this metric is based on."""
