"""Compile Lens metrics into their Kibana view models."""

from dataclasses import dataclass, field
from typing import Any

from humanize import ordinal

from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnLensFieldMetricColumn,
    KbnLensFormulaAggColumn,
    KbnLensFormulaAggColumnParams,
    KbnLensFormulaColumn,
    KbnLensFormulaColumnParams,
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
from dashboard_compiler.panels.charts.lens.metrics.formula_parser import (
    AggregationInfo,
    build_tinymath_ast_with_refs,
    parse_formula,
)
from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.shared.config import stable_id_generator
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
    if agg_info.filter_query:
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
        params=KbnLensFormulaAggColumnParams(emptyAsNull=False),
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


def _compile_formula_metric(
    metric: LensFormulaMetric,
    metric_format: KbnLensMetricFormatTypes | None,
) -> CompiledMetricResult:
    """Compile a formula metric with helper columns.

    This generates the full column structure that Kibana needs:
    1. Aggregation columns (X0, X1, ...) for each aggregation function
    2. Math column (Xn) containing the tinymathAST
    3. Formula column referencing the math column

    Args:
        metric: The formula metric configuration.
        metric_format: Optional format for the formula result.

    Returns:
        CompiledMetricResult with the formula column and all helper columns.

    """
    custom_label = None if metric.label is None else True
    formula_id = metric.id or stable_id_generator(['formula', metric.formula, metric.label or 'Formula'])

    # Parse the formula to extract aggregations
    parse_result = parse_formula(metric.formula)

    # If no aggregations, return simple formula column (Kibana will handle it)
    if not parse_result.aggregations:
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
    column_refs: dict[int, str] = {}
    agg_column_ids: list[str] = []

    # Create aggregation columns (X0, X1, X2, ...)
    for idx, agg_info in enumerate(parse_result.aggregations):
        agg_id = f'{formula_id}X{idx}'
        agg_column = _create_aggregation_column(agg_info, metric.formula)
        helper_columns[agg_id] = agg_column
        column_refs[idx] = agg_id
        agg_column_ids.append(agg_id)

    # Build tinymathAST with column references
    tinymath_ast = build_tinymath_ast_with_refs(parse_result, column_refs)

    # Check if formula is a simple aggregation (tinymath_ast is just a string column ID)
    # This happens when the formula is literally just one aggregation like "average(field='foo')"
    if isinstance(tinymath_ast, str):
        # Formula column should reference the aggregation column directly, no math column needed
        formula_column = KbnLensFormulaColumn(
            label=metric.label or 'Formula',
            customLabel=custom_label,
            dataType='number',
            operationType='formula',
            isBucketed=False,
            scale='ratio',
            references=agg_column_ids,
            params=KbnLensFormulaColumnParams(
                formula=metric.formula,
                isFormulaBroken=False,
                format=metric_format,
            ),
        )
    else:
        # Create math column (Xn where n = len(aggregations))
        math_id = f'{formula_id}X{len(parse_result.aggregations)}'
        math_column = _create_math_column(tinymath_ast, agg_column_ids, metric.formula)
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


def compile_lens_metric(metric: LensMetricTypes) -> CompiledMetricResult:
    """Compile a single LensMetricTypes object into its Kibana view model.

    Args:
        metric (LensMetricTypes): The LensMetricTypes object to compile.

    Returns:
        CompiledMetricResult containing the primary column and any helper columns.

    """
    # Handle static values
    if isinstance(metric, LensStaticValue):
        metric_id = metric.id or stable_id_generator(['static_value', str(metric.value)])
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
