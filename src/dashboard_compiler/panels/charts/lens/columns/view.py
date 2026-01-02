from typing import Annotated, Literal

from pydantic import Field

from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone

type KbnColumnTypes = KbnLensColumnTypes | KbnESQLColumnTypes

type KbnLensDimensionColumnTypes = (
    KbnLensDateHistogramDimensionColumn
    | KbnLensTermsDimensionColumn
    | KbnLensFiltersDimensionColumn
    | KbnLensIntervalsDimensionColumn
    | KbnLensCustomInvervalsDimensionColumn
)

type KbnLensMetricColumnTypes = KbnLensFieldMetricColumn | KbnLensStaticValueColumn | KbnLensFormulaColumn | KbnLensMathColumn

type KbnLensMetricFormatTypes = KbnLensMetricFormat


type KbnLensColumnTypes = KbnLensDimensionColumnTypes | KbnLensMetricColumnTypes


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


class KbnLensStaticValueColumnParams(BaseVwModel):
    """Parameters for static value columns."""

    value: int | float | str
    """The static value - can be numeric (for gauge charts) or string (for reference lines)."""


class KbnLensStaticValueColumn(KbnLensBaseColumn):
    """Represents a static value Lens column (not sourced from a field).

    Used for displaying fixed numeric values in gauge charts (min/max/goal)
    or reference lines. The value is specified directly rather than aggregated
    from data.
    """

    operationType: Literal['static_value']
    """Always 'static_value' for static value columns."""

    dataType: Literal['number']
    """Data type is always 'number' for static values."""

    isBucketed: Literal[False] = False
    """Static values are never bucketed."""

    isStaticValue: Literal[True] = True
    """Marker to indicate this is a static value column."""

    scale: Literal['ratio']
    """Scale is always 'ratio' for numeric static values."""

    params: KbnLensStaticValueColumnParams
    """Parameters containing the static value."""

    references: list[str] = Field(default_factory=list)
    """List of referenced column IDs (typically empty for static values)."""


class KbnLensDimensionColumnParams(BaseVwModel):
    """Additional parameters for dimension columns."""


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


class KbnLensTermsOrderBy(BaseVwModel):
    """Represents the orderBy parameter for terms dimension columns."""

    type: Literal['column', 'alphabetical']
    columnId: Annotated[str | None, OmitIfNone()] = Field(default=None)
    fallback: Annotated[bool | None, OmitIfNone()] = Field(default=None)


class KbnLensTermsParentFormatParams(BaseVwModel):
    """The parameters for the parent format for terms dimension columns."""


class KbnLensTermsParentFormat(BaseVwModel):
    """The parent format for terms dimension columns."""

    id: Literal['terms'] = Field(default='terms')
    # params: KbnLensTermsParentFormatParams | None = Field(default


class KbnLensTermsDimensionColumnParams(KbnLensDimensionColumnParams):
    """Parameters for terms dimension columns."""

    size: Annotated[int | None, OmitIfNone()] = Field(default=None)
    orderBy: Annotated[KbnLensTermsOrderBy | None, OmitIfNone()] = Field(default=None)
    orderDirection: Annotated[str | None, OmitIfNone()] = Field(default=None)
    otherBucket: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    missingBucket: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    parentFormat: Annotated[KbnLensTermsParentFormat | None, OmitIfNone()] = Field(default=None)
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


class KbnLensFiltersFilter(BaseVwModel):
    """Represents a single filter within the filters dimension columns."""

    label: str
    input: KbnQuery


class KbnLensFiltersDimensionColumnParams(KbnLensDimensionColumnParams):
    """Parameters for filters dimension columns."""

    filters: list[KbnLensFiltersFilter]


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


class KbnLensIntervalsRange(BaseVwModel):
    """Represents a single range within the intervals dimension columns."""

    from_value: int | float | None = Field(default=None, serialization_alias='from')
    to_value: int | float | None = Field(default=None, serialization_alias='to')
    label: Annotated[str | None, OmitIfNone()] = Field(default=None)


class KbnLensIntervalsDimensionColumnParams(KbnLensDimensionColumnParams):
    """Parameters for intervals dimension columns."""

    includeEmptyRows: bool
    type: Literal['histogram'] = Field(default='histogram')
    ranges: list[KbnLensIntervalsRange]
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
    ranges: list[KbnLensIntervalsRange]
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


class KbnLensFormulaParams(BaseVwModel):
    """Parameters for formula columns."""

    formula: str
    """The human-readable formula string (for display purposes)."""

    isFormulaBroken: Literal[False] = False
    """Whether the formula is broken (always False for compiled formulas)."""

    format: Annotated[KbnLensMetricFormat | None, OmitIfNone()] = Field(default=None)
    """Optional format for the formula result."""


class KbnLensFormulaColumn(KbnLensBaseColumn):
    """Represents a formula column in Lens.

    Formula columns are the user-facing representation of formulas in Kibana.
    They reference math columns which contain the actual computation logic.
    """

    operationType: Literal['formula'] = 'formula'
    dataType: Literal['number'] = 'number'
    isBucketed: Literal[False] = False
    scale: Literal['ratio'] = 'ratio'
    params: KbnLensFormulaParams
    references: list[str]
    """List of referenced column IDs (typically the math column)."""


class KbnLensMathParams(BaseVwModel):
    """Parameters for math columns containing tinymathAst."""

    tinymathAst: dict[str, object]
    """The TinymathAST structure representing the mathematical expression."""


class KbnLensMathColumn(KbnLensBaseColumn):
    """Represents a math operation column in Lens.

    Math columns contain the actual computation logic via tinymathAst.
    They are helper columns referenced by formula columns.
    """

    operationType: Literal['math'] = 'math'
    dataType: Literal['number'] = 'number'
    isBucketed: Literal[False] = False
    scale: Literal['ratio'] = 'ratio'
    params: KbnLensMathParams
    references: list[str]
    """List of referenced column IDs (aggregation columns)."""
