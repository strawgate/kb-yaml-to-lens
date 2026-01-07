from typing import Annotated, Literal

from pydantic import Field

from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone


class KbnESQLMetricFormatParams(BaseVwModel):
    """The parameters of the format for ES|QL metrics."""

    decimals: int
    """The number of decimal places to display."""

    suffix: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The suffix to display after the number."""

    compact: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    """Whether to display the number in a compact format."""

    pattern: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The pattern to display the number in."""


class KbnESQLMetricFormat(BaseVwModel):
    """The format of the ES|QL metric column."""

    id: Literal['number', 'bytes', 'bits', 'percent', 'duration', 'custom']

    params: KbnESQLMetricFormatParams
    """The parameters of the format."""


type KbnESQLMetricFormatTypes = KbnESQLMetricFormat


class KbnESQLFieldDimensionColumn(BaseVwModel):
    """Represents a field-sourced ESQL column in the Kibana JSON structure."""

    fieldName: str
    """The field that this column is based on."""

    columnId: str
    """The ID of the column."""


class KbnESQLMetricColumnParams(BaseVwModel):
    """Parameters for ES|QL metric column formatting."""

    format: Annotated[KbnESQLMetricFormatTypes | None, OmitIfNone()] = None
    """The format configuration for this metric."""


class KbnESQLColumnMeta(BaseVwModel):
    """Metadata about an ES|QL column type."""

    type: Literal['number', 'string', 'date', 'boolean']
    """The data type of the column."""

    esType: Annotated[str | None, OmitIfNone()] = None
    """The Elasticsearch field type (optional, e.g., 'long', 'double')."""


class KbnESQLFieldMetricColumn(BaseVwModel):
    """Represents a field-sourced ESQL column in the Kibana JSON structure."""

    fieldName: str
    """The field that this column is based on."""

    columnId: str
    """The ID of the column."""

    label: Annotated[str | None, OmitIfNone()] = None
    """Display label for the column."""

    customLabel: Annotated[bool | None, OmitIfNone()] = None
    """Whether the label is customized."""

    meta: Annotated[KbnESQLColumnMeta | None, OmitIfNone()] = None
    """Type metadata for the column."""

    inMetricDimension: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    """Whether this column should be treated as a metric dimension."""

    params: Annotated[KbnESQLMetricColumnParams | None, OmitIfNone()] = None
    """Optional formatting parameters for the metric."""


class KbnESQLStaticValueColumn(BaseVwModel):
    """Represents a static value ESQL column.

    ESQL uses the same column structure as Lens for static values,
    storing the value in the column definition.
    """

    fieldName: str
    """Field name (for static values, this is typically the string representation of the value)."""

    columnId: str
    """The ID of the column."""


type KbnESQLColumnTypes = KbnESQLMetricColumnTypes | KbnESQLDimensionColumnTypes

type KbnESQLMetricColumnTypes = KbnESQLFieldMetricColumn | KbnESQLStaticValueColumn

type KbnESQLDimensionColumnTypes = KbnESQLFieldDimensionColumn
