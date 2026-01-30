"""Compile Lens metrics into their Kibana view models."""

from dataclasses import dataclass, field
from typing import Any

from humanize import ordinal

from kb_dashboard_core.panels.charts.lens.columns.view import (
    KbnLensFieldMetricColumn,
    KbnLensFormulaAggColumn,
    KbnLensFormulaAggColumnParams,
    KbnLensFormulaColumn,
    KbnLensFormulaColumnParams,
    KbnLensFullReferenceColumn,
    KbnLensFullReferenceColumnParams,
    KbnLensMathColumn,
    KbnLensMathColumnParams,
    KbnLensMetricColumnParams,
    KbnLensMetricColumnTypes,
    KbnLensMetricFormat,
    KbnLensMetricFormatParams,
    KbnLensMetricFormatTypes,
    KbnLensStaticValueColumn,
    KbnLensStaticValueColumnParams,
)
from kb_dashboard_core.panels.charts.lens.metrics.config import (
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
from kb_dashboard_core.panels.charts.lens.metrics.formula_parser import (
    AggregationInfo,
    FullReferenceInfo,
    build_tinymath_ast_with_refs,
    parse_formula,
)
from kb_dashboard_core.queries.view import KbnQuery
from kb_dashboard_core.shared.defaults import default_true

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


@dataclass
class CompiledMetricResult:
    """Result of compiling a Lens metric.

    For simple metrics (aggregations, static values), helper_columns will be empty.
    For formula metrics, helper_columns contains the aggregation and math columns
    needed for proper rendering.
    """

    primary_id: str
    """The ID of the primary metric column."""

    primary_column: KbnLensMetricColumnTypes
    """The primary metric column (formula, aggregation, or static value)."""

    helper_columns: dict[str, KbnLensMetricColumnTypes] = field(default_factory=dict)
    """Helper columns needed for formula rendering (aggregation + math columns)."""


def _create_aggregation_column(
    agg_info: AggregationInfo,
    formula_text: str,
) -> KbnLensFormulaAggColumn:
    """Create an aggregation helper column for a formula.

    Args:
        agg_info: Information about the aggregation extracted from the formula.
        formula_text: The full formula text for generating labels.

    Returns:
        A KbnLensFormulaAggColumn for this aggregation.

    """
    # Generate a label that matches Kibana's format
    label = f'Part of {formula_text}'

    # Determine the source field
    source_field: str | None = agg_info.source_field
    if agg_info.operation_type == 'count' and source_field is None:
        source_field = '___records___'

    # Create filter if kql was specified
    filter_query: KbnQuery | None = None
    if agg_info.filter_query is not None:
        filter_query = KbnQuery(query=agg_info.filter_query, language='kuery')

    return KbnLensFormulaAggColumn(
        label=label,
        customLabel=True,
        dataType='number',
        operationType=agg_info.operation_type,
        isBucketed=False,
        scale='ratio',
        sourceField=source_field,
        filter=filter_query,
        # Note: emptyAsNull=False for formula helper columns preserves null values
        # in intermediate calculations, matching Kibana's formula column behavior
        params=KbnLensFormulaAggColumnParams(
            emptyAsNull=False,
            shift=agg_info.shift,
            reducedTimeRange=agg_info.reduced_time_range,
        ),
    )


def _create_math_column(
    tinymath_ast: dict[str, Any],
    references: list[str],
    formula_text: str,
) -> KbnLensMathColumn:
    """Create a math column for a formula.

    Args:
        tinymath_ast: The tinymathAST structure.
        references: List of aggregation column IDs this math column references.
        formula_text: The full formula text for generating labels.

    Returns:
        A KbnLensMathColumn containing the tinymathAST.

    """
    label = f'Part of {formula_text}'

    return KbnLensMathColumn(
        label=label,
        customLabel=True,
        dataType='number',
        operationType='math',
        isBucketed=False,
        scale='ratio',
        params=KbnLensMathColumnParams(tinymathAst=tinymath_ast),
        references=references,
    )


def _create_full_reference_column(
    full_ref_info: FullReferenceInfo,
    referenced_column_id: str,
    formula_text: str,
) -> KbnLensFullReferenceColumn:
    """Create a fullReference operation column for a formula.

    Args:
        full_ref_info: Information about the fullReference operation.
        referenced_column_id: The column ID that this operation references.
        formula_text: The full formula text for generating labels.

    Returns:
        A KbnLensFullReferenceColumn for this operation.

    """
    label = f'Part of {formula_text}'

    # Build params with optional window for moving_average
    params = KbnLensFullReferenceColumnParams(
        emptyAsNull=False,
        window=full_ref_info.window,
    )

    # Determine timeScale for rate operations (counter_rate uses per-second)
    time_scale: str | None = None
    if full_ref_info.operation_type == 'counter_rate':
        time_scale = 's'

    return KbnLensFullReferenceColumn(
        label=label,
        customLabel=True,
        dataType='number',
        operationType=full_ref_info.operation_type,
        isBucketed=False,
        scale='ratio',
        # Note: emptyAsNull=False for fullReference columns preserves null values
        # in intermediate calculations, matching Kibana's formula column behavior
        params=params,
        references=[referenced_column_id],
        timeScale=time_scale,
    )


def _compile_formula_metric(
    metric: LensFormulaMetric,
    metric_format: KbnLensMetricFormatTypes | None,
) -> CompiledMetricResult:
    """Compile a formula metric with helper columns.

    This generates the full column structure that Kibana needs:
    1. Aggregation columns (X0, X1, ...) for each field-based aggregation
    2. FullReference columns (Xn, Xn+1, ...) for operations like counter_rate
    3. Math column (Xm) containing the tinymathAST
    4. Formula column referencing the math column

    Args:
        metric: The formula metric configuration.
        metric_format: Optional format for the formula result.

    Returns:
        CompiledMetricResult with the formula column and all helper columns.

    """
    custom_label = None if metric.label is None else True
    formula_id = metric.get_id()

    # Parse the formula to extract aggregations and fullReference operations
    parse_result = parse_formula(metric.formula)

    # If no aggregations or fullReferences, return simple formula column (Kibana will handle it)
    if not parse_result.aggregations and not parse_result.full_references:
        formula_column = KbnLensFormulaColumn(
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
        return CompiledMetricResult(
            primary_id=formula_id,
            primary_column=formula_column,
        )

    # Generate helper columns
    helper_columns: dict[str, KbnLensMetricColumnTypes] = {}
    agg_column_refs: dict[int, str] = {}
    full_ref_column_refs: dict[int, str] = {}
    all_helper_column_ids: list[str] = []
    next_column_index = 0

    # Create aggregation columns (X0, X1, X2, ...)
    for idx, agg_info in enumerate(parse_result.aggregations):
        agg_id = f'{formula_id}X{next_column_index}'
        agg_column = _create_aggregation_column(agg_info, metric.formula)
        helper_columns[agg_id] = agg_column
        agg_column_refs[idx] = agg_id
        all_helper_column_ids.append(agg_id)
        next_column_index += 1

    # Create fullReference columns (Xn, Xn+1, ...)
    # These reference the aggregation columns they wrap
    for idx, full_ref_info in enumerate(parse_result.full_references):
        full_ref_id = f'{formula_id}X{next_column_index}'

        # Get the column ID of the inner aggregation
        inner_agg_index = full_ref_info.inner_aggregation_index
        # Fallback to empty if we can't find the inner aggregation (shouldn't happen with well-formed formulas)
        referenced_column_id = agg_column_refs.get(inner_agg_index, '') if inner_agg_index >= 0 else ''

        full_ref_column = _create_full_reference_column(full_ref_info, referenced_column_id, metric.formula)
        helper_columns[full_ref_id] = full_ref_column
        full_ref_column_refs[idx] = full_ref_id
        all_helper_column_ids.append(full_ref_id)
        next_column_index += 1

    # Build tinymathAST with column references (returns Any due to untyped TatSu AST)
    tinymath_ast = build_tinymath_ast_with_refs(parse_result, agg_column_refs, full_ref_column_refs)  # pyright: ignore[reportAny]

    # Check if formula is a simple aggregation/fullReference (tinymath_ast is just a string column ID)
    # This happens when the formula is literally just one operation like "counter_rate(max(field))"
    if isinstance(tinymath_ast, str):
        # Formula column should reference the column directly, no math column needed
        formula_column = KbnLensFormulaColumn(
            label=metric.label or 'Formula',
            customLabel=custom_label,
            dataType='number',
            operationType='formula',
            isBucketed=False,
            scale='ratio',
            references=all_helper_column_ids,
            params=KbnLensFormulaColumnParams(
                formula=metric.formula,
                isFormulaBroken=False,
                format=metric_format,
            ),
        )
    else:
        # Create math column (Xm where m = next_column_index)
        math_id = f'{formula_id}X{next_column_index}'
        math_column = _create_math_column(tinymath_ast, all_helper_column_ids, metric.formula)  # pyright: ignore[reportAny]
        helper_columns[math_id] = math_column

        # Create formula column referencing the math column
        formula_column = KbnLensFormulaColumn(
            label=metric.label or 'Formula',
            customLabel=custom_label,
            dataType='number',
            operationType='formula',
            isBucketed=False,
            scale='ratio',
            references=[math_id],
            params=KbnLensFormulaColumnParams(
                formula=metric.formula,
                isFormulaBroken=False,
                format=metric_format,
            ),
        )

    return CompiledMetricResult(
        primary_id=formula_id,
        primary_column=formula_column,
        helper_columns=helper_columns,
    )


def compile_lens_metric_format(metric_format: LensMetricFormatTypes) -> KbnLensMetricFormatTypes:
    """Compile a LensMetricFormat object into its Kibana view model.

    Args:
        metric_format (LensMetricFormat): The LensMetricFormat object to compile.

    Returns:
        KbnLensMetricFormat: The compiled Kibana view model.

    """
    if isinstance(metric_format, LensCustomMetricFormat):
        decimals = metric_format.decimals if metric_format.decimals is not None else 0
        return KbnLensMetricFormat(
            id='custom',
            params=KbnLensMetricFormatParams(
                decimals=decimals,
                pattern=metric_format.pattern,
            ),
        )

    # This check is necessary even though it appears redundant to type checkers
    # because metric_format could be a more specific subclass at runtime
    if isinstance(metric_format, LensMetricFormat):  # pyright: ignore[reportUnnecessaryIsInstance]
        decimals = metric_format.decimals if metric_format.decimals is not None else FORMAT_TO_DEFAULT_DECIMALS[metric_format.type]
        return KbnLensMetricFormat(
            id=metric_format.type,
            params=KbnLensMetricFormatParams(
                decimals=decimals,
                suffix=metric_format.suffix,
                compact=metric_format.compact,
            ),
        )

    # All LensMetricFormatTypes have been handled above, this is unreachable
    # but kept for type safety in case new types are added
    msg = f'Unsupported metric format type: {type(metric_format)}'  # pyright: ignore[reportUnreachable]
    raise NotImplementedError(msg)


def compile_lens_metric(metric: LensMetricTypes) -> CompiledMetricResult:
    """Compile a single LensMetricTypes object into its Kibana view model.

    Args:
        metric (LensMetricTypes): The LensMetricTypes object to compile.

    Returns:
        CompiledMetricResult containing the primary column and any helper columns.

    """
    # Handle static values
    if isinstance(metric, LensStaticValue):
        metric_id = metric.get_id()
        label = metric.label if metric.label is not None else str(metric.value)
        custom_label = metric.label is not None

        return CompiledMetricResult(
            primary_id=metric_id,
            primary_column=KbnLensStaticValueColumn(
                label=label,
                customLabel=custom_label,
                dataType='number',
                operationType='static_value',
                scale='ratio',
                params=KbnLensStaticValueColumnParams(value=metric.value),
            ),
        )

    custom_label = None if metric.label is None else True
    metric_format = compile_lens_metric_format(metric.format) if metric.format is not None else None

    if isinstance(metric, LensFormulaMetric):
        return _compile_formula_metric(metric, metric_format)

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

    return CompiledMetricResult(
        primary_id=metric_id,
        primary_column=KbnLensFieldMetricColumn(
            label=metric.label or default_label,
            customLabel=custom_label,
            dataType='number',
            operationType=metric.aggregation,
            scale='ratio',
            sourceField=metric.field or '___records___',
            params=metric_column_params,
            filter=metric_filter,
        ),
    )
