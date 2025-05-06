from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLFieldDimensionColumn, KbnESQLFieldMetricColumn
from dashboard_compiler.shared.config import random_id_generator, stable_id_generator


def compile_esql_metric(metric: ESQLMetricTypes) -> KbnESQLFieldMetricColumn:
    """Compile a single ESQLMetricTypes object into its Kibana view model.

    Args:
        metric (ESQLMetricTypes): The ESQLMetricTypes object to compile.

    Returns:
        tuple[str, KbnLensColumnTypes]: A tuple containing the metric ID and its compiled KbnLensColumnTypes.

    """
    metric_id = metric.id or stable_id_generator([metric.field])

    return KbnESQLFieldMetricColumn(
        fieldName=metric.field,
        columnId=metric_id,
    )


def compile_esql_metrics(metrics: list[ESQLMetricTypes]) -> list[KbnESQLFieldMetricColumn]:
    """Compile a list of ESQLMetricTypes into their Kibana view model representation.

    Args:
        metrics (list[ESQLMetricTypes]): The list of ESQLMetricTypes objects to compile.

    Returns:
        list[KbnESQLFieldMetricColumn]: A list of compiled KbnESQLFieldMetricColumn objects.

    """
    return [compile_esql_metric(metric) for metric in metrics]


def compile_esql_dimension(dimension: ESQLDimensionTypes) -> KbnESQLFieldDimensionColumn:
    """Compile a single ESQLDimensionTypes object into its Kibana view model.

    Args:
        dimension (ESQLDimensionTypes): The ESQLDimensionTypes object to compile.

    Returns:
        KbnESQLFieldDimensionColumn: The compiled Kibana view model.

    """
    dimension_id = dimension.id or random_id_generator()

    return KbnESQLFieldDimensionColumn(
        fieldName=dimension.field,
        columnId=dimension_id,
    )


def compile_esql_dimensions(dimensions: list[ESQLDimensionTypes]) -> list[KbnESQLFieldDimensionColumn]:
    """Compile a list of ESQLDimensionTypes objects into their Kibana view model representation.

    Args:
        dimensions (list[ESQLDimensionTypes]): The list of ESQLDimensionTypes objects to compile.

    Returns:
        list[KbnESQLFieldDimensionColumn]: The compiled Kibana view model.

    """
    return [compile_esql_dimension(dimension) for dimension in dimensions]
