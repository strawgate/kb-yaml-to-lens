"""Dynamic fixture generation tests - invoke fixture generator directly from pytest.

Each test:
1. Defines the YAML configuration (what users write)
2. Defines the equivalent LensConfigBuilder configuration as raw TypeScript
3. Generates the fixture dynamically via Docker
4. Compiles the YAML and diffs against the generated fixture
5. Snapshots the exact differences using inline_snapshot

This approach ensures tests are self-contained and always use the latest
LensConfigBuilder output.
"""

from typing import Any

import pytest
import yaml
from inline_snapshot import snapshot

from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.loader import DashboardConfig
from tests.conftest import de_json_kbn_dashboard
from tests.fixtures import (
    compare_with_deepdiff,
    normalize_compiled_panel,
    normalize_diff_paths,
)
from tests.fixtures.generator import FixtureGenerator


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


def compute_diff_dynamic(
    yaml_content: str,
    fixture: dict[str, Any],
) -> dict[str, Any]:
    """Compile YAML content, diff against dynamically generated fixture, return normalized diff dict."""
    compiled = compile_yaml_content(yaml_content)

    # Compare using DeepDiff (handles order, nesting, etc.)
    diff = compare_with_deepdiff(compiled, fixture)

    # Normalize paths for stable snapshots
    return normalize_diff_paths(diff)


# =============================================================================
# Dynamic Fixture Generation Tests
#
# These tests generate fixtures on-the-fly using Docker and the real
# LensConfigBuilder API. They require Docker to run.
# =============================================================================


@pytest.mark.slow
class TestDynamicMetricFixtures:
    """Dynamic fixture tests for metric visualizations."""

    async def test_metric_basic_esql_dynamic(
        self,
        require_fixture_generator: FixtureGenerator,
    ) -> None:
        """Test basic metric compilation against dynamically generated fixture.

        This test defines both the YAML config (what users write) and the
        LensConfigBuilder config (what Kibana uses) in the same test,
        ensuring they stay in sync.
        """
        # Define the YAML (what users write)
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

        # Define equivalent LensConfigBuilder config as raw TypeScript
        typescript_config = """
        {
            chartType: 'metric',
            title: 'Basic Count Metric',
            dataset: { esql: 'FROM logs-* | STATS count = COUNT()' },
            value: 'count',
            label: 'Total Events',
        }
        """

        # Generate fixture dynamically
        fixture = await require_fixture_generator.generate(
            typescript_config,
            'metric-basic-dynamic',
            {'from': 'now-24h', 'to': 'now', 'type': 'relative'},
        )

        # Compute and snapshot the diff
        diff = compute_diff_dynamic(yaml_content, fixture)

        # The diff captures exact differences between compiled output and Kibana
        # This snapshot will update as we improve the compiler
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
                    "root['state']['visualization']['label']": 'Total Events',
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


@pytest.mark.slow
class TestDynamicPieFixtures:
    """Dynamic fixture tests for pie chart visualizations."""

    async def test_pie_chart_esql_dynamic(
        self,
        require_fixture_generator: FixtureGenerator,
    ) -> None:
        """Test pie chart compilation against dynamically generated fixture."""
        # Define the YAML (what users write)
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

        # Define equivalent LensConfigBuilder config as raw TypeScript
        typescript_config = """
        {
            chartType: 'pie',
            title: 'Events by Status',
            dataset: { esql: 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 10' },
            value: 'count',
            breakdown: ['log.level'],
            legend: { show: true, position: 'right' },
        }
        """

        # Generate fixture dynamically
        fixture = await require_fixture_generator.generate(
            typescript_config,
            'pie-chart-dynamic',
            {'from': 'now-24h', 'to': 'now', 'type': 'relative'},
        )

        # Compute and snapshot the diff
        diff = compute_diff_dynamic(yaml_content, fixture)

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
                        'old_value': {
                            'columnId': 'metric_formula_accessor_breakdown_0',
                            'fieldName': 'log.level',
                        },
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
                        'old_value': {
                            'columnId': 'metric_formula_accessor_breakdown_0',
                            'fieldName': 'log.level',
                        },
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


@pytest.mark.slow
class TestDynamicXYFixtures:
    """Dynamic fixture tests for XY chart visualizations."""

    async def test_xy_chart_esql_dynamic(
        self,
        require_fixture_generator: FixtureGenerator,
    ) -> None:
        """Test XY line chart compilation against dynamically generated fixture."""
        # Define the YAML (what users write)
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

        # Define equivalent LensConfigBuilder config as raw TypeScript
        typescript_config = """
        {
            chartType: 'xy',
            title: 'Events Over Time',
            dataset: { esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp' },
            layers: [{
                type: 'series',
                seriesType: 'line',
                xAxis: '@timestamp',
                yAxis: [{ label: 'Count', value: 'count' }],
            }],
            legend: { show: true, position: 'right' },
        }
        """

        # Generate fixture dynamically
        fixture = await require_fixture_generator.generate(
            typescript_config,
            'xy-chart-dynamic',
            {'from': 'now-7d', 'to': 'now', 'type': 'relative'},
        )

        # Compute and snapshot the diff
        diff = compute_diff_dynamic(yaml_content, fixture)

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
                    "root['state']['visualization']['axisTitlesVisibilitySettings']": {
                        'x': True,
                        'yLeft': True,
                        'yRight': True,
                    },
                    "root['state']['visualization']['emphasizeFitting']": True,
                    "root['state']['visualization']['fittingFunction']": 'Linear',
                    "root['state']['visualization']['gridlinesVisibilitySettings']": {
                        'x': True,
                        'yLeft': True,
                        'yRight': True,
                    },
                    "root['state']['visualization']['hideEndzones']": True,
                    "root['state']['visualization']['labelsOrientation']": {'x': 0, 'yLeft': 0, 'yRight': 0},
                    "root['state']['visualization']['layers'][0]['yConfig']": [{'forAccessor': 'metric_formula_accessor0_0'}],
                    "root['state']['visualization']['legend']['isVisible']": True,
                    "root['state']['visualization']['tickLabelsVisibilitySettings']": {
                        'x': True,
                        'yLeft': True,
                        'yRight': True,
                    },
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


@pytest.mark.slow
class TestDynamicGaugeFixtures:
    """Dynamic fixture tests for gauge visualizations."""

    async def test_gauge_esql_dynamic(
        self,
        require_fixture_generator: FixtureGenerator,
    ) -> None:
        """Test gauge compilation against dynamically generated fixture."""
        # Define the YAML (what users write)
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

        # Define equivalent LensConfigBuilder config as raw TypeScript
        typescript_config = """
        {
            chartType: 'gauge',
            title: 'CPU Usage Gauge',
            dataset: { esql: 'FROM metrics-* | STATS avg_cpu = AVG(system.cpu.total.pct)' },
            value: 'avg_cpu',
            queryMinValue: '0',
            queryMaxValue: '1',
            queryGoalValue: '0.8',
            shape: 'arc',
        }
        """

        # Generate fixture dynamically
        fixture = await require_fixture_generator.generate(
            typescript_config,
            'gauge-dynamic',
            {'from': 'now-15m', 'to': 'now', 'type': 'relative'},
        )

        # Compute and snapshot the diff
        diff = compute_diff_dynamic(yaml_content, fixture)

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


@pytest.mark.slow
class TestDynamicHeatmapFixtures:
    """Dynamic fixture tests for heatmap visualizations."""

    async def test_heatmap_esql_dynamic(
        self,
        require_fixture_generator: FixtureGenerator,
    ) -> None:
        """Test heatmap compilation against dynamically generated fixture."""
        # Define the YAML (what users write)
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

        # Define equivalent LensConfigBuilder config as raw TypeScript
        typescript_config = """
        {
            chartType: 'heatmap',
            title: 'Traffic Heatmap by Geographic Location',
            dataset: { esql: 'FROM kibana_sample_data_logs | STATS bytes = SUM(bytes) BY geo.dest, geo.src' },
            xAxis: 'geo.src',
            breakdown: 'geo.dest',
            value: 'bytes',
            legend: { show: true, position: 'right' },
        }
        """

        # Generate fixture dynamically
        fixture = await require_fixture_generator.generate(
            typescript_config,
            'heatmap-dynamic',
            {'from': 'now-7d', 'to': 'now', 'type': 'relative'},
        )

        # Compute and snapshot the diff
        diff = compute_diff_dynamic(yaml_content, fixture)

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
