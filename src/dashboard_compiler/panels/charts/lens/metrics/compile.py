"""Compile Lens metrics into their Kibana view models."""

from collections.abc import Sequence

from humanize import ordinal

from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnLensFieldMetricColumn,
    KbnLensMetricColumnParams,
    KbnLensMetricColumnTypes,
    KbnLensMetricFormat,
    KbnLensMetricFormatParams,
    KbnLensMetricFormatTypes,
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
    LensSumAggregatedMetric,
)
from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.shared.compile import return_unless
from dashboard_compiler.shared.config import stable_id_generator

# def compile_lens_formula_metric(
#     metric_id: str,
#     metric: LensFormulaMetric,
# ) -> tuple[str, KbnLensFormulaSourcedColumn]:
#     """Compile a LensFormulaMetric object into its Kibana view model.

#     Args:
#         metric_id (str): The ID of the metric.
#         metric (LensFormulaMetric): The LensFormulaMetric object to compile.

#     Returns:
#         tuple[str, KbnLensFormulaSourcedColumn]: A tuple containing the metric ID and its compiled KbnLensFormulaSourcedColumn.

#     """
#     return metric_id, KbnLensFormulaSourcedColumn(
#         label=metric.label,
#         customLabel=metric.label is not None or None,
#         dataType='number',
#         operationType=metric.type,
#         scale='ratio',
#         formula=metric.formula,
#         isBucketed=False,
#         params={
#             'emptyAsNull': True,
#         },
#     )

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
    if isinstance(metric_format, LensMetricFormat):  # type: ignore[reportUnnecessaryIsInstance]
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
    msg = f'Unsupported metric format type: {type(metric_format)}'  # type: ignore[reportUnreachable]
    raise NotImplementedError(msg)  # type: ignore[reportUnreachable]


# def compile_lens_formula(metric: LensFormulaMetric) -> tuple[str, KbnLensFormulaMetricColumnTypes]:
#     """Compile a lens formula into its Kibana view model"""


def compile_lens_metric(metric: LensMetricTypes) -> tuple[str, KbnLensMetricColumnTypes]:
    """Compile a single LensMetricTypes object into its Kibana view model.

    Args:
        metric (LensMetricTypes): The LensMetricTypes object to compile.

    Returns:
        tuple[str, KbnColumn]: A tuple containing the metric ID and its compiled KbnColumn.

    """
    custom_label = None if metric.label is None else True
    metric_format = compile_lens_metric_format(metric.format) if metric.format is not None else None

    if isinstance(metric, LensFormulaMetric):
        msg = f'Formula metrics are not supported yet: {metric}'
        raise NotImplementedError(msg)
        # metric_id = metric.id or stable_id_generator(['formula', metric.label, metric.formula])
        # return metric_id, KbnLensFieldMetricColumn(
        #     label=metric.label or 'Formula',
        #     customLabel=custom_label,
        #     dataType='number',
        #     operationType='formula',
        #     scale='ratio',
        #     sourceField=metric.formula,  # Use formula as the source field
        #     params=KbnLensMetricColumnParams(
        #         format=metric_format,
        #         emptyAsNull=True,
        #     ),
        # )

    metric_column_params: KbnLensMetricColumnParams
    metric_filter: KbnQuery | None = None
    metric_id = metric.id or stable_id_generator([metric.aggregation, metric.field])

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
            emptyAsNull=return_unless(var=metric.exclude_zeros, is_none=True),
        )

    elif isinstance(metric, LensSumAggregatedMetric):
        metric_column_params = KbnLensMetricColumnParams(
            format=metric_format,
            emptyAsNull=return_unless(var=metric.exclude_zeros, is_none=True),
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
    elif isinstance(metric, LensOtherAggregatedMetric):  # type: ignore[reportUnnecessaryIsInstance]
        metric_column_params = KbnLensMetricColumnParams(
            format=metric_format,
            emptyAsNull=AGG_TO_DEFAULT_EXCLUDE_ZEROS.get(metric.aggregation, None),
        )
    else:
        # All LensMetricTypes have been handled above, this is unreachable
        # but kept for type safety in case new types are added
        msg = f'Unsupported metric type: {type(metric)}'  # type: ignore[reportUnreachable]
        raise NotImplementedError(msg)  # type: ignore[reportUnreachable]

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


def compile_lens_metrics(metrics: Sequence[LensMetricTypes]) -> dict[str, KbnLensMetricColumnTypes]:
    """Compile a sequence of LensMetricTypes into their Kibana view model representation.

    Args:
        metrics (Sequence[LensMetricTypes]): The sequence of LensMetricTypes objects to compile.

    Returns:
        dict[str, KbnLensMetricColumnTypes]: A dictionary of metric IDs to their compiled KbnLensColumnTypes.

    """
    compiled_metrics = [compile_lens_metric(metric) for metric in metrics]

    return dict(compiled_metrics)
