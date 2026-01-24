"""Decompile Kibana Lens metric columns back to config models."""

from typing import Any

from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnLensFieldMetricColumn,
    KbnLensFormulaColumn,
    KbnLensMetricColumnTypes,
    KbnLensStaticValueColumn,
)
from dashboard_compiler.panels.charts.lens.metrics.config import (
    LensCountAggregatedMetric,
    LensCustomMetricFormat,
    LensFormulaMetric,
    LensLastValueAggregatedMetric,
    LensMetricFormat,
    LensMetricFormatTypes,
    LensMetricTypes,
    LensOtherAggregatedMetric,
    LensPercentileAggregatedMetric,
    LensPercentileRankAggregatedMetric,
    LensStaticValue,
    LensSumAggregatedMetric,
)
from dashboard_compiler.shared.decompile_context import DecompileContext


def decompile_lens_metric_format(kbn_format: dict[str, Any] | None) -> LensMetricFormatTypes | None:
    """Decompile a Kibana metric format to config model.

    Args:
        kbn_format: The Kibana format dict.

    Returns:
        The decompiled format config, or None if no format.

    """
    if kbn_format is None:
        return None

    format_id = kbn_format.get('id')
    params = kbn_format.get('params', {})

    if format_id == 'custom':
        pattern = params.get('pattern', '0,0')
        return LensCustomMetricFormat(pattern=pattern)

    if format_id in ('number', 'bytes', 'bits', 'percent', 'duration'):
        suffix = params.get('suffix')
        compact = params.get('compact')
        pattern = params.get('pattern')
        return LensMetricFormat(
            type=format_id,
            suffix=suffix,
            compact=compact,
            pattern=pattern,
        )

    return None


def decompile_lens_metric(  # noqa: PLR0911, PLR0912
    column: KbnLensMetricColumnTypes,
    column_id: str,  # noqa: ARG001
    *,
    context: DecompileContext,
) -> LensMetricTypes | None:
    """Decompile a Kibana Lens metric column to config model.

    Args:
        column: The Kibana metric column.
        column_id: The column ID.
        context: Decompilation context for warnings.

    Returns:
        The decompiled metric config, or None if unsupported.

    """
    # Handle static values
    if isinstance(column, KbnLensStaticValueColumn):
        params = column.params
        value = params.value
        label = column.label if column.customLabel is True else None
        # Static value must be numeric for LensStaticValue
        if isinstance(value, str):
            context.warn(f'Static value column has string value: {value}')
            return None
        return LensStaticValue(value=value, label=label)

    # Handle formula metrics
    if isinstance(column, KbnLensFormulaColumn):
        params = column.params
        formula = params.formula
        label = column.label if column.customLabel is True else None
        metric_format = decompile_lens_metric_format(params.format.model_dump() if params.format is not None else None)
        return LensFormulaMetric(
            formula=formula,
            label=label,
            format=metric_format,
        )

    # Handle field-based metrics
    if isinstance(column, KbnLensFieldMetricColumn):
        operation_type = column.operationType
        source_field = column.sourceField
        label = column.label if column.customLabel is True else None
        params = column.params
        metric_format = decompile_lens_metric_format(params.format.model_dump() if params.format is not None else None)

        # Count metrics
        if operation_type == 'count':
            field = source_field if source_field != '___records___' else None
            return LensCountAggregatedMetric(
                aggregation='count',
                field=field,
                label=label,
                format=metric_format,
                exclude_zeros=params.emptyAsNull,
            )

        if operation_type == 'unique_count':
            return LensCountAggregatedMetric(
                aggregation='unique_count',
                field=source_field,
                label=label,
                format=metric_format,
                exclude_zeros=params.emptyAsNull,
            )

        # Sum metrics
        if operation_type == 'sum':
            return LensSumAggregatedMetric(
                aggregation='sum',
                field=source_field,
                label=label,
                format=metric_format,
                exclude_zeros=params.emptyAsNull,
            )

        # Percentile rank metrics
        if operation_type == 'percentile_rank':
            rank = params.value
            if rank is None:
                context.warn('Percentile rank metric missing value parameter')
                return None
            return LensPercentileRankAggregatedMetric(
                aggregation='percentile_rank',
                field=source_field,
                rank=rank,
                label=label,
                format=metric_format,
            )

        # Percentile metrics
        if operation_type == 'percentile':
            percentile = params.percentile
            if percentile is None:
                context.warn('Percentile metric missing percentile parameter')
                return None
            return LensPercentileAggregatedMetric(
                aggregation='percentile',
                field=source_field,
                percentile=percentile,
                label=label,
                format=metric_format,
            )

        # Last value metrics
        if operation_type == 'last_value':
            date_field = params.sortField
            return LensLastValueAggregatedMetric(
                aggregation='last_value',
                field=source_field,
                date_field=date_field,
                label=label,
                format=metric_format,
            )

        # Other aggregations (min, max, average, median)
        if operation_type in ('min', 'max', 'average', 'median'):
            return LensOtherAggregatedMetric(
                aggregation=operation_type,
                field=source_field,
                label=label,
                format=metric_format,
            )

        # Unsupported operation type
        context.warn(f'Unsupported metric operation type: {operation_type}')
        return None

    # Unsupported column type (formula helper columns like math, formula_agg, etc.)
    # These are internal helper columns and should not be decompiled as standalone metrics
    return None
