"""Snapshot tests for full dashboard compilation from example YAML files.

These tests ensure that changes to the compilation pipeline are captured in snapshots.
Each test loads an example dashboard YAML file, compiles it to Kibana JSON format,
and verifies the structure matches expectations.

The tests use a selection of example dashboards that cover different features:
- Panel types: markdown, links, lens charts
- Filter compilation
- Control group compilation
- Multi-dashboard files with navigation
"""

import re
from pathlib import Path
from typing import Any

import pytest
from inline_snapshot import snapshot

from dashboard_compiler.dashboard_compiler import load, render
from tests.conftest import de_json_kbn_dashboard

# Path to example dashboards
_project_root = Path(__file__).parent.parent.parent.parent
_example_dir = _project_root / 'docs' / 'examples'

# UUID pattern for normalization
_UUID_PATTERN = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.IGNORECASE)


def _replace_panel_indexes(result: dict[str, Any]) -> None:
    """Replace panelIndex values with consistent placeholders."""
    if 'attributes' in result and 'panelsJSON' in result['attributes']:
        panels = result['attributes']['panelsJSON']
        if isinstance(panels, list):
            for i, panel in enumerate(panels):
                panel['panelIndex'] = f'panel_{i}'


def _replace_references(result: dict[str, Any]) -> None:
    """Replace reference names with consistent placeholders."""
    if 'references' in result and isinstance(result['references'], list):
        for i, ref in enumerate(result['references']):
            if 'name' in ref:
                ref['name'] = f'ref_{i}'


def _replace_nested_references(attrs: dict[str, Any]) -> None:
    """Replace nested reference names in attributes."""
    if 'references' in attrs and isinstance(attrs['references'], list):
        for i, ref in enumerate(attrs['references']):
            if 'name' in ref:
                ref['name'] = f'nested_ref_{i}'


def _replace_nested_ids(result: dict[str, Any]) -> None:
    """Replace nested reference names in panel embeddable config."""
    if 'attributes' in result and 'panelsJSON' in result['attributes']:
        panels = result['attributes']['panelsJSON']
        if isinstance(panels, list):
            for panel in panels:
                if 'embeddableConfig' in panel and 'attributes' in panel['embeddableConfig']:
                    attrs = panel['embeddableConfig']['attributes']
                    _replace_nested_references(attrs)


def _replace_dynamic_ids(result: dict[str, Any]) -> dict[str, Any]:
    """Replace dynamic IDs with placeholders for consistent snapshots."""
    result['id'] = 'DYNAMIC_ID'
    result['created_at'] = 'DYNAMIC_TIMESTAMP'
    result['created_by'] = 'DYNAMIC_USER'
    result['updated_at'] = 'DYNAMIC_TIMESTAMP'
    result['updated_by'] = 'DYNAMIC_USER'
    result['version'] = 'DYNAMIC_VERSION'

    _replace_panel_indexes(result)
    _replace_references(result)
    _replace_nested_ids(result)

    return result


def _replace_grid_data_ids(result: dict[str, Any]) -> None:
    """Replace gridData 'i' values with sequential placeholders."""
    if 'attributes' in result and 'panelsJSON' in result['attributes']:
        panels = result['attributes']['panelsJSON']
        if isinstance(panels, list):
            for i, panel in enumerate(panels):
                if 'gridData' in panel and 'i' in panel['gridData']:
                    panel['gridData']['i'] = f'grid_id_{i}'


def _normalize_uuids_in_dict(obj: Any, uuid_map: dict[str, str] | None = None) -> Any:
    """Recursively replace UUIDs with consistent placeholders in a nested structure.

    This handles UUIDs as both values and dictionary keys.
    """
    if uuid_map is None:
        uuid_map = {}

    def get_placeholder(uuid_str: str) -> str:
        if uuid_str not in uuid_map:
            uuid_map[uuid_str] = f'UUID_{len(uuid_map)}'
        return uuid_map[uuid_str]

    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            # Check if key is a UUID
            new_key = key
            if isinstance(key, str) and _UUID_PATTERN.fullmatch(key):
                new_key = get_placeholder(key)
            new_dict[new_key] = _normalize_uuids_in_dict(value, uuid_map)
        return new_dict
    if isinstance(obj, list):
        return [_normalize_uuids_in_dict(item, uuid_map) for item in obj]
    if isinstance(obj, str) and _UUID_PATTERN.fullmatch(obj):
        return get_placeholder(obj)
    return obj


def _normalize_dashboard_for_snapshot(kbn_dashboard_dict: dict[str, Any]) -> dict[str, Any]:
    """Normalize a compiled dashboard for snapshot comparison.

    Applies all dynamic ID replacements to ensure snapshots are deterministic.
    """
    result = de_json_kbn_dashboard(kbn_dashboard_dict)
    result = _replace_dynamic_ids(result)
    _replace_grid_data_ids(result)
    # Normalize all UUIDs to placeholders
    return _normalize_uuids_in_dict(result)


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

    async def test_multi_panel_showcase_compiles_successfully(self, dashboard_path: Path) -> None:
        """Test that multi-panel-showcase.yaml compiles without errors."""
        dashboards = load(str(dashboard_path))
        assert len(dashboards) == 1

        kbn_dashboard = render(dashboard=dashboards[0])
        result = _normalize_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

        # Verify basic dashboard structure
        assert result['attributes']['title'] == '[Example] Multi-Panel Showcase'
        assert result['attributes']['description'] == 'Comprehensive example demonstrating all available panel types and chart variations'

    async def test_multi_panel_showcase_has_correct_panel_count(self, dashboard_path: Path) -> None:
        """Test that multi-panel-showcase has the expected number of panels."""
        dashboards = load(str(dashboard_path))
        kbn_dashboard = render(dashboard=dashboards[0])
        result = _normalize_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

        panels = result['attributes']['panelsJSON']
        assert len(panels) == 8

    async def test_multi_panel_showcase_panel_types(self, dashboard_path: Path) -> None:
        """Test that multi-panel-showcase contains the expected panel types."""
        dashboards = load(str(dashboard_path))
        kbn_dashboard = render(dashboard=dashboards[0])
        result = _normalize_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

        panels = result['attributes']['panelsJSON']
        panel_types = [p['type'] for p in panels]

        # Expected: 1 markdown (visualization), 1 links, 6 lens charts
        assert panel_types == snapshot(['visualization', 'links', 'lens', 'lens', 'lens', 'lens', 'lens', 'lens'])

    async def test_multi_panel_showcase_visualization_types(self, dashboard_path: Path) -> None:
        """Test that lens panels have the expected visualization types."""
        dashboards = load(str(dashboard_path))
        kbn_dashboard = render(dashboard=dashboards[0])
        result = _normalize_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

        panels = result['attributes']['panelsJSON']
        lens_panels = [p for p in panels if p['type'] == 'lens']

        vis_types = [p['embeddableConfig']['attributes']['visualizationType'] for p in lens_panels]

        # metric, pie, line, bar, area, tagcloud
        assert vis_types == snapshot(['lnsMetric', 'lnsPie', 'lnsXY', 'lnsXY', 'lnsXY', 'lnsTagcloud'])

    async def test_multi_panel_showcase_markdown_panel_snapshot(self, dashboard_path: Path) -> None:
        """Test the markdown panel structure."""
        dashboards = load(str(dashboard_path))
        kbn_dashboard = render(dashboard=dashboards[0])
        result = _normalize_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

        markdown_panel = result['attributes']['panelsJSON'][0]
        saved_vis = markdown_panel['embeddableConfig']['savedVis']

        assert saved_vis['type'] == 'markdown'
        assert saved_vis['title'] == 'Multi-Panel Dashboard Showcase'
        assert saved_vis['params']['fontSize'] == 12
        assert saved_vis['params']['openLinksInNewTab'] is True
        assert '# Welcome to the Multi-Panel Showcase' in saved_vis['params']['markdown']

    async def test_multi_panel_showcase_links_panel_snapshot(self, dashboard_path: Path) -> None:
        """Test the links panel structure."""
        dashboards = load(str(dashboard_path))
        kbn_dashboard = render(dashboard=dashboards[0])
        result = _normalize_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

        links_panel = result['attributes']['panelsJSON'][1]
        attrs = links_panel['embeddableConfig']['attributes']

        assert attrs['layout'] == 'horizontal'
        assert len(attrs['links']) == 3

        link_labels = [link['label'] for link in attrs['links']]
        assert link_labels == snapshot(['Kibana Documentation', 'Elasticsearch Guide', 'Project Repository'])

        # All should be external links
        for link in attrs['links']:
            assert link['type'] == 'externalLink'


class TestControlsExample:
    """Snapshot tests for dashboards with controls."""

    @pytest.fixture
    def dashboard_path(self) -> Path:
        """Path to controls-example.yaml."""
        return _example_dir / 'controls-example.yaml'

    async def test_controls_dashboard_compiles_with_control_group(self, dashboard_path: Path) -> None:
        """Test full compilation of controls-example.yaml has control group.

        This dashboard contains control group inputs with options controls.
        """
        dashboards = load(str(dashboard_path))
        assert len(dashboards) == 1

        kbn_dashboard = render(dashboard=dashboards[0])
        result = _normalize_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

        # Verify control group is present and has expected structure
        assert 'controlGroupInput' in result['attributes']
        control_group = result['attributes']['controlGroupInput']
        assert 'panelsJSON' in control_group
        assert isinstance(control_group['panelsJSON'], dict)
        assert len(control_group['panelsJSON']) == 2

    async def test_controls_dashboard_control_panel_structure(self, dashboard_path: Path) -> None:
        """Test the structure of control panels."""
        dashboards = load(str(dashboard_path))
        kbn_dashboard = render(dashboard=dashboards[0])
        result = _normalize_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

        control_group = result['attributes']['controlGroupInput']
        panels = control_group['panelsJSON']

        # Get control panel values
        control_panels = list(panels.values())
        assert len(control_panels) == 2

        # Verify control type
        for panel in control_panels:
            assert panel['type'] == 'optionsListControl'


class TestFiltersExample:
    """Snapshot tests for dashboards with panel-level filters."""

    @pytest.fixture
    def dashboard_path(self) -> Path:
        """Path to filters-example.yaml."""
        return _example_dir / 'filters-example.yaml'

    async def test_filters_dashboard_compiles_successfully(self, dashboard_path: Path) -> None:
        """Test full compilation of filters-example.yaml matches expectations.

        This dashboard demonstrates various filter types at the panel level.
        """
        dashboards = load(str(dashboard_path))
        assert len(dashboards) == 1

        kbn_dashboard = render(dashboard=dashboards[0])
        result = _normalize_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

        # Verify we have the expected number of panels
        panels = result['attributes']['panelsJSON']
        assert len(panels) == 9

        # Check dashboard title
        assert result['attributes']['title'] == '[Example] Advanced Filtering Techniques'

    async def test_filters_dashboard_panel_filters_present(self, dashboard_path: Path) -> None:
        """Test that panels have filters embedded in their configurations."""
        dashboards = load(str(dashboard_path))
        kbn_dashboard = render(dashboard=dashboards[0])
        result = _normalize_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

        panels = result['attributes']['panelsJSON']
        lens_panels = [p for p in panels if p['type'] == 'lens']

        # At least some lens panels should have filters
        panels_with_filters = [
            p
            for p in lens_panels
            if 'embeddableConfig' in p
            and 'attributes' in p['embeddableConfig']
            and 'state' in p['embeddableConfig']['attributes']
            and len(p['embeddableConfig']['attributes']['state'].get('filters', [])) > 0
        ]

        assert len(panels_with_filters) >= 1


class TestNavigationExample:
    """Snapshot tests for multi-dashboard files with navigation."""

    @pytest.fixture
    def dashboard_path(self) -> Path:
        """Path to navigation-example.yaml."""
        return _example_dir / 'navigation-example.yaml'

    async def test_navigation_dashboard_file_has_multiple_dashboards(self, dashboard_path: Path) -> None:
        """Test that navigation-example.yaml loads multiple dashboards."""
        dashboards = load(str(dashboard_path))
        assert len(dashboards) == 3

    async def test_navigation_overview_dashboard_compiles_correctly(self, dashboard_path: Path) -> None:
        """Test compilation of the Overview dashboard from navigation-example.yaml.

        This dashboard contains links panels that reference other dashboards by ID.
        """
        dashboards = load(str(dashboard_path))
        overview_dashboard = dashboards[0]

        kbn_dashboard = render(dashboard=overview_dashboard)
        result = _normalize_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

        # Verify dashboard title
        assert result['attributes']['title'] == '[Example] Navigation - Overview Dashboard'

        # Verify links panel has dashboard links
        links_panel = result['attributes']['panelsJSON'][0]
        assert links_panel['type'] == 'links'
        links = links_panel['embeddableConfig']['attributes']['links']
        assert len(links) == 3

        # All links should be dashboard links
        for link in links:
            assert link['type'] == 'dashboardLink'

    async def test_navigation_dashboard_titles(self, dashboard_path: Path) -> None:
        """Test all three dashboards have correct titles."""
        dashboards = load(str(dashboard_path))

        titles: list[str] = []
        for dashboard in dashboards:
            kbn_dashboard = render(dashboard=dashboard)
            result = _normalize_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))
            titles.append(str(result['attributes']['title']))

        assert titles == snapshot(
            [
                '[Example] Navigation - Overview Dashboard',
                '[Example] Navigation - Details Dashboard',
                '[Example] Navigation - Analytics Dashboard',
            ]
        )


class TestAerospikeOverview:
    """Snapshot tests for real-world integration dashboards."""

    @pytest.fixture
    def dashboard_path(self) -> Path:
        """Path to aerospike/overview.yaml."""
        return _example_dir / 'aerospike' / 'overview.yaml'

    async def test_aerospike_overview_compiles_successfully(self, dashboard_path: Path) -> None:
        """Test full compilation of aerospike/overview.yaml.

        This is a real-world integration dashboard with metrics panels and filters.
        """
        dashboards = load(str(dashboard_path))
        assert len(dashboards) == 1

        kbn_dashboard = render(dashboard=dashboards[0])
        result = _normalize_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

        # Verify dashboard title
        assert result['attributes']['title'] == '[Metrics Aerospike] Overview'

        # Verify we have expected panel count (links + metric + line charts)
        panels = result['attributes']['panelsJSON']
        assert len(panels) == 5

        # Verify first panel is links panel
        assert panels[0]['type'] == 'links'

        # Verify we have lens panels for metrics
        lens_panels = [p for p in panels if p['type'] == 'lens']
        assert len(lens_panels) == 4

    async def test_aerospike_overview_visualization_types(self, dashboard_path: Path) -> None:
        """Test the visualization types in the Aerospike overview dashboard."""
        dashboards = load(str(dashboard_path))
        kbn_dashboard = render(dashboard=dashboards[0])
        result = _normalize_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

        panels = result['attributes']['panelsJSON']
        lens_panels = [p for p in panels if p['type'] == 'lens']

        vis_types = [p['embeddableConfig']['attributes']['visualizationType'] for p in lens_panels]

        # 2 metrics and 2 line charts
        assert vis_types == snapshot(['lnsMetric', 'lnsXY', 'lnsMetric', 'lnsXY'])

    async def test_aerospike_overview_links_panel(self, dashboard_path: Path) -> None:
        """Test the navigation links panel in Aerospike overview."""
        dashboards = load(str(dashboard_path))
        kbn_dashboard = render(dashboard=dashboards[0])
        result = _normalize_dashboard_for_snapshot(kbn_dashboard.model_dump(by_alias=True))

        links_panel = result['attributes']['panelsJSON'][0]
        links = links_panel['embeddableConfig']['attributes']['links']

        link_labels = [link['label'] for link in links]
        assert link_labels == snapshot(['Overview', 'Node Metrics', 'Namespace Metrics'])

        # All links should be dashboard links
        for link in links:
            assert link['type'] == 'dashboardLink'
