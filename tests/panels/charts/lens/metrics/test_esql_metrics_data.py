"""Test data for Lens metrics compilation tests."""

from typing import Any

type TestCaseType = tuple[dict[str, Any], dict[str, Any]]

CASE_COUNT_METRIC: TestCaseType = (
    {
        'id': 'ac345678-90ab-cdef-1234-567890abcdef',
        'field': 'count(*)',
    },
    {
        'fieldName': 'count(*)',
        'columnId': 'ac345678-90ab-cdef-1234-567890abcdef',
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a count metric."""

TEST_CASES_ESQL = [
    CASE_COUNT_METRIC,
]

TEST_CASE_IDS_ESQL = [
    'Basic Count Metric',
]
