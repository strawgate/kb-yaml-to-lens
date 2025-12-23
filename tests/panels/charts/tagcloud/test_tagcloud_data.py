"""Test data for tagcloud compilation tests."""

from typing import Any

type InLensConfigType = dict[str, Any]

type InESQLConfigType = dict[str, Any]

type OutLensShapeType = dict[str, Any]

type OutViewType = dict[str, Any]

type TestCaseType = tuple[InLensConfigType, InESQLConfigType, OutLensShapeType, OutViewType]


LENS_TAGCLOUD_DIMENSION = {
    'field': 'tags',
    'id': '1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6',
}

LENS_TAGCLOUD_METRIC = {'aggregation': 'count', 'id': '6p5o4n3m2l1k-0j9i-8h7g-6f5e-4d3c2b1a'}

ESQL_TAGCLOUD_METRIC = {
    'field': 'count(*)',
    'id': '6p5o4n3m2l1k-0j9i-8h7g-6f5e-4d3c2b1a',
}

ESQL_TAGCLOUD_DIMENSION = {
    'field': 'tags',
    'id': '1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6',
}


CASE_TAGCLOUD_CHART: TestCaseType = (
    {
        'type': 'tagcloud',
        'data_view': 'logs-*',
        'tags': LENS_TAGCLOUD_DIMENSION,
        'metric': LENS_TAGCLOUD_METRIC,
    },
    {
        'type': 'tagcloud',
        'esql': 'FROM logs-* | STATS count(*) by tags',
        'tags': ESQL_TAGCLOUD_DIMENSION,
        'metric': ESQL_TAGCLOUD_METRIC,
    },
    {},
    {
        'layerId': 'test-layer-id',
        'tagAccessor': '1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6',
        'valueAccessor': '6p5o4n3m2l1k-0j9i-8h7g-6f5e-4d3c2b1a',
        'maxFontSize': 72,
        'minFontSize': 18,
        'orientation': 'single',
        'showLabel': True,
        'layerType': 'data',
        'colorMapping': {
            'assignments': [],
            'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            'paletteId': 'eui_amsterdam_color_blind',
            'colorMode': {'type': 'categorical'},
        },
        'palette': {'name': 'default', 'type': 'palette'},
    },
)

CASE_TAGCLOUD_CHART_WITH_APPEARANCE: TestCaseType = (
    {
        'type': 'tagcloud',
        'data_view': 'logs-*',
        'tags': LENS_TAGCLOUD_DIMENSION,
        'metric': LENS_TAGCLOUD_METRIC,
        'appearance': {
            'min_font_size': 12,
            'max_font_size': 96,
            'orientation': 'multiple',
            'show_label': False,
        },
        'color': {
            'palette': 'kibana_palette',
        },
    },
    {
        'type': 'tagcloud',
        'esql': 'FROM logs-* | STATS count(*) by tags',
        'tags': ESQL_TAGCLOUD_DIMENSION,
        'metric': ESQL_TAGCLOUD_METRIC,
        'appearance': {
            'min_font_size': 12,
            'max_font_size': 96,
            'orientation': 'multiple',
            'show_label': False,
        },
        'color': {
            'palette': 'kibana_palette',
        },
    },
    {},
    {
        'layerId': 'test-layer-id',
        'tagAccessor': '1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6',
        'valueAccessor': '6p5o4n3m2l1k-0j9i-8h7g-6f5e-4d3c2b1a',
        'maxFontSize': 96,
        'minFontSize': 12,
        'orientation': 'multiple',
        'showLabel': False,
        'layerType': 'data',
        'colorMapping': {
            'assignments': [],
            'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            'paletteId': 'kibana_palette',
            'colorMode': {'type': 'categorical'},
        },
        'palette': {'name': 'kibana_palette', 'type': 'palette'},
    },
)


TEST_CASES = [
    CASE_TAGCLOUD_CHART,
    CASE_TAGCLOUD_CHART_WITH_APPEARANCE,
]

TEST_CASE_IDS = [
    'basic-tagcloud',
    'tagcloud-with-appearance',
]
