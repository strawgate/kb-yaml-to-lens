"""Test data for filter compilation tests."""

CASE_PHRASE_FILTER = (
    {'field': 'status', 'equals': 'active'},
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
        '$state': {'store': 'appState'},
    },
)
"""Tuple[Config as Dict, View as Dict] for a `field is 'value'` filter"""

CASE_EXISTS_FILTER = (
    {'exists': 'status'},
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
        '$state': {'store': 'appState'},
    },
)
"""Tuple[Config as Dict, View as Dict] for a `field exists` filter"""

CASE_NOT_EXISTS_FILTER = (
    {'not': {'exists': 'status'}},
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
        '$state': {'store': 'appState'},
    },
)
"""Tuple[Config as Dict, View as Dict] for a `field not exists` filter"""

CASE_IN_LIST_FILTER = (
    {'field': 'status', 'in': ['active', 'inactive']},
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
        '$state': {'store': 'appState'},
    },
)
"""Tuple[Config as Dict, View as Dict] for a `field in [value a, value b]` filter"""

CASE_RANGE_FILTER = (
    {
        'field': '@timestamp',
        'gte': '0004-12-31T18:09:24.000-05:50',
        'lt': '0009-12-31T18:09:24.000-05:50',
    },
    {
        'meta': {
            'negate': False,
            'key': '@timestamp',
            'field': '@timestamp',
            'params': {'gte': '0004-12-31T18:09:24.000-05:50', 'lt': '0009-12-31T18:09:24.000-05:50'},
            'type': 'range',
            'disabled': False,
            'alias': None,
        },
        'query': {'range': {'@timestamp': {'gte': '0004-12-31T18:09:24.000-05:50', 'lt': '0009-12-31T18:09:24.000-05:50'}}},
        '$state': {'store': 'appState'},
    },
)
"""Tuple[Config as Dict, View as Dict] for a `field in range` filter with gte and lt"""

CASE_COMPOUND_AND_FILTER = (
    {
        'and': [
            {'field': 'status', 'in': ['a', 'b', 'c']},
            {'field': 'status_code', 'equals': 'a'},
        ],
    },
    {
        '$state': {'store': 'appState'},
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
    },
)
"""Tuple[Config as Dict, View as Dict] for a compound `and` filter with two sub-filters"""

CASE_COMPOUND_OR_FILTER = (
    {
        'or': [
            {'field': 'status', 'in': ['a', 'b', 'c']},
            {'field': 'status_code', 'equals': 'a'},
        ],
    },
    {
        '$state': {'store': 'appState'},
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
    },
)
"""Tuple[Config as Dict, View as Dict] for a compound `or` filter with two sub-filters"""


CASE_COMPOUND_OR_NOT_FILTER = (
    {
        'or': [
            {'field': 'status', 'in': ['a', 'b', 'c']},
            {
                'not': {'field': 'status_code', 'equals': 'a'},
            },
        ],
    },
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
        '$state': {'store': 'appState'},
    },
)
"""Tuple[Config as Dict, View as Dict] for a compound `or` filter with a negated sub-filter"""

CASE_COMPOUND_OR_AND_FILTER = (
    {
        'or': [
            {'field': 'status', 'in': ['a', 'b', 'c']},
            {
                'and': [
                    {'field': 'status_code', 'equals': 'a'},
                    {'exists': 'error.message'},
                ],
            },
        ],
    },
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
                    '$state': {'store': 'appState'},
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
        '$state': {'store': 'appState'},
    },
)
"""Tuple[Config as Dict, View as Dict] for a compound `or` filter with a compound `and` sub-filter"""

CASE_QUERY_DSL_FILTER = (
    {'dsl': {'match_phrase': {'status': 'active'}}},
    {
        'meta': {'type': 'custom', 'disabled': False, 'negate': False, 'alias': None, 'key': 'query'},
        '$state': {'store': 'appState'},
        'query': {'match_phrase': {'status': 'active'}},
    },
)
"""Tuple[Config as Dict, View as Dict] for a custom query DSL filter"""


TEST_CASES = [
    CASE_PHRASE_FILTER,
    CASE_EXISTS_FILTER,
    CASE_NOT_EXISTS_FILTER,
    CASE_IN_LIST_FILTER,
    CASE_RANGE_FILTER,
    CASE_COMPOUND_AND_FILTER,
    CASE_COMPOUND_OR_FILTER,
    CASE_COMPOUND_OR_NOT_FILTER,
    CASE_COMPOUND_OR_AND_FILTER,
    CASE_QUERY_DSL_FILTER,
]
TEST_CASE_IDS = [
    'phrase_filter',
    'exists_filter',
    'not_exists_filter',
    'in_list_filter',
    'range_filter',
    'compound_and_filter',
    'compound_or_filter',
    'compound_or_not_filter',
    'compound_or_and_filter',
    'query_dsl_filter',
]
