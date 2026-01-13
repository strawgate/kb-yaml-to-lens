"""Factory functions for ESQL text-based datasource layer construction."""

from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
from dashboard_compiler.panels.charts.view import KbnTextBasedDataSourceStateLayer
from dashboard_compiler.queries.compile import compile_esql_query
from dashboard_compiler.queries.types import ESQLQueryTypes


def compile_text_based_layer(
    query: ESQLQueryTypes,
    columns: list[KbnESQLColumnTypes],
    time_field: str,
) -> KbnTextBasedDataSourceStateLayer:
    """Construct a KbnTextBasedDataSourceStateLayer from compiled columns and query.

    This factory function centralizes layer construction for all ESQL-based chart types,
    handling query compilation internally.

    Args:
        query: The ESQL query configuration.
        columns: List of compiled ESQL column definitions.
        time_field: The time field for the datasource.

    Returns:
        KbnTextBasedDataSourceStateLayer with compiled query and columns.
    """
    return KbnTextBasedDataSourceStateLayer(
        query=compile_esql_query(query),
        columns=columns,
        allColumns=columns,
        timeField=time_field,
    )
