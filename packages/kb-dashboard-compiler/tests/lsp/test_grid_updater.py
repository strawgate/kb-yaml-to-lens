"""Tests for grid updater utilities."""

import textwrap
from pathlib import Path

import pytest

from dashboard_compiler.dashboard_compiler import load
from dashboard_compiler.lsp import grid_updater


def _write_dashboard(tmp_path: Path) -> Path:
    content = textwrap.dedent("""
        dashboards:
          - name: "Test Dashboard"
            panels:
              - id: "panel-a"
                title: "Markdown A"
                size: {w: 10, h: 5}
                position: {x: 0, y: 0}
                markdown:
                  content: "Hello"
              - id: "panel-b"
                title: "Markdown B"
                size: {w: 10, h: 5}
                position: {x: 10, y: 0}
                markdown:
                  content: "World"
        """)
    yaml_path = tmp_path / 'dashboard.yaml'
    yaml_path.write_text(content, encoding='utf-8')
    return yaml_path


def test_update_panel_grid_by_id(tmp_path: Path) -> None:
    """Update a panel grid by panel id."""
    yaml_path = _write_dashboard(tmp_path)

    result = grid_updater.update_panel_grid(yaml_path.as_posix(), 'panel-a', {'x': 2, 'y': 3, 'w': 12, 'h': 6})
    assert result['success'] is True

    dashboards = load(yaml_path.as_posix())
    panel = dashboards[0].panels[0]
    assert panel.position.x == 2
    assert panel.position.y == 3
    assert panel.size.w == 12
    assert panel.size.h == 6


def test_update_panel_grid_by_index(tmp_path: Path) -> None:
    """Update a panel grid by index-based panel id."""
    yaml_path = _write_dashboard(tmp_path)

    result = grid_updater.update_panel_grid(yaml_path.as_posix(), 'panel_1', {'x': 4, 'y': 1, 'w': 8, 'h': 4})
    assert result['success'] is True

    dashboards = load(yaml_path.as_posix())
    panel = dashboards[0].panels[1]
    assert panel.position.x == 4
    assert panel.position.y == 1
    assert panel.size.w == 8
    assert panel.size.h == 4


def test_update_panel_grid_missing_keys(tmp_path: Path) -> None:
    """Return an error when grid coordinates are missing required keys."""
    yaml_path = _write_dashboard(tmp_path)

    result = grid_updater.update_panel_grid(yaml_path.as_posix(), 'panel-a', {'x': 0, 'y': 0, 'w': 10})
    assert result['success'] is False
    assert 'missing required keys' in result['error']


def test_update_panel_grid_invalid_values(tmp_path: Path) -> None:
    """Return an error when grid coordinates are invalid."""
    yaml_path = _write_dashboard(tmp_path)

    result = grid_updater.update_panel_grid(yaml_path.as_posix(), 'panel-a', {'x': -1, 'y': 0, 'w': 10, 'h': 5})
    assert result['success'] is False
    assert 'non-negative integers' in result['error']


def test_update_panel_grid_dashboard_index_out_of_range(tmp_path: Path) -> None:
    """Return an error when dashboard index is out of range."""
    yaml_path = _write_dashboard(tmp_path)

    result = grid_updater.update_panel_grid(
        yaml_path.as_posix(),
        'panel-a',
        {'x': 0, 'y': 0, 'w': 10, 'h': 5},
        dashboard_index=2,
    )
    assert result['success'] is False
    assert 'out of range' in result['error']


def test_update_panel_grid_invalid_panel_index(tmp_path: Path) -> None:
    """Return an error when index-based panel id is invalid (non-digit suffix falls back to ID lookup)."""
    yaml_path = _write_dashboard(tmp_path)

    # 'panel_x' has non-digit suffix, so it falls back to ID lookup and is not found
    result = grid_updater.update_panel_grid(yaml_path.as_posix(), 'panel_x', {'x': 0, 'y': 0, 'w': 10, 'h': 5})
    assert result['success'] is False
    assert 'not found' in result['error']


def test_update_panel_grid_panel_not_found(tmp_path: Path) -> None:
    """Return an error when panel id cannot be found."""
    yaml_path = _write_dashboard(tmp_path)

    result = grid_updater.update_panel_grid(yaml_path.as_posix(), 'missing-panel', {'x': 0, 'y': 0, 'w': 10, 'h': 5})
    assert result['success'] is False
    assert 'not found' in result['error']


def test_update_panel_grid_load_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Return an error when dashboards fail to load."""
    yaml_path = _write_dashboard(tmp_path)

    def raise_load_error(_: str) -> None:
        raise ValueError

    monkeypatch.setattr(grid_updater, 'load_roundtrip', raise_load_error)

    result = grid_updater.update_panel_grid(yaml_path.as_posix(), 'panel-a', {'x': 0, 'y': 0, 'w': 10, 'h': 5})
    assert result['success'] is False
    assert 'Failed to load dashboard' in result['error']


def test_update_panel_grid_dump_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Return an error when dashboards fail to save."""
    yaml_path = _write_dashboard(tmp_path)

    def raise_dump_error(_: object, _path: str) -> None:
        raise RuntimeError

    monkeypatch.setattr(grid_updater, 'dump_roundtrip', raise_dump_error)

    result = grid_updater.update_panel_grid(yaml_path.as_posix(), 'panel-a', {'x': 0, 'y': 0, 'w': 10, 'h': 5})
    assert result['success'] is False
    assert 'Failed to save dashboard' in result['error']
