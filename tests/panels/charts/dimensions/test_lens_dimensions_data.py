"""Test data for Lens dimensions compilation tests."""

from typing import Any

type InputDimensionType = dict[str, Any]

type OutputDimensionType = dict[str, Any]

type InputMetricType = dict[str, Any]

type OutputMetricType = dict[str, Any]

type TestCaseType = tuple[InputDimensionType, InputMetricType, OutputMetricType, OutputDimensionType]

## Test cases in this file are organized in the following format:
# (input_dimension, input_metric, output_metric, output_dimension)

# Add more test cases for different dimension operations and field types.

INPUT_METRIC = {
    'aggregation': 'count',
    'id': '87416118-6032-41a2-aaf9-173fc0e525eb',
}

OUTPUT_METRIC = {
    'label': 'Count of records',
    'dataType': 'number',
    'operationType': 'count',
    'isBucketed': False,
    'scale': 'ratio',
    'sourceField': '___records___',
    'params': {
        'emptyAsNull': True,
    },
}

CASE_DATE_HISTOGRAM_DIMENSION: TestCaseType = (
    # Input dimension
    {'type': 'date_histogram', 'field': '@timestamp'},
    INPUT_METRIC,
    OUTPUT_METRIC,
    # Output dimension
    {
        'label': '@timestamp',
        'dataType': 'date',
        'operationType': 'date_histogram',
        'sourceField': '@timestamp',
        'isBucketed': True,
        'scale': 'interval',
        'params': {
            'interval': 'auto',
            'includeEmptyRows': True,
            'dropPartials': False,
        },
    },
)
"""Tuple[InDimension, InMetric, OutMetric, OutDimension] for date histogram dimension."""

CASE_TERMS_DIMENSION_SORTED: TestCaseType = (
    # Input dimension
    {
        'type': 'values',
        'field': 'agent.type',
        'sort': {
            'by': 'Count of records',
            'direction': 'desc',
        },
    },
    INPUT_METRIC,
    OUTPUT_METRIC,
    # Output dimension
    {
        'label': 'Top 3 values of agent.type',
        'dataType': 'string',
        'operationType': 'terms',
        'scale': 'ordinal',
        'sourceField': 'agent.type',
        'isBucketed': True,
        'params': {
            'size': 3,
            'orderBy': {'type': 'column', 'columnId': '87416118-6032-41a2-aaf9-173fc0e525eb'},
            'orderDirection': 'desc',
            'otherBucket': True,
            'missingBucket': False,
            'parentFormat': {'id': 'terms'},
            'include': [],
            'exclude': [],
            'includeIsRegex': False,
            'excludeIsRegex': False,
        },
    },
)
"""Tuple[InDimension, InMetric, OutMetric, OutDimension] for terms dimension with sorting."""

CASE_TERMS_DIMENSION_SORTED: TestCaseType = (
    # Input dimension
    {'type': 'values', 'field': 'agent.type', 'size': 10},
    INPUT_METRIC,
    OUTPUT_METRIC,
    # Output dimension
    {
        'label': 'Top 10 values of agent.type',
        'dataType': 'string',
        'operationType': 'terms',
        'scale': 'ordinal',
        'sourceField': 'agent.type',
        'isBucketed': True,
        'params': {
            'size': 10,
            'orderBy': {'type': 'column', 'columnId': '87416118-6032-41a2-aaf9-173fc0e525eb'},
            'orderDirection': 'desc',
            'otherBucket': True,
            'missingBucket': False,
            'parentFormat': {'id': 'terms'},
            'include': [],
            'exclude': [],
            'includeIsRegex': False,
            'excludeIsRegex': False,
        },
    },
)
"""Tuple[InDimension, InMetric, OutMetric, OutDimension] for terms dimension with sorting."""

CASE_FILTERS_DIMENSION: TestCaseType = (
    # Input dimension
    {
        'type': 'filters',
        'filters': [
            {'query': {'kql': 'agent.version: 8.*'}},
            {'query': {'kql': 'agent.version: 7.*'}},
        ],
    },
    INPUT_METRIC,
    OUTPUT_METRIC,
    # Output dimension
    {
        'label': 'Filters',
        'dataType': 'string',
        'operationType': 'filters',
        'scale': 'ordinal',
        'isBucketed': True,
        'params': {
            'filters': [
                {'label': '', 'input': {'query': 'agent.version: 8.*', 'language': 'kuery'}},
                {'input': {'query': 'agent.version: 7.*', 'language': 'kuery'}, 'label': ''},
            ]
        },
    },
)
"""Tuple[InDimension, InMetric, OutMetric, OutDimension] for filters dimension."""

CASE_INTERVALS_DIMENSION: TestCaseType = (
    # Input dimension
    {
        'type': 'intervals',
        'field': 'apache.uptime',
    },
    INPUT_METRIC,
    OUTPUT_METRIC,
    {
        'label': 'apache.uptime',
        'dataType': 'number',
        'operationType': 'range',
        'sourceField': 'apache.uptime',
        'isBucketed': True,
        'scale': 'interval',
        'params': {'includeEmptyRows': True, 'type': 'histogram', 'ranges': [{'from': 0, 'to': 1000, 'label': ''}], 'maxBars': 'auto'},
    },
)
"""Tuple[InDimension, InMetric, OutMetric, OutDimension] for intervals dimension."""


CASE_INTERVALS_DIMENSION_CUSTOM_GRANULARITY: TestCaseType = (
    # Input dimension
    {
        'type': 'intervals',
        'field': 'apache.uptime',
        'granularity': 2,
    },
    INPUT_METRIC,
    OUTPUT_METRIC,
    {
        'label': 'apache.uptime',
        'dataType': 'number',
        'operationType': 'range',
        'sourceField': 'apache.uptime',
        'isBucketed': True,
        'scale': 'interval',
        'params': {'includeEmptyRows': True, 'type': 'histogram', 'ranges': [{'from': 0, 'to': 1000, 'label': ''}], 'maxBars': 167.5},
    },
)
"""Tuple[InDimension, InMetric, OutMetric, OutDimension] for intervals dimension with custom granularity."""


CASE_INTERVALS_DIMENSION_CUSTOM_INTERVALS: TestCaseType = (
    # Input dimension
    {
        'type': 'intervals',
        'field': 'apache.uptime',
        'intervals': [
            {'to': 0},
            {'from': 0, 'to': 1000},
            {'from': 1000, 'to': 2000, 'label': 'Custom Label'},
            {'from': 2000},
        ],
    },
    INPUT_METRIC,
    OUTPUT_METRIC,
    {
        'label': 'apache.uptime',
        'dataType': 'string',
        'operationType': 'range',
        'sourceField': 'apache.uptime',
        'isBucketed': True,
        'scale': 'ordinal',
        'params': {
            'type': 'range',
            'ranges': [
                {'from': None, 'to': 0, 'label': ''},
                {'from': 0, 'to': 1000, 'label': ''},
                {'from': 1000, 'to': 2000, 'label': 'Custom Label'},
                {'from': 2000, 'to': None, 'label': ''},
            ],
            'maxBars': 499.5,
            'parentFormat': {'id': 'range', 'params': {'template': 'arrow_right', 'replaceInfinity': True}},
        },
    },
)
"""Tuple[InDimension, InMetric, OutMetric, OutDimension] for intervals dimension with custom intervals."""


TEST_CASES = [
    CASE_DATE_HISTOGRAM_DIMENSION,
    CASE_TERMS_DIMENSION_SORTED,
    CASE_FILTERS_DIMENSION,
    CASE_INTERVALS_DIMENSION,
    CASE_INTERVALS_DIMENSION_CUSTOM_GRANULARITY,
    CASE_INTERVALS_DIMENSION_CUSTOM_INTERVALS,
]

TEST_CASE_IDS = [
    'Date Histogram Dimension',
    'Terms Dimension with Sorting',
    'Filters Dimension',
    'Intervals Dimension',
    'Intervals Dimension with Custom Granularity',
    'Intervals Dimension with Custom Intervals',
]
