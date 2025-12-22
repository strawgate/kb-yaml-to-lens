"""Test the compilation of filters from config models to view models using inline snapshots."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel

from dashboard_compiler.filters.compile import compile_filters
from dashboard_compiler.filters.config import FilterTypes


class FilterHolder(BaseModel):
    """A holder for filter configurations to be used in tests."""

    filter: FilterTypes


@pytest.fixture
def compile_filter_snapshot() -> Callable[[dict], dict]:
    """Fixture that returns a function to compile filters and return dict for snapshot."""

    def _compile(config: dict) -> dict:
        filter_holder = FilterHolder.model_validate({'filter': config})
        kbn_filter = compile_filters(filters=[filter_holder.filter])[0]
        kbn_filter_as_dict = kbn_filter.model_dump()

        # Remove the $state field as it's dynamic and not important for testing
        if '$state' in kbn_filter_as_dict:
            del kbn_filter_as_dict['$state']

        return kbn_filter_as_dict

    return _compile


def test_compile_phrase_filter(compile_filter_snapshot):
    """Test the compilation of a phrase filter."""
    config = {'field': 'status', 'equals': 'active'}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        {
            'meta': {
                'disabled': False,
                'negate': False,
                'alias': None,
                'key': 'status',
                'field': 'status',
                'params': {'query': 'active'},
                'type': 'phrase',
            },
            'query': {'match_phrase': {'status': 'active'}},
        }
    )


def test_compile_exists_filter(compile_filter_snapshot):
    """Test the compilation of an exists filter."""
    config = {'exists': 'status'}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        {
            'meta': {
                'disabled': False,
                'negate': False,
                'alias': None,
                'key': 'status',
                'field': 'status',
                'type': 'exists',
            },
            'query': {'exists': {'field': 'status'}},
        }
    )


def test_compile_not_exists_filter(compile_filter_snapshot):
    """Test the compilation of a not exists filter."""
    config = {'not': {'exists': 'status'}}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        {
            'meta': {
                'disabled': False,
                'negate': True,
                'alias': None,
                'key': 'status',
                'field': 'status',
                'type': 'exists',
            },
            'query': {'exists': {'field': 'status'}},
        }
    )


def test_compile_phrase_negated_filter(compile_filter_snapshot):
    """Test the compilation of a negated phrase filter."""
    config = {'not': {'field': 'status', 'equals': 'active'}}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        {
            'meta': {
                'disabled': False,
                'negate': True,
                'alias': None,
                'key': 'status',
                'field': 'status',
                'params': {'query': 'active'},
                'type': 'phrase',
            },
            'query': {'match_phrase': {'status': 'active'}},
        }
    )


def test_compile_range_filter(compile_filter_snapshot):
    """Test the compilation of a range filter."""
    config = {'field': '@timestamp', 'gte': '0004-12-31T18:09:24.000-05:50', 'lt': '0009-12-31T18:09:24.000-05:50'}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        {
            'meta': {
                'disabled': False,
                'negate': False,
                'alias': None,
                'key': '@timestamp',
                'field': '@timestamp',
                'params': {'gte': '0004-12-31T18:09:24.000-05:50', 'lt': '0009-12-31T18:09:24.000-05:50'},
                'type': 'range',
            },
            'query': {'range': {'@timestamp': {'gte': '0004-12-31T18:09:24.000-05:50', 'lt': '0009-12-31T18:09:24.000-05:50'}}},
        }
    )


def test_compile_in_list_filter(compile_filter_snapshot):
    """Test the compilation of an in-list filter."""
    config = {'field': 'status', 'in': ['active', 'inactive']}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        {
            'meta': {
                'disabled': False,
                'negate': False,
                'alias': None,
                'key': 'status',
                'field': 'status',
                'params': ['active', 'inactive'],
                'type': 'phrases',
            },
            'query': {
                'bool': {
                    'minimum_should_match': 1,
                    'should': [
                        {'match_phrase': {'status': 'active'}},
                        {'match_phrase': {'status': 'inactive'}},
                    ],
                },
            },
        }
    )


def test_compile_compound_and_filter(compile_filter_snapshot):
    """Test the compilation of a compound AND filter with two sub-filters."""
    config = {
        'and': [
            {'field': 'status', 'in': ['a', 'b', 'c']},
            {'field': 'status_code', 'equals': 'a'},
        ],
    }
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        {
            'meta': {
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
            'query': {},
        }
    )


def test_compile_compound_or_filter(compile_filter_snapshot):
    """Test the compilation of a compound OR filter with two sub-filters."""
    config = {
        'or': [
            {'field': 'status', 'in': ['a', 'b', 'c']},
            {'field': 'status_code', 'equals': 'a'},
        ],
    }
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        {
            'meta': {
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
            'query': {},
        }
    )


def test_compile_compound_or_not_filter(compile_filter_snapshot):
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
        {
            'meta': {
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
            'query': {},
        }
    )


def test_compile_compound_or_and_filter(compile_filter_snapshot):
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
        {
            'meta': {
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
            'query': {},
        }
    )


def test_compile_query_dsl_filter(compile_filter_snapshot):
    """Test the compilation of a custom query DSL filter."""
    config = {'dsl': {'match_phrase': {'status': 'active'}}}
    result = compile_filter_snapshot(config)

    assert result == snapshot(
        {
            'meta': {'type': 'custom', 'disabled': False, 'negate': False, 'alias': None, 'key': 'query'},
            'query': {'match_phrase': {'status': 'active'}},
        }
    )
