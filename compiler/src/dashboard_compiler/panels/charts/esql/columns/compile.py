from collections.abc import Sequence

from dashboard_compiler.panels.charts.esql.columns.config import (
    ESQLCustomMetricFormat,
    ESQLDimensionTypes,
    ESQLMetric,
    ESQLMetricFormat,
    ESQLMetricFormatTypes,
    ESQLMetricTypes,
    ESQLStaticValue,
)
from dashboard_compiler.panels.charts.esql.columns.view import (
    KbnESQLColumnMeta,
    KbnESQLFieldDimensionColumn,
    KbnESQLFieldMetricColumn,
    KbnESQLMetricColumnParams,
    KbnESQLMetricColumnTypes,
    KbnESQLMetricFormat,
    KbnESQLMetricFormatParams,
    KbnESQLStaticValueColumn,
)


def compile_esql_metric_format(metric_format: ESQLMetricFormatTypes) -> KbnESQLMetricFormat:
    """Compile ES|QL metric format configuration to Kibana view model.

    Args:
        metric_format (ESQLMetricFormatTypes): The ES|QL metric format configuration.

    Returns:
        KbnESQLMetricFormat: The compiled Kibana format view model.

    """
    # Determine default decimals based on format type
    if isinstance(metric_format, ESQLCustomMetricFormat):
        format_id = 'custom'
        decimals = 0
        pattern = metric_format.pattern
        suffix = None
        compact = None
    elif isinstance(metric_format, ESQLMetricFormat):  # pyright: ignore[reportUnnecessaryIsInstance]
        format_id = metric_format.type
        # Use explicit decimals if provided, otherwise default based on type
        decimals = metric_format.decimals if metric_format.decimals is not None else 0 if metric_format.type in ('bits', 'duration') else 2
        pattern = metric_format.pattern
        suffix = metric_format.suffix
        compact = metric_format.compact
    else:
        msg = f'Unknown metric format type: {type(metric_format).__name__}'
        raise TypeError(msg)  # pyright: ignore[reportUnreachable]

    return KbnESQLMetricFormat(
        id=format_id,
        params=KbnESQLMetricFormatParams(
            decimals=decimals,
            suffix=suffix,
            compact=compact,
            pattern=pattern,
        ),
    )


def compile_esql_metric(metric: ESQLMetricTypes) -> KbnESQLMetricColumnTypes:
    """Compile a single ESQLMetricTypes object into its Kibana view model.

    Args:
        metric (ESQLMetricTypes): The ESQLMetricTypes object to compile.

    Returns:
        KbnESQLMetricColumnTypes: The compiled Kibana column.

    """
    if isinstance(metric, ESQLStaticValue):
        field_name = metric.label if metric.label is not None else str(metric.value)
        return KbnESQLStaticValueColumn(
            fieldName=field_name,
            columnId=metric.get_id(),
        )

    if not isinstance(metric, ESQLMetric):  # pyright: ignore[reportUnnecessaryIsInstance]
        msg = f'Unknown metric type: {type(metric).__name__}'
        raise TypeError(msg)  # pyright: ignore[reportUnreachable]

    # Compile format if provided
    params = None
    if metric.format is not None:
        esql_format = compile_esql_metric_format(metric.format)
        params = KbnESQLMetricColumnParams(format=esql_format)

    label = metric.label if metric.label is not None else metric.field
    custom_label = metric.label is not None
    meta = KbnESQLColumnMeta(type='number', esType='long')

    return KbnESQLFieldMetricColumn(
        fieldName=metric.field,
        columnId=metric.get_id(),
        label=label,
        customLabel=custom_label,
        meta=meta,
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
    dimension_id = dimension.get_id()

    # Add meta information for date fields if data_type is explicitly set
    meta = None
    if dimension.data_type == 'date':
        meta = KbnESQLColumnMeta(type='date', esType='date')

    return KbnESQLFieldDimensionColumn(
        fieldName=dimension.field,
        columnId=dimension_id,
        label=dimension.field,
        customLabel=False,
        meta=meta,
    )


def compile_esql_dimensions(dimensions: Sequence[ESQLDimensionTypes]) -> list[KbnESQLFieldDimensionColumn]:
    """Compile a sequence of ESQLDimensionTypes objects into their Kibana view model representation.

    Args:
        dimensions (Sequence[ESQLDimensionTypes]): The sequence of ESQLDimensionTypes objects to compile.

    Returns:
        list[KbnESQLFieldDimensionColumn]: The compiled Kibana view model.

    """
    return [compile_esql_dimension(dimension) for dimension in dimensions]
