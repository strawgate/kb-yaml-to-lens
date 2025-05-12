"""Test data for Lens metrics compilation tests."""

from typing import Any

type TestCaseType = tuple[dict[str, Any], dict[str, Any]]

CASE_COUNT_FORMULA: TestCaseType = (
    {'formula': {'count': '___records___'}},
    {
        'c4313b68-0421-440d-9323-66c2c39bcc0f': {
            'label': '@timestamp',
            'dataType': 'date',
            'operationType': 'date_histogram',
            'sourceField': '@timestamp',
            'isBucketed': True,
            'scale': 'interval',
            'params': {'interval': 'auto', 'includeEmptyRows': True, 'dropPartials': False},
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18eX0': {
            'label': 'Part of count()',
            'dataType': 'number',
            'operationType': 'count',
            'isBucketed': False,
            'scale': 'ratio',
            'sourceField': '___records___',
            'params': {'emptyAsNull': False},
            'customLabel': True,
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18e': {
            'label': 'count()',
            'dataType': 'number',
            'operationType': 'formula',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {'formula': 'count()', 'isFormulaBroken': False},
            'references': ['3d670c2e-8a46-4d24-90b0-34900df3a18eX0'],
        },
    },
)

CASE_COUNT_FIELD_FORMULA: TestCaseType = (
    {'formula': {'count': 'aerospike.namespace'}},
    {
        'c4313b68-0421-440d-9323-66c2c39bcc0f': {
            'label': '@timestamp',
            'dataType': 'date',
            'operationType': 'date_histogram',
            'sourceField': '@timestamp',
            'isBucketed': True,
            'scale': 'interval',
            'params': {'interval': 'auto', 'includeEmptyRows': True, 'dropPartials': False},
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18eX0': {
            'label': 'Part of count(aerospike.namespace)',
            'dataType': 'number',
            'operationType': 'count',
            'isBucketed': False,
            'scale': 'ratio',
            'sourceField': 'aerospike.namespace',
            'params': {'emptyAsNull': False},
            'customLabel': True,
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18e': {
            'label': 'count(aerospike.namespace)',
            'dataType': 'number',
            'operationType': 'formula',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {'formula': 'count(aerospike.namespace)', 'isFormulaBroken': False},
            'references': ['3d670c2e-8a46-4d24-90b0-34900df3a18eX0'],
        },
    },
)

CASE_COUNT_MATH_FORMULA: TestCaseType = (
    {'formula': {'subtract': [{'constant': 1}, {'divide': [{'count': '___records___'}, {'count': '___records___'}]}]}},
    {
        'c4313b68-0421-440d-9323-66c2c39bcc0f': {
            'label': '@timestamp',
            'dataType': 'date',
            'operationType': 'date_histogram',
            'sourceField': '@timestamp',
            'isBucketed': True,
            'scale': 'interval',
            'params': {'interval': 'auto', 'includeEmptyRows': True, 'dropPartials': False},
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18eX0': {
            'label': 'Part of 1 - count() / count()',
            'dataType': 'number',
            'operationType': 'count',
            'isBucketed': False,
            'scale': 'ratio',
            'sourceField': '___records___',
            'params': {'emptyAsNull': False},
            'customLabel': True,
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18eX1': {
            'label': 'Part of 1 - count() / count()',
            'dataType': 'number',
            'operationType': 'count',
            'isBucketed': False,
            'scale': 'ratio',
            'sourceField': '___records___',
            'params': {'emptyAsNull': False},
            'customLabel': True,
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18eX2': {
            'label': 'Part of 1 - count() / count()',
            'dataType': 'number',
            'operationType': 'math',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {
                'tinymathAst': {
                    'type': 'function',
                    'name': 'subtract',
                    'args': [
                        1,
                        {
                            'type': 'function',
                            'name': 'divide',
                            'args': ['3d670c2e-8a46-4d24-90b0-34900df3a18eX0', '3d670c2e-8a46-4d24-90b0-34900df3a18eX1'],
                            'location': {'min': 3, 'max': 21},
                            'text': ' count() / count()',
                        },
                    ],
                    'location': {'min': 0, 'max': 21},
                    'text': '1 - count() / count()',
                }
            },
            'references': ['3d670c2e-8a46-4d24-90b0-34900df3a18eX0', '3d670c2e-8a46-4d24-90b0-34900df3a18eX1'],
            'customLabel': True,
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18e': {
            'label': '1 - count() / count()',
            'dataType': 'number',
            'operationType': 'formula',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {'formula': '1 - count() / count()', 'isFormulaBroken': False},
            'references': ['3d670c2e-8a46-4d24-90b0-34900df3a18eX2'],
        },
    },
)

CASE_COUNT_FIELD_KQL_FORMULA: TestCaseType = (
    {'formula': {'subtract': [1, {'count': {'field': 'aerospike.namespace', 'kql': 'aerospike.namespace :*'}}]}},
    {
        'c4313b68-0421-440d-9323-66c2c39bcc0f': {
            'label': '@timestamp',
            'dataType': 'date',
            'operationType': 'date_histogram',
            'sourceField': '@timestamp',
            'isBucketed': True,
            'scale': 'interval',
            'params': {'interval': 'auto', 'includeEmptyRows': True, 'dropPartials': False},
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18eX0': {
            'label': "Part of 1 - count(aerospike.namespace, kql='aerospike.namespace :*')",
            'dataType': 'number',
            'operationType': 'count',
            'isBucketed': False,
            'scale': 'ratio',
            'sourceField': 'aerospike.namespace',
            'filter': {'query': 'aerospike.namespace :*', 'language': 'kuery'},
            'params': {'emptyAsNull': False},
            'customLabel': True,
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18eX1': {
            'label': "Part of 1 - count(aerospike.namespace, kql='aerospike.namespace :*')",
            'dataType': 'number',
            'operationType': 'math',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {
                'tinymathAst': {
                    'type': 'function',
                    'name': 'subtract',
                    'args': [1, '3d670c2e-8a46-4d24-90b0-34900df3a18eX0'],
                    'location': {'min': 0, 'max': 60},
                    'text': "1 - count(aerospike.namespace, kql='aerospike.namespace :*')",
                }
            },
            'references': ['3d670c2e-8a46-4d24-90b0-34900df3a18eX0'],
            'customLabel': True,
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18e': {
            'label': "1 - count(aerospike.namespace, kql='aerospike.namespace :*')",
            'dataType': 'number',
            'operationType': 'formula',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {'formula': "1 - count(aerospike.namespace, kql='aerospike.namespace :*')", 'isFormulaBroken': False},
            'references': ['3d670c2e-8a46-4d24-90b0-34900df3a18eX1'],
        },
    },
)

CASE_COUNT_FIELD_LUCENE_FORMULA: TestCaseType = (
    {'formula': {'subtract': [1, {'count': {'field': 'aerospike.namespace', 'lucene': 'aerospike.namespace: dev'}}]}},
    {
        'c4313b68-0421-440d-9323-66c2c39bcc0f': {
            'label': '@timestamp',
            'dataType': 'date',
            'operationType': 'date_histogram',
            'sourceField': '@timestamp',
            'isBucketed': True,
            'scale': 'interval',
            'params': {'interval': 'auto', 'includeEmptyRows': True, 'dropPartials': False},
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18eX0': {
            'label': "Part of 1 - count(aerospike.namespace, lucene='aerospike.namespace: dev')",
            'dataType': 'number',
            'operationType': 'count',
            'isBucketed': False,
            'scale': 'ratio',
            'sourceField': 'aerospike.namespace',
            'filter': {'query': 'aerospike.namespace: dev', 'language': 'lucene'},
            'params': {'emptyAsNull': False},
            'customLabel': True,
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18eX1': {
            'label': "Part of 1 - count(aerospike.namespace, lucene='aerospike.namespace: dev')",
            'dataType': 'number',
            'operationType': 'math',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {
                'tinymathAst': {
                    'type': 'function',
                    'name': 'subtract',
                    'args': [1, '3d670c2e-8a46-4d24-90b0-34900df3a18eX0'],
                    'location': {'min': 0, 'max': 65},
                    'text': "1 - count(aerospike.namespace, lucene='aerospike.namespace: dev')",
                }
            },
            'references': ['3d670c2e-8a46-4d24-90b0-34900df3a18eX0'],
            'customLabel': True,
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18e': {
            'label': "1 - count(aerospike.namespace, lucene='aerospike.namespace: dev')",
            'dataType': 'number',
            'operationType': 'formula',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {'formula': "1 - count(aerospike.namespace, lucene='aerospike.namespace: dev')", 'isFormulaBroken': False},
            'references': ['3d670c2e-8a46-4d24-90b0-34900df3a18eX1'],
        },
    },
)

### Yaml Version

# formula:
#   subtract:
#   - add:
#     - subtract:
#       - count.field: "___records___"
#       - 1
#     - multiply:
#       - 2
#       - 3
#   - divide:
#     - 2
#     - 4

CASE_COUNT_CONSTANT_OPERATORS: TestCaseType = (
    {
        'formula': {
            'subtract': [
                {
                    'add': [
                        {
                            'subtract': [
                                {'count': {'field': '___records___'}},
                                1,
                            ],
                        },
                        {
                            'multiply': [2, 3],
                        },
                    ]
                },
                {
                    'divide': [2, 4],
                },
            ]
        },
    },
    {
        'c4313b68-0421-440d-9323-66c2c39bcc0f': {
            'label': '@timestamp',
            'dataType': 'date',
            'operationType': 'date_histogram',
            'sourceField': '@timestamp',
            'isBucketed': True,
            'scale': 'interval',
            'params': {'interval': 'auto', 'includeEmptyRows': True, 'dropPartials': False},
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18eX0': {
            'label': 'Part of count() - 1 + (2 * 3) - (2 / 4)',
            'dataType': 'number',
            'operationType': 'count',
            'isBucketed': False,
            'scale': 'ratio',
            'sourceField': '___records___',
            'params': {'emptyAsNull': False},
            'customLabel': True,
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18eX1': {
            'label': 'Part of count() - 1 + (2 * 3) - (2 / 4)',
            'dataType': 'number',
            'operationType': 'math',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {
                'tinymathAst': {
                    'type': 'function',
                    'name': 'subtract',
                    'args': [
                        {
                            'type': 'function',
                            'name': 'add',
                            'args': [
                                {'type': 'function', 'name': 'subtract', 'args': ['3d670c2e-8a46-4d24-90b0-34900df3a18eX0', 1]},
                                {
                                    'type': 'function',
                                    'name': 'multiply',
                                    'args': [2, 3],
                                    'location': {'min': 13, 'max': 22},
                                    'text': ' (2 * 3) ',
                                },
                            ],
                        },
                        {'type': 'function', 'name': 'divide', 'args': [2, 4], 'location': {'min': 23, 'max': 31}, 'text': ' (2 / 4)'},
                    ],
                    'location': {'min': 0, 'max': 31},
                    'text': 'count() - 1 + (2 * 3) - (2 / 4)',
                }
            },
            'references': ['3d670c2e-8a46-4d24-90b0-34900df3a18eX0'],
            'customLabel': True,
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18e': {
            'label': 'count() - 1 + (2 * 3) - (2 / 4)',
            'dataType': 'number',
            'operationType': 'formula',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {'formula': 'count() - 1 + (2 * 3) - (2 / 4)', 'isFormulaBroken': False},
            'references': ['3d670c2e-8a46-4d24-90b0-34900df3a18eX1'],
        },
    },
)

CASE_CUMULATIVE_SUM: TestCaseType = (
    {},
    {
        'c4313b68-0421-440d-9323-66c2c39bcc0f': {
            'label': '@timestamp',
            'dataType': 'date',
            'operationType': 'date_histogram',
            'sourceField': '@timestamp',
            'isBucketed': True,
            'scale': 'interval',
            'params': {'interval': 'auto', 'includeEmptyRows': True, 'dropPartials': False},
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18eX0': {
            'label': 'Part of cumulative_sum(max(aerospike.node.memory.free))',
            'dataType': 'number',
            'operationType': 'max',
            'sourceField': 'aerospike.node.memory.free',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {'emptyAsNull': False},
            'customLabel': True,
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18eX1': {
            'label': 'Part of cumulative_sum(max(aerospike.node.memory.free))',
            'dataType': 'number',
            'operationType': 'cumulative_sum',
            'isBucketed': False,
            'scale': 'ratio',
            'references': ['3d670c2e-8a46-4d24-90b0-34900df3a18eX0'],
            'customLabel': True,
        },
        '3d670c2e-8a46-4d24-90b0-34900df3a18e': {
            'label': 'cumulative_sum(max(aerospike.node.memory.free))',
            'dataType': 'number',
            'operationType': 'formula',
            'isBucketed': False,
            'scale': 'ratio',
            'params': {'formula': 'cumulative_sum(max(aerospike.node.memory.free))', 'isFormulaBroken': False},
            'references': ['3d670c2e-8a46-4d24-90b0-34900df3a18eX1'],
        },
    },
)

CASE_MANY_OPERATIONS: TestCaseType = (
    {},
    {
        'columns': {
            'c4313b68-0421-440d-9323-66c2c39bcc0f': {
                'label': '@timestamp',
                'dataType': 'date',
                'operationType': 'date_histogram',
                'sourceField': '@timestamp',
                'isBucketed': True,
                'scale': 'interval',
                'params': {'interval': 'auto', 'includeEmptyRows': True, 'dropPartials': False},
            },
            '3d670c2e-8a46-4d24-90b0-34900df3a18eX0': {
                'label': 'Part of average(aerospike.node.connection.open) + min(aerospike.node.connection.open) + max(aerospike.node.connection.open) + last_value(aerospike.node.connection.open) + sum(aerospike.node.connection.open) + unique_count(aerospike.node.connection.open)',
                'dataType': 'number',
                'operationType': 'average',
                'sourceField': 'aerospike.node.connection.open',
                'isBucketed': False,
                'scale': 'ratio',
                'params': {'emptyAsNull': False},
                'customLabel': True,
            },
            '3d670c2e-8a46-4d24-90b0-34900df3a18eX1': {
                'label': 'Part of average(aerospike.node.connection.open) + min(aerospike.node.connection.open) + max(aerospike.node.connection.open) + last_value(aerospike.node.connection.open) + sum(aerospike.node.connection.open) + unique_count(aerospike.node.connection.open)',
                'dataType': 'number',
                'operationType': 'min',
                'sourceField': 'aerospike.node.connection.open',
                'isBucketed': False,
                'scale': 'ratio',
                'params': {'emptyAsNull': False},
                'customLabel': True,
            },
            '3d670c2e-8a46-4d24-90b0-34900df3a18eX2': {
                'label': 'Part of average(aerospike.node.connection.open) + min(aerospike.node.connection.open) + max(aerospike.node.connection.open) + last_value(aerospike.node.connection.open) + sum(aerospike.node.connection.open) + unique_count(aerospike.node.connection.open)',
                'dataType': 'number',
                'operationType': 'max',
                'sourceField': 'aerospike.node.connection.open',
                'isBucketed': False,
                'scale': 'ratio',
                'params': {'emptyAsNull': False},
                'customLabel': True,
            },
            '3d670c2e-8a46-4d24-90b0-34900df3a18eX3': {
                'label': 'Part of average(aerospike.node.connection.open) + min(aerospike.node.connection.open) + max(aerospike.node.connection.open) + last_value(aerospike.node.connection.open) + sum(aerospike.node.connection.open) + unique_count(aerospike.node.connection.open)',
                'dataType': 'number',
                'operationType': 'last_value',
                'isBucketed': False,
                'scale': 'ratio',
                'sourceField': 'aerospike.node.connection.open',
                'filter': {'query': '"aerospike.node.connection.open": *', 'language': 'kuery'},
                'params': {'sortField': '@timestamp'},
                'customLabel': True,
            },
            '3d670c2e-8a46-4d24-90b0-34900df3a18eX4': {
                'label': 'Part of average(aerospike.node.connection.open) + min(aerospike.node.connection.open) + max(aerospike.node.connection.open) + last_value(aerospike.node.connection.open) + sum(aerospike.node.connection.open) + unique_count(aerospike.node.connection.open)',
                'dataType': 'number',
                'operationType': 'sum',
                'sourceField': 'aerospike.node.connection.open',
                'isBucketed': False,
                'scale': 'ratio',
                'params': {'emptyAsNull': False},
                'customLabel': True,
            },
            '3d670c2e-8a46-4d24-90b0-34900df3a18eX5': {
                'label': 'Part of average(aerospike.node.connection.open) + min(aerospike.node.connection.open) + max(aerospike.node.connection.open) + last_value(aerospike.node.connection.open) + sum(aerospike.node.connection.open) + unique_count(aerospike.node.connection.open)',
                'dataType': 'number',
                'operationType': 'unique_count',
                'scale': 'ratio',
                'sourceField': 'aerospike.node.connection.open',
                'isBucketed': False,
                'params': {'emptyAsNull': False},
                'customLabel': True,
            },
            '3d670c2e-8a46-4d24-90b0-34900df3a18eX6': {
                'label': 'Part of average(aerospike.node.connection.open) + min(aerospike.node.connection.open) + max(aerospike.node.connection.open) + last_value(aerospike.node.connection.open) + sum(aerospike.node.connection.open) + unique_count(aerospike.node.connection.open)',
                'dataType': 'number',
                'operationType': 'math',
                'isBucketed': False,
                'scale': 'ratio',
                'params': {
                    'tinymathAst': {
                        'type': 'function',
                        'name': 'add',
                        'args': [
                            {
                                'type': 'function',
                                'name': 'add',
                                'args': [
                                    {
                                        'type': 'function',
                                        'name': 'add',
                                        'args': [
                                            {
                                                'type': 'function',
                                                'name': 'add',
                                                'args': [
                                                    {
                                                        'type': 'function',
                                                        'name': 'add',
                                                        'args': [
                                                            '3d670c2e-8a46-4d24-90b0-34900df3a18eX0',
                                                            '3d670c2e-8a46-4d24-90b0-34900df3a18eX1',
                                                        ],
                                                    },
                                                    '3d670c2e-8a46-4d24-90b0-34900df3a18eX2',
                                                ],
                                            },
                                            '3d670c2e-8a46-4d24-90b0-34900df3a18eX3',
                                        ],
                                    },
                                    '3d670c2e-8a46-4d24-90b0-34900df3a18eX4',
                                ],
                            },
                            '3d670c2e-8a46-4d24-90b0-34900df3a18eX5',
                        ],
                        'location': {'min': 0, 'max': 245},
                        'text': 'average(aerospike.node.connection.open) + min(aerospike.node.connection.open) + max(aerospike.node.connection.open) + last_value(aerospike.node.connection.open) + sum(aerospike.node.connection.open) + unique_count(aerospike.node.connection.open)',
                    }
                },
            },
        }
    },
)

# CASE_COUNT_METRIC: TestCaseType = (
#     {
#         'aggregation': 'count',
#     },
#     {
#         'label': 'Count of records',
#         'dataType': 'number',
#         'operationType': 'count',
#         'isBucketed': False,
#         'scale': 'ratio',
#         'sourceField': '___records___',
#         'params': {'emptyAsNull': True},
#     },
# )
# """Tuple[Config as Dict, View as Dict, References as List] for a count metric."""
# CASE_SUM_METRIC: TestCaseType = (
#     {
#         'aggregation': 'sum',
#         'field': 'aerospike.node.connection.open',
#     },
#     {
#         'label': 'Sum of aerospike.node.connection.open',
#         'dataType': 'number',
#         'operationType': 'sum',
#         'sourceField': 'aerospike.node.connection.open',
#         'isBucketed': False,
#         'scale': 'ratio',
#         'params': {'emptyAsNull': True},
#     },
# )
# """Tuple[Config as Dict, View as Dict, References as List] for a sum metric."""

# CASE_SUM_VALUE_NUMBER_FORMAT: TestCaseType = (
#     {
#         'aggregation': 'sum',
#         'field': 'aerospike.node.connection.open',
#         'format': {'type': 'number'},
#     },
#     {
#         'label': 'Sum of aerospike.node.connection.open',
#         'dataType': 'number',
#         'operationType': 'sum',
#         'sourceField': 'aerospike.node.connection.open',
#         'isBucketed': False,
#         'scale': 'ratio',
#         'params': {'format': {'id': 'number', 'params': {'decimals': 2}}, 'emptyAsNull': True},
#     },
# )
# """Tuple[Config as Dict, View as Dict, References as List] for a sum metric with number format."""

# CASE_SUM_VALUE_PCT_FORMAT = (
#     {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'percent'}},
#     {
#         'label': 'Sum of aerospike.node.connection.open',
#         'dataType': 'number',
#         'operationType': 'sum',
#         'sourceField': 'aerospike.node.connection.open',
#         'isBucketed': False,
#         'scale': 'ratio',
#         'params': {'format': {'id': 'percent', 'params': {'decimals': 2}}, 'emptyAsNull': True},
#     },
# )
# """Tuple[Config as Dict, View as Dict, References as List] for a sum metric with percent format."""

# CASE_SUM_VALUE_BYTES_FORMAT = (
#     {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'bytes'}},
#     {
#         'label': 'Sum of aerospike.node.connection.open',
#         'dataType': 'number',
#         'operationType': 'sum',
#         'sourceField': 'aerospike.node.connection.open',
#         'isBucketed': False,
#         'scale': 'ratio',
#         'params': {'format': {'id': 'bytes', 'params': {'decimals': 2}}, 'emptyAsNull': True},
#     },
# )
# """Tuple[Config as Dict, View as Dict, References as List] for a sum metric with bytes format."""

# CASE_SUM_VALUE_BITS_FORMAT = (
#     {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'bits'}},
#     {
#         'label': 'Sum of aerospike.node.connection.open',
#         'dataType': 'number',
#         'operationType': 'sum',
#         'sourceField': 'aerospike.node.connection.open',
#         'isBucketed': False,
#         'scale': 'ratio',
#         'params': {'format': {'id': 'bits', 'params': {'decimals': 0}}, 'emptyAsNull': True},
#     },
# )
# """Tuple[Config as Dict, View as Dict, References as List] for a sum metric with bits format."""

# CASE_SUM_VALUE_DURATION_FORMAT = (
#     {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'duration'}},
#     {
#         'label': 'Sum of aerospike.node.connection.open',
#         'dataType': 'number',
#         'operationType': 'sum',
#         'sourceField': 'aerospike.node.connection.open',
#         'isBucketed': False,
#         'scale': 'ratio',
#         'params': {'format': {'id': 'duration', 'params': {'decimals': 0}}, 'emptyAsNull': True},
#     },
# )
# """Tuple[Config as Dict, View as Dict, References as List] for a sum metric with duration format."""

# CASE_SUM_VALUE_CUSTOM_FORMAT = (
#     {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'custom', 'pattern': '0,0.[0000]'}},
#     {
#         'label': 'Sum of aerospike.node.connection.open',
#         'dataType': 'number',
#         'operationType': 'sum',
#         'sourceField': 'aerospike.node.connection.open',
#         'isBucketed': False,
#         'scale': 'ratio',
#         'params': {'format': {'id': 'custom', 'params': {'decimals': 0, 'pattern': '0,0.[0000]'}}, 'emptyAsNull': True},
#     },
# )
# """Tuple[Config as Dict, View as Dict, References as List] for a sum metric with custom format."""

# CASE_SUM_VALUE_NUMBER_FORMAT_WITH_SUFFIX: TestCaseType = (
#     {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'number', 'suffix': 'KB'}},
#     {
#         'label': 'Sum of aerospike.node.connection.open',
#         'dataType': 'number',
#         'operationType': 'sum',
#         'sourceField': 'aerospike.node.connection.open',
#         'isBucketed': False,
#         'scale': 'ratio',
#         'params': {'format': {'id': 'number', 'params': {'decimals': 2, 'suffix': 'KB'}}, 'emptyAsNull': True},
#     },
# )
# """Tuple[Config as Dict, View as Dict, References as List] for a sum metric with number format and suffix."""

# CASE_SUM_VALUE_NUMBER_FORMAT_WITH_COMPACT: TestCaseType = (
#     {'aggregation': 'sum', 'field': 'aerospike.node.connection.open', 'format': {'type': 'number', 'compact': True}},
#     {
#         'label': 'Sum of aerospike.node.connection.open',
#         'dataType': 'number',
#         'operationType': 'sum',
#         'sourceField': 'aerospike.node.connection.open',
#         'isBucketed': False,
#         'scale': 'ratio',
#         'params': {'format': {'id': 'number', 'params': {'decimals': 2, 'compact': True}}, 'emptyAsNull': True},
#     },
# )
# """Tuple[Config as Dict, View as Dict, References as List] for a sum metric with number format and compact."""

# CASE_LAST_VALUE_METRIC: TestCaseType = (
#     {
#         'aggregation': 'last_value',
#         'field': 'aerospike.namespace.query.count',
#     },
#     {
#         'label': 'Last value of aerospike.namespace.query.count',
#         'dataType': 'number',
#         'operationType': 'last_value',
#         'isBucketed': False,
#         'scale': 'ratio',
#         'sourceField': 'aerospike.namespace.query.count',
#         'filter': {'query': '"aerospike.namespace.query.count": *', 'language': 'kuery'},
#         'params': {'sortField': '@timestamp'},
#     },
# )
# """Tuple[Config as Dict, View as Dict, References as List] for a last value metric."""

# CASE_MIN_METRIC: TestCaseType = (
#     {
#         'aggregation': 'min',
#         'field': 'aerospike.node.connection.open',
#     },
#     {
#         'label': 'Minimum of aerospike.node.connection.open',
#         'dataType': 'number',
#         'operationType': 'min',
#         'sourceField': 'aerospike.node.connection.open',
#         'isBucketed': False,
#         'scale': 'ratio',
#         'params': {'emptyAsNull': True},
#     },
# )
# """Tuple[Config as Dict, View as Dict, References as List] for a min metric."""

# CASE_MAX_METRIC: tuple[dict[str, Any], dict[str, Any]] = (
#     {
#         'aggregation': 'max',
#         'field': 'aerospike.node.connection.open',
#     },
#     {
#         'label': 'Maximum of aerospike.node.connection.open',
#         'dataType': 'number',
#         'operationType': 'max',
#         'sourceField': 'aerospike.node.connection.open',
#         'isBucketed': False,
#         'scale': 'ratio',
#         'params': {'emptyAsNull': True},
#     },
# )
# """Tuple[Config as Dict, View as Dict, References as List] for a max metric."""

# CASE_PCT_RANK_METRIC: tuple[dict[str, str | int], dict[str, Any]] = (
#     {
#         'aggregation': 'percentile_rank',
#         'field': 'aerospike.node.connection.open',
#         'rank': 5,
#     },
#     {
#         'label': 'Percentile rank (5) of aerospike.node.connection.open',
#         'dataType': 'number',
#         'operationType': 'percentile_rank',
#         'sourceField': 'aerospike.node.connection.open',
#         'isBucketed': False,
#         'scale': 'ratio',
#         'params': {'value': 5},
#     },
# )

# CASE_P95_METRIC: tuple[dict[str, str | int], dict[str, Any]] = (
#     {
#         'aggregation': 'percentile',
#         'field': 'aerospike.node.connection.open',
#         'percentile': 95,
#     },
#     {
#         'label': '95th percentile of aerospike.node.connection.open',
#         'dataType': 'number',
#         'operationType': 'percentile',
#         'sourceField': 'aerospike.node.connection.open',
#         'isBucketed': False,
#         'scale': 'ratio',
#         'params': {'percentile': 95},
#     },
# )
# """Tuple[Config as Dict, View as Dict, References as List] for a 95th percentile metric."""

# TEST_CASES_LENS = [
#     CASE_COUNT_METRIC,
#     CASE_SUM_METRIC,
#     CASE_SUM_VALUE_NUMBER_FORMAT,
#     CASE_SUM_VALUE_PCT_FORMAT,
#     CASE_SUM_VALUE_BYTES_FORMAT,
#     CASE_SUM_VALUE_BITS_FORMAT,
#     CASE_SUM_VALUE_DURATION_FORMAT,
#     CASE_SUM_VALUE_CUSTOM_FORMAT,
#     CASE_SUM_VALUE_NUMBER_FORMAT_WITH_SUFFIX,
#     CASE_SUM_VALUE_NUMBER_FORMAT_WITH_COMPACT,
#     CASE_LAST_VALUE_METRIC,
#     CASE_MIN_METRIC,
#     CASE_MAX_METRIC,
#     CASE_PCT_RANK_METRIC,
#     CASE_P95_METRIC,
# ]

# TEST_CASE_IDS_LENS = [
#     'Basic Count Metric',
#     'Basic Sum Metric',
#     'Sum Metric with Number Format',
#     'Sum Metric with Percent Format',
#     'Sum Metric with Bytes Format',
#     'Sum Metric with Bits Format',
#     'Sum Metric with Duration Format',
#     'Sum Metric with Custom Format',
#     'Sum Metric with Number Format and Suffix',
#     'Sum Metric with Number Format and Compact',
#     'Last Value Metric',
#     'Min Metric',
#     'Max Metric',
#     'Percentile Rank Metric',
#     '95th Percentile Metric',
# ]

TEST_CASES = [
    CASE_COUNT_FORMULA,
    CASE_COUNT_FIELD_FORMULA,
]

TEST_CASE_IDS = [
    'Basic Count Metric',
    'Basic Count Field Metric',
]
