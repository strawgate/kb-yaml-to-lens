from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.charts.lens.dimensions.config import CollapseAggregationEnum
from dashboard_compiler.shared.config import BaseCfgModel

type ESQLColumnTypes = ESQLDimension | ESQLMetric | ESQLStaticValue

type ESQLDimensionTypes = ESQLDimension

type ESQLMetricTypes = ESQLMetric | ESQLStaticValue

type ESQLMetricFormatTypes = ESQLMetricFormat | ESQLCustomMetricFormat


class ESQLMetricFormat(BaseCfgModel):
    """The format configuration for ES|QL metrics.

    Supports standard format types like number, bytes, bits, percent, and duration.
    This is separate from LensMetricFormat as ES|QL and Lens formatting may diverge in the future.
    """

    type: Literal['number', 'bytes', 'bits', 'percent', 'duration']

    suffix: str | None = Field(default=None)
    """The suffix to display after the number."""

    compact: bool | None = Field(default=None)
    """Whether to display the number in a compact format."""

    pattern: str | None = Field(default=None)
    """The pattern to display the number in."""


class ESQLCustomMetricFormat(BaseCfgModel):
    """Custom format configuration for ES|QL metrics.

    Allows specifying a custom number format pattern.
    This is separate from LensCustomMetricFormat as ES|QL and Lens formatting may diverge in the future.
    """

    type: Literal['custom'] = 'custom'

    pattern: str = Field(...)
    """The pattern to display the number in."""


class BaseESQLColumn(BaseCfgModel):
    """A base class for ESQL columns."""

    id: str | None = Field(default=None)
    """A unique identifier for the column. If not provided, one may be generated during compilation."""


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

    label: str | None = Field(default=None)
    """Optional display label for the metric."""

    format: ESQLMetricFormatTypes | None = Field(default=None)
    """The format of the metric (number, bytes, bits, percent, duration, or custom)."""


class ESQLStaticValue(BaseESQLColumn):
    """A static numeric value metric for ESQL charts.

    Used to display a fixed numeric value rather than querying from data.
    Commonly used for gauge min/max/goal values or reference lines.
    """

    value: int | float = Field(...)
    """The static numeric value to display."""

    label: str | None = Field(default=None)
    """Optional label for the static value."""
