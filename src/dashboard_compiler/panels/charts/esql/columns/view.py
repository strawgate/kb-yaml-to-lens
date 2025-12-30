from typing import Annotated, Literal

from pydantic import Field

from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone


class KbnESQLColumnMeta(BaseVwModel):
    """Metadata for ES|QL columns."""

    type: Annotated[Literal['number', 'string', 'date', 'boolean'] | None, OmitIfNone()] = Field(default=None)
    """The data type of the column."""

    esType: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The Elasticsearch field type."""


class KbnESQLFieldDimensionColumn(BaseVwModel):
    """Represents a field-sourced ESQL column in the Kibana JSON structure."""

    fieldName: str
    """The field that this column is based on."""

    columnId: str
    """The ID of the column."""

    meta: Annotated[KbnESQLColumnMeta | None, OmitIfNone()] = Field(default=None)
    """Optional metadata about the column type."""


class KbnESQLFieldMetricColumn(BaseVwModel):
    """Represents a field-sourced ESQL column in the Kibana JSON structure."""

    fieldName: str
    """The field that this column is based on."""

    columnId: str
    """The ID of the column."""

    meta: Annotated[KbnESQLColumnMeta | None, OmitIfNone()] = Field(default=None)
    """Optional metadata about the column type."""


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
