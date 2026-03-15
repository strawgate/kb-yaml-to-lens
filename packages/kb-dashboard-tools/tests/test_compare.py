"""Tests for dashboard comparison tool."""

import json
from pathlib import Path

import pytest

from kb_dashboard_tools.compare import compare_disassembled_dashboards


def _write_panel(output_dir: Path, filename: str, panel_type: str, title: str) -> None:
    panels_dir = output_dir / 'panels'
    panels_dir.mkdir(parents=True, exist_ok=True)
    panel_payload = {
        'type': panel_type,
        'title': title,
    }
    (panels_dir / filename).write_text(json.dumps(panel_payload), encoding='utf-8')


def test_compare_disassembled_dashboards_all_match(tmp_path: Path) -> None:
    """Comparison reports all panels matching when type order is identical."""
    original_dir = tmp_path / 'original'
    compiled_dir = tmp_path / 'compiled'

    _write_panel(original_dir, '000_panel_a_lens.json', 'lens', 'CPU Usage')
    _write_panel(original_dir, '001_panel_b_markdown.json', 'markdown', 'Summary')

    _write_panel(compiled_dir, '000_panel_a_lens.json', 'lens', 'CPU Usage')
    _write_panel(compiled_dir, '001_panel_b_markdown.json', 'markdown', 'Summary')

    result = compare_disassembled_dashboards(original_dir, compiled_dir)

    assert result.original_count == 2
    assert result.compiled_count == 2
    assert result.matching_panel_types == 2
    assert result.all_panels_match is True


def test_compare_disassembled_dashboards_detects_type_mismatch(tmp_path: Path) -> None:
    """Comparison reports per-index mismatches when panel types differ."""
    original_dir = tmp_path / 'original'
    compiled_dir = tmp_path / 'compiled'

    _write_panel(original_dir, '000_panel_a_lens.json', 'lens', 'CPU Usage')
    _write_panel(compiled_dir, '000_panel_a_markdown.json', 'markdown', 'CPU Usage')

    result = compare_disassembled_dashboards(original_dir, compiled_dir)

    assert result.original_count == 1
    assert result.compiled_count == 1
    assert result.matching_panel_types == 0
    assert result.all_panels_match is False
    assert result.panels[0].types_match is False


def test_compare_disassembled_dashboards_requires_panels_directory(tmp_path: Path) -> None:
    """Comparison fails when disassembled directory is missing panels/."""
    original_dir = tmp_path / 'original'
    compiled_dir = tmp_path / 'compiled'
    original_dir.mkdir()
    compiled_dir.mkdir()
    (original_dir / 'panels').mkdir()

    with pytest.raises(FileNotFoundError, match='Panels directory not found'):
        _ = compare_disassembled_dashboards(original_dir, compiled_dir)
