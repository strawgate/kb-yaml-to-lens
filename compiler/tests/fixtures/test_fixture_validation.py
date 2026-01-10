"""Explicit fixture validation tests - one test per Kibana fixture file.

Each test:
1. Compiles an inline YAML definition
2. Diffs it against the corresponding Kibana fixture JSON from fixture-generator/output/
3. Snapshots the exact differences using inline_snapshot

This allows us to track how compiler output differs from Kibana's LensConfigBuilder output
and detect any changes as the compiler evolves.
"""

from typing import Any

import yaml
from deepdiff import DeepDiff
from inline_snapshot import snapshot

from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.loader import DashboardConfig
from tests.conftest import de_json_kbn_dashboard
from tests.fixtures import (
    diff_to_dict,
    get_fixture_files,
    load_fixture,
    normalize_compiled_panel,
    normalize_layer_ids,
)


def compile_yaml_content(yaml_content: str) -> dict[str, Any]:
    """Compile YAML content and return the normalized panel config."""
    config_data = yaml.safe_load(yaml_content)
    config = DashboardConfig.model_validate(config_data)
    dashboards = config.dashboards
    assert len(dashboards) > 0, 'No dashboards produced from YAML content'
    kbn_dashboard = render(dashboards[0])
    dashboard_dict = kbn_dashboard.model_dump(by_alias=True, exclude_none=True)
    dashboard = de_json_kbn_dashboard(dashboard_dict)
    panels = dashboard['attributes']['panelsJSON']
    assert len(panels) > 0, 'No panels in dashboard from YAML content'
    return normalize_compiled_panel(panels[0])


def compute_diff(yaml_content: str, fixture_name: str) -> dict[str, Any]:
    """Compile YAML content, diff against Kibana fixture, return diff dict."""
    compiled = compile_yaml_content(yaml_content)
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
# Discovery Tests
# =============================================================================


def test_fixture_files_exist() -> None:
    """Verify that fixture JSON files were found."""
    # Ensure fixture-generator output is present for the default version
    fixture_files = get_fixture_files()
    assert len(fixture_files) > 0, 'No fixture JSON files found in fixture-generator/output/ (default version)'


# =============================================================================
# Explicit Snapshot Tests - One Per Fixture
#
# Each test below explicitly validates a single fixture file.
# The YAML content is defined inline so the test is self-contained.
# The snapshot captures the exact diff between compiled output and Kibana fixture.
# Any changes to the compiler that affect output will cause the snapshot to fail.
# =============================================================================


def test_metric_basic_esql_snapshot() -> None:
    """Explicit snapshot test for metric-basic-esql fixture.

    Tests a basic ES|QL metric visualization with a simple COUNT() aggregation.
    This is the simplest possible metric fixture.
    """
    yaml_content = """
dashboards:
  - name: Basic Count Metric Test
    panels:
      - title: Basic Count Metric
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          type: metric
          query: FROM logs-* | STATS count = COUNT()
          primary:
            field: count
            id: metric_formula_accessor
"""
    diff = compute_diff(yaml_content, 'metric-basic-esql')
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
    yaml_content = """
dashboards:
  - name: Pie Chart Test
    panels:
      - title: Events by Status
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          type: pie
          query: FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 10
          metrics:
            - field: count
              id: metric_formula_accessor
          dimensions:
            - field: log.level
              id: metric_formula_accessor_breakdown_0
"""
    diff = compute_diff(yaml_content, 'pie-chart-esql')
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
