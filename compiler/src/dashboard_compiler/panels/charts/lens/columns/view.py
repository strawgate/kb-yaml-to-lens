from typing import Annotated, Any, Literal

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
    | KbnLensCustomIntervalsDimensionColumn
)

type KbnLensMetricColumnTypes = (
    KbnLensFieldMetricColumn
    | KbnLensStaticValueColumn
    | KbnLensFormulaColumn
    | KbnLensMathColumn
    | KbnLensFormulaAggColumn
    | KbnLensFullReferenceColumn
)

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


class KbnLensFormulaColumnParams(BaseVwModel):
    """Parameters for formula columns."""

    formula: str
    """The raw formula string to be evaluated."""

    isFormulaBroken: bool = False
    """Whether the formula has syntax errors."""

    format: Annotated[KbnLensMetricFormat | None, OmitIfNone()] = Field(default=None)
    """Optional format for the formula result."""


class KbnLensFormulaColumn(KbnLensBaseColumn):
    """Represents a formula Lens column.

    Formula columns allow for custom calculations using Kibana's formula syntax.
    Kibana parses the formula string and generates the necessary AST internally.
    """

    operationType: Literal['formula']
    """Always 'formula' for formula columns."""

    dataType: Literal['number']
    """Data type is always 'number' for formulas."""

    isBucketed: Literal[False] = False
    """Formulas are never bucketed."""

    scale: Literal['ratio']
    """Scale is always 'ratio' for formula results."""

    params: KbnLensFormulaColumnParams
    """Parameters containing the formula string."""

    references: list[str] = Field(default_factory=list)
    """List of referenced column IDs. Points to the math column for complete formulas."""


class KbnLensMathColumnParams(BaseVwModel):
    """Parameters for math columns used in formula helper structures."""

    tinymathAst: dict[str, Any]
    """The TinyMath AST structure representing the mathematical expression."""


class KbnLensMathColumn(KbnLensBaseColumn):
    """Represents a math column used in formula helper structures.

    Math columns contain the tinymathAST that combines aggregation columns
    into the final formula result. They reference the aggregation helper columns.
    """

    operationType: Literal['math']
    """Always 'math' for math columns."""

    dataType: Literal['number']
    """Data type is always 'number' for math operations."""

    isBucketed: Literal[False] = False
    """Math columns are never bucketed."""

    scale: Literal['ratio']
    """Scale is always 'ratio' for math results."""

    params: KbnLensMathColumnParams
    """Parameters containing the tinymathAst."""

    references: list[str] = Field(default_factory=list)
    """List of referenced aggregation column IDs."""


class KbnLensFormulaAggColumnParams(BaseVwModel):
    """Parameters for formula aggregation helper columns."""

    emptyAsNull: bool = False
    """Whether to treat empty results as null."""

    shift: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Time shift for the aggregation (e.g., '1d', '1w')."""

    reducedTimeRange: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Reduced time range for the aggregation (e.g., '1h', '1d')."""


class KbnLensFormulaAggColumn(KbnLensBaseColumn):
    """Represents an aggregation helper column used in formula structures.

    These columns are generated for each aggregation function (average, sum, count, etc.)
    found in a formula. They serve as intermediate columns that the math column references.
    """

    sourceField: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The field being aggregated (None for count without field)."""

    dataType: Literal['number']
    """Data type is always 'number' for aggregations."""

    isBucketed: Literal[False] = False
    """Aggregation columns are never bucketed."""

    scale: Literal['ratio']
    """Scale is always 'ratio' for aggregation results."""

    params: KbnLensFormulaAggColumnParams
    """Parameters for the aggregation column."""


class KbnLensFullReferenceColumnParams(BaseVwModel):
    """Parameters for fullReference operation columns."""

    emptyAsNull: bool = False
    """Whether to treat empty results as null."""

    window: Annotated[int | None, OmitIfNone()] = Field(default=None)
    """Window size for moving_average operations."""


class KbnLensFullReferenceColumn(KbnLensBaseColumn):
    """Represents a fullReference operation column used in formula structures.

    FullReference operations (counter_rate, cumulative_sum, differences, moving_average,
    normalize, time_scale) wrap other columns rather than operating on fields directly.
    They reference aggregation columns and apply time-series transformations.
    """

    dataType: Literal['number']
    """Data type is always 'number' for fullReference operations."""

    isBucketed: Literal[False] = False
    """FullReference columns are never bucketed."""

    scale: Literal['ratio']
    """Scale is always 'ratio' for fullReference results."""

    params: KbnLensFullReferenceColumnParams
    """Parameters for the fullReference column."""

    references: list[str] = Field(default_factory=list)
    """List of referenced column IDs that this operation wraps."""

    timeScale: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Time scale for rate calculations (e.g., 's' for per-second rates)."""


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

    id: Literal['terms', 'multi_terms'] = Field(default='terms')
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
    secondaryFields: Annotated[list[str] | None, OmitIfNone()] = Field(default=None)
    """Additional fields for multi-term aggregations (2nd, 3rd, etc.)."""


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


class KbnLensCustomIntervalsDimensionColumnParams(KbnLensDimensionColumnParams):
    """Parameters for custom intervals dimension columns."""

    type: Literal['range'] = Field(default='range')
    ranges: list[KbnLensIntervalsRange]
    maxBars: Annotated[str | float | None, OmitIfNone()] = Field(default=None)
    parentFormat: Annotated[KbnLensCustomIntervalsDimensionColumnParentFormat | None, OmitIfNone()] = Field(default=None)


class KbnLensCustomIntervalsDimensionColumn(KbnLensBaseDimensionColumn):
    """Represents a custom intervals dimension column."""

    sourceField: str
    operationType: Literal['range'] = Field(default='range')
    dataType: Literal['string'] = Field(default='string')
    scale: Literal['ordinal'] = Field(default='ordinal')
    isBucketed: Literal[True] = Field(default=True)
    params: KbnLensCustomIntervalsDimensionColumnParams
