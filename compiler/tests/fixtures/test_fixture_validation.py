"""Test fixture validation - compare compiled output against Kibana-generated fixtures.

This module implements tests that:
1. Load YAML fixture definitions from tests/fixtures/yaml/
2. Compile them to Kibana dashboard JSON
3. Compare the output against fixture-generator output using deepdiff
4. Snapshot the differences for tracking over time

These tests validate that the compiler produces output compatible with
Kibana's own LensConfigBuilder API and track any known differences.
"""

from pathlib import Path
from typing import Any

import pytest
from deepdiff import DeepDiff
from inline_snapshot import snapshot

from dashboard_compiler.dashboard_compiler import load, render
from tests.conftest import de_json_kbn_dashboard
from tests.fixtures import (
    diff_to_dict,
    get_yaml_fixture_files,
    load_fixture,
    normalize_compiled_panel,
    normalize_layer_ids,
)

# Auto-discover fixture YAML files
_fixture_yamls = get_yaml_fixture_files()


def extract_esql_layer(panel_config: dict[str, Any]) -> dict[str, Any] | None:
    """Extract the ES|QL layer configuration.

    Returns the first textBased layer found, normalized for comparison.
    """
    state = panel_config.get('state', {})
    datasource_states = state.get('datasourceStates', {})
    text_based = datasource_states.get('textBased', {})
    layers = text_based.get('layers', {})

    if len(layers) == 0:
        return None

    # Get first layer (there should only be one for simple fixtures)
    layer_id = next(iter(layers.keys()))
    layer = layers[layer_id]

    return {
        'query': layer.get('query', {}),
        'columns': layer.get('columns', []),
    }


def test_fixture_files_exist() -> None:
    """Verify that fixture YAML files were found."""
    assert len(_fixture_yamls) > 0, 'No fixture YAML files found in tests/fixtures/yaml/'


def test_fixture_coverage() -> None:
    """Report coverage of fixture-generator output by YAML tests."""
    from tests.fixtures import get_fixture_files

    fixture_files = {f.stem for f in get_fixture_files()}  # pyright: ignore[reportUnknownMemberType]
    yaml_files = {f.stem for f in get_yaml_fixture_files()}  # pyright: ignore[reportUnknownMemberType]

    covered = fixture_files & yaml_files
    missing = fixture_files - yaml_files

    coverage_pct = len(covered) / len(fixture_files) * 100 if len(fixture_files) > 0 else 0

    # Report coverage statistics
    print('\n=== Fixture Coverage Report ===')
    print(f'Total fixtures: {len(fixture_files)}')
    print(f'YAML tests: {len(yaml_files)}')
    print(f'Coverage: {coverage_pct:.1f}%')

    if len(missing) > 0:
        print(f'\nFixtures without YAML tests ({len(missing)}):')
        for name in sorted(list(missing)[:10]):
            print(f'  - {name}')
        if len(missing) > 10:
            print(f'  ... and {len(missing) - 10} more')

    # This is informational, not a failure condition
    assert coverage_pct >= 0


class TestMetricBasicEsql:
    """Tests for the metric-basic-esql fixture."""

    @pytest.fixture
    def compiled_config(self) -> dict[str, Any]:
        """Load and compile the metric-basic-esql fixture."""
        yaml_path = Path(__file__).parent / 'yaml' / 'metric-basic-esql.yaml'
        dashboards = load(str(yaml_path))
        kbn_dashboard = render(dashboards[0])
        dashboard_dict = kbn_dashboard.model_dump(by_alias=True, exclude_none=True)
        dashboard = de_json_kbn_dashboard(dashboard_dict)
        panels = dashboard['attributes']['panelsJSON']
        return normalize_compiled_panel(panels[0])

    @pytest.fixture
    def fixture_config(self) -> dict[str, Any]:
        """Load the metric-basic-esql fixture from fixture-generator."""
        return load_fixture('metric-basic-esql')

    def test_visualization_type(self, compiled_config: dict[str, Any]) -> None:
        """Verify the correct visualization type is used."""
        assert compiled_config['visualizationType'] == snapshot('lnsMetric')

    def test_esql_query_matches(self, compiled_config: dict[str, Any], fixture_config: dict[str, Any]) -> None:
        """Verify the ES|QL query matches the fixture."""
        compiled_layer = extract_esql_layer(compiled_config)
        fixture_layer = extract_esql_layer(fixture_config)

        assert compiled_layer is not None
        assert fixture_layer is not None

        # The query should match exactly
        assert compiled_layer['query'] == fixture_layer['query']

    def test_column_structure(self, compiled_config: dict[str, Any], fixture_config: dict[str, Any]) -> None:
        """Verify the column structure matches the fixture.

        The compiler may add additional metadata to columns, so we check
        that the essential fields match.
        """
        compiled_layer = extract_esql_layer(compiled_config)
        fixture_layer = extract_esql_layer(fixture_config)

        assert compiled_layer is not None
        assert fixture_layer is not None

        compiled_columns = compiled_layer['columns']
        fixture_columns = fixture_layer['columns']

        # Same number of columns
        assert len(compiled_columns) == len(fixture_columns)

        # Check column IDs and field names match
        compiled_ids = {col['columnId'] for col in compiled_columns}
        fixture_ids = {col['columnId'] for col in fixture_columns}
        assert compiled_ids == fixture_ids

        # Check field names match for each column
        for fixture_col in fixture_columns:
            col_id = fixture_col['columnId']
            compiled_col = next(c for c in compiled_columns if c['columnId'] == col_id)
            assert compiled_col['fieldName'] == fixture_col['fieldName']

    def test_metric_accessor(self, compiled_config: dict[str, Any], fixture_config: dict[str, Any]) -> None:
        """Verify the metric accessor matches the fixture."""
        compiled_viz = compiled_config['state']['visualization']
        fixture_viz = fixture_config['state']['visualization']

        assert compiled_viz.get('metricAccessor') == fixture_viz.get('metricAccessor')

    def test_full_diff_snapshot(self, compiled_config: dict[str, Any], fixture_config: dict[str, Any]) -> None:
        """Snapshot the full diff between compiled output and fixture.

        This test documents all differences between the compiler output and
        the Kibana fixture. Any changes to the compiler that affect output
        will be caught here.
        """
        # Normalize layer IDs for stable comparison
        normalized_compiled = normalize_layer_ids(compiled_config)
        normalized_fixture = normalize_layer_ids(fixture_config)

        diff = DeepDiff(
            normalized_fixture,
            normalized_compiled,
            ignore_order=True,
            verbose_level=2,
        )

        # Snapshot the exact differences for explicit tracking
        diff_dict = diff_to_dict(diff)
        assert diff_dict == snapshot(
            {
                'dictionary_item_added': {
                    "root['state']['datasourceStates']['formBased']": {'layers': {}},
                    "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER_ID>_0']['allColumns'][0]['customLabel']": False,
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER_ID>_0']['allColumns'][0]['inMetricDimension']": True,
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER_ID>_0']['allColumns'][0]['label']": 'count',
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER_ID>_0']['allColumns'][0]['meta']['esType']": 'long',
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER_ID>_0']['columns'][0]['customLabel']": False,
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER_ID>_0']['columns'][0]['inMetricDimension']": True,
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER_ID>_0']['columns'][0]['label']": 'count',
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER_ID>_0']['columns'][0]['meta']['esType']": 'long',
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER_ID>_0']['timeField']": '@timestamp',
                },
                'dictionary_item_removed': {
                    ('root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']'): {},
                    (
                        "root['state']['datasourceStates']['textBased']['layers']['<LAYER_ID>_0']['index']"
                    ): '{"index":"logs-*","timeFieldName":"@timestamp"}',
                },
                'iterable_item_removed': {
                    "root['references'][0]": {
                        'type': 'index-pattern',
                        'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                        'name': 'indexpattern-datasource-layer-layer_0',
                    },
                },
                'values_changed': {
                    "root['state']['query']": {
                        'old_value': {'language': 'kuery', 'query': ''},
                        'new_value': {'esql': 'FROM logs-* | STATS count = COUNT()'},
                    },
                    "root['title']": {
                        'old_value': 'Basic Count Metric',
                        'new_value': '',
                    },
                },
            }
        )


class TestPieChartEsql:
    """Tests for the pie-chart-esql fixture."""

    @pytest.fixture
    def compiled_config(self) -> dict[str, Any]:
        """Load and compile the pie-chart-esql fixture."""
        yaml_path = Path(__file__).parent / 'yaml' / 'pie-chart-esql.yaml'
        dashboards = load(str(yaml_path))
        kbn_dashboard = render(dashboards[0])
        dashboard_dict = kbn_dashboard.model_dump(by_alias=True, exclude_none=True)
        dashboard = de_json_kbn_dashboard(dashboard_dict)
        panels = dashboard['attributes']['panelsJSON']
        return normalize_compiled_panel(panels[0])

    @pytest.fixture
    def fixture_config(self) -> dict[str, Any]:
        """Load the pie-chart-esql fixture from fixture-generator."""
        return load_fixture('pie-chart-esql')

    def test_visualization_type(self, compiled_config: dict[str, Any]) -> None:
        """Verify the correct visualization type is used."""
        assert compiled_config['visualizationType'] == snapshot('lnsPie')

    def test_esql_query_matches(self, compiled_config: dict[str, Any], fixture_config: dict[str, Any]) -> None:
        """Verify the ES|QL query matches the fixture."""
        compiled_layer = extract_esql_layer(compiled_config)
        fixture_layer = extract_esql_layer(fixture_config)

        assert compiled_layer is not None
        assert fixture_layer is not None

        # The query should match exactly
        assert compiled_layer['query'] == fixture_layer['query']

    def test_column_structure(self, compiled_config: dict[str, Any], fixture_config: dict[str, Any]) -> None:
        """Verify the column structure matches the fixture."""
        compiled_layer = extract_esql_layer(compiled_config)
        fixture_layer = extract_esql_layer(fixture_config)

        assert compiled_layer is not None
        assert fixture_layer is not None

        compiled_columns = compiled_layer['columns']
        fixture_columns = fixture_layer['columns']

        # Same number of columns
        assert len(compiled_columns) == len(fixture_columns)

        # Check column IDs and field names match
        compiled_ids = {col['columnId'] for col in compiled_columns}
        fixture_ids = {col['columnId'] for col in fixture_columns}
        assert compiled_ids == fixture_ids

    def test_pie_layer_structure(self, compiled_config: dict[str, Any], fixture_config: dict[str, Any]) -> None:
        """Verify the pie chart layer structure."""
        compiled_viz = compiled_config['state']['visualization']
        fixture_viz = fixture_config['state']['visualization']

        # Both should have layers
        assert 'layers' in compiled_viz
        assert 'layers' in fixture_viz

        # Compare layer structure
        compiled_layer = compiled_viz['layers'][0]
        fixture_layer = fixture_viz['layers'][0]

        # Layer type should match
        assert compiled_layer.get('layerType') == fixture_layer.get('layerType')

        # Metrics should match
        assert compiled_layer.get('metrics') == fixture_layer.get('metrics')

        # Primary groups should match
        assert compiled_layer.get('primaryGroups') == fixture_layer.get('primaryGroups')

    def test_full_diff_snapshot(self, compiled_config: dict[str, Any], fixture_config: dict[str, Any]) -> None:
        """Snapshot the full diff between compiled output and fixture."""
        # Normalize layer IDs for stable comparison
        normalized_compiled = normalize_layer_ids(compiled_config)
        normalized_fixture = normalize_layer_ids(fixture_config)

        diff = DeepDiff(
            normalized_fixture,
            normalized_compiled,
            ignore_order=True,
            verbose_level=2,
        )

        # Snapshot the exact differences for explicit tracking
        diff_dict = diff_to_dict(diff)
        assert diff_dict == snapshot(
            {
                'dictionary_item_added': {
                    "root['state']['datasourceStates']['formBased']": {'layers': {}},
                    "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER_ID>_0']['timeField']": '@timestamp',
                    "root['state']['visualization']['layers'][0]['colorMapping']": {
                        'assignments': [],
                        'specialAssignments': [
                            {
                                'rule': {'type': 'other'},
                                'color': {'type': 'loop'},
                                'touched': False,
                            }
                        ],
                        'paletteId': 'eui_amsterdam_color_blind',
                        'colorMode': {'type': 'categorical'},
                    },
                    "root['state']['visualization']['layers'][0]['nestedLegend']": False,
                },
                'dictionary_item_removed': {
                    ('root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']'): {},
                    (
                        "root['state']['datasourceStates']['textBased']['layers']['<LAYER_ID>_0']['index']"
                    ): '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    "root['state']['visualization']['layers'][0]['allowMultipleMetrics']": False,
                    "root['state']['visualization']['layers'][0]['legendPosition']": 'right',
                },
                'iterable_item_removed': {
                    "root['references'][0]": {
                        'type': 'index-pattern',
                        'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                        'name': 'indexpattern-datasource-layer-layer_0',
                    },
                },
                'values_changed': {
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER_ID>_0']['allColumns'][0]": {
                        'old_value': {'columnId': 'metric_formula_accessor_breakdown_0', 'fieldName': 'log.level'},
                        'new_value': {
                            'fieldName': 'count',
                            'columnId': 'metric_formula_accessor',
                            'label': 'count',
                            'customLabel': False,
                            'meta': {'type': 'number', 'esType': 'long'},
                            'inMetricDimension': True,
                        },
                    },
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER_ID>_0']['allColumns'][1]": {
                        'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                        'new_value': {
                            'fieldName': 'log.level',
                            'columnId': 'metric_formula_accessor_breakdown_0',
                            'label': 'log.level',
                            'customLabel': False,
                        },
                    },
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER_ID>_0']['columns'][0]": {
                        'old_value': {'columnId': 'metric_formula_accessor_breakdown_0', 'fieldName': 'log.level'},
                        'new_value': {
                            'fieldName': 'count',
                            'columnId': 'metric_formula_accessor',
                            'label': 'count',
                            'customLabel': False,
                            'meta': {'type': 'number', 'esType': 'long'},
                            'inMetricDimension': True,
                        },
                    },
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER_ID>_0']['columns'][1]": {
                        'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                        'new_value': {
                            'fieldName': 'log.level',
                            'columnId': 'metric_formula_accessor_breakdown_0',
                            'label': 'log.level',
                            'customLabel': False,
                        },
                    },
                    "root['state']['query']": {
                        'old_value': {'language': 'kuery', 'query': ''},
                        'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 10'},
                    },
                    "root['state']['visualization']['layers'][0]['legendDisplay']": {
                        'old_value': 'show',
                        'new_value': 'default',
                    },
                    "root['title']": {
                        'old_value': 'Events by Status',
                        'new_value': '',
                    },
                },
            }
        )
