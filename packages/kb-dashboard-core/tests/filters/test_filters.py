"""Test the compilation of filters from config models to view models using inline snapshots."""

from typing import Any

from dirty_equals import IsPartialDict
from inline_snapshot import snapshot
from pydantic import BaseModel

from kb_dashboard_core.filters.compile import compile_filters
from kb_dashboard_core.filters.config import FilterTypes


class FilterHolder(BaseModel):
    """A holder for filter configurations to be used in tests."""

    filter: FilterTypes


def compile_filter_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    """Compile filter config and return dict for snapshot testing."""
    filter_holder = FilterHolder.model_validate({'filter': config})
    kbn_filter = compile_filters(filters=[filter_holder.filter])[0]
    return kbn_filter.model_dump()


def test_compile_phrase_filter() -> None:
    """Test the compilation of a phrase filter."""
    config = {'field': 'status', 'equals': 'active'}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        IsPartialDict(
            meta={
                'disabled': False,
                'negate': False,
                'alias': None,
                'key': 'status',
                'field': 'status',
                'params': {'query': 'active'},
                'type': 'phrase',
            },
            query={'match_phrase': {'status': 'active'}},
        )
    )


def test_compile_exists_filter() -> None:
    """Test the compilation of an exists filter."""
    config = {'exists': 'status'}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        IsPartialDict(
            meta={
                'disabled': False,
                'negate': False,
                'alias': None,
                'key': 'status',
                'field': 'status',
                'type': 'exists',
            },
            query={'exists': {'field': 'status'}},
        )
    )


def test_compile_not_exists_filter() -> None:
    """Test the compilation of a not exists filter."""
    config = {'not': {'exists': 'status'}}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        IsPartialDict(
            meta={
                'disabled': False,
                'negate': True,
                'alias': None,
                'key': 'status',
                'field': 'status',
                'type': 'exists',
            },
            query={'exists': {'field': 'status'}},
        )
    )


def test_compile_phrase_negated_filter() -> None:
    """Test the compilation of a negated phrase filter."""
    config = {'not': {'field': 'status', 'equals': 'active'}}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        IsPartialDict(
            meta={
                'disabled': False,
                'negate': True,
                'alias': None,
                'key': 'status',
                'field': 'status',
                'params': {'query': 'active'},
                'type': 'phrase',
            },
            query={'match_phrase': {'status': 'active'}},
        )
    )


def test_compile_range_filter() -> None:
    """Test the compilation of a range filter."""
    config = {'field': '@timestamp', 'gte': '0004-12-31T18:09:24.000-05:50', 'lt': '0009-12-31T18:09:24.000-05:50'}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        IsPartialDict(
            meta={
                'disabled': False,
                'negate': False,
                'alias': None,
                'key': '@timestamp',
                'field': '@timestamp',
                'params': {'gte': '0004-12-31T18:09:24.000-05:50', 'lt': '0009-12-31T18:09:24.000-05:50'},
                'type': 'range',
            },
            query={'range': {'@timestamp': {'gte': '0004-12-31T18:09:24.000-05:50', 'lt': '0009-12-31T18:09:24.000-05:50'}}},
        )
    )


def test_compile_in_list_filter() -> None:
    """Test the compilation of an in-list filter."""
    config = {'field': 'status', 'in': ['active', 'inactive']}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        IsPartialDict(
            meta={
                'disabled': False,
                'negate': False,
                'alias': None,
                'key': 'status',
                'field': 'status',
                'params': ['active', 'inactive'],
                'type': 'phrases',
            },
            query={
                'bool': {
                    'minimum_should_match': 1,
                    'should': [
                        {'match_phrase': {'status': 'active'}},
                        {'match_phrase': {'status': 'inactive'}},
                    ],
                },
            },
        )
    )


def test_compile_compound_and_filter() -> None:
    """Test the compilation of a compound AND filter with two sub-filters."""
    config = {
        'and': [
            {'field': 'status', 'in': ['a', 'b', 'c']},
            {'field': 'status_code', 'equals': 'a'},
        ],
    }
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        IsPartialDict(
            meta={
                'type': 'combined',
                'relation': 'AND',
                'params': [
                    {
                        'query': {
                            'bool': {
                                'minimum_should_match': 1,
                                'should': [
                                    {'match_phrase': {'status': 'a'}},
                                    {'match_phrase': {'status': 'b'}},
                                    {'match_phrase': {'status': 'c'}},
                                ],
                            },
                        },
                        'meta': {
                            'negate': False,
                            'key': 'status',
                            'field': 'status',
                            'params': ['a', 'b', 'c'],
                            'type': 'phrases',
                            'disabled': False,
                            'alias': None,
                        },
                    },
                    {
                        'meta': {
                            'negate': False,
                            'key': 'status_code',
                            'field': 'status_code',
                            'params': {'query': 'a'},
                            'type': 'phrase',
                            'disabled': False,
                            'alias': None,
                        },
                        'query': {'match_phrase': {'status_code': 'a'}},
                    },
                ],
                'disabled': False,
                'negate': False,
                'alias': None,
            },
            query={},
        )
    )


def test_compile_compound_or_filter() -> None:
    """Test the compilation of a compound OR filter with two sub-filters."""
    config = {
        'or': [
            {'field': 'status', 'in': ['a', 'b', 'c']},
            {'field': 'status_code', 'equals': 'a'},
        ],
    }
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        IsPartialDict(
            meta={
                'type': 'combined',
                'relation': 'OR',
                'params': [
                    {
                        'query': {
                            'bool': {
                                'minimum_should_match': 1,
                                'should': [
                                    {'match_phrase': {'status': 'a'}},
                                    {'match_phrase': {'status': 'b'}},
                                    {'match_phrase': {'status': 'c'}},
                                ],
                            },
                        },
                        'meta': {
                            'negate': False,
                            'key': 'status',
                            'field': 'status',
                            'params': ['a', 'b', 'c'],
                            'type': 'phrases',
                            'disabled': False,
                            'alias': None,
                        },
                    },
                    {
                        'meta': {
                            'negate': False,
                            'key': 'status_code',
                            'field': 'status_code',
                            'params': {'query': 'a'},
                            'type': 'phrase',
                            'disabled': False,
                            'alias': None,
                        },
                        'query': {'match_phrase': {'status_code': 'a'}},
                    },
                ],
                'disabled': False,
                'negate': False,
                'alias': None,
            },
            query={},
        )
    )


def test_compile_compound_or_not_filter() -> None:
    """Test the compilation of a compound OR filter with a negated sub-filter."""
    config = {
        'or': [
            {'field': 'status', 'in': ['a', 'b', 'c']},
            {
                'not': {'field': 'status_code', 'equals': 'a'},
            },
        ],
    }
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        IsPartialDict(
            meta={
                'type': 'combined',
                'relation': 'OR',
                'params': [
                    {
                        'query': {
                            'bool': {
                                'minimum_should_match': 1,
                                'should': [
                                    {'match_phrase': {'status': 'a'}},
                                    {'match_phrase': {'status': 'b'}},
                                    {'match_phrase': {'status': 'c'}},
                                ],
                            },
                        },
                        'meta': {
                            'negate': False,
                            'key': 'status',
                            'field': 'status',
                            'params': ['a', 'b', 'c'],
                            'type': 'phrases',
                            'disabled': False,
                            'alias': None,
                        },
                    },
                    {
                        'meta': {
                            'negate': True,
                            'key': 'status_code',
                            'field': 'status_code',
                            'params': {'query': 'a'},
                            'type': 'phrase',
                            'disabled': False,
                            'alias': None,
                        },
                        'query': {'match_phrase': {'status_code': 'a'}},
                    },
                ],
                'disabled': False,
                'negate': False,
                'alias': None,
            },
            query={},
        )
    )


def test_compile_compound_or_and_filter() -> None:
    """Test the compilation of a compound OR filter with a nested compound AND sub-filter."""
    config = {
        'or': [
            {'field': 'status', 'in': ['a', 'b', 'c']},
            {
                'and': [
                    {'field': 'status_code', 'equals': 'a'},
                    {'exists': 'error.message'},
                ],
            },
        ],
    }
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        IsPartialDict(
            meta={
                'type': 'combined',
                'relation': 'OR',
                'params': [
                    {
                        'query': {
                            'bool': {
                                'minimum_should_match': 1,
                                'should': [
                                    {'match_phrase': {'status': 'a'}},
                                    {'match_phrase': {'status': 'b'}},
                                    {'match_phrase': {'status': 'c'}},
                                ],
                            },
                        },
                        'meta': {
                            'negate': False,
                            'key': 'status',
                            'field': 'status',
                            'params': ['a', 'b', 'c'],
                            'type': 'phrases',
                            'disabled': False,
                            'alias': None,
                        },
                    },
                    {
                        'meta': {
                            'type': 'combined',
                            'relation': 'AND',
                            'params': [
                                {
                                    'query': {'match_phrase': {'status_code': 'a'}},
                                    'meta': {
                                        'negate': False,
                                        'key': 'status_code',
                                        'field': 'status_code',
                                        'params': {'query': 'a'},
                                        'type': 'phrase',
                                        'disabled': False,
                                        'alias': None,
                                    },
                                },
                                {
                                    'meta': {
                                        'negate': False,
                                        'key': 'error.message',
                                        'field': 'error.message',
                                        'type': 'exists',
                                        'disabled': False,
                                        'alias': None,
                                    },
                                    'query': {'exists': {'field': 'error.message'}},
                                },
                            ],
                            'disabled': False,
                            'negate': False,
                            'alias': None,
                        },
                        'query': {},
                    },
                ],
                'disabled': False,
                'negate': False,
                'alias': None,
            },
            query={},
        )
    )


def test_compile_query_dsl_filter() -> None:
    """Test the compilation of a custom query DSL filter."""
    config = {'dsl': {'match_phrase': {'status': 'active'}}}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        IsPartialDict(
            meta={'type': 'custom', 'disabled': False, 'negate': False, 'alias': None, 'key': 'query'},
            query={'match_phrase': {'status': 'active'}},
        )
    )


def test_compile_range_filter_with_lte() -> None:
    """Test the compilation of a range filter with lte operator."""
    config = {'field': '@timestamp', 'lte': '2023-12-31T23:59:59.999Z'}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        IsPartialDict(
            meta={
                'disabled': False,
                'negate': False,
                'alias': None,
                'key': '@timestamp',
                'field': '@timestamp',
                'params': {'lte': '2023-12-31T23:59:59.999Z'},
                'type': 'range',
            },
            query={'range': {'@timestamp': {'lte': '2023-12-31T23:59:59.999Z'}}},
        )
    )


def test_compile_range_filter_with_gt() -> None:
    """Test the compilation of a range filter with gt operator."""
    config = {'field': 'count', 'gt': '100'}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        IsPartialDict(
            meta={
                'disabled': False,
                'negate': False,
                'alias': None,
                'key': 'count',
                'field': 'count',
                'params': {'gt': '100'},
                'type': 'range',
            },
            query={'range': {'count': {'gt': '100'}}},
        )
    )


def test_compile_range_filter_with_all_operators() -> None:
    """Test the compilation of a range filter with all range operators."""
    config = {'field': 'count', 'gte': '10', 'lte': '100', 'gt': '5', 'lt': '200'}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        IsPartialDict(
            meta={
                'disabled': False,
                'negate': False,
                'alias': None,
                'key': 'count',
                'field': 'count',
                'params': {'gte': '10', 'lte': '100', 'gt': '5', 'lt': '200'},
                'type': 'range',
            },
            query={'range': {'count': {'gte': '10', 'lte': '100', 'gt': '5', 'lt': '200'}}},
        )
    )
