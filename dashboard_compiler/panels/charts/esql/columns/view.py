from dashboard_compiler.shared.view import BaseVwModel


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


type KbnESQLColumnTypes = KbnESQLMetricColumnTypes | KbnESQLDimensionColumnTypes

type KbnESQLMetricColumnTypes = KbnESQLFieldMetricColumn

type KbnESQLDimensionColumnTypes = KbnESQLFieldDimensionColumn
