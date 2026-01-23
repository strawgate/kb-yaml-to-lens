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

import pytest

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import load, render
from tests.conftest import de_json_kbn_dashboard

# Path to example dashboards
_project_root = Path(__file__).parent.parent.parent.parent
_example_dir = _project_root / 'docs' / 'examples'
_snapshot_dir = Path(__file__).parent / 'snapshots'


def _prepare_dashboard_for_snapshot(kbn_dashboard_dict: dict[str, Any]) -> dict[str, Any]:
    """Prepare a compiled dashboard for snapshot comparison.

    Deserializes JSON fields and returns as a dict for comparison.
    All IDs are deterministic and do not need normalization.
    """
    return de_json_kbn_dashboard(kbn_dashboard_dict)


def _load_snapshot(filename: str) -> dict[str, Any]:
    """Load a snapshot file from the snapshots directory."""
    with (_snapshot_dir / filename).open(encoding='utf-8') as f:
        return json.load(f)


def _find_dashboard_by_id(dashboards: list[Dashboard], dashboard_id: str) -> Dashboard:
    """Find a dashboard in a list by its id."""
    for d in dashboards:
        if d.id == dashboard_id:
            return d
    msg = f"Dashboard with id '{dashboard_id}' not found"
    raise ValueError(msg)


class TestMultiPanelShowcase:
    """Snapshot tests for the multi-panel showcase dashboard.

    This dashboard demonstrates all supported panel types:
    - Markdown panels
    - Links panels
    - Lens charts (metric, pie, line, bar, area, tagcloud)
    """

    @pytest.fixture
    def dashboard_path(self) -> Path:
        """Path to multi-panel-showcase.yaml."""
        return _example_dir / 'multi-panel-showcase.yaml'

    @pytest.fixture
    def compiled_dashboard(self, dashboard_path: Path) -> dict[str, Any]:
        """Load and compile the dashboard to JSON."""
        dashboards = load(str(dashboard_path))
        assert len(dashboards) == 1
        kbn_dashboard = render(dashboard=dashboards[0])
        return _prepare_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

    def test_full_dashboard_snapshot(self, compiled_dashboard: dict[str, Any]) -> None:
        """Snapshot the entire compiled multi-panel-showcase dashboard."""
        expected = _load_snapshot('multi_panel_showcase.json')
        assert compiled_dashboard == expected


class TestControlsExample:
    """Snapshot tests for dashboards with controls."""

    @pytest.fixture
    def dashboard_path(self) -> Path:
        """Path to controls-example.yaml."""
        return _example_dir / 'controls-example.yaml'

    @pytest.fixture
    def compiled_dashboard(self, dashboard_path: Path) -> dict[str, Any]:
        """Load and compile the dashboard to JSON."""
        dashboards = load(str(dashboard_path))
        assert len(dashboards) == 1
        kbn_dashboard = render(dashboard=dashboards[0])
        return _prepare_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

    def test_full_dashboard_snapshot(self, compiled_dashboard: dict[str, Any]) -> None:
        """Snapshot the entire compiled controls-example dashboard."""
        expected = _load_snapshot('controls_example.json')
        assert compiled_dashboard == expected


class TestFiltersExample:
    """Snapshot tests for dashboards with panel-level filters."""

    @pytest.fixture
    def dashboard_path(self) -> Path:
        """Path to filters-example.yaml."""
        return _example_dir / 'filters-example.yaml'

    @pytest.fixture
    def compiled_dashboard(self, dashboard_path: Path) -> dict[str, Any]:
        """Load and compile the dashboard to JSON."""
        dashboards = load(str(dashboard_path))
        assert len(dashboards) == 1
        kbn_dashboard = render(dashboard=dashboards[0])
        return _prepare_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

    def test_full_dashboard_snapshot(self, compiled_dashboard: dict[str, Any]) -> None:
        """Snapshot the entire compiled filters-example dashboard."""
        expected = _load_snapshot('filters_example.json')
        assert compiled_dashboard == expected


class TestNavigationExample:
    """Snapshot tests for multi-dashboard files with navigation.

    Uses dashboard id lookup instead of index-based access to avoid
    test failures if YAML ordering changes.
    """

    @pytest.fixture
    def dashboard_path(self) -> Path:
        """Path to navigation-example.yaml."""
        return _example_dir / 'navigation-example.yaml'

    @pytest.fixture
    def dashboards(self, dashboard_path: Path) -> list[Dashboard]:
        """Load all dashboards from the navigation example."""
        dashboards = load(str(dashboard_path))
        assert len(dashboards) == 3
        return dashboards

    def test_overview_dashboard_snapshot(self, dashboards: list[Dashboard]) -> None:
        """Snapshot the Overview dashboard from navigation-example."""
        dashboard = _find_dashboard_by_id(dashboards, 'nav-overview-001')
        kbn_dashboard = render(dashboard=dashboard)
        result = _prepare_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))
        expected = _load_snapshot('navigation_overview.json')
        assert result == expected

    def test_details_dashboard_snapshot(self, dashboards: list[Dashboard]) -> None:
        """Snapshot the Details dashboard from navigation-example."""
        dashboard = _find_dashboard_by_id(dashboards, 'nav-details-001')
        kbn_dashboard = render(dashboard=dashboard)
        result = _prepare_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))
        expected = _load_snapshot('navigation_details.json')
        assert result == expected

    def test_analytics_dashboard_snapshot(self, dashboards: list[Dashboard]) -> None:
        """Snapshot the Analytics dashboard from navigation-example."""
        dashboard = _find_dashboard_by_id(dashboards, 'nav-analytics-001')
        kbn_dashboard = render(dashboard=dashboard)
        result = _prepare_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))
        expected = _load_snapshot('navigation_analytics.json')
        assert result == expected


class TestAerospikeOverview:
    """Snapshot tests for real-world integration dashboards."""

    @pytest.fixture
    def dashboard_path(self) -> Path:
        """Path to aerospike/overview.yaml."""
        return _example_dir / 'aerospike' / 'overview.yaml'

    @pytest.fixture
    def compiled_dashboard(self, dashboard_path: Path) -> dict[str, Any]:
        """Load and compile the dashboard to JSON."""
        dashboards = load(str(dashboard_path))
        assert len(dashboards) == 1
        kbn_dashboard = render(dashboard=dashboards[0])
        return _prepare_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

    def test_full_dashboard_snapshot(self, compiled_dashboard: dict[str, Any]) -> None:
        """Snapshot the entire compiled aerospike/overview dashboard."""
        expected = _load_snapshot('aerospike_overview.json')
        assert compiled_dashboard == expected
