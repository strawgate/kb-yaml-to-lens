"""Decompile Kibana Lens dimension columns back to config models."""

from typing import Any

from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnLensCustomIntervalsDimensionColumn,
    KbnLensDateHistogramDimensionColumn,
    KbnLensDimensionColumnTypes,
    KbnLensFiltersDimensionColumn,
    KbnLensIntervalsDimensionColumn,
    KbnLensTermsDimensionColumn,
)
from dashboard_compiler.panels.charts.lens.dimensions.config import (
    LensDateHistogramDimension,
    LensDimensionTypes,
    LensFiltersDimension,
    LensFiltersDimensionFilter,
    LensIntervalsDimension,
    LensIntervalsDimensionInterval,
    LensMultiTermsDimension,
    LensTermsDimension,
)
from dashboard_compiler.queries.decompile import decompile_query
from dashboard_compiler.shared.decompile_context import DecompileContext


def decompile_lens_dimension(  # noqa: PLR0911, PLR0912, PLR0915
    column: KbnLensDimensionColumnTypes,
    column_id: str,  # noqa: ARG001
    *,
    context: DecompileContext,
) -> LensDimensionTypes | None:
    """Decompile a Kibana Lens dimension column to config model.

    Args:
        column: The Kibana dimension column.
        column_id: The column ID.
        context: Decompilation context for warnings.

    Returns:
        The decompiled dimension config, or None if unsupported.

    """
    # Handle date histogram dimensions
    if isinstance(column, KbnLensDateHistogramDimensionColumn):
        source_field = column.sourceField
        params = column.params
        interval = params.interval
        label = column.label if column.customLabel is True else None

        # Use None for 'auto' interval to use default behavior
        minimum_interval = interval if interval != 'auto' else None

        return LensDateHistogramDimension(
            type='date_histogram',
            field=source_field,
            minimum_interval=minimum_interval,
            label=label,
        )

    # Handle terms dimensions (including multi-terms)
    if isinstance(column, KbnLensTermsDimensionColumn):
        source_field = column.sourceField
        params = column.params
        label = column.label if column.customLabel is True else None

        # Check if this is a multi-terms dimension
        secondary_fields = params.secondaryFields
        if secondary_fields is not None and len(secondary_fields) > 0:
            # Multi-terms dimension
            fields = [source_field, *secondary_fields]

            # Extract sort configuration
            sort = None
            order_by = params.orderBy
            if order_by is not None and order_by.type == 'column':
                # Column-based sorting - we can't reliably decompile this without
                # knowing the metric column labels, so skip for now
                pass

            return LensMultiTermsDimension(
                type='values',
                fields=fields,
                size=params.size,
                sort=sort,
                other_bucket=params.otherBucket,
                missing_bucket=params.missingBucket,
                include=params.include,
                exclude=params.exclude,
                include_is_regex=params.includeIsRegex,
                exclude_is_regex=params.excludeIsRegex,
                label=label,
            )

        # Single-field terms dimension
        # Extract sort configuration
        sort = None
        order_by = params.orderBy
        if order_by is not None and order_by.type == 'column':
            # Column-based sorting - we can't reliably decompile this without
            # knowing the metric column labels, so skip for now
            pass

        return LensTermsDimension(
            type='values',
            field=source_field,
            size=params.size,
            sort=sort,
            other_bucket=params.otherBucket,
            missing_bucket=params.missingBucket,
            include=params.include,
            exclude=params.exclude,
            include_is_regex=params.includeIsRegex,
            exclude_is_regex=params.excludeIsRegex,
            label=label,
        )

    # Handle filters dimensions
    if isinstance(column, KbnLensFiltersDimensionColumn):
        params = column.params
        label = column.label if column.customLabel is True else None

        filters = []
        for kbn_filter in params.filters:
            # Create a minimal DecompileContext for query decompilation
            query_context = DecompileContext()
            query = decompile_query(kbn_filter.input, context=query_context)
            filter_label = kbn_filter.label if kbn_filter.label != '' else None
            if query is not None:
                filters.append(LensFiltersDimensionFilter(query=query, label=filter_label))

        return LensFiltersDimension(
            type='filters',
            filters=filters,
            label=label,
        )

    # Handle intervals dimensions (auto-generated ranges)
    if isinstance(column, KbnLensIntervalsDimensionColumn):
        source_field = column.sourceField
        params = column.params
        label = column.label if column.customLabel is True else None

        # Auto-generated intervals don't have custom interval specifications
        # We can infer granularity from maxBars if present
        granularity = None
        max_bars = params.maxBars
        if max_bars is not None and isinstance(max_bars, (int, float)):
            # Reverse lookup from GRANULARITY_TO_BARS mapping
            # This is approximate - we'll pick the closest match
            granularity_map = {
                1: 1,
                167.5: 2,
                334: 3,
                499.5: 4,
                666: 5,
                833.5: 6,
                1000: 7,
            }
            # Find closest match
            closest_granularity = min(granularity_map.keys(), key=lambda x: abs(x - max_bars))
            granularity = granularity_map[closest_granularity]

        return LensIntervalsDimension(
            type='intervals',
            field=source_field,
            granularity=granularity,
            label=label,
        )

    # Handle custom intervals dimensions
    if isinstance(column, KbnLensCustomIntervalsDimensionColumn):
        source_field = column.sourceField
        params = column.params
        label = column.label if column.customLabel is True else None

        intervals = []
        for kbn_range in params.ranges:
            # Use the proper aliased field name for LensIntervalsDimensionInterval
            interval_dict: dict[str, Any] = {}
            if kbn_range.from_value is not None:
                interval_dict['from'] = kbn_range.from_value
            if kbn_range.to_value is not None:
                interval_dict['to'] = kbn_range.to_value
            if kbn_range.label is not None and kbn_range.label != '':
                interval_dict['label'] = kbn_range.label
            intervals.append(LensIntervalsDimensionInterval.model_validate(interval_dict))

        return LensIntervalsDimension(
            type='intervals',
            field=source_field,
            intervals=intervals,
            label=label,
        )

    # Unsupported dimension type
    context.warn(f'Unsupported dimension column type: {type(column).__name__}')
    return None
