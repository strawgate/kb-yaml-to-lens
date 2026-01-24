"""Decompile Kibana filters back to config models."""

from collections.abc import Sequence

from dashboard_compiler.filters.config import (
    AndFilter,
    CustomFilter,
    ExistsFilter,
    FilterTypes,
    NegateFilter,
    OrFilter,
    PhraseFilter,
    PhrasesFilter,
    RangeFilter,
)
from dashboard_compiler.filters.view import (
    KbnCombinedFilterMeta,
    KbnCustomFilterMeta,
    KbnFilter,
    KbnFilterMeta,
)
from dashboard_compiler.shared.decompile_context import DecompileContext


def decompile_exists_filter(meta: KbnFilterMeta) -> ExistsFilter:
    """Decompile an exists filter."""
    return ExistsFilter(
        exists=meta.field,
        alias=meta.alias,
        disabled=meta.disabled if meta.disabled else None,
    )


def decompile_phrase_filter(meta: KbnFilterMeta) -> PhraseFilter:
    """Decompile a phrase filter."""
    # meta.params is {'query': 'value'}
    params = meta.params
    value_str: str
    if isinstance(params, dict):
        value_obj: object = params.get('query', '')
        value_str = str(value_obj)
    else:
        value_str = ''

    return PhraseFilter(
        field=meta.field,
        equals=value_str,
        alias=meta.alias,
        disabled=meta.disabled if meta.disabled else None,
    )


def decompile_phrases_filter(meta: KbnFilterMeta) -> PhrasesFilter:
    """Decompile a phrases filter.

    Note: Using 'in' as keyword argument since it's the field alias.
    """
    # meta.params is a list of values
    params = meta.params
    values = [str(v) for v in params] if isinstance(params, list) else []

    # Use 'in' as the keyword since that's the field alias in config
    return PhrasesFilter.model_validate(
        {
            'field': meta.field,
            'in': values,
            'alias': meta.alias,
            'disabled': meta.disabled if meta.disabled else None,
        }
    )


def decompile_range_filter(meta: KbnFilterMeta) -> RangeFilter:
    """Decompile a range filter."""
    params = meta.params
    if not isinstance(params, dict):
        params = {}

    return RangeFilter(
        field=meta.field,
        gte=params.get('gte'),
        lte=params.get('lte'),
        gt=params.get('gt'),
        lt=params.get('lt'),
        alias=meta.alias,
        disabled=meta.disabled if meta.disabled else None,
    )


def decompile_custom_filter(kbn_filter: KbnFilter, meta: KbnCustomFilterMeta) -> CustomFilter:
    """Decompile a custom filter."""
    return CustomFilter.model_validate(
        {
            'dsl': kbn_filter.query or {},
            'alias': meta.alias,
            'disabled': meta.disabled if meta.disabled else None,
        }
    )


def decompile_combined_filter(
    meta: KbnCombinedFilterMeta,
    *,
    context: DecompileContext,
) -> AndFilter | OrFilter:
    """Decompile a combined (AND/OR) filter.

    Note: Using field aliases 'and' and 'or' as keyword arguments.
    """
    sub_filters = [decompile_filter(f, context=context) for f in (meta.params or [])]

    if meta.relation == 'AND':
        # Use 'and' as the keyword since that's the field alias in config
        return AndFilter.model_validate(
            {
                'and': sub_filters,
                'alias': meta.alias,
                'disabled': meta.disabled if meta.disabled else None,
            }
        )
    # Use 'or' as the keyword since that's the field alias in config
    return OrFilter.model_validate(
        {
            'or': sub_filters,
            'alias': meta.alias,
            'disabled': meta.disabled if meta.disabled else None,
        }
    )


def decompile_filter(
    kbn_filter: KbnFilter,
    *,
    context: DecompileContext,
) -> FilterTypes:
    """Decompile a single Kibana filter to config model.

    Args:
        kbn_filter: The Kibana filter view model.
        context: Decompilation context for warnings.

    Returns:
        The decompiled filter config model.

    """
    meta = kbn_filter.meta

    # Handle negation wrapping
    is_negated = meta.negate

    # Decompile based on filter type
    result: FilterTypes

    if isinstance(meta, KbnCombinedFilterMeta):
        result = decompile_combined_filter(meta, context=context)
    elif isinstance(meta, KbnCustomFilterMeta):
        result = decompile_custom_filter(kbn_filter, meta)
    elif isinstance(meta, KbnFilterMeta):  # pyright: ignore[reportUnnecessaryIsInstance]
        if meta.type == 'exists':
            result = decompile_exists_filter(meta)
        elif meta.type == 'phrase':
            result = decompile_phrase_filter(meta)
        elif meta.type == 'phrases':
            result = decompile_phrases_filter(meta)
        elif meta.type == 'range':
            result = decompile_range_filter(meta)
        else:
            context.warn(f'Unknown filter type: {meta.type}')
            result = CustomFilter.model_validate({'dsl': kbn_filter.query or {}})
    else:
        context.warn(f'Unknown filter meta type: {type(meta).__name__}')
        result = CustomFilter.model_validate({'dsl': kbn_filter.query or {}})

    # Wrap in NegateFilter if negated
    if is_negated:
        return NegateFilter(not_filter=result)

    return result


def decompile_filters(
    kbn_filters: Sequence[KbnFilter],
    *,
    context: DecompileContext,
) -> list[FilterTypes]:
    """Decompile a list of Kibana filters.

    Args:
        kbn_filters: The Kibana filter view models.
        context: Decompilation context for warnings.

    Returns:
        List of decompiled filter config models.

    """
    return [decompile_filter(f, context=context) for f in kbn_filters]
