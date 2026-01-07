from collections.abc import Mapping, Sequence

from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnLensCustomIntervalsDimensionColumnParentFormat,
    KbnLensCustomIntervalsDimensionColumnParentFormatParams,
    KbnLensCustomInvervalsDimensionColumn,
    KbnLensCustomInvervalsDimensionColumnParams,
    KbnLensDateHistogramDimensionColumn,
    KbnLensDateHistogramDimensionColumnParams,
    KbnLensDimensionColumnTypes,
    KbnLensFiltersDimensionColumn,
    KbnLensFiltersDimensionColumnParams,
    KbnLensFiltersFilter,
    KbnLensIntervalsDimensionColumn,
    KbnLensIntervalsDimensionColumnParams,
    KbnLensIntervalsRange,
    KbnLensMetricColumnTypes,
    KbnLensTermsDimensionColumn,
    KbnLensTermsDimensionColumnParams,
    KbnLensTermsOrderBy,
    KbnLensTermsParentFormat,
)
from dashboard_compiler.panels.charts.lens.dimensions.config import (
    LensDateHistogramDimension,
    LensDimensionTypes,
    LensFiltersDimension,
    LensIntervalsDimension,
    LensTopValuesDimension,
)
from dashboard_compiler.queries.compile import compile_nonesql_query  # Import compile_query
from dashboard_compiler.shared.config import stable_id_generator
from dashboard_compiler.shared.defaults import default_false, default_true

# Maps user-friendly granularity levels (1=finest to 7=coarsest) to Kibana's
# maxBars parameter. These values control histogram bucketing precision:
# - Lower granularity (1-3): More buckets, finer detail, slower queries
# - Higher granularity (5-7): Fewer buckets, coarser detail, faster queries
# Values are calibrated to match Kibana's native granularity slider behavior
GRANULARITY_TO_BARS = {
    1: 1,  # Finest: Maximum detail
    2: 167.5,
    3: 334,
    4: 499.5,  # Medium: Balanced
    5: 666,
    6: 833.5,
    7: 1000,  # Coarsest: Minimum buckets
}


def compile_lens_dimension(
    dimension: LensDimensionTypes,
    *,
    kbn_metric_column_by_id: Mapping[str, KbnLensMetricColumnTypes],
) -> tuple[str, KbnLensDimensionColumnTypes]:
    """Compile a single LensDimensionTypes object into its Kibana view model.

    Args:
        dimension (LensDimensionTypes): The LensDimensionTypes object to compile.
        kbn_metric_column_by_id (Mapping[str, KbnLensMetricColumnTypes]): A mapping of compiled KbnLensFieldMetricColumn objects.

    Returns:
        tuple[str, KbnLensDimensionColumnTypes]: A tuple containing the dimension ID and the compiled Kibana view model.

    """
    kbn_column_name_to_id = {column.label: column_id for column_id, column in kbn_metric_column_by_id.items()}

    custom_label = True if dimension.label is not None else None

    if isinstance(dimension, LensDateHistogramDimension):
        dimension_id = dimension.id or stable_id_generator([dimension.type, dimension.label, dimension.field])

        return dimension_id, KbnLensDateHistogramDimensionColumn(
            label=dimension.label or dimension.field,
            customLabel=custom_label,
            dataType='date',
            operationType='date_histogram',
            sourceField=dimension.field,
            scale='interval',
            params=KbnLensDateHistogramDimensionColumnParams(
                interval=dimension.minimum_interval or 'auto',
                includeEmptyRows=True,
                dropPartials=False,
            ),
        )
    if isinstance(dimension, LensTopValuesDimension):
        dimension_id = dimension.id or stable_id_generator([dimension.type, dimension.label, dimension.field])

        order_by = None
        if dimension.sort is not None:
            if dimension.sort.by not in kbn_column_name_to_id:
                msg = f'Column {dimension.sort.by} not found in kbn_metric_column_by_id'
                raise ValueError(msg)
            order_by = KbnLensTermsOrderBy(
                type='column',
                columnId=kbn_column_name_to_id[dimension.sort.by],
            )
        elif len(kbn_metric_column_by_id) > 0:
            # Default to ordering by first metric column if it's not a formula
            # Formula columns cannot be used for aggregation ordering in Elasticsearch
            first_metric_id = next(iter(kbn_metric_column_by_id.keys()))
            first_metric = kbn_metric_column_by_id[first_metric_id]

            if first_metric.operationType == 'formula':
                # Formula columns are computed post-aggregation, use alphabetical ordering
                order_by = KbnLensTermsOrderBy(
                    type='alphabetical',
                    fallback=True,
                )
            else:
                # Non-formula metrics can be used for ordering
                order_by = KbnLensTermsOrderBy(
                    type='column',
                    columnId=first_metric_id,
                )
        else:
            # No metrics available, fall back to alphabetical
            order_by = KbnLensTermsOrderBy(
                type='alphabetical',
                fallback=True,
            )

        return dimension_id, KbnLensTermsDimensionColumn(
            label=dimension.label or f'Top {dimension.size or 3} values of {dimension.field}',
            customLabel=custom_label,
            dataType='string',
            operationType='terms',
            scale='ordinal',
            sourceField=dimension.field,
            params=KbnLensTermsDimensionColumnParams(
                size=dimension.size,
                orderBy=order_by,
                orderDirection=dimension.sort.direction if dimension.sort else 'desc',
                otherBucket=default_true(dimension.other_bucket),
                missingBucket=default_false(dimension.missing_bucket),
                parentFormat=KbnLensTermsParentFormat(),
                include=dimension.include or [],
                exclude=dimension.exclude or [],
                includeIsRegex=dimension.include_is_regex or False,
                excludeIsRegex=dimension.exclude_is_regex or False,
            ),
        )
    if isinstance(dimension, LensFiltersDimension):
        dimension_id = dimension.id or stable_id_generator([dimension.type, dimension.label])
        return dimension_id, KbnLensFiltersDimensionColumn(
            label=dimension.label or 'Filters',
            customLabel=custom_label,
            dataType='string',
            operationType='filters',
            scale='ordinal',
            params=KbnLensFiltersDimensionColumnParams(
                filters=[KbnLensFiltersFilter(label=f.label or '', input=compile_nonesql_query(f.query)) for f in dimension.filters]
            ),
        )

    # This check is necessary even though it appears redundant to type checkers
    # because dimension could be a more specific subclass at runtime
    if isinstance(dimension, LensIntervalsDimension):  # pyright: ignore[reportUnnecessaryIsInstance]
        dimension_id = dimension.id or stable_id_generator([dimension.type, dimension.label])

        if dimension.intervals is None:
            return dimension_id, KbnLensIntervalsDimensionColumn(
                label=dimension.label or dimension.field or '',
                customLabel=custom_label,
                sourceField=dimension.field,
                params=KbnLensIntervalsDimensionColumnParams(
                    includeEmptyRows=True,
                    type='histogram',
                    ranges=[KbnLensIntervalsRange(from_value=0, to_value=1000, label='')],
                    maxBars=GRANULARITY_TO_BARS[dimension.granularity] if dimension.granularity else 'auto',
                ),
            )
        ranges = [
            KbnLensIntervalsRange(
                from_value=interval.from_value,
                to_value=interval.to_value,
                label=interval.label or '',
            )
            for interval in dimension.intervals
        ]
        return dimension_id, KbnLensCustomInvervalsDimensionColumn(
            label=dimension.label or dimension.field or '',
            customLabel=custom_label,
            sourceField=dimension.field,
            params=KbnLensCustomInvervalsDimensionColumnParams(
                ranges=ranges,
                maxBars=499.5,
                parentFormat=KbnLensCustomIntervalsDimensionColumnParentFormat(
                    id='range',
                    params=KbnLensCustomIntervalsDimensionColumnParentFormatParams(
                        template='arrow_right',
                        replaceInfinity=True,
                    ),
                ),
            ),
        )

    # All LensDimensionTypes have been handled above, this is unreachable
    # but kept for type safety in case new types are added
    msg = f'Unsupported dimension type: {type(dimension)}'  # pyright: ignore[reportUnreachable]
    raise NotImplementedError(msg)


def compile_lens_dimensions(
    dimensions: Sequence[LensDimensionTypes],
    *,
    kbn_metric_column_by_id: Mapping[str, KbnLensMetricColumnTypes],
) -> dict[str, KbnLensDimensionColumnTypes]:
    """Compile a sequence of LensDimensionTypes objects into their Kibana view model representation.

    Args:
        dimensions (Sequence[LensDimensionTypes]): The sequence of LensDimensionTypes objects to compile.
        kbn_metric_column_by_id (Mapping[str, KbnLensMetricColumnTypes]): A mapping of compiled KbnLensFieldMetricColumn objects.

    Returns:
        dict[str, KbnLensDimensionColumnTypes]: A dictionary of compiled KbnLensDimensionColumnTypes objects.

    """
    return dict(compile_lens_dimension(dimension, kbn_metric_column_by_id=kbn_metric_column_by_id) for dimension in dimensions)
