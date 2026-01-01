"""Compile Lens metrics into their Kibana view models."""

from collections.abc import Sequence

from humanize import ordinal

from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnLensFieldMetricColumn,
    KbnLensFormulaColumn,
    KbnLensFormulaParams,
    KbnLensMathColumn,
    KbnLensMathParams,
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
    LensFormulaAdd,
    LensFormulaAggregations,
    LensFormulaAverageAgg,
    LensFormulaCountAgg,
    LensFormulaDivide,
    LensFormulaMaxAgg,
    LensFormulaMedianAgg,
    LensFormulaMetric,
    LensFormulaMinAgg,
    LensFormulaMultiply,
    LensFormulaOperations,
    LensFormulaSubtract,
    LensFormulaSumAgg,
    LensFormulaUniqueCountAgg,
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
from dashboard_compiler.queries.compile import compile_nonesql_query
from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.shared.compile import return_unless
from dashboard_compiler.shared.config import stable_id_generator

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


def build_formula_string(operation: LensFormulaOperations | LensFormulaAggregations) -> str:  # noqa: PLR0911, PLR0912, PLR0915
    """Build a human-readable formula string from an operation tree.

    Args:
        operation: The formula operation or aggregation to convert to a string.

    Returns:
        str: The human-readable formula string.

    """
    if isinstance(operation, int | float):
        return str(operation)

    if isinstance(operation, LensFormulaCountAgg):
        parts: list[str] = []
        if operation.count.filter is not None:
            filter_query = compile_nonesql_query(operation.count.filter)
            parts.append(f"kql='{filter_query.query}'")
        return f'count({", ".join(parts)})' if len(parts) > 0 else 'count()'

    if isinstance(operation, LensFormulaUniqueCountAgg):
        parts = [f"field='{operation.unique_count.field}'"]
        if operation.unique_count.filter is not None:
            filter_query = compile_nonesql_query(operation.unique_count.filter)
            parts.append(f"kql='{filter_query.query}'")
        return f'unique_count({", ".join(parts)})'

    if isinstance(operation, LensFormulaSumAgg):
        parts = [f"field='{operation.sum.field}'"]
        if operation.sum.filter is not None:
            filter_query = compile_nonesql_query(operation.sum.filter)
            parts.append(f"kql='{filter_query.query}'")
        return f'sum({", ".join(parts)})'

    if isinstance(operation, LensFormulaAverageAgg):
        parts = [f"field='{operation.average.field}'"]
        if operation.average.filter is not None:
            filter_query = compile_nonesql_query(operation.average.filter)
            parts.append(f"kql='{filter_query.query}'")
        return f'average({", ".join(parts)})'

    if isinstance(operation, LensFormulaMinAgg):
        parts = [f"field='{operation.min.field}'"]
        if operation.min.filter is not None:
            filter_query = compile_nonesql_query(operation.min.filter)
            parts.append(f"kql='{filter_query.query}'")
        return f'min({", ".join(parts)})'

    if isinstance(operation, LensFormulaMaxAgg):
        parts = [f"field='{operation.max.field}'"]
        if operation.max.filter is not None:
            filter_query = compile_nonesql_query(operation.max.filter)
            parts.append(f"kql='{filter_query.query}'")
        return f'max({", ".join(parts)})'

    if isinstance(operation, LensFormulaMedianAgg):
        parts = [f"field='{operation.median.field}'"]
        if operation.median.filter is not None:
            filter_query = compile_nonesql_query(operation.median.filter)
            parts.append(f"kql='{filter_query.query}'")
        return f'median({", ".join(parts)})'

    if isinstance(operation, LensFormulaAdd):
        left = build_formula_string(operation.add.left)
        right = build_formula_string(operation.add.right)
        return f'({left} + {right})'

    if isinstance(operation, LensFormulaSubtract):
        left = build_formula_string(operation.subtract.left)
        right = build_formula_string(operation.subtract.right)
        return f'({left} - {right})'

    if isinstance(operation, LensFormulaMultiply):
        left = build_formula_string(operation.multiply.left)
        right = build_formula_string(operation.multiply.right)
        return f'({left} * {right})'

    if isinstance(operation, LensFormulaDivide):  # pyright: ignore[reportUnnecessaryIsInstance]
        left = build_formula_string(operation.divide.left)
        right = build_formula_string(operation.divide.right)
        return f'({left} / {right})'

    msg = f'Unsupported formula operation type: {type(operation)}'  # pyright: ignore[reportUnreachable]
    raise NotImplementedError(msg)


def build_tinymath_ast(
    operation: LensFormulaOperations | LensFormulaAggregations, column_refs: dict[int, str]
) -> dict[str, object] | str | int | float:
    """Build a TinymathAST structure from a formula operation.

    Args:
        operation: The formula operation or aggregation.
        column_refs: Map of aggregation object IDs to their column IDs.

    Returns:
        The TinymathAST structure (dict), column reference (str), or literal value (int/float).

    """
    if isinstance(operation, int | float):
        return operation

    # For aggregations, reference the column ID
    if isinstance(
        operation,
        (
            LensFormulaCountAgg,
            LensFormulaUniqueCountAgg,
            LensFormulaSumAgg,
            LensFormulaAverageAgg,
            LensFormulaMinAgg,
            LensFormulaMaxAgg,
            LensFormulaMedianAgg,
        ),
    ):
        agg_key = id(operation)
        if agg_key not in column_refs:
            msg = f'Aggregation {operation} not found in column references'
            raise ValueError(msg)
        return column_refs[agg_key]

    # For operations, build the AST recursively
    if isinstance(operation, LensFormulaAdd):
        return {
            'type': 'function',
            'name': 'add',
            'args': [
                build_tinymath_ast(operation.add.left, column_refs),
                build_tinymath_ast(operation.add.right, column_refs),
            ],
        }

    if isinstance(operation, LensFormulaSubtract):
        return {
            'type': 'function',
            'name': 'subtract',
            'args': [
                build_tinymath_ast(operation.subtract.left, column_refs),
                build_tinymath_ast(operation.subtract.right, column_refs),
            ],
        }

    if isinstance(operation, LensFormulaMultiply):
        return {
            'type': 'function',
            'name': 'multiply',
            'args': [
                build_tinymath_ast(operation.multiply.left, column_refs),
                build_tinymath_ast(operation.multiply.right, column_refs),
            ],
        }

    if isinstance(operation, LensFormulaDivide):  # pyright: ignore[reportUnnecessaryIsInstance]
        return {
            'type': 'function',
            'name': 'divide',
            'args': [
                build_tinymath_ast(operation.divide.left, column_refs),
                build_tinymath_ast(operation.divide.right, column_refs),
            ],
        }

    msg = f'Unsupported formula operation type: {type(operation)}'  # pyright: ignore[reportUnreachable]
    raise NotImplementedError(msg)


def collect_aggregations(
    operation: LensFormulaOperations | LensFormulaAggregations,
) -> list[LensFormulaAggregations]:
    """Collect all aggregation operations from a formula operation tree.

    Args:
        operation: The formula operation or aggregation.

    Returns:
        list: List of all aggregation operations found.

    """
    if isinstance(operation, int | float):
        return []

    if isinstance(
        operation,
        (
            LensFormulaCountAgg,
            LensFormulaUniqueCountAgg,
            LensFormulaSumAgg,
            LensFormulaAverageAgg,
            LensFormulaMinAgg,
            LensFormulaMaxAgg,
            LensFormulaMedianAgg,
        ),
    ):
        return [operation]

    aggregations: list[LensFormulaAggregations] = []

    if isinstance(operation, (LensFormulaAdd, LensFormulaSubtract, LensFormulaMultiply, LensFormulaDivide)):  # pyright: ignore[reportUnnecessaryIsInstance]
        if isinstance(operation, LensFormulaAdd):
            left_right = operation.add
        elif isinstance(operation, LensFormulaSubtract):
            left_right = operation.subtract
        elif isinstance(operation, LensFormulaMultiply):
            left_right = operation.multiply
        else:  # LensFormulaDivide
            left_right = operation.divide

        aggregations.extend(collect_aggregations(left_right.left))
        aggregations.extend(collect_aggregations(left_right.right))

    return aggregations


def compile_lens_metric(metric: LensMetricTypes) -> tuple[str, KbnLensMetricColumnTypes]:  # noqa: PLR0912, PLR0915
    """Compile a single LensMetricTypes object into its Kibana view model.

    Args:
        metric (LensMetricTypes): The LensMetricTypes object to compile.

    Returns:
        tuple[str, KbnColumn]: A tuple containing the metric ID and its compiled KbnColumn.

    """
    # Handle static values
    if isinstance(metric, LensStaticValue):
        metric_id = metric.id or stable_id_generator(['static_value', str(metric.value)])
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
        # Generate the human-readable formula string
        formula_string = build_formula_string(metric.operation)

        # Generate base metric ID
        base_metric_id = metric.id or stable_id_generator(['formula', formula_string])

        # Collect all aggregations from the formula
        aggregations = collect_aggregations(metric.operation)

        # Create aggregation columns and track their IDs
        agg_columns: dict[str, KbnLensFieldMetricColumn] = {}
        column_refs: dict[int, str] = {}

        for idx, agg in enumerate(aggregations):
            agg_id = f'{base_metric_id}X{idx}'
            column_refs[id(agg)] = agg_id

            # Determine aggregation type and create appropriate column
            if isinstance(agg, LensFormulaCountAgg):
                agg_filter = None
                if agg.count.filter is not None:
                    agg_filter = compile_nonesql_query(agg.count.filter)

                agg_columns[agg_id] = KbnLensFieldMetricColumn(
                    label=f'Part of {formula_string}',
                    customLabel=True,
                    dataType='number',
                    operationType='count',
                    scale='ratio',
                    sourceField='___records___',
                    params=KbnLensMetricColumnParams(emptyAsNull=False),
                    filter=agg_filter,
                )

            elif isinstance(agg, LensFormulaUniqueCountAgg):
                if agg.unique_count.field is None:
                    msg = 'unique_count aggregation requires a field'
                    raise ValueError(msg)

                agg_filter = None
                if agg.unique_count.filter is not None:
                    agg_filter = compile_nonesql_query(agg.unique_count.filter)

                agg_columns[agg_id] = KbnLensFieldMetricColumn(
                    label=f'Part of {formula_string}',
                    customLabel=True,
                    dataType='number',
                    operationType='unique_count',
                    scale='ratio',
                    sourceField=agg.unique_count.field,
                    params=KbnLensMetricColumnParams(emptyAsNull=False),
                    filter=agg_filter,
                )

            elif isinstance(agg, LensFormulaSumAgg):
                if agg.sum.field is None:
                    msg = 'sum aggregation requires a field'
                    raise ValueError(msg)

                agg_filter = None
                if agg.sum.filter is not None:
                    agg_filter = compile_nonesql_query(agg.sum.filter)

                agg_columns[agg_id] = KbnLensFieldMetricColumn(
                    label=f'Part of {formula_string}',
                    customLabel=True,
                    dataType='number',
                    operationType='sum',
                    scale='ratio',
                    sourceField=agg.sum.field,
                    params=KbnLensMetricColumnParams(emptyAsNull=False),
                    filter=agg_filter,
                )

            elif isinstance(agg, LensFormulaAverageAgg):
                if agg.average.field is None:
                    msg = 'average aggregation requires a field'
                    raise ValueError(msg)

                agg_filter = None
                if agg.average.filter is not None:
                    agg_filter = compile_nonesql_query(agg.average.filter)

                agg_columns[agg_id] = KbnLensFieldMetricColumn(
                    label=f'Part of {formula_string}',
                    customLabel=True,
                    dataType='number',
                    operationType='average',
                    scale='ratio',
                    sourceField=agg.average.field,
                    params=KbnLensMetricColumnParams(emptyAsNull=False),
                    filter=agg_filter,
                )

            elif isinstance(agg, LensFormulaMinAgg):
                if agg.min.field is None:
                    msg = 'min aggregation requires a field'
                    raise ValueError(msg)

                agg_filter = None
                if agg.min.filter is not None:
                    agg_filter = compile_nonesql_query(agg.min.filter)

                agg_columns[agg_id] = KbnLensFieldMetricColumn(
                    label=f'Part of {formula_string}',
                    customLabel=True,
                    dataType='number',
                    operationType='min',
                    scale='ratio',
                    sourceField=agg.min.field,
                    params=KbnLensMetricColumnParams(emptyAsNull=False),
                    filter=agg_filter,
                )

            elif isinstance(agg, LensFormulaMaxAgg):
                if agg.max.field is None:
                    msg = 'max aggregation requires a field'
                    raise ValueError(msg)

                agg_filter = None
                if agg.max.filter is not None:
                    agg_filter = compile_nonesql_query(agg.max.filter)

                agg_columns[agg_id] = KbnLensFieldMetricColumn(
                    label=f'Part of {formula_string}',
                    customLabel=True,
                    dataType='number',
                    operationType='max',
                    scale='ratio',
                    sourceField=agg.max.field,
                    params=KbnLensMetricColumnParams(emptyAsNull=False),
                    filter=agg_filter,
                )

            elif isinstance(agg, LensFormulaMedianAgg):  # pyright: ignore[reportUnnecessaryIsInstance]
                if agg.median.field is None:
                    msg = 'median aggregation requires a field'
                    raise ValueError(msg)

                agg_filter = None
                if agg.median.filter is not None:
                    agg_filter = compile_nonesql_query(agg.median.filter)

                agg_columns[agg_id] = KbnLensFieldMetricColumn(
                    label=f'Part of {formula_string}',
                    customLabel=True,
                    dataType='number',
                    operationType='median',
                    scale='ratio',
                    sourceField=agg.median.field,
                    params=KbnLensMetricColumnParams(emptyAsNull=False),
                    filter=agg_filter,
                )

        # Build the TinymathAST
        tinymath_ast = build_tinymath_ast(metric.operation, column_refs)

        # Ensure the AST is a dict (it should always be for the root operation)
        if not isinstance(tinymath_ast, dict):
            msg = f'Expected TinymathAST to be a dict, got {type(tinymath_ast)}'
            raise TypeError(msg)

        # Create math column
        math_id = f'{base_metric_id}X_math'
        math_column = KbnLensMathColumn(
            label=f'Part of {formula_string}',
            customLabel=True,
            params=KbnLensMathParams(tinymathAst=tinymath_ast),
            references=list(agg_columns.keys()),
        )

        # Create formula column
        formula_column = KbnLensFormulaColumn(
            label=metric.label or 'Formula',
            customLabel=custom_label,
            params=KbnLensFormulaParams(
                formula=formula_string,
                format=metric_format,
            ),
            references=[math_id],
        )

        # Return a special structure for formulas that includes all columns
        # We need to modify the return type to support multiple columns
        # For now, we'll return the formula column and store others separately
        # This requires changes to how compile_lens_metrics works

        # Store all columns in a way the caller can access them
        # We'll use a hack: store additional columns as an attribute
        formula_column._formula_helper_columns = {  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue]
            **agg_columns,
            math_id: math_column,
        }

        return base_metric_id, formula_column

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


def compile_lens_metrics(metrics: Sequence[LensMetricTypes]) -> dict[str, KbnLensMetricColumnTypes]:
    """Compile a sequence of LensMetricTypes into their Kibana view model representation.

    Args:
        metrics (Sequence[LensMetricTypes]): The sequence of LensMetricTypes objects to compile.

    Returns:
        dict[str, KbnLensMetricColumnTypes]: A dictionary of metric IDs to their compiled KbnLensColumnTypes.

    """
    compiled_metrics = [compile_lens_metric(metric) for metric in metrics]

    result_columns: dict[str, KbnLensMetricColumnTypes] = {}

    for metric_id, column in compiled_metrics:
        result_columns[metric_id] = column

        # If this is a formula column with helper columns, add them too
        if hasattr(column, '_formula_helper_columns'):
            helper_columns: dict[str, KbnLensMetricColumnTypes] = column._formula_helper_columns  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue, reportUnknownVariableType, reportUnknownMemberType]
            result_columns.update(helper_columns)  # pyright: ignore[reportUnknownArgumentType]
            # Clean up the temporary attribute
            delattr(column, '_formula_helper_columns')

    return result_columns
