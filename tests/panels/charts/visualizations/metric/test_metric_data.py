"""Test data for Lens metrics compilation tests."""

from typing import Any

type InLensConfigType = dict[str, Any]

type InESQLConfigType = dict[str, Any]

type OutViewType = dict[str, Any]


type TestCaseType = tuple[InLensConfigType, InESQLConfigType, OutViewType]


LENS_METRIC_PRIMARY = {
    'field': 'aerospike.namespace.name',
    'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
    'aggregation': 'count',
}

LENS_METRIC_SECONDARY = {
    'field': 'aerospike.node.name',
    'id': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
    'aggregation': 'unique_count',
}

LENS_METRIC_DIMENSION = {
    'type': 'values',
    'field': 'agent.name',
    'id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
}

ESQL_METRIC_PRIMARY = {
    'field': 'count(aerospike.namespace)',
    'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
}

ESQL_METRIC_SECONDARY = {
    'field': 'count_distinct(aerospike.node.name)',
    'id': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
}

ESQL_METRIC_DIMENSION = {
    'field': 'agent.name',
    'id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
}


CASE_METRIC_CHART_PRIMARY_ONLY: TestCaseType = (
    {
        'type': 'metric',
        'primary': LENS_METRIC_PRIMARY,
    },
    {
        'type': 'metric',
        'esql': 'FROM metrics-* | STATS count(aerospike.namespace)',
        'primary': ESQL_METRIC_PRIMARY,
    },
    {
        'layerId': '65632693-9b81-4142-8c92-5fce93aa49e5',
        'layerType': 'data',
        'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
    },
)
"""Tuple[Lens Config, ESQL Config, Lens View] for a metric chart with only a primary metric."""

CASE_METRIC_CHART_PRIMARY_AND_SECONDARY: TestCaseType = (
    {
        'type': 'metric',
        'primary': LENS_METRIC_PRIMARY,
        'secondary': LENS_METRIC_SECONDARY,
    },
    {
        'type': 'metric',
        'esql': 'FROM metrics-* | STATS count(aerospike.namespace), count_distinct(aerospike.node.name)',
        'primary': ESQL_METRIC_PRIMARY,
        'secondary': ESQL_METRIC_SECONDARY,
    },
    {
        'layerId': '65632693-9b81-4142-8c92-5fce93aa49e5',
        'layerType': 'data',
        'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
        'secondaryMetricAccessor': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
    },
)
"""Tuple[Lens Config, ESQL Config, Lens View] for a metric chart with a primary and secondary metric."""

CASE_METRIC_CHART_PRIMARY_AND_SECONDARY_AND_BREAKDOWN: TestCaseType = (
    {
        'type': 'metric',
        'primary': LENS_METRIC_PRIMARY,
        'secondary': LENS_METRIC_SECONDARY,
        'breakdown': LENS_METRIC_DIMENSION,
    },
    {
        'type': 'metric',
        'esql': 'FROM metrics-* | STATS count(aerospike.namespace), count_distinct(aerospike.node.name) by agent.name',
        'primary': ESQL_METRIC_PRIMARY,
        'secondary': ESQL_METRIC_SECONDARY,
        'breakdown': ESQL_METRIC_DIMENSION,
    },
    {
        'layerId': '65632693-9b81-4142-8c92-5fce93aa49e5',
        'layerType': 'data',
        'metricAccessor': '156e3e91-7bb6-406f-8ae5-cb409747953b',
        'secondaryMetricAccessor': 'a1ec5883-19b2-4ab9-b027-a13d6074128b',
        'breakdownByAccessor': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
    },
)
"""Tuple[Lens Config, ESQL Config, Lens View] for a metric chart with a primary and secondary metric and a breakdown."""

TEST_CASES = [
    CASE_METRIC_CHART_PRIMARY_ONLY,
    CASE_METRIC_CHART_PRIMARY_AND_SECONDARY,
    CASE_METRIC_CHART_PRIMARY_AND_SECONDARY_AND_BREAKDOWN,
]

TEST_CASE_IDS = [
    'Basic Metric Chart',
    'Metric Chart with Secondary Metric',
    'Metric Chart with Secondary Metric and Breakdown',
]
