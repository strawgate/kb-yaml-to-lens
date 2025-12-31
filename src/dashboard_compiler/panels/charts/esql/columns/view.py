from typing import Annotated

from pydantic import Field

from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone


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
