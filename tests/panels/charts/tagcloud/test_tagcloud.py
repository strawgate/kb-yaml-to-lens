"""Test the compilation of tagcloud charts from config models to view models using inline snapshots."""

from typing import Any

import pytest
from dirty_equals import IsUUID
from inline_snapshot import snapshot

from dashboard_compiler.panels.charts.tagcloud.compile import (
    compile_esql_tagcloud_chart,
    compile_lens_tagcloud_chart,
)
from dashboard_compiler.panels.charts.tagcloud.config import ESQLTagcloudChart, LensTagcloudChart


@pytest.fixture
def compile_tagcloud_chart_snapshot():
    """Fixture that returns a function to compile tagcloud charts and return dict for snapshot."""

    def _compile(config: dict[str, Any], chart_type: str = 'lens') -> dict[str, Any]:
        if chart_type == 'lens':
            lens_chart = LensTagcloudChart.model_validate(config)
            layer_id, kbn_columns_by_id, kbn_state_visualization = compile_lens_tagcloud_chart(chart=lens_chart)
        else:  # esql
            esql_chart = ESQLTagcloudChart.model_validate(config)
            layer_id, kbn_columns, kbn_state_visualization = compile_esql_tagcloud_chart(chart=esql_chart)

        assert kbn_state_visualization is not None
        assert len(kbn_state_visualization.layers) > 0
        kbn_state_visualization_layer = kbn_state_visualization.layers[0]
        return kbn_state_visualization_layer.model_dump()

    return _compile


def test_basic_tagcloud_chart_lens(compile_tagcloud_chart_snapshot):
    """Test the compilation of a basic tagcloud chart (Lens)."""
    config = {
        'type': 'tagcloud',
        'data_view': 'logs-*',
        'tags': {
            'field': 'tags',
            'id': '1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6',
        },
        'metric': {
            'aggregation': 'count',
            'id': '6p5o4n3m2l1k-0j9i-8h7g-6f5e-4d3c2b1a',
        },
    }

    result = compile_tagcloud_chart_snapshot(config, 'lens')

    assert result == snapshot(
        {
            'layerId': IsUUID,
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
        }
    )


def test_basic_tagcloud_chart_esql(compile_tagcloud_chart_snapshot):
    """Test the compilation of a basic tagcloud chart (ESQL)."""
    config = {
        'type': 'tagcloud',
        'esql': 'FROM logs-* | STATS count(*) by tags',
        'tags': {
            'field': 'tags',
            'id': '1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6',
        },
        'metric': {
            'field': 'count(*)',
            'id': '6p5o4n3m2l1k-0j9i-8h7g-6f5e-4d3c2b1a',
        },
    }

    result = compile_tagcloud_chart_snapshot(config, 'esql')

    assert result == snapshot(
        {
            'layerId': IsUUID,
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
        }
    )


def test_tagcloud_chart_with_appearance_lens(compile_tagcloud_chart_snapshot):
    """Test the compilation of a tagcloud chart with custom appearance settings (Lens)."""
    config = {
        'type': 'tagcloud',
        'data_view': 'logs-*',
        'tags': {
            'field': 'tags',
            'id': '1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6',
        },
        'metric': {
            'aggregation': 'count',
            'id': '6p5o4n3m2l1k-0j9i-8h7g-6f5e-4d3c2b1a',
        },
        'appearance': {
            'min_font_size': 12,
            'max_font_size': 96,
            'orientation': 'multiple',
            'show_label': False,
        },
        'color': {
            'palette': 'kibana_palette',
        },
    }

    result = compile_tagcloud_chart_snapshot(config, 'lens')

    assert result == snapshot(
        {
            'layerId': IsUUID,
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
        }
    )


def test_tagcloud_chart_with_appearance_esql(compile_tagcloud_chart_snapshot):
    """Test the compilation of a tagcloud chart with custom appearance settings (ESQL)."""
    config = {
        'type': 'tagcloud',
        'esql': 'FROM logs-* | STATS count(*) by tags',
        'tags': {
            'field': 'tags',
            'id': '1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6',
        },
        'metric': {
            'field': 'count(*)',
            'id': '6p5o4n3m2l1k-0j9i-8h7g-6f5e-4d3c2b1a',
        },
        'appearance': {
            'min_font_size': 12,
            'max_font_size': 96,
            'orientation': 'multiple',
            'show_label': False,
        },
        'color': {
            'palette': 'kibana_palette',
        },
    }

    result = compile_tagcloud_chart_snapshot(config, 'esql')

    assert result == snapshot(
        {
            'layerId': IsUUID,
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
        }
    )
