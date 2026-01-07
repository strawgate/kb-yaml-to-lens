from collections.abc import Sequence

from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetric, ESQLMetricTypes, ESQLStaticValue
from dashboard_compiler.panels.charts.esql.columns.view import (
    KbnESQLFieldDimensionColumn,
    KbnESQLFieldMetricColumn,
    KbnESQLMetricColumnParams,
    KbnESQLMetricColumnTypes,
    KbnESQLStaticValueColumn,
)
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric_format
from dashboard_compiler.shared.config import get_layer_id, stable_id_generator


def compile_esql_metric(metric: ESQLMetricTypes) -> KbnESQLMetricColumnTypes:
    """Compile a single ESQLMetricTypes object into its Kibana view model.

    Args:
        metric (ESQLMetricTypes): The ESQLMetricTypes object to compile.

    Returns:
        KbnESQLMetricColumnTypes: The compiled Kibana column.

    """
    # Handle static values
    if isinstance(metric, ESQLStaticValue):
        metric_id = metric.id or stable_id_generator(['static_value', str(metric.value)])
        field_name = metric.label if metric.label is not None else str(metric.value)

        return KbnESQLStaticValueColumn(
            fieldName=field_name,
            columnId=metric_id,
        )

    # Handle regular field-based metrics (aggregations always return numbers in ES|QL)
    if not isinstance(metric, ESQLMetric):  # pyright: ignore[reportUnnecessaryIsInstance]
        msg = f'Unknown metric type: {type(metric).__name__}'
        raise TypeError(msg)  # pyright: ignore[reportUnreachable]

    metric_id = metric.id or stable_id_generator([metric.field])

    # Compile format if provided
    metric_format = compile_lens_metric_format(metric.format) if metric.format is not None else None

    # Create params only if format is present
    # Note: KbnLensMetricFormat and KbnESQLMetricFormat have identical structure, so cast is safe
    params = KbnESQLMetricColumnParams(format=metric_format) if metric_format is not None else None  # pyright: ignore[reportArgumentType]

    return KbnESQLFieldMetricColumn(
        fieldName=metric.field,
        columnId=metric_id,
        inMetricDimension=True,
        params=params,
    )


def compile_esql_metrics(metrics: Sequence[ESQLMetricTypes]) -> list[KbnESQLMetricColumnTypes]:
    """Compile a sequence of ESQLMetricTypes into their Kibana view model representation.

    Args:
        metrics (Sequence[ESQLMetricTypes]): The sequence of ESQLMetricTypes objects to compile.

    Returns:
        list[KbnESQLMetricColumnTypes]: A list of compiled metric columns (field-based or static values).

    """
    return [compile_esql_metric(metric) for metric in metrics]


def compile_esql_dimension(dimension: ESQLDimensionTypes) -> KbnESQLFieldDimensionColumn:
    """Compile a single ESQLDimensionTypes object into its Kibana view model.

    Args:
        dimension (ESQLDimensionTypes): The ESQLDimensionTypes object to compile.

    Returns:
        KbnESQLFieldDimensionColumn: The compiled Kibana view model.

    """
    dimension_id = get_layer_id(dimension)

    return KbnESQLFieldDimensionColumn(
        fieldName=dimension.field,
        columnId=dimension_id,
    )


def compile_esql_dimensions(dimensions: Sequence[ESQLDimensionTypes]) -> list[KbnESQLFieldDimensionColumn]:
    """Compile a sequence of ESQLDimensionTypes objects into their Kibana view model representation.

    Args:
        dimensions (Sequence[ESQLDimensionTypes]): The sequence of ESQLDimensionTypes objects to compile.

    Returns:
        list[KbnESQLFieldDimensionColumn]: The compiled Kibana view model.

    """
    return [compile_esql_dimension(dimension) for dimension in dimensions]
