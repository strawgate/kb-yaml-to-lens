"""Compile Lens metrics into their Kibana view models."""

from humanize import ordinal

from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnLensFieldMetricColumn,
    KbnLensFormulaColumn,
    KbnLensFormulaColumnParams,
    KbnLensMetricColumnParams,
    KbnLensMetricColumnTypes,
    KbnLensMetricFormat,
    KbnLensMetricFormatParams,
    KbnLensMetricFormatTypes,
    KbnLensStaticValueColumn,
    KbnLensStaticValueColumnParams,
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
from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.shared.defaults import default_true

FORMAT_TO_DEFAULT_DECIMALS = {
    'number': 2,
    'bytes': 2,
    'bits': 0,
    'percent': 2,
    'duration': 0,
}

AGG_TO_FRIENDLY_TITLE = {
    'count': 'Count',
    'sum': 'Sum',
    'min': 'Minimum',
    'max': 'Maximum',
    'average': 'Average',
    'median': 'Median',
    'percentile_rank': 'Percentile rank',
    'percentile': 'percentile',
    'last_value': 'Last value',
    'unique_count': 'Unique count',
}

AGG_TO_DEFAULT_EXCLUDE_ZEROS = {
    'count': True,
    'unique_count': True,
    'min': True,
    'max': True,
    'sum': True,
}


def compile_lens_metric_format(metric_format: LensMetricFormatTypes) -> KbnLensMetricFormatTypes:
    """Compile a LensMetricFormat object into its Kibana view model.

    Args:
        metric_format (LensMetricFormat): The LensMetricFormat object to compile.

    Returns:
        KbnLensMetricFormat: The compiled Kibana view model.

    """
    if isinstance(metric_format, LensCustomMetricFormat):
        return KbnLensMetricFormat(
            id='custom',
            params=KbnLensMetricFormatParams(
                decimals=0,
                pattern=metric_format.pattern,
            ),
        )

    # This check is necessary even though it appears redundant to type checkers
    # because metric_format could be a more specific subclass at runtime
    if isinstance(metric_format, LensMetricFormat):  # pyright: ignore[reportUnnecessaryIsInstance]
        return KbnLensMetricFormat(
            id=metric_format.type,
            params=KbnLensMetricFormatParams(
                decimals=FORMAT_TO_DEFAULT_DECIMALS[metric_format.type],
                suffix=metric_format.suffix,
                compact=metric_format.compact,
            ),
        )

    # All LensMetricFormatTypes have been handled above, this is unreachable
    # but kept for type safety in case new types are added
    msg = f'Unsupported metric format type: {type(metric_format)}'  # pyright: ignore[reportUnreachable]
    raise NotImplementedError(msg)


def compile_lens_metric(metric: LensMetricTypes) -> tuple[str, KbnLensMetricColumnTypes]:
    """Compile a single LensMetricTypes object into its Kibana view model.

    Args:
        metric (LensMetricTypes): The LensMetricTypes object to compile.

    Returns:
        tuple[str, KbnColumn]: A tuple containing the metric ID and its compiled KbnColumn.

    """
    # Handle static values
    if isinstance(metric, LensStaticValue):
        metric_id = metric.get_id()
        label = metric.label if metric.label is not None else str(metric.value)
        custom_label = metric.label is not None

        return metric_id, KbnLensStaticValueColumn(
            label=label,
            customLabel=custom_label,
            dataType='number',
            operationType='static_value',
            scale='ratio',
            params=KbnLensStaticValueColumnParams(value=metric.value),
        )

    custom_label = None if metric.label is None else True
    metric_format = compile_lens_metric_format(metric.format) if metric.format is not None else None

    if isinstance(metric, LensFormulaMetric):
        metric_id = metric.get_id()

        return metric_id, KbnLensFormulaColumn(
            label=metric.label or 'Formula',
            customLabel=custom_label,
            dataType='number',
            operationType='formula',
            isBucketed=False,
            scale='ratio',
            references=[],
            params=KbnLensFormulaColumnParams(
                formula=metric.formula,
                format=metric_format,
            ),
        )

    metric_column_params: KbnLensMetricColumnParams
    metric_filter: KbnQuery | None = None
    metric_id = metric.get_id()

    # Generate Kibana-style default labels that match the native Lens editor UX.
    # Strategy varies by aggregation type to provide user-friendly descriptions:
    # - Standard aggs: "{Aggregation} of {field}" (e.g., "Average of response_time")
    # - Percentiles: "{nth} percentile of {field}" (e.g., "95th percentile of latency")
    # - Percentile rank: "Percentile rank (value) of {field}"
    # - Count: "Count of records" (field optional)
    default_label: str = f'{AGG_TO_FRIENDLY_TITLE[metric.aggregation]} of {metric.field}'

    if isinstance(metric, LensCountAggregatedMetric):
        default_label = f'{AGG_TO_FRIENDLY_TITLE[metric.aggregation]} of {metric.field or "records"}'
        metric_column_params = KbnLensMetricColumnParams(
            format=metric_format,
            emptyAsNull=default_true(metric.exclude_zeros),
        )

    elif isinstance(metric, LensSumAggregatedMetric):
        metric_column_params = KbnLensMetricColumnParams(
            format=metric_format,
            emptyAsNull=default_true(metric.exclude_zeros),
        )

    elif isinstance(metric, LensPercentileRankAggregatedMetric):
        default_label = f'{AGG_TO_FRIENDLY_TITLE[metric.aggregation]} ({metric.rank}) of {metric.field}'
        metric_column_params = KbnLensMetricColumnParams(
            format=metric_format,
            value=metric.rank,
        )

    elif isinstance(metric, LensPercentileAggregatedMetric):
        default_label = f'{ordinal(metric.percentile)} {AGG_TO_FRIENDLY_TITLE[metric.aggregation]} of {metric.field}'
        metric_column_params = KbnLensMetricColumnParams(
            format=metric_format,
            percentile=metric.percentile,
        )

    elif isinstance(metric, LensLastValueAggregatedMetric):
        # last_value aggregation requires special handling: Kibana needs an implicit
        # filter to ensure the field exists, otherwise it returns incorrect results.
        # We inject a Kuery filter "{field}": * which matches any document where the
        # field is present (not null/missing). This filter is automatically added to
        # the metric column and isn't visible in the user's config.
        metric_column_params = KbnLensMetricColumnParams(
            format=metric_format,
            sortField=metric.date_field or '@timestamp',
        )
        metric_filter = KbnQuery(query=f'"{metric.field}": *', language='kuery')

    # This check is necessary even though it appears redundant to type checkers
    # because metric could be a more specific subclass at runtime
    elif isinstance(metric, LensOtherAggregatedMetric):  # pyright: ignore[reportUnnecessaryIsInstance]
        metric_column_params = KbnLensMetricColumnParams(
            format=metric_format,
            emptyAsNull=AGG_TO_DEFAULT_EXCLUDE_ZEROS.get(metric.aggregation, None),
        )
    else:
        # All LensMetricTypes have been handled above, this is unreachable
        # but kept for type safety in case new types are added
        msg = f'Unsupported metric type: {type(metric)}'  # pyright: ignore[reportUnreachable]
        raise NotImplementedError(msg)

    return metric_id, KbnLensFieldMetricColumn(
        label=metric.label or default_label,
        customLabel=custom_label,
        dataType='number',
        operationType=metric.aggregation,
        scale='ratio',
        sourceField=metric.field or '___records___',
        params=metric_column_params,
        filter=metric_filter,
    )
