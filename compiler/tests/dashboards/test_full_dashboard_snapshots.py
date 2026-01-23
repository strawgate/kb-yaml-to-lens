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

These tests use inline-snapshot's outsource feature to store large dashboard
outputs in external files, keeping the test file readable.
"""

import json
from pathlib import Path
from typing import Any

import pytest
from inline_snapshot import external, outsource, snapshot

from dashboard_compiler.dashboard_compiler import load, render
from tests.conftest import de_json_kbn_dashboard

# Path to example dashboards
_project_root = Path(__file__).parent.parent.parent.parent
_example_dir = _project_root / 'docs' / 'examples'


def _prepare_dashboard_for_snapshot(kbn_dashboard_dict: dict[str, Any]) -> str:
    """Prepare a compiled dashboard for snapshot comparison.

    Deserializes JSON fields and returns as formatted JSON string for external storage.
    All IDs are deterministic and do not need normalization.
    """
    result = de_json_kbn_dashboard(kbn_dashboard_dict)
    return json.dumps(result, indent=2, sort_keys=True)


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
    def compiled_dashboard(self, dashboard_path: Path) -> str:
        """Load and compile the dashboard to JSON."""
        dashboards = load(str(dashboard_path))
        assert len(dashboards) == 1
        kbn_dashboard = render(dashboard=dashboards[0])
        return _prepare_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

    def test_full_dashboard_snapshot(self, compiled_dashboard: str) -> None:
        """Snapshot the entire compiled multi-panel-showcase dashboard."""
        assert outsource(compiled_dashboard, suffix='.json') == snapshot(
            external('55846b0ac98233450588ce41390c5ab99be4f8e6cb64ef1834102883c7fdabf3.json')
        )


class TestControlsExample:
    """Snapshot tests for dashboards with controls."""

    @pytest.fixture
    def dashboard_path(self) -> Path:
        """Path to controls-example.yaml."""
        return _example_dir / 'controls-example.yaml'

    @pytest.fixture
    def compiled_dashboard(self, dashboard_path: Path) -> str:
        """Load and compile the dashboard to JSON."""
        dashboards = load(str(dashboard_path))
        assert len(dashboards) == 1
        kbn_dashboard = render(dashboard=dashboards[0])
        return _prepare_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

    def test_full_dashboard_snapshot(self, compiled_dashboard: str) -> None:
        """Snapshot the entire compiled controls-example dashboard."""
        assert outsource(compiled_dashboard, suffix='.json') == snapshot(
            external('9d09f5869c9442f0d53257857f65ce49555a60fea29a6c83a02cd72f73d3ffd9.json')
        )


class TestFiltersExample:
    """Snapshot tests for dashboards with panel-level filters."""

    @pytest.fixture
    def dashboard_path(self) -> Path:
        """Path to filters-example.yaml."""
        return _example_dir / 'filters-example.yaml'

    @pytest.fixture
    def compiled_dashboard(self, dashboard_path: Path) -> str:
        """Load and compile the dashboard to JSON."""
        dashboards = load(str(dashboard_path))
        assert len(dashboards) == 1
        kbn_dashboard = render(dashboard=dashboards[0])
        return _prepare_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

    def test_full_dashboard_snapshot(self, compiled_dashboard: str) -> None:
        """Snapshot the entire compiled filters-example dashboard."""
        assert outsource(compiled_dashboard, suffix='.json') == snapshot(
            external('db6a2b9344026a56d7ea597fdafb027efafa11ef2ea6462ac8382d73fabb2961.json')
        )


class TestNavigationExample:
    """Snapshot tests for multi-dashboard files with navigation."""

    @pytest.fixture
    def dashboard_path(self) -> Path:
        """Path to navigation-example.yaml."""
        return _example_dir / 'navigation-example.yaml'

    @pytest.fixture
    def compiled_dashboards(self, dashboard_path: Path) -> list[str]:
        """Load and compile all dashboards to JSON."""
        dashboards = load(str(dashboard_path))
        assert len(dashboards) == 3
        return [_prepare_dashboard_for_snapshot(render(dashboard=d).model_dump(by_alias=True)) for d in dashboards]

    def test_overview_dashboard_snapshot(self, compiled_dashboards: list[str]) -> None:
        """Snapshot the Overview dashboard from navigation-example."""
        assert outsource(compiled_dashboards[0], suffix='.json') == snapshot(
            external('3a39b1a4827f233e62bd5e81c64a319f786473df48eb08d7c48a93be67db6136.json')
        )

    def test_details_dashboard_snapshot(self, compiled_dashboards: list[str]) -> None:
        """Snapshot the Details dashboard from navigation-example."""
        assert outsource(compiled_dashboards[1], suffix='.json') == snapshot(
            external('4b7c83caa392f99d6b229a13ef5fbfaa4ccd7b488b5daa89236292bba6f92599.json')
        )

    def test_analytics_dashboard_snapshot(self, compiled_dashboards: list[str]) -> None:
        """Snapshot the Analytics dashboard from navigation-example."""
        assert outsource(compiled_dashboards[2], suffix='.json') == snapshot(
            external('108c07568edb60efe3888e3e42e1541404b2cb64bcf6d2927f09d7952fd78296.json')
        )


class TestAerospikeOverview:
    """Snapshot tests for real-world integration dashboards."""

    @pytest.fixture
    def dashboard_path(self) -> Path:
        """Path to aerospike/overview.yaml."""
        return _example_dir / 'aerospike' / 'overview.yaml'

    @pytest.fixture
    def compiled_dashboard(self, dashboard_path: Path) -> str:
        """Load and compile the dashboard to JSON."""
        dashboards = load(str(dashboard_path))
        assert len(dashboards) == 1
        kbn_dashboard = render(dashboard=dashboards[0])
        return _prepare_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

    def test_full_dashboard_snapshot(self, compiled_dashboard: str) -> None:
        """Snapshot the entire compiled aerospike/overview dashboard."""
        assert outsource(compiled_dashboard, suffix='.json') == snapshot(
            external('6786a73a6264f0e5067b237a6b85e0fc609b051bfac37be4e2cde7487d2c0b52.json')
        )
