from typing import Annotated, Any, Literal

from pydantic import Field

from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone

type KbnColumnTypes = KbnLensColumnTypes | KbnESQLColumnTypes

type KbnLensColumnTypes = KbnLensMetricColumnTypes | KbnLensDimensionColumnTypes

type KbnLensDimensionColumnTypes = (
    KbnLensDateHistogramDimensionColumn | KbnLensTermsDimensionColumn | KbnLensFiltersDimensionColumn | KbnLensIntervalsDimensionColumn | KbnLensCustomInvervalsDimensionColumn
)

type KbnLensMetricColumnTypes = KbnLensFieldMetricColumn

type KbnLensMetricFormatTypes = KbnLensMetricFormat

type KbnESQLColumnTypes = KbnESQLFieldMetricColumn


class KbnLensMetricFormatParams(BaseVwModel):
    """The parameters of the format."""

    decimals: int
    """The number of decimal places to display."""

    suffix: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The suffix to display after the number."""

    compact: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    """Whether to display the number in a compact format."""

    pattern: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The pattern to display the number in."""


class KbnLensMetricFormat(BaseVwModel):
    """The format of the column."""

    id: Literal['number', 'bytes', 'bits', 'percent', 'duration', 'custom']

    params: KbnLensMetricFormatParams
    """The parameters of the format."""


class KbnLensBaseColumn(BaseVwModel):
    """Base class for column definitions in the Kibana JSON structure."""

    label: str
    """The display label for the column."""

    dataType: str
    """The data type of the column, such as 'date', 'number', 'string', etc."""

    customLabel: Annotated[bool | None, OmitIfNone()]
    """Whether the column has a custom label. Should be set to true if a custom label was provided."""

    operationType: str
    """The type of aggregation performed by the column, such as 'count', 'average', 'terms', etc."""

    isBucketed: bool = Field(default=False)
    """Whether the column is bucketed. Bucketed columns are used for grouping data, while non-bucketed columns are used for metrics."""

    filter: Annotated[KbnQuery | None, OmitIfNone()] = Field(default=None)

    scale: str
    """The scale of the column, such as 'ordinal', 'ratio', 'interval', etc."""


class KbnLensMetricColumnParams(BaseVwModel):
    """Additional parameters for metric columns."""

    format: Annotated[KbnLensMetricFormat | None, OmitIfNone()] = Field(default=None)

    emptyAsNull: Annotated[bool | None, OmitIfNone()] = Field(default=None)

    sortField: Annotated[str | None, OmitIfNone()] = Field(default=None)

    value: Annotated[int | None, OmitIfNone()] = Field(default=None)

    percentile: Annotated[int | None, OmitIfNone()] = Field(default=None)


class KbnLensFieldMetricColumn(KbnLensBaseColumn):
    """Represents a field-sourced Lens metric column."""

    sourceField: str
    """The field that this column is based on."""

    params: KbnLensMetricColumnParams
    """Additional parameters for the metric column."""


class KbnESQLFieldMetricColumn(BaseVwModel):
    """Represents a field-sourced ESQL column in the Kibana JSON structure."""

    fieldName: str
    """The field that this column is based on."""

    columnId: str
    """The ID of the column."""


# Dimension View Models


class KbnLensDimensionColumnParams(BaseVwModel):
    """Additional parameters for dimension columns."""

    # This will be a flexible model to accommodate different dimension types
    # We can add specific fields here as needed based on dimension types
    # For now, using Any as a placeholder


class KbnLensBaseDimensionColumn(KbnLensBaseColumn):
    """Base class for Lens dimension columns."""

    params: KbnLensDimensionColumnParams
    """Additional parameters for the dimension column."""


class KbnLensDateHistogramDimensionColumnParams(KbnLensDimensionColumnParams):
    """Parameters for date histogram dimension columns."""

    interval: str
    includeEmptyRows: bool
    dropPartials: bool


class KbnLensDateHistogramDimensionColumn(KbnLensBaseDimensionColumn):
    """Represents a date histogram dimension column."""

    sourceField: str
    operationType: Literal['date_histogram']
    dataType: Literal['date']
    scale: Literal['interval']
    isBucketed: Literal[True] = True
    params: KbnLensDateHistogramDimensionColumnParams


class KbnLensTermsDimensionColumnParams(KbnLensDimensionColumnParams):
    """Parameters for terms dimension columns."""

    size: Annotated[int | None, OmitIfNone()] = Field(default=None)
    orderBy: Annotated[dict[str, Any] | None, OmitIfNone()] = Field(default=None)  # TODO: Define a proper model for orderBy
    orderDirection: Annotated[str | None, OmitIfNone()] = Field(default=None)
    otherBucket: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    missingBucket: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    parentFormat: Annotated[dict[str, Any] | None, OmitIfNone()] = Field(default=None)  # TODO: Define a proper model for parentFormat
    include: Annotated[list[str] | None, OmitIfNone()] = Field(default=None)
    exclude: Annotated[list[str] | None, OmitIfNone()] = Field(default=None)
    includeIsRegex: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    excludeIsRegex: Annotated[bool | None, OmitIfNone()] = Field(default=None)


class KbnLensTermsDimensionColumn(KbnLensBaseDimensionColumn):
    """Represents a terms dimension column."""

    sourceField: str
    operationType: Literal['terms']
    dataType: Literal['string']
    scale: Literal['ordinal']
    isBucketed: Literal[True] = True
    params: KbnLensTermsDimensionColumnParams


class KbnLensFiltersDimensionColumnParams(KbnLensDimensionColumnParams):
    """Parameters for filters dimension columns."""

    filters: list[dict[str, Any]]  # TODO: Define a proper model for filters


class KbnLensFiltersDimensionColumn(KbnLensBaseDimensionColumn):
    """Represents a filters dimension column."""

    operationType: Literal['filters']
    dataType: Literal['string']
    scale: Literal['ordinal']
    isBucketed: Literal[True] = True
    params: KbnLensFiltersDimensionColumnParams

class KbnLensCustomIntervalsDimensionColumnParentFormatParams(BaseVwModel):
    """The parameters for the parent format for intervals dimension columns."""

    template: str
    replaceInfinity: bool

class KbnLensCustomIntervalsDimensionColumnParentFormat(BaseVwModel):
    """The parent format for intervals dimension columns."""

    id: Literal['range']
    params: KbnLensCustomIntervalsDimensionColumnParentFormatParams

class KbnLensIntervalsDimensionColumnParams(KbnLensDimensionColumnParams):
    """Parameters for intervals dimension columns."""

    includeEmptyRows: bool
    type: Literal['histogram'] = Field(default='histogram')
    ranges: list[dict[str, Any]]
    maxBars: Annotated[str | float | None, OmitIfNone()] = Field(default=None)
    parentFormat: Annotated[KbnLensCustomIntervalsDimensionColumnParentFormat | None, OmitIfNone()] = Field(default=None)


class KbnLensIntervalsDimensionColumn(KbnLensBaseDimensionColumn):
    """Represents an intervals dimension column."""

    sourceField: str
    operationType: Literal['range'] = Field(default='range')
    dataType: Literal['number'] = Field(default='number')
    scale: Literal['interval'] = Field(default='interval')
    isBucketed: Literal[True] = Field(default=True)
    params: KbnLensIntervalsDimensionColumnParams


class KbnLensCustomInvervalsDimensionColumnParams(KbnLensDimensionColumnParams):
    """Parameters for custom intervals dimension columns."""

    type: Literal['range'] = Field(default='range')
    ranges: list[dict[str, Any]]
    maxBars: Annotated[str | float | None, OmitIfNone()] = Field(default=None)
    parentFormat: Annotated[KbnLensCustomIntervalsDimensionColumnParentFormat | None, OmitIfNone()] = Field(default=None)


class KbnLensCustomInvervalsDimensionColumn(KbnLensBaseDimensionColumn):
    """Represents a custom intervals dimension column."""

    sourceField: str
    operationType: Literal['range'] = Field(default='range')
    dataType: Literal['string'] = Field(default='string')
    scale: Literal['ordinal'] = Field(default='ordinal')
    isBucketed: Literal[True] = Field(default=True)
    params: KbnLensCustomInvervalsDimensionColumnParams
