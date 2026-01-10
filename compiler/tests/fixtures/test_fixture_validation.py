"""Explicit fixture validation tests - one test per Kibana fixture file.

Each test:
1. Compiles a YAML fixture from tests/fixtures/yaml/
2. Diffs it against the corresponding Kibana fixture JSON from fixture-generator/output/
3. Snapshots the exact differences using inline_snapshot

This allows us to track how compiler output differs from Kibana's LensConfigBuilder output
and detect any changes as the compiler evolves.
"""

from pathlib import Path
from typing import Any

from deepdiff import DeepDiff
from inline_snapshot import snapshot

from dashboard_compiler.dashboard_compiler import load, render
from tests.conftest import de_json_kbn_dashboard
from tests.fixtures import (
    diff_to_dict,
    get_fixture_files,
    get_yaml_fixture_files,
    load_fixture,
    normalize_compiled_panel,
    normalize_layer_ids,
)


def compile_yaml_fixture(fixture_name: str) -> dict[str, Any]:
    """Compile a YAML fixture and return the normalized panel config."""
    yaml_path = Path(__file__).parent / 'yaml' / f'{fixture_name}.yaml'
    dashboards = load(str(yaml_path))
    assert len(dashboards) > 0, f'No dashboards produced for fixture {fixture_name}'
    kbn_dashboard = render(dashboards[0])
    dashboard_dict = kbn_dashboard.model_dump(by_alias=True, exclude_none=True)
    dashboard = de_json_kbn_dashboard(dashboard_dict)
    panels = dashboard['attributes']['panelsJSON']
    assert len(panels) > 0, f'No panels in dashboard for fixture {fixture_name}'
    return normalize_compiled_panel(panels[0])


def compute_fixture_diff(fixture_name: str) -> dict[str, Any]:
    """Compile YAML fixture, diff against Kibana fixture, return diff dict."""
    compiled = compile_yaml_fixture(fixture_name)
    fixture = load_fixture(fixture_name)

    # Normalize layer IDs for stable comparison
    normalized_compiled = normalize_layer_ids(compiled)
    normalized_fixture = normalize_layer_ids(fixture)

    diff = DeepDiff(
        normalized_fixture,
        normalized_compiled,
        ignore_order=True,
        verbose_level=2,
    )

    return diff_to_dict(diff)


# =============================================================================
# Discovery and Coverage Tests
# =============================================================================


def test_fixture_files_exist() -> None:
    """Verify that fixture YAML and JSON files were found."""
    yaml_files = get_yaml_fixture_files()
    assert len(yaml_files) > 0, 'No fixture YAML files found in tests/fixtures/yaml/'

    # Ensure fixture-generator output is present for the default version
    fixture_files = get_fixture_files()
    assert len(fixture_files) > 0, 'No fixture JSON files found in fixture-generator/output/ (default version)'


def test_fixture_coverage() -> None:
    """Report coverage of fixture-generator output by YAML tests."""
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


# =============================================================================
# Explicit Snapshot Tests - One Per Fixture
#
# Each test below explicitly validates a single fixture file.
# The snapshot captures the exact diff between compiled output and Kibana fixture.
# Any changes to the compiler that affect output will cause the snapshot to fail.
# =============================================================================


def test_metric_basic_esql_snapshot() -> None:
    """Explicit snapshot test for metric-basic-esql fixture.

    Tests a basic ES|QL metric visualization with a simple COUNT() aggregation.
    This is the simplest possible metric fixture.
    """
    diff = compute_fixture_diff('metric-basic-esql')
    assert diff == snapshot(
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
            },
        }
    )


def test_pie_chart_esql_snapshot() -> None:
    """Explicit snapshot test for pie-chart-esql fixture.

    Tests an ES|QL pie chart with COUNT() grouped by log.level.
    This validates dimension/metric handling in pie visualizations.
    """
    diff = compute_fixture_diff('pie-chart-esql')
    assert diff == snapshot(
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
            },
        }
    )
