"""Snapshot tests for full dashboard compilation from example YAML files.

These tests ensure that changes to the compilation pipeline are captured in snapshots.
Each test loads an example dashboard YAML file, compiles it to Kibana JSON format,
and verifies the full output structure matches expectations.

The tests use a selection of example dashboards that cover different features:
- Panel types: markdown, links, lens charts
- Filter compilation
- Control group compilation
- Multi-dashboard files with navigation

Note: All IDs in the compiler are deterministic - the same YAML input will always
produce the same output, including all UUIDs, panel indexes, and reference names.
This is achieved via stable_id_generator() which hashes input data with SHA-1.

Snapshots are stored as JSON files in the snapshots/ subdirectory.
"""

import json
from pathlib import Path
from typing import Any

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import load, render
from tests.conftest import de_json_kbn_dashboard

# Paths
_project_root = Path(__file__).parent.parent.parent.parent
_example_dir = _project_root / 'docs' / 'examples'
_snapshot_dir = Path(__file__).parent / 'snapshots'


# Helpers


def _compile_dashboard(yaml_path: Path) -> dict[str, Any]:
    """Load a single-dashboard YAML file and compile to JSON dict."""
    dashboards = load(str(yaml_path))
    assert len(dashboards) == 1
    kbn_dashboard = render(dashboard=dashboards[0])
    return de_json_kbn_dashboard(kbn_dashboard.model_dump(by_alias=True))


def _compile_dashboards(yaml_path: Path) -> list[tuple[Dashboard, dict[str, Any]]]:
    """Load a multi-dashboard YAML file and compile all to JSON dicts."""
    dashboards = load(str(yaml_path))
    results: list[tuple[Dashboard, dict[str, Any]]] = []
    for dashboard in dashboards:
        kbn_dashboard = render(dashboard=dashboard)
        compiled = de_json_kbn_dashboard(kbn_dashboard.model_dump(by_alias=True))
        results.append((dashboard, compiled))
    return results


def _load_snapshot(filename: str) -> dict[str, Any]:
    """Load a snapshot file from the snapshots directory."""
    with (_snapshot_dir / filename).open(encoding='utf-8') as f:
        return json.load(f)


# Tests for multi-panel-showcase.yaml
# Demonstrates all supported panel types: markdown, links, lens charts


def test_multi_panel_showcase_snapshot() -> None:
    """Snapshot the entire compiled multi-panel-showcase dashboard."""
    result = _compile_dashboard(_example_dir / 'multi-panel-showcase.yaml')
    expected = _load_snapshot('multi_panel_showcase.json')
    assert result == expected


# Tests for controls-example.yaml
# Demonstrates control group compilation


def test_controls_example_snapshot() -> None:
    """Snapshot the entire compiled controls-example dashboard."""
    result = _compile_dashboard(_example_dir / 'controls-example.yaml')
    expected = _load_snapshot('controls_example.json')
    assert result == expected


# Tests for filters-example.yaml
# Demonstrates panel-level filter compilation


def test_filters_example_snapshot() -> None:
    """Snapshot the entire compiled filters-example dashboard."""
    result = _compile_dashboard(_example_dir / 'filters-example.yaml')
    expected = _load_snapshot('filters_example.json')
    assert result == expected


# Tests for navigation-example.yaml
# Demonstrates multi-dashboard files with navigation links


def test_navigation_overview_snapshot() -> None:
    """Snapshot the Overview dashboard from navigation-example."""
    compiled = _compile_dashboards(_example_dir / 'navigation-example.yaml')
    result = next(c for d, c in compiled if d.id == 'nav-overview-001')
    expected = _load_snapshot('navigation_overview.json')
    assert result == expected


def test_navigation_details_snapshot() -> None:
    """Snapshot the Details dashboard from navigation-example."""
    compiled = _compile_dashboards(_example_dir / 'navigation-example.yaml')
    result = next(c for d, c in compiled if d.id == 'nav-details-001')
    expected = _load_snapshot('navigation_details.json')
    assert result == expected


def test_navigation_analytics_snapshot() -> None:
    """Snapshot the Analytics dashboard from navigation-example."""
    compiled = _compile_dashboards(_example_dir / 'navigation-example.yaml')
    result = next(c for d, c in compiled if d.id == 'nav-analytics-001')
    expected = _load_snapshot('navigation_analytics.json')
    assert result == expected


# Tests for aerospike/overview.yaml
# Real-world integration dashboard


def test_aerospike_overview_snapshot() -> None:
    """Snapshot the entire compiled aerospike/overview dashboard."""
    result = _compile_dashboard(_example_dir / 'aerospike' / 'overview.yaml')
    expected = _load_snapshot('aerospike_overview.json')
    assert result == expected
