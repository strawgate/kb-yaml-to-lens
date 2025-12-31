from typing import Annotated, Literal

from pydantic import Field

from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone


class KbnESQLMetaType(BaseVwModel):
    """Represents column metadata in the Kibana JSON structure."""

    type: Literal['number', 'string', 'date', 'boolean']
    """The data type of the column."""


class KbnESQLFieldDimensionColumn(BaseVwModel):
    """Represents a field-sourced ESQL column in the Kibana JSON structure."""

    fieldName: str
    """The field that this column is based on."""

    columnId: str
    """The ID of the column."""


class KbnESQLFieldMetricColumn(BaseVwModel):
    """Represents a field-sourced ESQL column in the Kibana JSON structure."""

    fieldName: str
    """The field that this column is based on."""

    columnId: str
    """The ID of the column."""

    meta: Annotated[KbnESQLMetaType | None, OmitIfNone()] = Field(default=None)
    """Column metadata (type information)."""

    inMetricDimension: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    """Whether this column should be treated as a metric dimension."""


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
