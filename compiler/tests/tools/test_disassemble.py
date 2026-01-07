"""Tests for dashboard disassembler tool."""

import json
from pathlib import Path

import pytest

from dashboard_compiler.tools.disassemble import disassemble_dashboard, parse_ndjson


def test_parse_ndjson_with_dashboard() -> None:
    """Test parsing NDJSON content containing a dashboard."""
    ndjson = """{"type":"dashboard","id":"test-id","attributes":{"title":"Test Dashboard"}}"""

    result = parse_ndjson(ndjson)

    assert result['type'] == 'dashboard'
    assert result['id'] == 'test-id'
    assert result['attributes']['title'] == 'Test Dashboard'


def test_parse_ndjson_with_multiple_objects() -> None:
    """Test parsing NDJSON with multiple objects, returns the dashboard."""
    ndjson = """{"type":"index-pattern","id":"test-pattern"}
{"type":"dashboard","id":"test-dashboard","attributes":{"title":"Test"}}
{"type":"visualization","id":"test-viz"}"""

    result = parse_ndjson(ndjson)

    assert result['type'] == 'dashboard'
    assert result['id'] == 'test-dashboard'


def test_parse_ndjson_without_dashboard() -> None:
    """Test parsing NDJSON that doesn't contain a dashboard."""
    ndjson = """{"type":"index-pattern","id":"test-pattern"}
{"type":"visualization","id":"test-viz"}"""

    with pytest.raises(ValueError, match='No dashboard object found'):
        _ = parse_ndjson(ndjson)


def test_parse_ndjson_with_empty_lines() -> None:
    """Test parsing NDJSON with empty lines."""
    ndjson = """
{"type":"index-pattern","id":"test-pattern"}

{"type":"dashboard","id":"test-dashboard","attributes":{"title":"Test"}}

"""

    result = parse_ndjson(ndjson)

    assert result is not None
    assert result['type'] == 'dashboard'


def test_disassemble_dashboard_metadata(tmp_path: Path) -> None:
    """Test disassembling dashboard metadata."""
    dashboard = {
        'id': 'test-dashboard-id',
        'type': 'dashboard',
        'version': 'WzEsMV0=',
        'coreMigrationVersion': '8.0.0',
        'typeMigrationVersion': '8.0.0',
        'managed': False,
        'created_at': '2024-01-01T00:00:00.000Z',
        'created_by': 'test-user',
        'updated_at': '2024-01-02T00:00:00.000Z',
        'updated_by': 'test-user',
        'attributes': {
            'title': 'Test Dashboard',
            'description': 'A test dashboard',
        },
    }

    _ = disassemble_dashboard(dashboard, tmp_path)

    metadata_file = tmp_path / 'metadata.json'
    assert metadata_file.exists()

    metadata = json.loads(metadata_file.read_text())
    assert metadata['id'] == 'test-dashboard-id'
    assert metadata['title'] == 'Test Dashboard'
    assert metadata['description'] == 'A test dashboard'
    assert metadata['version'] == 'WzEsMV0='


def test_disassemble_dashboard_options(tmp_path: Path) -> None:
    """Test disassembling dashboard options."""
    dashboard = {
        'id': 'test-id',
        'type': 'dashboard',
        'attributes': {
            'title': 'Test',
            'optionsJSON': json.dumps(
                {
                    'useMargins': True,
                    'syncColors': False,
                    'syncCursor': True,
                    'syncTooltips': False,
                    'hidePanelTitles': False,
                }
            ),
        },
    }

    _ = disassemble_dashboard(dashboard, tmp_path)

    options_file = tmp_path / 'options.json'
    assert options_file.exists()

    options = json.loads(options_file.read_text())
    assert options['useMargins'] is True
    assert options['syncColors'] is False


def test_disassemble_dashboard_options_as_object(tmp_path: Path) -> None:
    """Test disassembling dashboard options when provided as object instead of string."""
    dashboard = {
        'id': 'test-id',
        'type': 'dashboard',
        'attributes': {
            'title': 'Test',
            'optionsJSON': {
                'useMargins': True,
                'syncColors': False,
            },
        },
    }

    _ = disassemble_dashboard(dashboard, tmp_path)

    options_file = tmp_path / 'options.json'
    assert options_file.exists()

    options = json.loads(options_file.read_text())
    assert options['useMargins'] is True


def test_disassemble_dashboard_controls(tmp_path: Path) -> None:
    """Test disassembling dashboard controls."""
    dashboard = {
        'id': 'test-id',
        'type': 'dashboard',
        'attributes': {
            'title': 'Test',
            'controlGroupInput': {
                'controlStyle': 'oneLine',
                'chainingSystem': 'HIERARCHICAL',
                'panelsJSON': json.dumps(
                    {
                        'control-1': {
                            'type': 'optionsListControl',
                            'order': 0,
                        },
                    }
                ),
            },
        },
    }

    _ = disassemble_dashboard(dashboard, tmp_path)

    controls_file = tmp_path / 'controls.json'
    assert controls_file.exists()

    controls = json.loads(controls_file.read_text())
    assert controls['controlStyle'] == 'oneLine'
    assert controls['chainingSystem'] == 'HIERARCHICAL'


def test_disassemble_dashboard_filters(tmp_path: Path) -> None:
    """Test disassembling dashboard filters."""
    dashboard = {
        'id': 'test-id',
        'type': 'dashboard',
        'attributes': {
            'title': 'Test',
            'kibanaSavedObjectMeta': {
                'searchSourceJSON': json.dumps(
                    {
                        'query': {'query': '', 'language': 'kuery'},
                        'filter': [
                            {
                                'meta': {'disabled': False, 'alias': 'Test Filter'},
                                'query': {'match_phrase': {'field': 'value'}},
                            },
                        ],
                    }
                ),
            },
        },
    }

    _ = disassemble_dashboard(dashboard, tmp_path)

    filters_file = tmp_path / 'filters.json'
    assert filters_file.exists()

    filters = json.loads(filters_file.read_text())
    assert len(filters) == 1
    assert filters[0]['meta']['alias'] == 'Test Filter'


def test_disassemble_dashboard_no_filters(tmp_path: Path) -> None:
    """Test disassembling dashboard with no filters."""
    dashboard = {
        'id': 'test-id',
        'type': 'dashboard',
        'attributes': {
            'title': 'Test',
            'kibanaSavedObjectMeta': {
                'searchSourceJSON': json.dumps(
                    {
                        'query': {'query': '', 'language': 'kuery'},
                        'filter': [],
                    }
                ),
            },
        },
    }

    _ = disassemble_dashboard(dashboard, tmp_path)

    filters_file = tmp_path / 'filters.json'
    assert not filters_file.exists()


def test_disassemble_dashboard_references(tmp_path: Path) -> None:
    """Test disassembling dashboard references."""
    dashboard = {
        'id': 'test-id',
        'type': 'dashboard',
        'attributes': {'title': 'Test'},
        'references': [
            {
                'type': 'index-pattern',
                'id': 'logs-*',
                'name': 'ref-1',
            },
            {
                'type': 'index-pattern',
                'id': 'metrics-*',
                'name': 'ref-2',
            },
        ],
    }

    _ = disassemble_dashboard(dashboard, tmp_path)

    references_file = tmp_path / 'references.json'
    assert references_file.exists()

    references = json.loads(references_file.read_text())
    assert len(references) == 2
    assert references[0]['id'] == 'logs-*'
    assert references[1]['id'] == 'metrics-*'


def test_disassemble_dashboard_no_references(tmp_path: Path) -> None:
    """Test disassembling dashboard with no references."""
    dashboard = {
        'id': 'test-id',
        'type': 'dashboard',
        'attributes': {'title': 'Test'},
        'references': [],
    }

    _ = disassemble_dashboard(dashboard, tmp_path)

    references_file = tmp_path / 'references.json'
    assert not references_file.exists()


def test_disassemble_dashboard_panels(tmp_path: Path) -> None:
    """Test disassembling dashboard panels."""
    dashboard = {
        'id': 'test-id',
        'type': 'dashboard',
        'attributes': {
            'title': 'Test',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'panel-1',
                        'type': 'lens',
                        'gridData': {'x': 0, 'y': 0, 'w': 24, 'h': 15},
                    },
                    {
                        'panelIndex': 'panel-2',
                        'type': 'markdown',
                        'gridData': {'x': 24, 'y': 0, 'w': 24, 'h': 15},
                    },
                ]
            ),
        },
    }

    _ = disassemble_dashboard(dashboard, tmp_path)

    panels_dir = tmp_path / 'panels'
    assert panels_dir.exists()
    assert panels_dir.is_dir()

    panel_files = sorted(panels_dir.glob('*.json'))
    assert len(panel_files) == 2

    assert panel_files[0].name == '000_panel-1_lens.json'
    assert panel_files[1].name == '001_panel-2_markdown.json'

    panel_1 = json.loads(panel_files[0].read_text())
    assert panel_1['panelIndex'] == 'panel-1'
    assert panel_1['type'] == 'lens'


def test_disassemble_dashboard_panels_as_object(tmp_path: Path) -> None:
    """Test disassembling dashboard panels when provided as object instead of string."""
    dashboard = {
        'id': 'test-id',
        'type': 'dashboard',
        'attributes': {
            'title': 'Test',
            'panelsJSON': [
                {
                    'panelIndex': 'panel-1',
                    'type': 'lens',
                },
            ],
        },
    }

    _ = disassemble_dashboard(dashboard, tmp_path)

    panels_dir = tmp_path / 'panels'
    assert panels_dir.exists()

    panel_files = list(panels_dir.glob('*.json'))
    assert len(panel_files) == 1


def test_disassemble_dashboard_no_panels(tmp_path: Path) -> None:
    """Test disassembling dashboard with no panels."""
    dashboard = {
        'id': 'test-id',
        'type': 'dashboard',
        'attributes': {
            'title': 'Test',
            'panelsJSON': json.dumps([]),
        },
    }

    _ = disassemble_dashboard(dashboard, tmp_path)

    panels_dir = tmp_path / 'panels'
    assert not panels_dir.exists()


def test_disassemble_dashboard_complete(tmp_path: Path) -> None:
    """Test complete dashboard disassembly with all components."""
    dashboard = {
        'id': 'complete-dashboard',
        'type': 'dashboard',
        'version': 'WzEsMV0=',
        'coreMigrationVersion': '8.0.0',
        'typeMigrationVersion': '8.0.0',
        'managed': False,
        'created_at': '2024-01-01T00:00:00.000Z',
        'created_by': 'test-user',
        'updated_at': '2024-01-02T00:00:00.000Z',
        'updated_by': 'test-user',
        'attributes': {
            'title': 'Complete Dashboard',
            'description': 'A complete test dashboard',
            'optionsJSON': json.dumps({'useMargins': True}),
            'controlGroupInput': {'controlStyle': 'oneLine'},
            'kibanaSavedObjectMeta': {
                'searchSourceJSON': json.dumps(
                    {
                        'filter': [{'meta': {'alias': 'test'}}],
                    }
                ),
            },
            'panelsJSON': json.dumps(
                [
                    {'panelIndex': 'p1', 'type': 'lens'},
                    {'panelIndex': 'p2', 'type': 'markdown'},
                ]
            ),
        },
        'references': [{'type': 'index-pattern', 'id': 'logs-*'}],
    }

    _ = disassemble_dashboard(dashboard, tmp_path)

    assert (tmp_path / 'metadata.json').exists()
    assert (tmp_path / 'options.json').exists()
    assert (tmp_path / 'controls.json').exists()
    assert (tmp_path / 'filters.json').exists()
    assert (tmp_path / 'references.json').exists()
    assert (tmp_path / 'panels').exists()

    panel_files = list((tmp_path / 'panels').glob('*.json'))
    assert len(panel_files) == 2
