"""Compile Dashboard filter objects into their Kibana view model representations."""

from dashboard_compiler.filters import (
    AndFilter,
    CustomFilter,
    ExistsFilter,
    NegateFilter,
    OrFilter,
    PhraseFilter,
    PhrasesFilter,
    RangeFilter,
)
from dashboard_compiler.filters.config import FilterTypes
from dashboard_compiler.filters.view import KbnCombinedFilterMeta, KbnCustomFilterMeta, KbnFilter, KbnFilterMeta, KbnFilterState


def compile_exists_filter(*, exists_filter: ExistsFilter, negate: bool = False, nested: bool = False) -> KbnFilter:
    """Compile an ExistsFilter object into its Kibana view model representation.

    Args:
        exists_filter (ExistsFilter): The ExistsFilter object to compile.
        negate (bool): Whether to negate the filter. Defaults to False.
        nested (bool): Whether the filter is nested within another filter. Defaults to False.

    Returns:
        KbnFilter: The compiled Kibana filter view model.
    """
    meta = KbnFilterMeta(
        type='exists',
        key=exists_filter.exists,
        field=exists_filter.exists,
        disabled=exists_filter.disabled or False,
        negate=negate,
    )

    return KbnFilter(
        meta=meta,
        state=KbnFilterState() if not nested else None,
        query={'exists': {'field': exists_filter.exists}},
    )


def compile_custom_filter(*, custom_filter: CustomFilter, negate: bool = False, nested: bool = False) -> KbnFilter:
    """Compile a custom filter object into its Kibana view model representation.

    Args:
        custom_filter (CustomFilter): The CustomFilter object to compile.
        negate (bool): Whether to negate the filter. Defaults to False.
        nested (bool): Whether the filter is nested within another filter. Defaults to False.

    Returns:
        KbnFilter: The compiled Kibana filter view model.
    """
    return KbnFilter(
        meta=KbnCustomFilterMeta(
            type='custom',
            disabled=False,
            negate=negate,
        ),
        state=KbnFilterState() if not nested else None,
        query=custom_filter.dsl,
    )


def compile_phrase_filter(*, phrase_filter: PhraseFilter, negate: bool = False, nested: bool = False) -> KbnFilter:
    """Compile a PhraseFilter object into its Kibana view model representation.

    Args:
        phrase_filter (PhraseFilter): The PhraseFilter object to compile.
        negate (bool): Whether to negate the filter. Defaults to False.
        nested (bool): Whether the filter is nested within another filter. Defaults to False.

    Returns:
        KbnFilter: The compiled Kibana filter view model.
    """
    meta = KbnFilterMeta(
        type='phrase',
        params={'query': phrase_filter.equals},
        disabled=phrase_filter.disabled or False,
        key=phrase_filter.field,
        field=phrase_filter.field,
        negate=negate,
    )

    return KbnFilter(
        meta=meta,
        state=KbnFilterState() if not nested else None,
        query={'match_phrase': {phrase_filter.field: phrase_filter.equals}},
    )


def compile_phrases_filter(*, phrases_filter: PhrasesFilter, negate: bool = False, nested: bool = False) -> KbnFilter:
    """Compile a PhrasesFilter object into its Kibana view model representation.

    Args:
        phrases_filter (PhrasesFilter): The PhrasesFilter object to compile.
        negate (bool): Whether to negate the filter. Defaults to False.
        nested (bool): Whether the filter is nested within another filter. Defaults to False.

    Returns:
        KbnFilter: The compiled Kibana filter view model.
    """
    meta = KbnFilterMeta(
        type='phrases',
        params=list(phrases_filter.in_list),
        disabled=phrases_filter.disabled or False,
        key=phrases_filter.field,
        field=phrases_filter.field,
        negate=negate,
    )

    return KbnFilter(
        meta=meta,
        state=KbnFilterState() if not nested else None,
        query={
            'bool': {
                'minimum_should_match': 1,
                'should': [{'match_phrase': {phrases_filter.field: value}} for value in phrases_filter.in_list],
            },
        },
    )


def compile_range_filter(*, range_filter: RangeFilter, negate: bool = False, nested: bool = False) -> KbnFilter:
    """Compile a RangeFilter object into its Kibana view model representation.

    Args:
        range_filter (RangeFilter): The Filter object to compile.
        negate (bool): Whether to negate the filter. Defaults to False.
        nested (bool): Whether the filter is nested within another filter. Defaults to False.

    Returns:
        KbnFilter: The compiled Kibana filter view model.
    """
    range_query = {}

    if range_filter.gte is not None:
        range_query['gte'] = range_filter.gte
    if range_filter.lte is not None:
        range_query['lte'] = range_filter.lte
    if range_filter.gt is not None:
        range_query['gt'] = range_filter.gt
    if range_filter.lt is not None:
        range_query['lt'] = range_filter.lt

    return KbnFilter(
        meta=KbnFilterMeta(
            type='range',
            params=range_query,
            disabled=range_filter.disabled or False,
            key=range_filter.field,
            field=range_filter.field,
            negate=negate,
        ),
        state=KbnFilterState() if not nested else None,
        query={'range': {range_filter.field: range_query}},
    )


def compile_and_filter(*, and_filter: AndFilter, negate: bool = False, nested: bool = False) -> KbnFilter:
    """Compile an AndFilter object into its Kibana view model representation.

    Args:
        and_filter (AndFilter): The AndFilter object to compile.
        negate (bool): Whether to negate the filter. Defaults to False.
        nested (bool): Whether the filter is nested within another filter. Defaults to False.

    Returns:
        KbnFilter: The compiled Kibana filter view model.
    """
    return KbnFilter(
        meta=KbnCombinedFilterMeta(
            type='combined',
            relation='AND',
            params=[compile_filter(filter=sub_filter, negate=negate, nested=True) for sub_filter in and_filter.and_filters],
            disabled=and_filter.disabled or False,
            negate=negate,
        ),
        state=KbnFilterState() if not nested else None,
        query={},
    )


def compile_or_filter(*, or_filter: OrFilter, negate: bool = False, nested: bool = False) -> KbnFilter:
    """Compile an OrFilter object into its Kibana view model representation.

    Args:
        or_filter (OrFilter): The OrFilter object to compile.
        negate (bool): Whether to negate the filter. Defaults to False.
        nested (bool): Whether the filter is nested within another filter. Defaults to False.

    Returns:
        KbnFilter: The compiled Kibana filter view model.
    """
    return KbnFilter(
        meta=KbnCombinedFilterMeta(
            type='combined',
            relation='OR',
            params=[compile_filter(filter=sub_filter, negate=negate, nested=True) for sub_filter in or_filter.or_filters],
            disabled=or_filter.disabled or False,
            negate=negate,
        ),
        state=KbnFilterState() if not nested else None,
        query={},
    )


def compile_filter(*, filter: FilterTypes, negate: bool = False, nested: bool = False) -> KbnFilter:  # noqa: A002, PLR0911
    """Compile a single filter object into its Kibana view model representation.

    Args:
        filter (FilterTypes): The filter object to compile.
        negate (bool): Whether to negate the filter. Defaults to False.
        nested (bool): Whether the filter is nested within another filter. Defaults to False.

    Returns:
        KbnFilter: The compiled Kibana filter view model.
    """
    if isinstance(filter, NegateFilter):
        return compile_filter(filter=filter.not_filter, negate=True, nested=nested)
    if isinstance(filter, ExistsFilter):
        return compile_exists_filter(exists_filter=filter, negate=negate, nested=nested)
    if isinstance(filter, PhraseFilter):
        return compile_phrase_filter(phrase_filter=filter, negate=negate, nested=nested)
    if isinstance(filter, PhrasesFilter):
        return compile_phrases_filter(phrases_filter=filter, negate=negate, nested=nested)
    if isinstance(filter, RangeFilter):
        return compile_range_filter(range_filter=filter, negate=negate, nested=nested)
    if isinstance(filter, CustomFilter):
        return compile_custom_filter(custom_filter=filter, negate=negate, nested=nested)
    if isinstance(filter, AndFilter):
        return compile_and_filter(and_filter=filter, negate=negate, nested=nested)
    if isinstance(filter, OrFilter):
        return compile_or_filter(or_filter=filter, negate=negate, nested=nested)

    msg = f'Unimplemented filter type: {type(filter)}'
    raise NotImplementedError(msg)


def compile_filters(*, filters: list[FilterTypes]) -> list[KbnFilter]:
    """Compile the filters of a Dashboard object into its Kibana view model representation.

    Args:
        filters (list[FilterTypes]): The list of filter objects to compile.

    Returns:
        list[KbnFilter]: The compiled list of Kibana filter view models.
    """
    return [compile_filter(filter=dashboard_filter) for dashboard_filter in filters]
