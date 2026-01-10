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
from inline_snapshot import snapshot

from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.loader import DashboardConfig
from tests.conftest import de_json_kbn_dashboard
from tests.fixtures import (
    compare_with_deepdiff,
    get_fixture_files,
    load_fixture,
    normalize_compiled_panel,
    normalize_diff_paths,
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
    """Compile YAML content, diff against Kibana fixture, return normalized diff dict.

    Uses DeepDiff with verbose_level=2 for detailed comparisons, then normalizes
    the paths in the result to replace dynamic IDs with stable placeholders.
    """
    compiled = compile_yaml_content(yaml_content)
    fixture = load_fixture(fixture_name)

    # Compare using DeepDiff (handles order, nesting, etc.)
    diff = compare_with_deepdiff(compiled, fixture)

    # Normalize paths for stable snapshots
    return normalize_diff_paths(diff)


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
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['allColumns'][0]['customLabel']": False,
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['allColumns'][0]['inMetricDimension']": True,
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['allColumns'][0]['label']": 'count',
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['allColumns'][0]['meta']['esType']": 'long',
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['columns'][0]['customLabel']": False,
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['columns'][0]['inMetricDimension']": True,
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['columns'][0]['label']": 'count',
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['columns'][0]['meta']['esType']": 'long',
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                ('root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']'): {},
                (
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['index']"
                ): '{"index":"logs-*","timeFieldName":"@timestamp"}',
            },
            'iterable_item_removed': {
                "root['references'][0]": {
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                    'type': 'index-pattern',
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
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['timeField']": '@timestamp',
                "root['state']['visualization']['layers'][0]['colorMapping']": {
                    'assignments': [],
                    'colorMode': {'type': 'categorical'},
                    'paletteId': 'eui_amsterdam_color_blind',
                    'specialAssignments': [
                        {
                            'color': {'type': 'loop'},
                            'rule': {'type': 'other'},
                            'touched': False,
                        }
                    ],
                },
                "root['state']['visualization']['layers'][0]['nestedLegend']": False,
            },
            'dictionary_item_removed': {
                ('root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']'): {},
                (
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['index']"
                ): '{"index":"logs-*","timeFieldName":"@timestamp"}',
                "root['state']['visualization']['layers'][0]['allowMultipleMetrics']": False,
                "root['state']['visualization']['layers'][0]['legendPosition']": 'right',
            },
            'iterable_item_removed': {
                "root['references'][0]": {
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                    'type': 'index-pattern',
                },
            },
            'values_changed': {
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['allColumns'][0]": {
                    'old_value': {'columnId': 'metric_formula_accessor_breakdown_0', 'fieldName': 'log.level'},
                    'new_value': {
                        'columnId': 'metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'count',
                        'inMetricDimension': True,
                        'label': 'count',
                        'meta': {'esType': 'long', 'type': 'number'},
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['allColumns'][1]": {
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                    'new_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'customLabel': False,
                        'fieldName': 'log.level',
                        'label': 'log.level',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['columns'][0]": {
                    'old_value': {'columnId': 'metric_formula_accessor_breakdown_0', 'fieldName': 'log.level'},
                    'new_value': {
                        'columnId': 'metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'count',
                        'inMetricDimension': True,
                        'label': 'count',
                        'meta': {'esType': 'long', 'type': 'number'},
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['columns'][1]": {
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                    'new_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'customLabel': False,
                        'fieldName': 'log.level',
                        'label': 'log.level',
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


def test_xy_chart_esql_snapshot() -> None:
    """Explicit snapshot test for xy-chart-esql fixture.

    Tests an ES|QL XY (line) chart with time series data.
    This validates layer structure and axis configuration.
    """
    yaml_content = """
dashboards:
  - name: XY Chart Test
    panels:
      - title: Events Over Time
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          type: line
          query: FROM logs-* | STATS count = COUNT() BY @timestamp
          dimension:
            field: '@timestamp'
            id: x_metric_formula_accessor0
          metrics:
            - field: count
              id: metric_formula_accessor0_0
"""
    diff = compute_diff(yaml_content, 'xy-chart-esql')
    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['timeField']": '@timestamp',
                "root['state']['visualization']['layers'][0]['colorMapping']": {
                    'assignments': [],
                    'colorMode': {'type': 'categorical'},
                    'paletteId': 'eui_amsterdam_color_blind',
                    'specialAssignments': [{'color': {'type': 'loop'}, 'rule': {'type': 'other'}, 'touched': False}],
                },
                "root['state']['visualization']['layers'][0]['position']": 'top',
                "root['state']['visualization']['layers'][0]['showGridlines']": False,
            },
            'dictionary_item_removed': {
                ('root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']'): {},
                (
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['index']"
                ): '{"index":"logs-*","timeFieldName":"@timestamp"}',
                "root['state']['visualization']['axisTitlesVisibilitySettings']": {'x': True, 'yLeft': True, 'yRight': True},
                "root['state']['visualization']['emphasizeFitting']": True,
                "root['state']['visualization']['fittingFunction']": 'Linear',
                "root['state']['visualization']['gridlinesVisibilitySettings']": {'x': True, 'yLeft': True, 'yRight': True},
                "root['state']['visualization']['hideEndzones']": True,
                "root['state']['visualization']['labelsOrientation']": {'x': 0, 'yLeft': 0, 'yRight': 0},
                "root['state']['visualization']['layers'][0]['yConfig']": [{'forAccessor': 'metric_formula_accessor0_0'}],
                "root['state']['visualization']['legend']['isVisible']": True,
                "root['state']['visualization']['tickLabelsVisibilitySettings']": {'x': True, 'yLeft': True, 'yRight': True},
                "root['state']['visualization']['yLeftExtent']": {'mode': 'full'},
            },
            'iterable_item_removed': {
                "root['references'][0]": {
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                    'type': 'index-pattern',
                },
            },
            'values_changed': {
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['allColumns'][0]": {
                    'old_value': {'columnId': 'x_metric_formula_accessor0', 'fieldName': '@timestamp'},
                    'new_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'customLabel': False,
                        'fieldName': 'count',
                        'inMetricDimension': True,
                        'label': 'count',
                        'meta': {'esType': 'long', 'type': 'number'},
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['allColumns'][1]": {
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                    'new_value': {
                        'columnId': 'x_metric_formula_accessor0',
                        'customLabel': False,
                        'fieldName': '@timestamp',
                        'label': '@timestamp',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['columns'][0]": {
                    'old_value': {'columnId': 'x_metric_formula_accessor0', 'fieldName': '@timestamp'},
                    'new_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'customLabel': False,
                        'fieldName': 'count',
                        'inMetricDimension': True,
                        'label': 'count',
                        'meta': {'esType': 'long', 'type': 'number'},
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['columns'][1]": {
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                    'new_value': {
                        'columnId': 'x_metric_formula_accessor0',
                        'customLabel': False,
                        'fieldName': '@timestamp',
                        'label': '@timestamp',
                    },
                },
                "root['state']['query']": {
                    'old_value': {'language': 'kuery', 'query': ''},
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY @timestamp'},
                },
            },
        }
    )


def test_gauge_esql_snapshot() -> None:
    """Explicit snapshot test for gauge-esql fixture.

    Tests an ES|QL gauge visualization with min/max/goal values.
    This validates gauge-specific configuration.
    """
    yaml_content = """
dashboards:
  - name: Gauge Test
    panels:
      - title: CPU Usage Gauge
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          type: gauge
          query: FROM metrics-* | STATS avg_cpu = AVG(system.cpu.total.pct)
          metric:
            field: avg_cpu
            id: metric_formula_accessor
          minimum: 0
          maximum: 1
          goal: 0.8
          appearance:
            shape: arc
"""
    diff = compute_diff(yaml_content, 'gauge-esql')
    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                ('root[\'state\'][\'adHocDataViews\'][\'{"index":"metrics-*","timeFieldName":"@timestamp"}\']'): {},
                (
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['index']"
                ): '{"index":"metrics-*","timeFieldName":"@timestamp"}',
                "root['state']['visualization']['showBar']": True,
            },
            'iterable_item_removed': {
                "root['references'][0]": {
                    'id': '{"index":"metrics-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                    'type': 'index-pattern',
                },
            },
            'values_changed': {
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['allColumns'][0]": {
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'avg_cpu'},
                    'new_value': {
                        'columnId': 'metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'avg_cpu',
                        'inMetricDimension': True,
                        'label': 'avg_cpu',
                        'meta': {'esType': 'long', 'type': 'number'},
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['allColumns'][1]": {
                    'old_value': {'columnId': 'metric_formula_accessor_max', 'fieldName': '1'},
                    'new_value': {'columnId': '<LAYER>_1', 'fieldName': '0'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['allColumns'][2]": {
                    'old_value': {'columnId': 'metric_formula_accessor_min', 'fieldName': '0'},
                    'new_value': {'columnId': '<LAYER>_2', 'fieldName': '1'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['allColumns'][3]": {
                    'old_value': {'columnId': 'metric_formula_accessor_goal', 'fieldName': '0.8'},
                    'new_value': {'columnId': '<LAYER>_3', 'fieldName': '0.8'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['columns'][0]": {
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'avg_cpu'},
                    'new_value': {
                        'columnId': 'metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'avg_cpu',
                        'inMetricDimension': True,
                        'label': 'avg_cpu',
                        'meta': {'esType': 'long', 'type': 'number'},
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['columns'][1]": {
                    'old_value': {'columnId': 'metric_formula_accessor_max', 'fieldName': '1'},
                    'new_value': {'columnId': '<LAYER>_1', 'fieldName': '0'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['columns'][2]": {
                    'old_value': {'columnId': 'metric_formula_accessor_min', 'fieldName': '0'},
                    'new_value': {'columnId': '<LAYER>_2', 'fieldName': '1'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['columns'][3]": {
                    'old_value': {'columnId': 'metric_formula_accessor_goal', 'fieldName': '0.8'},
                    'new_value': {'columnId': '<LAYER>_3', 'fieldName': '0.8'},
                },
                "root['state']['query']": {
                    'old_value': {'language': 'kuery', 'query': ''},
                    'new_value': {'esql': 'FROM metrics-* | STATS avg_cpu = AVG(system.cpu.total.pct)'},
                },
                "root['state']['visualization']['goalAccessor']": {
                    'old_value': 'metric_formula_accessor_goal',
                    'new_value': '<LAYER>_3',
                },
                "root['state']['visualization']['maxAccessor']": {
                    'old_value': 'metric_formula_accessor_max',
                    'new_value': '<LAYER>_2',
                },
                "root['state']['visualization']['minAccessor']": {
                    'old_value': 'metric_formula_accessor_min',
                    'new_value': '<LAYER>_1',
                },
            },
        }
    )


def test_heatmap_esql_snapshot() -> None:
    """Explicit snapshot test for heatmap-esql fixture.

    Tests an ES|QL heatmap visualization with x/y dimensions and value metric.
    This validates heatmap-specific configuration including grid settings.
    """
    yaml_content = """
dashboards:
  - name: Heatmap Test
    panels:
      - title: Traffic Heatmap by Geographic Location
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          type: heatmap
          query: FROM kibana_sample_data_logs | STATS bytes = SUM(bytes) BY geo.dest, geo.src
          x_axis:
            field: geo.src
            id: x_metric_formula_accessor
          y_axis:
            field: geo.dest
            id: y_metric_formula_accessor
          value:
            field: bytes
            id: metric_formula_accessor
"""
    diff = compute_diff(yaml_content, 'heatmap-esql')
    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"kibana_sample_data_logs","timeFieldName":"@timestamp"}\']': {},
                (
                    "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['index']"
                ): '{"index":"kibana_sample_data_logs","timeFieldName":"@timestamp"}',
            },
            'iterable_item_removed': {
                "root['references'][0]": {
                    'id': '{"index":"kibana_sample_data_logs","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                    'type': 'index-pattern',
                },
            },
            'values_changed': {
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['allColumns'][0]": {
                    'old_value': {'columnId': 'y_metric_formula_accessor', 'fieldName': 'geo.dest'},
                    'new_value': {
                        'columnId': 'x_metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'geo.src',
                        'label': 'geo.src',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['allColumns'][1]": {
                    'old_value': {'columnId': 'x_metric_formula_accessor', 'fieldName': 'geo.src'},
                    'new_value': {
                        'columnId': 'y_metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'geo.dest',
                        'label': 'geo.dest',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['allColumns'][2]": {
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'bytes'},
                    'new_value': {
                        'columnId': 'metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'bytes',
                        'inMetricDimension': True,
                        'label': 'bytes',
                        'meta': {'esType': 'long', 'type': 'number'},
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['columns'][0]": {
                    'old_value': {'columnId': 'y_metric_formula_accessor', 'fieldName': 'geo.dest'},
                    'new_value': {
                        'columnId': 'x_metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'geo.src',
                        'label': 'geo.src',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['columns'][1]": {
                    'old_value': {'columnId': 'x_metric_formula_accessor', 'fieldName': 'geo.src'},
                    'new_value': {
                        'columnId': 'y_metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'geo.dest',
                        'label': 'geo.dest',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['<LAYER>_0']['columns'][2]": {
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'bytes'},
                    'new_value': {
                        'columnId': 'metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'bytes',
                        'inMetricDimension': True,
                        'label': 'bytes',
                        'meta': {'esType': 'long', 'type': 'number'},
                    },
                },
                "root['state']['query']": {
                    'old_value': {'language': 'kuery', 'query': ''},
                    'new_value': {'esql': 'FROM kibana_sample_data_logs | STATS bytes = SUM(bytes) BY geo.dest, geo.src'},
                },
            },
        }
    )
