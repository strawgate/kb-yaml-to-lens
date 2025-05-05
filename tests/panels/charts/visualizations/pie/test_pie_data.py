"""Test data for Lens metrics compilation tests."""

from typing import Any

type InLensConfigType = dict[str, Any]

type InESQLConfigType = dict[str, Any]

type OutLensShapeType = dict[str, Any]

type OutViewType = dict[str, Any]

type TestCaseType = tuple[InLensConfigType, InESQLConfigType, OutLensShapeType, OutViewType]


LENS_PIE_DIMENSION = {
    'field': 'aerospike.namespace.name',
    'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df',
}

LENS_PIE_METRIC = {'aggregation': 'count', 'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5'}

ESQL_PIE_METRIC = {
    'field': 'count(*)',
    'id': '8f020607-379e-4b54-bc9e-e5550e84f5d5',
}

ESQL_PIE_DIMENSION = {
    'field': 'aerospike.namespace.name',
    'id': '6e73286b-85cf-4343-9676-b7ee2ed0a3df',
}


CASE_PIE_CHART: TestCaseType = (
    {
        'type': 'pie',
        'metric': LENS_PIE_METRIC,
        'slice_by': [LENS_PIE_DIMENSION],
    },
    {
        'type': 'pie',
        'esql': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'metric': ESQL_PIE_METRIC,
        'slice_by': [ESQL_PIE_DIMENSION],
    },
    {
        'shape': 'pie',
    },
    {
        'layerId': 'a72f6386-04e9-4228-ab7a-6e5edb63ca4a',
        'primaryGroups': ['6e73286b-85cf-4343-9676-b7ee2ed0a3df'],
        'metrics': ['8f020607-379e-4b54-bc9e-e5550e84f5d5'],
        'numberDisplay': 'percent',
        'categoryDisplay': 'default',
        'legendDisplay': 'default',
        'nestedLegend': False,
        'layerType': 'data',
        'colorMapping': {
            'assignments': [],
            'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            'paletteId': 'eui_amsterdam_color_blind',
            'colorMode': {'type': 'categorical'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a pie chart."""

CASE_DONUT_CHART: TestCaseType = (
    {
        'type': 'pie',
        'metric': LENS_PIE_METRIC,
        'slice_by': [LENS_PIE_DIMENSION],
        'appearance': {
            'donut': 'medium',
        },
    },
    {
        'type': 'pie',
        'esql': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'metric': ESQL_PIE_METRIC,
        'slice_by': [ESQL_PIE_DIMENSION],
        'appearance': {
            'donut': 'medium',
        },
    },
    {
        'shape': 'donut',
    },
    {
        'layerId': 'a72f6386-04e9-4228-ab7a-6e5edb63ca4a',
        'primaryGroups': ['6e73286b-85cf-4343-9676-b7ee2ed0a3df'],
        'metrics': ['8f020607-379e-4b54-bc9e-e5550e84f5d5'],
        'numberDisplay': 'percent',
        'categoryDisplay': 'default',
        'legendDisplay': 'default',
        'nestedLegend': False,
        'layerType': 'data',
        'colorMapping': {
            'assignments': [],
            'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            'paletteId': 'eui_amsterdam_color_blind',
            'colorMode': {'type': 'categorical'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a donut chart."""

CASE_PIE_CHART_INSIDE_LABELS_INTEGER_VALUES: TestCaseType = (
    {
        'type': 'pie',
        'metric': LENS_PIE_METRIC,
        'slice_by': [LENS_PIE_DIMENSION],
        'titles_and_text': {
            'slice_labels': 'inside',
            'slice_values': 'integer',
        },
    },
    {
        'type': 'pie',
        'esql': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'metric': ESQL_PIE_METRIC,
        'slice_by': [ESQL_PIE_DIMENSION],
        'titles_and_text': {
            'slice_labels': 'inside',
            'slice_values': 'integer',
        },
    },
    {
        'shape': 'pie',
    },
    {
        'layerId': 'a72f6386-04e9-4228-ab7a-6e5edb63ca4a',
        'primaryGroups': ['6e73286b-85cf-4343-9676-b7ee2ed0a3df'],
        'metrics': ['8f020607-379e-4b54-bc9e-e5550e84f5d5'],
        'numberDisplay': 'value',
        'categoryDisplay': 'inside',
        'legendDisplay': 'default',
        'nestedLegend': False,
        'layerType': 'data',
        'colorMapping': {
            'assignments': [],
            'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            'paletteId': 'eui_amsterdam_color_blind',
            'colorMode': {'type': 'categorical'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a pie chart with inside labels and integer values."""

CASE_PIE_CHART_SHOW_LARGE_LEGEND_NO_TRUNCATE: TestCaseType = (
    {
        'type': 'pie',
        'metric': LENS_PIE_METRIC,
        'slice_by': [LENS_PIE_DIMENSION],
        'legend': {
            'visible': 'show',
            'width': 'large',
            'truncate_labels': 0,
        },
    },
    {
        'type': 'pie',
        'esql': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'metric': ESQL_PIE_METRIC,
        'slice_by': [ESQL_PIE_DIMENSION],
        'legend': {
            'visible': 'show',
            'width': 'large',
            'truncate_labels': 0,
        },
    },
    {
        'shape': 'pie',
    },
    {
        'layerId': 'a72f6386-04e9-4228-ab7a-6e5edb63ca4a',
        'primaryGroups': ['6e73286b-85cf-4343-9676-b7ee2ed0a3df'],
        'metrics': ['8f020607-379e-4b54-bc9e-e5550e84f5d5'],
        'numberDisplay': 'percent',
        'categoryDisplay': 'default',
        'legendDisplay': 'show',
        'nestedLegend': False,
        'layerType': 'data',
        'colorMapping': {
            'assignments': [],
            'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            'paletteId': 'eui_amsterdam_color_blind',
            'colorMode': {'type': 'categorical'},
        },
        'legendSize': 'large',
        'truncateLegend': False,
    },
)
"""Tuple[Config as Dict, View as Dict, References as List] for a pie chart with a large legend and no label truncation."""

TEST_CASES = [
    CASE_PIE_CHART,
    CASE_DONUT_CHART,
    CASE_PIE_CHART_INSIDE_LABELS_INTEGER_VALUES,
    CASE_PIE_CHART_SHOW_LARGE_LEGEND_NO_TRUNCATE,
]

TEST_CASE_IDS = [
    'Basic Pie Chart',
    'Basic Donut Chart',
    'Pie Chart with Inside Labels and Integer Values',
    'Pie Chart with Large Legend and No Label Truncation',
]
