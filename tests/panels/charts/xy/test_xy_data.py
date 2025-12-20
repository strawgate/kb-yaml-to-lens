"""Test data for Lens metrics compilation tests."""

from typing import Any

type InLensConfigType = dict[str, Any]

type InESQLConfigType = dict[str, Any]

type OutViewType = dict[str, Any]

type TestCaseType = tuple[InLensConfigType, InESQLConfigType, OutViewType]


LENS_XY_DIMENSION = {
    'field': '@timestamp',
    'id': '451e4374-f869-4ee9-8569-3092cd16ac18',
}

LENS_XY_METRIC = {'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}

LENS_XY_BREAKDOWN = {
    'field': 'aerospike.namespace.name',
    'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
}

ESQL_XY_METRIC = {
    'field': 'count(*)',
    'id': 'f1c1076b-5312-4458-aa74-535c908194fe',
}

ESQL_XY_DIMENSION = {
    'field': '@timestamp',
    'id': '451e4374-f869-4ee9-8569-3092cd16ac18',
}

ESQL_XY_BREAKDOWN = {
    'field': 'aerospike.namespace.name',
    'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
}


CASE_BAR_STACKED_CHART: TestCaseType = (
    {
        'type': 'bar',
        'mode': 'stacked',
        'data_view': 'metrics-*',
        'dimensions': [LENS_XY_DIMENSION],
        'metrics': [LENS_XY_METRIC],
        'breakdown': LENS_XY_BREAKDOWN,
    },
    {
        'type': 'bar',
        'mode': 'stacked',
        #'esql': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'dimensions': [ESQL_XY_DIMENSION],
        'metrics': [ESQL_XY_METRIC],
        'breakdown': ESQL_XY_BREAKDOWN,
    },
    {
        'layerId': '6f7b3b27-cc23-4061-82e0-f5227c7c0ed9',
        'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
        'position': 'top',
        'seriesType': 'bar_stacked',
        'showGridlines': False,
        'layerType': 'data',
        'colorMapping': {
            'assignments': [],
            'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            'paletteId': 'eui_amsterdam_color_blind',
            'colorMode': {'type': 'categorical'},
        },
        'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
        'splitAccessor': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
    },
)
"""Tuple[Lens chart config, ESQL chart config, Kibana view config] for a bar stacked chart."""

CASE_BAR_UNSTACKED_CHART: TestCaseType = (
    {
        'type': 'bar',
        'mode': 'unstacked',
        'data_view': 'metrics-*',
        'dimensions': [LENS_XY_DIMENSION],
        'metrics': [LENS_XY_METRIC],
        'breakdown': LENS_XY_BREAKDOWN,
    },
    {
        'type': 'bar',
        'mode': 'unstacked',
        'dimensions': [ESQL_XY_DIMENSION],
        'metrics': [ESQL_XY_METRIC],
        'breakdown': ESQL_XY_BREAKDOWN,
    },
    {
        'layerId': '6f7b3b27-cc23-4061-82e0-f5227c7c0ed9',
        'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
        'position': 'top',
        'seriesType': 'bar_unstacked',
        'showGridlines': False,
        'layerType': 'data',
        'colorMapping': {
            'assignments': [],
            'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            'paletteId': 'eui_amsterdam_color_blind',
            'colorMode': {'type': 'categorical'},
        },
        'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
        'splitAccessor': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
    },
)
"""Tuple[Lens chart config, ESQL chart config, Kibana view config] for a bar unstacked chart."""

CASE_LINE_CHART: TestCaseType = (
    {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimensions': [LENS_XY_DIMENSION],
        'metrics': [LENS_XY_METRIC],
        'breakdown': LENS_XY_BREAKDOWN,
    },
    {
        'type': 'line',
        #'esql': 'FROM metrics-* | STATS count(*) by aerospike.namespace',
        'dimensions': [ESQL_XY_DIMENSION],
        'metrics': [ESQL_XY_METRIC],
        'breakdown': ESQL_XY_BREAKDOWN,
    },
    {
        'layerId': '6f7b3b27-cc23-4061-82e0-f5227c7c0ed9',
        'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
        'position': 'top',
        'seriesType': 'line',
        'showGridlines': False,
        'layerType': 'data',
        'colorMapping': {
            'assignments': [],
            'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            'paletteId': 'eui_amsterdam_color_blind',
            'colorMode': {'type': 'categorical'},
        },
        'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
        'splitAccessor': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
    },
)
"""Tuple[Lens chart config, ESQL chart config, Kibana view config] for a line chart."""
CASE_AREA_CHART: TestCaseType = (
    {
        'type': 'area',
        'data_view': 'metrics-*',
        'dimensions': [LENS_XY_DIMENSION],
        'metrics': [LENS_XY_METRIC],
        'breakdown': LENS_XY_BREAKDOWN,
    },
    {
        'type': 'area',
        'dimensions': [ESQL_XY_DIMENSION],
        'metrics': [ESQL_XY_METRIC],
        'breakdown': ESQL_XY_BREAKDOWN,
    },
    {
        'layerId': '6f7b3b27-cc23-4061-82e0-f5227c7c0ed9',
        'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
        'position': 'top',
        'seriesType': 'area',
        'showGridlines': False,
        'layerType': 'data',
        'colorMapping': {
            'assignments': [],
            'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            'paletteId': 'eui_amsterdam_color_blind',
            'colorMode': {'type': 'categorical'},
        },
        'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
        'splitAccessor': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
    },
)
"""Tuple[Lens chart config, ESQL chart config, Kibana view config] for a area chart."""

CASE_AREA_PERCENT_CHART: TestCaseType = (
    {
        'type': 'area',
        'mode': 'percentage',
        'data_view': 'metrics-*',
        'dimensions': [LENS_XY_DIMENSION],
        'metrics': [LENS_XY_METRIC],
        'breakdown': LENS_XY_BREAKDOWN,
    },
    {
        'type': 'area',
        'mode': 'percentage',
        'dimensions': [ESQL_XY_DIMENSION],
        'metrics': [ESQL_XY_METRIC],
        'breakdown': ESQL_XY_BREAKDOWN,
    },
    {
        'layerId': '6f7b3b27-cc23-4061-82e0-f5227c7c0ed9',
        'accessors': ['f1c1076b-5312-4458-aa74-535c908194fe'],
        'position': 'top',
        'seriesType': 'area_percentage_stacked',
        'showGridlines': False,
        'layerType': 'data',
        'colorMapping': {
            'assignments': [],
            'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            'paletteId': 'eui_amsterdam_color_blind',
            'colorMode': {'type': 'categorical'},
        },
        'xAccessor': '451e4374-f869-4ee9-8569-3092cd16ac18',
        'splitAccessor': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9',
    },
)
"""Tuple[Lens chart config, ESQL chart config, Kibana view config] for a area percent chart."""


TEST_CASES = [
    CASE_BAR_STACKED_CHART,
    CASE_BAR_UNSTACKED_CHART,
    CASE_LINE_CHART,
    CASE_AREA_CHART,
    CASE_AREA_PERCENT_CHART,
]

TEST_CASE_IDS = [
    'Basic Bar Stacked Chart',
    'Basic Bar Unstacked Chart',
    'Basic Line Chart',
    'Basic Area Chart',
    'Basic Area Percent Chart',
]
