"""Test the compilation of tagcloud charts from config models to view models using inline snapshots."""

from collections.abc import Callable
from typing import Any

import pytest
from dirty_equals import IsUUID
from inline_snapshot import snapshot

from dashboard_compiler.panels.charts.config import ESQLTagcloudPanelConfig
from dashboard_compiler.panels.charts.tagcloud.compile import (
    compile_esql_tagcloud_chart,
    compile_lens_tagcloud_chart,
)
from dashboard_compiler.panels.charts.tagcloud.config import LensTagcloudChart

# Type alias for the fixture return type
CompileTagcloudSnapshot = Callable[[dict[str, Any], str], dict[str, Any]]


@pytest.fixture
def compile_tagcloud_chart_snapshot() -> CompileTagcloudSnapshot:
    """Fixture that returns a function to compile tagcloud charts and return dict for snapshot."""

    def _compile(config: dict[str, Any], chart_type: str = 'lens') -> dict[str, Any]:
        if chart_type == 'lens':
            lens_chart = LensTagcloudChart.model_validate(config)
            _layer_id, _kbn_columns_by_id, kbn_state_visualization = compile_lens_tagcloud_chart(chart=lens_chart)
        else:  # esql
            esql_chart = ESQLTagcloudPanelConfig.model_validate(config)
            _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_tagcloud_chart(chart=esql_chart)

        assert kbn_state_visualization is not None
        # Tagcloud visualization state is flat (no layers array)
        return kbn_state_visualization.model_dump()

    return _compile


def test_basic_tagcloud_chart_lens(compile_tagcloud_chart_snapshot: CompileTagcloudSnapshot) -> None:
    """Test the compilation of a basic tagcloud chart (Lens)."""
    config = {
        'type': 'tagcloud',
        'data_view': 'logs-*',
        'tags': {
            'type': 'values',
            'field': 'tags',
            'id': '1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6',
        },
        'metrics': {
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
            'minFontSize': 12,
            'orientation': 'single',
            'showLabel': True,
        }
    )


def test_basic_tagcloud_chart_esql(compile_tagcloud_chart_snapshot: CompileTagcloudSnapshot) -> None:
    """Test the compilation of a basic tagcloud chart (ESQL)."""
    config = {
        'type': 'tagcloud',
        'query': 'FROM logs-* | STATS count(*) by tags',
        'tags': {
            'field': 'tags',
            'id': '1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6',
        },
        'metrics': {
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
            'minFontSize': 12,
            'orientation': 'single',
            'showLabel': True,
        }
    )


def test_tagcloud_chart_with_appearance_lens(compile_tagcloud_chart_snapshot: CompileTagcloudSnapshot) -> None:
    """Test the compilation of a tagcloud chart with custom appearance settings (Lens)."""
    config = {
        'type': 'tagcloud',
        'data_view': 'logs-*',
        'tags': {
            'type': 'values',
            'field': 'tags',
            'id': '1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6',
        },
        'metrics': {
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
        }
    )


def test_tagcloud_chart_with_appearance_esql(compile_tagcloud_chart_snapshot: CompileTagcloudSnapshot) -> None:
    """Test the compilation of a tagcloud chart with custom appearance settings (ESQL)."""
    config = {
        'type': 'tagcloud',
        'query': 'FROM logs-* | STATS count(*) by tags',
        'tags': {
            'field': 'tags',
            'id': '1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6',
        },
        'metrics': {
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
        }
    )


def test_tagcloud_right_angled_orientation_lens(compile_tagcloud_chart_snapshot: CompileTagcloudSnapshot) -> None:
    """Test tagcloud with right angled orientation (Lens)."""
    config = {
        'type': 'tagcloud',
        'data_view': 'logs-*',
        'tags': {
            'type': 'values',
            'field': 'tags',
            'id': 'tag-id-123',
        },
        'metrics': {
            'aggregation': 'count',
            'id': 'metric-id-456',
        },
        'appearance': {
            'orientation': 'right angled',
        },
    }

    result = compile_tagcloud_chart_snapshot(config, 'lens')

    assert result == snapshot(
        {
            'layerId': IsUUID,
            'tagAccessor': 'tag-id-123',
            'valueAccessor': 'metric-id-456',
            'maxFontSize': 72,
            'minFontSize': 12,
            'orientation': 'right angled',
            'showLabel': True,
        }
    )


def test_tagcloud_min_max_font_sizes_lens(compile_tagcloud_chart_snapshot: CompileTagcloudSnapshot) -> None:
    """Test tagcloud with extreme font size settings (Lens)."""
    config = {
        'type': 'tagcloud',
        'data_view': 'logs-*',
        'tags': {
            'type': 'values',
            'field': 'tags',
            'id': 'tag-id-789',
        },
        'metrics': {
            'aggregation': 'sum',
            'field': 'bytes',
            'id': 'metric-id-abc',
        },
        'appearance': {
            'min_font_size': 1,  # Minimum allowed
            'max_font_size': 200,  # Maximum allowed
        },
    }

    result = compile_tagcloud_chart_snapshot(config, 'lens')

    assert result == snapshot(
        {
            'layerId': IsUUID,
            'tagAccessor': 'tag-id-789',
            'valueAccessor': 'metric-id-abc',
            'maxFontSize': 200,
            'minFontSize': 1,
            'orientation': 'single',
            'showLabel': True,
        }
    )


def test_tagcloud_show_label_false_esql(compile_tagcloud_chart_snapshot: CompileTagcloudSnapshot) -> None:
    """Test tagcloud with labels hidden (ESQL)."""
    config = {
        'type': 'tagcloud',
        'query': 'FROM logs-* | STATS total = SUM(bytes) BY host.name',
        'tags': {
            'field': 'host.name',
            'id': 'host-dimension',
        },
        'metrics': {
            'field': 'total',
            'id': 'bytes-metric',
        },
        'appearance': {
            'show_label': False,
        },
    }

    result = compile_tagcloud_chart_snapshot(config, 'esql')

    assert result == snapshot(
        {
            'layerId': IsUUID,
            'tagAccessor': 'host-dimension',
            'valueAccessor': 'bytes-metric',
            'maxFontSize': 72,
            'minFontSize': 12,
            'orientation': 'single',
            'showLabel': False,
        }
    )


def test_tagcloud_partial_appearance_settings_lens(compile_tagcloud_chart_snapshot: CompileTagcloudSnapshot) -> None:
    """Test tagcloud with only some appearance settings provided (Lens)."""
    config = {
        'type': 'tagcloud',
        'data_view': 'logs-*',
        'tags': {
            'type': 'values',
            'field': 'user.name',
            'id': 'user-id',
        },
        'metrics': {
            'aggregation': 'count',
            'id': 'count-id',
        },
        'appearance': {
            'max_font_size': 120,  # Only set max, min should use default
        },
    }

    result = compile_tagcloud_chart_snapshot(config, 'lens')

    assert result == snapshot(
        {
            'layerId': IsUUID,
            'tagAccessor': 'user-id',
            'valueAccessor': 'count-id',
            'maxFontSize': 120,
            'minFontSize': 12,  # Default value
            'orientation': 'single',  # Default value
            'showLabel': True,  # Default value
        }
    )


def test_tagcloud_all_orientations_esql(compile_tagcloud_chart_snapshot: CompileTagcloudSnapshot) -> None:
    """Test all three orientation options (ESQL)."""
    configs = [
        ('single', 'single'),
        ('right angled', 'right angled'),
        ('multiple', 'multiple'),
    ]

    for orientation_value, expected_orientation in configs:
        config = {
            'type': 'tagcloud',
            'query': 'FROM logs-* | STATS count(*) BY service.name',
            'tags': {
                'field': 'service.name',
                'id': 'service-tag',
            },
            'metrics': {
                'field': 'count(*)',
                'id': 'service-count',
            },
            'appearance': {
                'orientation': orientation_value,
            },
        }

        result = compile_tagcloud_chart_snapshot(config, 'esql')

        # Verify orientation is correctly applied
        assert result['orientation'] == expected_orientation
