"""Tests for dashboard compiler load policy behavior."""

from pathlib import Path

import pytest

from kb_dashboard_core.dashboard_compiler import load


def _write_deprecated_dashboard_yaml(tmp_path: Path) -> Path:
    yaml_path = tmp_path / 'deprecated-dashboard.yaml'
    yaml_path.write_text("""\
dashboards:
  - name: Deprecated Dashboard
    panels:
      - title: Deprecated Pie
        size: {w: 24, h: 12}
        position: {x: 0, y: 0}
        esql:
          type: pie
          query: |
            FROM logs-* | STATS total = COUNT(*) BY service.name
          metrics:
            - field: total
          breakdowns:
            - field: service.name
          titles_and_text:
            slice_values: integer
""")
    return yaml_path


def test_load_rejects_deprecated_fields_by_default(tmp_path: Path) -> None:
    """Deprecated translation paths should be opt-in."""
    yaml_path = _write_deprecated_dashboard_yaml(tmp_path)

    with pytest.raises(ValueError, match='--allow-deprecated'):
        _ = load(str(yaml_path))


def test_load_accepts_deprecated_fields_when_opted_in(tmp_path: Path) -> None:
    """allow_deprecated=True should preserve compatibility behavior."""
    yaml_path = _write_deprecated_dashboard_yaml(tmp_path)

    dashboards = load(str(yaml_path), allow_deprecated=True)

    assert len(dashboards) == 1
    assert dashboards[0].name == 'Deprecated Dashboard'
