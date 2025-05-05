"""Test data for Lens metrics compilation tests."""

from typing import Any

type TestCaseType = tuple[dict[str, Any], dict[str, Any]]

CASE_COUNT_METRIC: TestCaseType = (
    {
        'aggregation': 'count',
    },
    {
        'label': 'Count of records',
        'dataType': 'number',
        'operationType': 'count',
        'isBucketed': False,
        'scale': 'ratio',
        'sourceField': '___records___',
        'params': {'emptyAsNull': True},
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a count metric."""
CASE_SUM_METRIC: TestCaseType = (
    {
        'aggregation': 'sum',
        'field': 'aerospike.node.connection.open',
    },
    {
        'label': 'Sum of aerospike.node.connection.open',
        'dataType': 'number',
        'operationType': 'sum',
        'sourceField': 'aerospike.node.connection.open',
        'isBucketed': False,
        'scale': 'ratio',
        'params': {'emptyAsNull': True},
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a sum metric."""

CASE_SUM_VALUE_NUMBER_FORMAT: TestCaseType = (
    {
        'aggregation': 'sum',
        'field': 'aerospike.node.connection.open',
        'format': {'type': 'number'},
    },
    {
        'label': 'Sum of aerospike.node.connection.open',
        'dataType': 'number',
        'operationType': 'sum',
        'sourceField': 'aerospike.node.connection.open',
        'isBucketed': False,
        'scale': 'ratio',
        'params': {'format': {'id': 'number', 'params': {'decimals': 2}}, 'emptyAsNull': True},
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a sum metric with number format."""

CASE_SUM_VALUE_PCT_FORMAT = (
    {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'percent'}},
    {
        'label': 'Sum of aerospike.node.connection.open',
        'dataType': 'number',
        'operationType': 'sum',
        'sourceField': 'aerospike.node.connection.open',
        'isBucketed': False,
        'scale': 'ratio',
        'params': {'format': {'id': 'percent', 'params': {'decimals': 2}}, 'emptyAsNull': True},
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a sum metric with percent format."""

CASE_SUM_VALUE_BYTES_FORMAT = (
    {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'bytes'}},
    {
        'label': 'Sum of aerospike.node.connection.open',
        'dataType': 'number',
        'operationType': 'sum',
        'sourceField': 'aerospike.node.connection.open',
        'isBucketed': False,
        'scale': 'ratio',
        'params': {'format': {'id': 'bytes', 'params': {'decimals': 2}}, 'emptyAsNull': True},
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a sum metric with bytes format."""

CASE_SUM_VALUE_BITS_FORMAT = (
    {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'bits'}},
    {
        'label': 'Sum of aerospike.node.connection.open',
        'dataType': 'number',
        'operationType': 'sum',
        'sourceField': 'aerospike.node.connection.open',
        'isBucketed': False,
        'scale': 'ratio',
        'params': {'format': {'id': 'bits', 'params': {'decimals': 0}}, 'emptyAsNull': True},
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a sum metric with bits format."""

CASE_SUM_VALUE_DURATION_FORMAT = (
    {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'duration'}},
    {
        'label': 'Sum of aerospike.node.connection.open',
        'dataType': 'number',
        'operationType': 'sum',
        'sourceField': 'aerospike.node.connection.open',
        'isBucketed': False,
        'scale': 'ratio',
        'params': {'format': {'id': 'duration', 'params': {'decimals': 0}}, 'emptyAsNull': True},
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a sum metric with duration format."""

CASE_SUM_VALUE_CUSTOM_FORMAT = (
    {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'custom', 'pattern': '0,0.[0000]'}},
    {
        'label': 'Sum of aerospike.node.connection.open',
        'dataType': 'number',
        'operationType': 'sum',
        'sourceField': 'aerospike.node.connection.open',
        'isBucketed': False,
        'scale': 'ratio',
        'params': {'format': {'id': 'custom', 'params': {'decimals': 0, 'pattern': '0,0.[0000]'}}, 'emptyAsNull': True},
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a sum metric with custom format."""

CASE_SUM_VALUE_NUMBER_FORMAT_WITH_SUFFIX: TestCaseType = (
    {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'number', 'suffix': 'KB'}},
    {
        'label': 'Sum of aerospike.node.connection.open',
        'dataType': 'number',
        'operationType': 'sum',
        'sourceField': 'aerospike.node.connection.open',
        'isBucketed': False,
        'scale': 'ratio',
        'params': {'format': {'id': 'number', 'params': {'decimals': 2, 'suffix': 'KB'}}, 'emptyAsNull': True},
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a sum metric with number format and suffix."""

CASE_SUM_VALUE_NUMBER_FORMAT_WITH_COMPACT: TestCaseType = (
    {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'number', 'compact': True}},
    {
        'label': 'Sum of aerospike.node.connection.open',
        'dataType': 'number',
        'operationType': 'sum',
        'sourceField': 'aerospike.node.connection.open',
        'isBucketed': False,
        'scale': 'ratio',
        'params': {'format': {'id': 'number', 'params': {'decimals': 2, 'compact': True}}, 'emptyAsNull': True},
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a sum metric with number format and compact."""

CASE_LAST_VALUE_METRIC: TestCaseType = (
    {
        'aggregation': 'last_value',
        'field': 'aerospike.namespace.query.count',
    },
    {
        'label': 'Last value of aerospike.namespace.query.count',
        'dataType': 'number',
        'operationType': 'last_value',
        'isBucketed': False,
        'scale': 'ratio',
        'sourceField': 'aerospike.namespace.query.count',
        'filter': {'query': '"aerospike.namespace.query.count": *', 'language': 'kuery'},
        'params': {'sortField': '@timestamp'},
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a last value metric."""

CASE_MIN_METRIC: TestCaseType = (
    {
        'aggregation': 'min',
        'field': 'aerospike.node.connection.open',
    },
    {
        'label': 'Minimum of aerospike.node.connection.open',
        'dataType': 'number',
        'operationType': 'min',
        'sourceField': 'aerospike.node.connection.open',
        'isBucketed': False,
        'scale': 'ratio',
        'params': {'emptyAsNull': True},
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a min metric."""

CASE_MAX_METRIC: tuple[dict[str, Any], dict[str, Any]] = (
    {
        'aggregation': 'max',
        'field': 'aerospike.node.connection.open',
    },
    {
        'label': 'Maximum of aerospike.node.connection.open',
        'dataType': 'number',
        'operationType': 'max',
        'sourceField': 'aerospike.node.connection.open',
        'isBucketed': False,
        'scale': 'ratio',
        'params': {'emptyAsNull': True},
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a max metric."""

CASE_PCT_RANK_METRIC: tuple[dict[str, str | int], dict[str, Any]] = (
    {
        'aggregation': 'percentile_rank',
        'field': 'aerospike.node.connection.open',
        'rank': 5,
    },
    {
        'label': 'Percentile rank (5) of aerospike.node.connection.open',
        'dataType': 'number',
        'operationType': 'percentile_rank',
        'sourceField': 'aerospike.node.connection.open',
        'isBucketed': False,
        'scale': 'ratio',
        'params': {'value': 5},
    },
)

CASE_P95_METRIC: tuple[dict[str, str | int], dict[str, Any]] = (
    {
        'aggregation': 'percentile',
        'field': 'aerospike.node.connection.open',
        'percentile': 95,
    },
    {
        'label': '95th percentile of aerospike.node.connection.open',
        'dataType': 'number',
        'operationType': 'percentile',
        'sourceField': 'aerospike.node.connection.open',
        'isBucketed': False,
        'scale': 'ratio',
        'params': {'percentile': 95},
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a 95th percentile metric."""

TEST_CASES_LENS = [
    CASE_COUNT_METRIC,
    CASE_SUM_METRIC,
    CASE_SUM_VALUE_NUMBER_FORMAT,
    CASE_SUM_VALUE_PCT_FORMAT,
    CASE_SUM_VALUE_BYTES_FORMAT,
    CASE_SUM_VALUE_BITS_FORMAT,
    CASE_SUM_VALUE_DURATION_FORMAT,
    CASE_SUM_VALUE_CUSTOM_FORMAT,
    CASE_SUM_VALUE_NUMBER_FORMAT_WITH_SUFFIX,
    CASE_SUM_VALUE_NUMBER_FORMAT_WITH_COMPACT,
    CASE_LAST_VALUE_METRIC,
    CASE_MIN_METRIC,
    CASE_MAX_METRIC,
    CASE_PCT_RANK_METRIC,
    CASE_P95_METRIC,
]

TEST_CASE_IDS_LENS = [
    'Basic Count Metric',
    'Basic Sum Metric',
    'Sum Metric with Number Format',
    'Sum Metric with Percent Format',
    'Sum Metric with Bytes Format',
    'Sum Metric with Bits Format',
    'Sum Metric with Duration Format',
    'Sum Metric with Custom Format',
    'Sum Metric with Number Format and Suffix',
    'Sum Metric with Number Format and Compact',
    'Last Value Metric',
    'Min Metric',
    'Max Metric',
    'Percentile Rank Metric',
    '95th Percentile Metric',
]
