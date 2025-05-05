"""Compile Lens metrics into their Kibana view models."""

from humanize import ordinal

from dashboard_compiler.panels.charts.columns.view import (
    KbnESQLFieldMetricColumn,
    KbnLensFieldMetricColumn,
    KbnLensMetricColumnParams,
    KbnLensMetricColumnTypes,
    KbnLensMetricFormat,
    KbnLensMetricFormatParams,
    KbnLensMetricFormatTypes,
)
from dashboard_compiler.panels.charts.metrics.config import (
    ESQLMetricTypes,
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
from dashboard_compiler.queries.compile import compile_query
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

    if isinstance(metric_format, LensMetricFormat):
        return KbnLensMetricFormat(
            id=metric_format.type,
            params=KbnLensMetricFormatParams(
                decimals=FORMAT_TO_DEFAULT_DECIMALS[metric_format.type],
                suffix=metric_format.suffix,
                compact=metric_format.compact,
            ),
        )

    msg = f'Unsupported metric format type: {type(metric_format)}'
    raise NotImplementedError(msg)


def compile_lens_metric(metric: LensMetricTypes) -> tuple[str, KbnLensMetricColumnTypes]:
    """Compile a single LensMetricTypes object into its Kibana view model.

    Args:
        metric (LensMetricTypes): The LensMetricTypes object to compile.

    Returns:
        tuple[str, KbnColumn]: A tuple containing the metric ID and its compiled KbnColumn.
    """
    custom_label = None if metric.label is None else True
    metric_format = compile_lens_metric_format(metric.format) if metric.format is not None else None

    # Handle formula metrics separately since they have a different structure
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

    default_label: str = f'{AGG_TO_FRIENDLY_TITLE[metric.aggregation]} of {metric.field}'

    if isinstance(metric, LensCountAggregatedMetric):
        default_label = f'{AGG_TO_FRIENDLY_TITLE[metric.aggregation]} of {metric.field or "records"}'
        metric_column_params = KbnLensMetricColumnParams(
            format=metric_format,
            emptyAsNull=return_unless(var=metric.exclude_zeros, is_none=True),
        )

    if isinstance(metric, LensSumAggregatedMetric):
        metric_column_params = KbnLensMetricColumnParams(
            format=metric_format,
            emptyAsNull=return_unless(var=metric.exclude_zeros, is_none=True),
        )

    if isinstance(metric, LensPercentileRankAggregatedMetric):
        default_label = f'{AGG_TO_FRIENDLY_TITLE[metric.aggregation]} ({metric.rank}) of {metric.field}'
        metric_column_params = KbnLensMetricColumnParams(
            format=metric_format,
            value=metric.rank,
        )

    if isinstance(metric, LensPercentileAggregatedMetric):
        default_label = f'{ordinal(metric.percentile)} {AGG_TO_FRIENDLY_TITLE[metric.aggregation]} of {metric.field}'
        metric_column_params = KbnLensMetricColumnParams(
            format=metric_format,
            percentile=metric.percentile,
        )

    if isinstance(metric, LensLastValueAggregatedMetric):
        metric_column_params = KbnLensMetricColumnParams(
            format=metric_format,
            sortField=metric.date_field or '@timestamp',
        )
        metric_filter = KbnQuery(query=f'"{metric.field}": *', language='kuery') if metric.filter is None else compile_query(metric.filter)

    if isinstance(metric, LensOtherAggregatedMetric):
        metric_column_params = KbnLensMetricColumnParams(
            format=metric_format,
            emptyAsNull=AGG_TO_DEFAULT_EXCLUDE_ZEROS.get(metric.aggregation, None),
        )

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


def compile_lens_metrics(metrics: list[LensMetricTypes]) -> dict[str, KbnLensMetricColumnTypes]:
    """Compile a list of LensMetricTypes into their Kibana view model representation.

    Args:
        metrics (list[LensMetricTypes]): The list of LensMetricTypes objects to compile.

    Returns:
        tuple[dict[str, KbnLensColumnTypes]] A dictionary of metric IDs to their compiled KbnLensColumnTypes.

    """
    compiled_metrics = [compile_lens_metric(metric) for metric in metrics]

    return dict(compiled_metrics)


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
