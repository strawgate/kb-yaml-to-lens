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

from pathlib import Path
from typing import Any

import pytest
import yaml
from inline_snapshot import snapshot

# Mark all tests in this module to use session-scoped event loop
# This allows them to share the session-scoped fixture container
pytestmark = pytest.mark.asyncio(loop_scope='session')

from dashboard_compiler.dashboard_compiler import render
from dashboard_compiler.loader import DashboardConfig
from tests.conftest import de_json_kbn_dashboard
from tests.fixtures.fixture_utils import (
    compare_with_deepdiff,
    normalize_compiled_panel,
)
from tests.fixtures.generator import generate_fixture


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


def compute_diff(
    yaml_content: str,
    fixture: dict[str, Any],
) -> dict[str, Any]:
    """Compile YAML content, diff against dynamically generated fixture, return diff dict."""
    compiled = compile_yaml_content(yaml_content)
    diff = compare_with_deepdiff(compiled, fixture)
    return diff.to_dict()  # pyright: ignore[reportUnknownMemberType]


# =============================================================================
# Dynamic Fixture Generation Tests
#
# These tests generate fixtures on-the-fly using Docker and the real
# LensConfigBuilder API. They require Docker to run.
# =============================================================================


@pytest.mark.slow
async def test_metric_basic_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test basic metric compilation against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Basic Count Metric Test
    panels:
      - title: Basic Count Metric
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: metric
          query: FROM logs-* | STATS count = COUNT()
          primary:
            field: count
            id: metric_formula_accessor
"""

    typescript_config = """
    {
        chartType: 'metric',
        title: 'Basic Count Metric',
        dataset: { esql: 'FROM logs-* | STATS count = COUNT()' },
        value: 'count',
        label: 'Total Events',
    }
    """

    container, output_dir = shared_fixture_container
    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'metric-basic-dynamic',
        'LensMetricConfig',
        {'from': 'now-24h', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]['label']": 'count',
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]['customLabel']": False,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]['inMetricDimension']": True,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]['meta']['esType']": 'long',
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]['label']": 'count',
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]['customLabel']": False,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]['inMetricDimension']": True,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]['meta']['esType']": 'long',
            },
            'dictionary_item_removed': {
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
            'values_changed': {
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT()'},
                    'old_value': {'language': 'kuery', 'query': ''},
                }
            },
        }
    )


@pytest.mark.slow
async def test_pie_chart_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test pie chart compilation against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Pie Chart Test
    panels:
      - title: Events by Status
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: pie
          query: FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 10
          metrics:
            - field: count
              id: metric_formula_accessor
          dimensions:
            - field: log.level
              id: metric_formula_accessor_breakdown_0
"""

    typescript_config = """
    {
        chartType: 'pie',
        title: 'Events by Status',
        dataset: { esql: 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 10' },
        value: 'count',
        breakdown: ['log.level'],
        legend: { show: true },
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'pie-chart-dynamic',
        'LensPieConfig',
        {'from': 'now-24h', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
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
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
                "root['state']['visualization']['layers'][0]['allowMultipleMetrics']": False,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                "root['state']['visualization']['layers'][0]['legendPosition']": 'right',
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
            'values_changed': {
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 10'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['visualization']['layers'][0]['legendDisplay']": {
                    'new_value': 'default',
                    'old_value': 'show',
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'fieldName': 'log.level',
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'label': 'log.level',
                        'customLabel': False,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'fieldName': 'log.level',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'fieldName': 'log.level',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'fieldName': 'log.level',
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'label': 'log.level',
                        'customLabel': False,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                },
            },
        }
    )


@pytest.mark.slow
async def test_xy_chart_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test XY line chart compilation against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: XY Chart Test
    panels:
      - title: Events Over Time
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: line
          query: FROM logs-* | STATS count = COUNT() BY @timestamp
          dimension:
            field: '@timestamp'
            id: x_metric_formula_accessor0
          metrics:
            - field: count
              id: metric_formula_accessor0_0
"""

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
        legend: { show: true },
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'xy-chart-dynamic',
        'LensXYConfig',
        {'from': 'now-7d', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['visualization']['layers'][0]['colorMapping']": {
                    'assignments': [],
                    'colorMode': {'type': 'categorical'},
                    'paletteId': 'eui_amsterdam_color_blind',
                    'specialAssignments': [{'color': {'type': 'loop'}, 'rule': {'type': 'other'}, 'touched': False}],
                },
                "root['state']['visualization']['layers'][0]['position']": 'top',
                "root['state']['visualization']['layers'][0]['showGridlines']": False,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
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
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                "root['state']['visualization']['yLeftExtent']": {'mode': 'full'},
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
            'values_changed': {
                "root['state']['visualization']['legend']['position']": {'new_value': 'right', 'old_value': 'left'},
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY @timestamp'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'fieldName': '@timestamp',
                        'columnId': 'x_metric_formula_accessor0',
                        'label': '@timestamp',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor0_0',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor0', 'fieldName': '@timestamp'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor0_0',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor0', 'fieldName': '@timestamp'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'fieldName': '@timestamp',
                        'columnId': 'x_metric_formula_accessor0',
                        'label': '@timestamp',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                },
            },
        }
    )


@pytest.mark.slow
async def test_gauge_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test gauge compilation against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Gauge Test
    panels:
      - title: CPU Usage Gauge
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
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

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'gauge-dynamic',
        'LensGaugeConfig',
        {'from': 'now-15m', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"metrics-*","timeFieldName":"@timestamp"}\']': {},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"metrics-*","timeFieldName":"@timestamp"}',
                "root['state']['visualization']['showBar']": True,
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"metrics-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
            'values_changed': {
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM metrics-* | STATS avg_cpu = AVG(system.cpu.total.pct)'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['visualization']['goalAccessor']": {
                    'new_value': '9d42c6a6-8c1f-1504-751c-61a1b77b8b30',
                    'old_value': 'metric_formula_accessor_goal',
                },
                "root['state']['visualization']['maxAccessor']": {
                    'new_value': '937e1915-1fe1-eff3-2bca-2e6f3dfdd536',
                    'old_value': 'metric_formula_accessor_max',
                },
                "root['state']['visualization']['minAccessor']": {
                    'new_value': 'd346c9c0-f807-92dc-4a87-dd7cfe500505',
                    'old_value': 'metric_formula_accessor_min',
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {'fieldName': '0', 'columnId': 'd346c9c0-f807-92dc-4a87-dd7cfe500505'},
                    'old_value': {'columnId': 'metric_formula_accessor_max', 'fieldName': '1'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][2]": {
                    'new_value': {'fieldName': '1', 'columnId': '937e1915-1fe1-eff3-2bca-2e6f3dfdd536'},
                    'old_value': {'columnId': 'metric_formula_accessor_min', 'fieldName': '0'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {'fieldName': '0', 'columnId': 'd346c9c0-f807-92dc-4a87-dd7cfe500505'},
                    'old_value': {'columnId': 'metric_formula_accessor_max', 'fieldName': '1'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'avg_cpu',
                        'columnId': 'metric_formula_accessor',
                        'label': 'avg_cpu',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'avg_cpu'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'avg_cpu',
                        'columnId': 'metric_formula_accessor',
                        'label': 'avg_cpu',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'avg_cpu'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][3]": {
                    'new_value': {
                        'fieldName': '0.8',
                        'columnId': '9d42c6a6-8c1f-1504-751c-61a1b77b8b30',
                    },
                    'old_value': {'columnId': 'metric_formula_accessor_goal', 'fieldName': '0.8'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][3]": {
                    'new_value': {
                        'fieldName': '0.8',
                        'columnId': '9d42c6a6-8c1f-1504-751c-61a1b77b8b30',
                    },
                    'old_value': {'columnId': 'metric_formula_accessor_goal', 'fieldName': '0.8'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][2]": {
                    'new_value': {'fieldName': '1', 'columnId': '937e1915-1fe1-eff3-2bca-2e6f3dfdd536'},
                    'old_value': {'columnId': 'metric_formula_accessor_min', 'fieldName': '0'},
                },
            },
        }
    )


@pytest.mark.slow
async def test_heatmap_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test heatmap compilation against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Heatmap Test
    panels:
      - title: Traffic Heatmap by Geographic Location
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
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

    typescript_config = """
    {
        chartType: 'heatmap',
        title: 'Traffic Heatmap by Geographic Location',
        dataset: { esql: 'FROM kibana_sample_data_logs | STATS bytes = SUM(bytes) BY geo.dest, geo.src' },
        xAxis: 'geo.src',
        breakdown: 'geo.dest',
        value: 'bytes',
        legend: { show: true },
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'heatmap-dynamic',
        'LensHeatmapConfig',
        {'from': 'now-7d', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"kibana_sample_data_logs","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"kibana_sample_data_logs","timeFieldName":"@timestamp"}\']': {},
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"kibana_sample_data_logs","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
            'values_changed': {
                "root['state']['visualization']['legend']['position']": {'new_value': 'right', 'old_value': 'left'},
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM kibana_sample_data_logs | STATS bytes = SUM(bytes) BY geo.dest, geo.src'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'fieldName': 'geo.dest',
                        'columnId': 'y_metric_formula_accessor',
                        'label': 'geo.dest',
                        'customLabel': False,
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor', 'fieldName': 'geo.src'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][2]": {
                    'new_value': {
                        'fieldName': 'bytes',
                        'columnId': 'metric_formula_accessor',
                        'label': 'bytes',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'bytes'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'fieldName': 'geo.dest',
                        'columnId': 'y_metric_formula_accessor',
                        'label': 'geo.dest',
                        'customLabel': False,
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor', 'fieldName': 'geo.src'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'geo.src',
                        'columnId': 'x_metric_formula_accessor',
                        'label': 'geo.src',
                        'customLabel': False,
                    },
                    'old_value': {'columnId': 'y_metric_formula_accessor', 'fieldName': 'geo.dest'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'geo.src',
                        'columnId': 'x_metric_formula_accessor',
                        'label': 'geo.src',
                        'customLabel': False,
                    },
                    'old_value': {'columnId': 'y_metric_formula_accessor', 'fieldName': 'geo.dest'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][2]": {
                    'new_value': {
                        'fieldName': 'bytes',
                        'columnId': 'metric_formula_accessor',
                        'label': 'bytes',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'bytes'},
                },
            },
        }
    )


@pytest.mark.slow
async def test_tagcloud_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test tagcloud compilation against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Tagcloud Test
    panels:
      - title: Top Log Levels
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: tagcloud
          query: FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 20
          dimension:
            field: log.level
            id: metric_formula_accessor_breakdown
          metric:
            field: count
            id: metric_formula_accessor
"""

    typescript_config = """
    {
        chartType: 'tagcloud',
        title: 'Top Log Levels',
        dataset: { esql: 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 20' },
        value: 'count',
        breakdown: 'log.level',
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'tagcloud-dynamic',
        'LensTagCloudConfig',
        {'from': 'now-24h', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
            'values_changed': {
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 20'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown',
                        'fieldName': 'log.level',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'log.level',
                        'columnId': 'metric_formula_accessor_breakdown',
                        'label': 'log.level',
                        'customLabel': False,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'log.level',
                        'columnId': 'metric_formula_accessor_breakdown',
                        'label': 'log.level',
                        'customLabel': False,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown',
                        'fieldName': 'log.level',
                    },
                },
            },
        }
    )


@pytest.mark.slow
async def test_metric_with_breakdown_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test metric with breakdown compilation against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Metric Breakdown Test
    panels:
      - title: Count by Agent
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: metric
          query: FROM logs-* | STATS count = COUNT() BY agent.name | SORT count DESC | LIMIT 5
          primary:
            field: count
            id: metric_formula_accessor
          breakdown:
            field: agent.name
            id: metric_formula_accessor_breakdown
"""

    typescript_config = """
    {
        chartType: 'metric',
        title: 'Count by Agent',
        dataset: { esql: 'FROM logs-* | STATS count = COUNT() BY agent.name | SORT count DESC | LIMIT 5' },
        value: 'count',
        breakdown: 'agent.name',
        label: 'Events per Agent',
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'metric-breakdown-dynamic',
        'LensMetricConfig',
        {'from': 'now-24h', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
            'values_changed': {
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY agent.name | SORT count DESC | LIMIT 5'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'fieldName': 'agent.name',
                        'columnId': 'metric_formula_accessor_breakdown',
                        'label': 'agent.name',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown',
                        'fieldName': 'agent.name',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown',
                        'fieldName': 'agent.name',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'fieldName': 'agent.name',
                        'columnId': 'metric_formula_accessor_breakdown',
                        'label': 'agent.name',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                },
            },
        }
    )


@pytest.mark.slow
async def test_datatable_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test datatable compilation against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Datatable Test
    panels:
      - title: Agent Version Stats
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: datatable
          query: FROM logs-* | STATS count = COUNT() BY agent.version | SORT count DESC | LIMIT 10
          dimensions:
            - field: agent.version
              id: metric_formula_accessor_breakdown_0
          metrics:
            - field: count
              id: metric_formula_accessor
"""

    typescript_config = """
    {
        chartType: 'table',
        title: 'Agent Version Stats',
        dataset: { esql: 'FROM logs-* | STATS count = COUNT() BY agent.version | SORT count DESC | LIMIT 10' },
        breakdown: ['agent.version'],
        value: 'count',
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'datatable-dynamic',
        'LensTableConfig',
        {'from': 'now-24h', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
            'values_changed': {
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY agent.version | SORT count DESC | LIMIT 10'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['visualization']['columns'][0]": {
                    'new_value': {'columnId': 'metric_formula_accessor_breakdown_0', 'isTransposed': False, 'isMetric': False},
                    'old_value': {'columnId': 'metric_formula_accessor'},
                },
                "root['state']['visualization']['columns'][1]": {
                    'new_value': {'columnId': 'metric_formula_accessor', 'isTransposed': False, 'isMetric': True},
                    'old_value': {'columnId': 'metric_formula_accessor_breakdown_0'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'agent.version',
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'label': 'agent.version',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'fieldName': 'agent.version',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'agent.version',
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'label': 'agent.version',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'fieldName': 'agent.version',
                    },
                },
            },
        }
    )


# =============================================================================
# Additional Dynamic Fixture Tests
#
# Tests for additional chart types and configurations.
# =============================================================================


@pytest.mark.slow
async def test_pie_chart_donut_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test donut chart compilation against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Donut Chart Test
    panels:
      - title: Response Codes Distribution (Donut)
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: pie
          query: FROM logs-* | STATS count = COUNT() BY response.keyword
          metrics:
            - field: count
              id: metric_formula_accessor
          dimensions:
            - field: response.keyword
              id: metric_formula_accessor_breakdown_0
          appearance:
            donut: medium
"""

    typescript_config = """
    {
        chartType: 'donut',
        title: 'Response Codes Distribution (Donut)',
        dataset: { esql: 'FROM logs-* | STATS count = COUNT() BY response.keyword' },
        value: 'count',
        breakdown: ['response.keyword'],
        legend: { show: true },
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'pie-chart-donut-dynamic',
        'LensPieConfig',
        {'from': 'now-7d', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['visualization']['layers'][0]['colorMapping']": {
                    'assignments': [],
                    'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                    'paletteId': 'eui_amsterdam_color_blind',
                    'colorMode': {'type': 'categorical'},
                },
                "root['state']['visualization']['layers'][0]['nestedLegend']": False,
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['visualization']['layers'][0]['allowMultipleMetrics']": False,
                "root['state']['visualization']['layers'][0]['legendPosition']": 'right',
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
            },
            'values_changed': {
                "root['state']['visualization']['layers'][0]['legendDisplay']": {
                    'new_value': 'default',
                    'old_value': 'show',
                },
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY response.keyword'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'fieldName': 'response.keyword',
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'label': 'response.keyword',
                        'customLabel': False,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'fieldName': 'response.keyword',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'fieldName': 'response.keyword',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'fieldName': 'response.keyword',
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'label': 'response.keyword',
                        'customLabel': False,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                },
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
        }
    )


@pytest.mark.slow
async def test_pie_chart_bottom_legend_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test pie chart with bottom legend position against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Pie Chart Bottom Legend Test
    panels:
      - title: Request Methods Distribution
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: pie
          query: FROM logs-* | STATS count = COUNT() BY request.method
          metrics:
            - field: count
              id: metric_formula_accessor
          dimensions:
            - field: request.method
              id: metric_formula_accessor_breakdown_0
"""

    typescript_config = """
    {
        chartType: 'pie',
        title: 'Request Methods Distribution',
        dataset: { esql: 'FROM logs-* | STATS count = COUNT() BY request.method' },
        value: 'count',
        breakdown: ['request.method'],
        legend: { show: true },
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'pie-chart-bottom-legend-dynamic',
        'LensPieConfig',
        {'from': 'now-24h', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['visualization']['layers'][0]['colorMapping']": {
                    'assignments': [],
                    'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                    'paletteId': 'eui_amsterdam_color_blind',
                    'colorMode': {'type': 'categorical'},
                },
                "root['state']['visualization']['layers'][0]['nestedLegend']": False,
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['visualization']['layers'][0]['allowMultipleMetrics']": False,
                "root['state']['visualization']['layers'][0]['legendPosition']": 'right',
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
            },
            'values_changed': {
                "root['state']['visualization']['layers'][0]['legendDisplay']": {
                    'new_value': 'default',
                    'old_value': 'show',
                },
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY request.method'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'fieldName': 'request.method',
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'label': 'request.method',
                        'customLabel': False,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'fieldName': 'request.method',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'fieldName': 'request.method',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'fieldName': 'request.method',
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'label': 'request.method',
                        'customLabel': False,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                },
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
        }
    )


@pytest.mark.slow
async def test_xy_bar_chart_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test XY bar chart compilation against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Bar Chart Test
    panels:
      - title: Events Over Time (Bar)
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: bar
          query: FROM logs-* | STATS count = COUNT() BY @timestamp
          dimension:
            field: '@timestamp'
            id: x_metric_formula_accessor0
          metrics:
            - field: count
              id: metric_formula_accessor0_0
"""

    typescript_config = """
    {
        chartType: 'xy',
        title: 'Events Over Time (Bar)',
        dataset: { esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp' },
        layers: [{
            type: 'series',
            seriesType: 'bar',
            xAxis: '@timestamp',
            yAxis: [{ label: 'Count', value: 'count' }],
        }],
        legend: { show: true },
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'xy-bar-chart-dynamic',
        'LensXYConfig',
        {'from': 'now-7d', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['visualization']['layers'][0]['position']": 'top',
                "root['state']['visualization']['layers'][0]['showGridlines']": False,
                "root['state']['visualization']['layers'][0]['colorMapping']": {
                    'assignments': [],
                    'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                    'paletteId': 'eui_amsterdam_color_blind',
                    'colorMode': {'type': 'categorical'},
                },
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['visualization']['axisTitlesVisibilitySettings']": {
                    'x': True,
                    'yLeft': True,
                    'yRight': True,
                },
                "root['state']['visualization']['hideEndzones']": True,
                "root['state']['visualization']['emphasizeFitting']": True,
                "root['state']['visualization']['fittingFunction']": 'Linear',
                "root['state']['visualization']['yLeftExtent']": {'mode': 'full'},
                "root['state']['visualization']['tickLabelsVisibilitySettings']": {
                    'x': True,
                    'yLeft': True,
                    'yRight': True,
                },
                "root['state']['visualization']['labelsOrientation']": {
                    'x': 0,
                    'yLeft': 0,
                    'yRight': 0,
                },
                "root['state']['visualization']['gridlinesVisibilitySettings']": {
                    'x': True,
                    'yLeft': True,
                    'yRight': True,
                },
                "root['state']['visualization']['layers'][0]['yConfig']": [{'forAccessor': 'metric_formula_accessor0_0'}],
                "root['state']['visualization']['legend']['isVisible']": True,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
            },
            'values_changed': {
                "root['state']['visualization']['layers'][0]['seriesType']": {
                    'new_value': 'bar_stacked',
                    'old_value': 'bar',
                },
                "root['state']['visualization']['legend']['position']": {'new_value': 'right', 'old_value': 'left'},
                "root['state']['visualization']['preferredSeriesType']": {
                    'new_value': 'bar_stacked',
                    'old_value': 'line',
                },
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY @timestamp'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'fieldName': '@timestamp',
                        'columnId': 'x_metric_formula_accessor0',
                        'label': '@timestamp',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor0_0',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor0', 'fieldName': '@timestamp'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor0_0',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor0', 'fieldName': '@timestamp'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'fieldName': '@timestamp',
                        'columnId': 'x_metric_formula_accessor0',
                        'label': '@timestamp',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                },
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
        }
    )


@pytest.mark.slow
async def test_xy_area_chart_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test XY area chart compilation against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Area Chart Test
    panels:
      - title: Events Over Time (Area)
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: area
          query: FROM logs-* | STATS count = COUNT() BY @timestamp
          dimension:
            field: '@timestamp'
            id: x_metric_formula_accessor0
          metrics:
            - field: count
              id: metric_formula_accessor0_0
"""

    typescript_config = """
    {
        chartType: 'xy',
        title: 'Events Over Time (Area)',
        dataset: { esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp' },
        layers: [{
            type: 'series',
            seriesType: 'area',
            xAxis: '@timestamp',
            yAxis: [{ label: 'Count', value: 'count' }],
        }],
        legend: { show: true },
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'xy-area-chart-dynamic',
        'LensXYConfig',
        {'from': 'now-7d', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['visualization']['layers'][0]['position']": 'top',
                "root['state']['visualization']['layers'][0]['showGridlines']": False,
                "root['state']['visualization']['layers'][0]['colorMapping']": {
                    'assignments': [],
                    'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                    'paletteId': 'eui_amsterdam_color_blind',
                    'colorMode': {'type': 'categorical'},
                },
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['visualization']['axisTitlesVisibilitySettings']": {
                    'x': True,
                    'yLeft': True,
                    'yRight': True,
                },
                "root['state']['visualization']['hideEndzones']": True,
                "root['state']['visualization']['emphasizeFitting']": True,
                "root['state']['visualization']['fittingFunction']": 'Linear',
                "root['state']['visualization']['yLeftExtent']": {'mode': 'full'},
                "root['state']['visualization']['tickLabelsVisibilitySettings']": {
                    'x': True,
                    'yLeft': True,
                    'yRight': True,
                },
                "root['state']['visualization']['labelsOrientation']": {
                    'x': 0,
                    'yLeft': 0,
                    'yRight': 0,
                },
                "root['state']['visualization']['gridlinesVisibilitySettings']": {
                    'x': True,
                    'yLeft': True,
                    'yRight': True,
                },
                "root['state']['visualization']['layers'][0]['yConfig']": [{'forAccessor': 'metric_formula_accessor0_0'}],
                "root['state']['visualization']['legend']['isVisible']": True,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
            },
            'values_changed': {
                "root['state']['visualization']['legend']['position']": {'new_value': 'right', 'old_value': 'left'},
                "root['state']['visualization']['preferredSeriesType']": {
                    'new_value': 'area',
                    'old_value': 'line',
                },
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY @timestamp'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'fieldName': '@timestamp',
                        'columnId': 'x_metric_formula_accessor0',
                        'label': '@timestamp',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor0_0',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor0', 'fieldName': '@timestamp'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor0_0',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor0', 'fieldName': '@timestamp'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'fieldName': '@timestamp',
                        'columnId': 'x_metric_formula_accessor0',
                        'label': '@timestamp',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                },
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
        }
    )


@pytest.mark.slow
async def test_xy_line_chart_fitting_function_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test XY line chart with fitting function (Linear interpolation)."""
    yaml_content = """
dashboards:
  - name: Line Chart Fitting Function Test
    panels:
      - title: Line Chart - Linear Fitting
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: line
          query: FROM logs-* | STATS count = COUNT() BY @timestamp
          dimension:
            field: '@timestamp'
            id: x_metric_formula_accessor0
          metrics:
            - field: count
              id: metric_formula_accessor0_0
          appearance:
            missing_values: Linear
            show_as_dotted: true
"""

    typescript_config = """
    {
        chartType: 'xy',
        title: 'Line Chart - Linear Fitting',
        dataset: { esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp' },
        layers: [{
            type: 'series',
            seriesType: 'line',
            xAxis: '@timestamp',
            yAxis: [{ label: 'Count', value: 'count' }],
        }],
        fittingFunction: 'Linear',
        emphasizeFitting: true,
    }
    """
    container, output_dir = shared_fixture_container
    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'xy-line-fitting-dynamic',
        'LensXYConfig',
        {'from': 'now-7d', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['visualization']['layers'][0]['position']": 'top',
                "root['state']['visualization']['layers'][0]['showGridlines']": False,
                "root['state']['visualization']['layers'][0]['colorMapping']": {
                    'assignments': [],
                    'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                    'paletteId': 'eui_amsterdam_color_blind',
                    'colorMode': {'type': 'categorical'},
                },
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['visualization']['axisTitlesVisibilitySettings']": {
                    'x': True,
                    'yLeft': True,
                    'yRight': True,
                },
                "root['state']['visualization']['hideEndzones']": True,
                "root['state']['visualization']['yLeftExtent']": {'mode': 'full'},
                "root['state']['visualization']['tickLabelsVisibilitySettings']": {
                    'x': True,
                    'yLeft': True,
                    'yRight': True,
                },
                "root['state']['visualization']['labelsOrientation']": {
                    'x': 0,
                    'yLeft': 0,
                    'yRight': 0,
                },
                "root['state']['visualization']['gridlinesVisibilitySettings']": {
                    'x': True,
                    'yLeft': True,
                    'yRight': True,
                },
                "root['state']['visualization']['layers'][0]['yConfig']": [{'forAccessor': 'metric_formula_accessor0_0'}],
                "root['state']['visualization']['legend']['isVisible']": True,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
            },
            'values_changed': {
                "root['state']['visualization']['legend']['position']": {
                    'new_value': 'right',
                    'old_value': 'left',
                },
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY @timestamp'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'fieldName': '@timestamp',
                        'columnId': 'x_metric_formula_accessor0',
                        'label': '@timestamp',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor0_0',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor0', 'fieldName': '@timestamp'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor0_0',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor0', 'fieldName': '@timestamp'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'fieldName': '@timestamp',
                        'columnId': 'x_metric_formula_accessor0',
                        'label': '@timestamp',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                },
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
        }
    )


@pytest.mark.slow
async def test_xy_multi_metric_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test XY chart with multiple metrics (multi-series) against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Multi-Metric Chart Test
    panels:
      - title: ES|QL Multi-Metric Chart
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: bar
          query: FROM logs-* | STATS event_count = COUNT(), total_bytes = SUM(bytes), avg_bytes = AVG(bytes) BY @timestamp
          dimension:
            field: '@timestamp'
            id: x_metric_formula_accessor0
          metrics:
            - field: event_count
              id: metric_formula_accessor0_0
          legend:
            position: bottom
"""

    typescript_config = """
    {
        chartType: 'xy',
        title: 'ES|QL Multi-Metric Chart',
        dataset: { esql: 'FROM logs-* | STATS event_count = COUNT(), total_bytes = SUM(bytes), avg_bytes = AVG(bytes) BY @timestamp' },
        layers: [{
            type: 'series',
            seriesType: 'bar',
            xAxis: '@timestamp',
            yAxis: [{ label: 'Event Count', value: 'event_count' }],
        }],
        legend: { show: true },
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'xy-multi-metric-dynamic',
        'LensXYConfig',
        {'from': 'now-24h', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['visualization']['layers'][0]['position']": 'top',
                "root['state']['visualization']['layers'][0]['showGridlines']": False,
                "root['state']['visualization']['layers'][0]['colorMapping']": {
                    'assignments': [],
                    'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                    'paletteId': 'eui_amsterdam_color_blind',
                    'colorMode': {'type': 'categorical'},
                },
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['visualization']['axisTitlesVisibilitySettings']": {
                    'x': True,
                    'yLeft': True,
                    'yRight': True,
                },
                "root['state']['visualization']['hideEndzones']": True,
                "root['state']['visualization']['emphasizeFitting']": True,
                "root['state']['visualization']['fittingFunction']": 'Linear',
                "root['state']['visualization']['yLeftExtent']": {'mode': 'full'},
                "root['state']['visualization']['tickLabelsVisibilitySettings']": {
                    'x': True,
                    'yLeft': True,
                    'yRight': True,
                },
                "root['state']['visualization']['labelsOrientation']": {
                    'x': 0,
                    'yLeft': 0,
                    'yRight': 0,
                },
                "root['state']['visualization']['gridlinesVisibilitySettings']": {
                    'x': True,
                    'yLeft': True,
                    'yRight': True,
                },
                "root['state']['visualization']['layers'][0]['yConfig']": [{'forAccessor': 'metric_formula_accessor0_0'}],
                "root['state']['visualization']['legend']['isVisible']": True,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
            },
            'values_changed': {
                "root['state']['visualization']['layers'][0]['seriesType']": {
                    'new_value': 'bar_stacked',
                    'old_value': 'bar',
                },
                "root['state']['visualization']['legend']['position']": {'new_value': 'bottom', 'old_value': 'left'},
                "root['state']['visualization']['preferredSeriesType']": {
                    'new_value': 'bar_stacked',
                    'old_value': 'line',
                },
                "root['state']['query']": {
                    'new_value': {
                        'esql': 'FROM logs-* | STATS event_count = COUNT(), total_bytes = SUM(bytes), avg_bytes = AVG(bytes) BY @timestamp'
                    },
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'fieldName': '@timestamp',
                        'columnId': 'x_metric_formula_accessor0',
                        'label': '@timestamp',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'fieldName': 'event_count',
                        'meta': {'type': 'number'},
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'event_count',
                        'columnId': 'metric_formula_accessor0_0',
                        'label': 'event_count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor0', 'fieldName': '@timestamp'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'event_count',
                        'columnId': 'metric_formula_accessor0_0',
                        'label': 'event_count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor0', 'fieldName': '@timestamp'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'fieldName': '@timestamp',
                        'columnId': 'x_metric_formula_accessor0',
                        'label': '@timestamp',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'fieldName': 'event_count',
                        'meta': {'type': 'number'},
                    },
                },
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
        }
    )


@pytest.mark.slow
async def test_xy_chart_with_breakdown_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test XY chart with breakdown dimension (split series) against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: XY Chart Breakdown Test
    panels:
      - title: Events by Status Over Time
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: line
          query: FROM logs-* | STATS count = COUNT() BY @timestamp, log.level | SORT @timestamp
          dimension:
            field: '@timestamp'
            id: x_metric_formula_accessor0
          metrics:
            - field: count
              id: metric_formula_accessor0_0
          breakdown:
            field: log.level
            id: breakdown_metric_formula_accessor0
"""

    typescript_config = """
    {
        chartType: 'xy',
        title: 'Events by Status Over Time',
        dataset: { esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp, log.level | SORT @timestamp' },
        layers: [{
            type: 'series',
            seriesType: 'line',
            xAxis: '@timestamp',
            yAxis: [{ label: 'Count', value: 'count' }],
            breakdown: 'log.level',
        }],
        legend: { show: true },
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'xy-chart-breakdown-dynamic',
        'LensXYConfig',
        {'from': 'now-7d', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['visualization']['layers'][0]['position']": 'top',
                "root['state']['visualization']['layers'][0]['showGridlines']": False,
                "root['state']['visualization']['layers'][0]['colorMapping']": {
                    'assignments': [],
                    'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                    'paletteId': 'eui_amsterdam_color_blind',
                    'colorMode': {'type': 'categorical'},
                },
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['visualization']['axisTitlesVisibilitySettings']": {
                    'x': True,
                    'yLeft': True,
                    'yRight': True,
                },
                "root['state']['visualization']['hideEndzones']": True,
                "root['state']['visualization']['emphasizeFitting']": True,
                "root['state']['visualization']['fittingFunction']": 'Linear',
                "root['state']['visualization']['yLeftExtent']": {'mode': 'full'},
                "root['state']['visualization']['tickLabelsVisibilitySettings']": {
                    'x': True,
                    'yLeft': True,
                    'yRight': True,
                },
                "root['state']['visualization']['labelsOrientation']": {
                    'x': 0,
                    'yLeft': 0,
                    'yRight': 0,
                },
                "root['state']['visualization']['gridlinesVisibilitySettings']": {
                    'x': True,
                    'yLeft': True,
                    'yRight': True,
                },
                "root['state']['visualization']['layers'][0]['yConfig']": [{'forAccessor': 'metric_formula_accessor0_0'}],
                "root['state']['visualization']['legend']['isVisible']": True,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
            },
            'values_changed': {
                "root['state']['visualization']['legend']['position']": {'new_value': 'right', 'old_value': 'left'},
                "root['state']['visualization']['layers'][0]['splitAccessor']": {
                    'new_value': 'breakdown_metric_formula_accessor0',
                    'old_value': 'metric_formula_accessor0_breakdown',
                },
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY @timestamp, log.level | SORT @timestamp'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'fieldName': '@timestamp',
                        'columnId': 'x_metric_formula_accessor0',
                        'label': '@timestamp',
                        'customLabel': False,
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor0', 'fieldName': '@timestamp'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][2]": {
                    'new_value': {
                        'fieldName': 'log.level',
                        'columnId': 'breakdown_metric_formula_accessor0',
                        'label': 'log.level',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'fieldName': '@timestamp',
                        'columnId': 'x_metric_formula_accessor0',
                        'label': '@timestamp',
                        'customLabel': False,
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor0', 'fieldName': '@timestamp'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor0_0',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_breakdown',
                        'fieldName': 'log.level',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor0_0',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_breakdown',
                        'fieldName': 'log.level',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][2]": {
                    'new_value': {
                        'fieldName': 'log.level',
                        'columnId': 'breakdown_metric_formula_accessor0',
                        'label': 'log.level',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                },
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
        }
    )


@pytest.mark.slow
async def test_gauge_semi_circle_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test gauge with arc shape against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Gauge Arc Test
    panels:
      - title: Memory Usage Gauge
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: gauge
          query: FROM metrics-* | STATS avg_memory = AVG(system.memory.used.pct)
          metric:
            field: avg_memory
            id: metric_formula_accessor
          minimum: 0
          maximum: 1
          goal: 0.7
          appearance:
            shape: arc
"""

    typescript_config = """
    {
        chartType: 'gauge',
        title: 'Memory Usage Gauge',
        dataset: { esql: 'FROM metrics-* | STATS avg_memory = AVG(system.memory.used.pct)' },
        value: 'avg_memory',
        queryMinValue: '0',
        queryMaxValue: '1',
        queryGoalValue: '0.7',
        shape: 'arc',
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'gauge-semi-circle-dynamic',
        'LensGaugeConfig',
        {'from': 'now-15m', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['visualization']['showBar']": True,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"metrics-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"metrics-*","timeFieldName":"@timestamp"}\']': {},
            },
            'values_changed': {
                "root['state']['visualization']['minAccessor']": {
                    'new_value': 'd346c9c0-f807-92dc-4a87-dd7cfe500505',
                    'old_value': 'metric_formula_accessor_min',
                },
                "root['state']['visualization']['maxAccessor']": {
                    'new_value': '937e1915-1fe1-eff3-2bca-2e6f3dfdd536',
                    'old_value': 'metric_formula_accessor_max',
                },
                "root['state']['visualization']['goalAccessor']": {
                    'new_value': 'cf52eadf-a491-a207-b2ea-cb3c8a455724',
                    'old_value': 'metric_formula_accessor_goal',
                },
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM metrics-* | STATS avg_memory = AVG(system.memory.used.pct)'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'avg_memory',
                        'columnId': 'metric_formula_accessor',
                        'label': 'avg_memory',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'avg_memory'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][3]": {
                    'new_value': {
                        'fieldName': '0.7',
                        'columnId': 'cf52eadf-a491-a207-b2ea-cb3c8a455724',
                    },
                    'old_value': {'columnId': 'metric_formula_accessor_goal', 'fieldName': '0.7'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][3]": {
                    'new_value': {
                        'fieldName': '0.7',
                        'columnId': 'cf52eadf-a491-a207-b2ea-cb3c8a455724',
                    },
                    'old_value': {'columnId': 'metric_formula_accessor_goal', 'fieldName': '0.7'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'avg_memory',
                        'columnId': 'metric_formula_accessor',
                        'label': 'avg_memory',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'avg_memory'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {'fieldName': '0', 'columnId': 'd346c9c0-f807-92dc-4a87-dd7cfe500505'},
                    'old_value': {'columnId': 'metric_formula_accessor_max', 'fieldName': '1'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {'fieldName': '0', 'columnId': 'd346c9c0-f807-92dc-4a87-dd7cfe500505'},
                    'old_value': {'columnId': 'metric_formula_accessor_max', 'fieldName': '1'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][2]": {
                    'new_value': {'fieldName': '1', 'columnId': '937e1915-1fe1-eff3-2bca-2e6f3dfdd536'},
                    'old_value': {'columnId': 'metric_formula_accessor_min', 'fieldName': '0'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][2]": {
                    'new_value': {'fieldName': '1', 'columnId': '937e1915-1fe1-eff3-2bca-2e6f3dfdd536'},
                    'old_value': {'columnId': 'metric_formula_accessor_min', 'fieldName': '0'},
                },
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"metrics-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
        }
    )


@pytest.mark.slow
async def test_gauge_circle_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test gauge with circle shape against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Gauge Circle Test
    panels:
      - title: Disk Usage Gauge
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: gauge
          query: FROM metrics-* | STATS avg_disk = AVG(system.filesystem.used.pct)
          metric:
            field: avg_disk
            id: metric_formula_accessor
          minimum: 0
          maximum: 1
          goal: 0.9
          appearance:
            shape: circle
"""

    typescript_config = """
    {
        chartType: 'gauge',
        title: 'Disk Usage Gauge',
        dataset: { esql: 'FROM metrics-* | STATS avg_disk = AVG(system.filesystem.used.pct)' },
        value: 'avg_disk',
        queryMinValue: '0',
        queryMaxValue: '1',
        queryGoalValue: '0.9',
        shape: 'circle',
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'gauge-circle-dynamic',
        'LensGaugeConfig',
        {'from': 'now-15m', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['visualization']['showBar']": True,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"metrics-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"metrics-*","timeFieldName":"@timestamp"}\']': {},
            },
            'values_changed': {
                "root['state']['visualization']['minAccessor']": {
                    'new_value': 'd346c9c0-f807-92dc-4a87-dd7cfe500505',
                    'old_value': 'metric_formula_accessor_min',
                },
                "root['state']['visualization']['maxAccessor']": {
                    'new_value': '937e1915-1fe1-eff3-2bca-2e6f3dfdd536',
                    'old_value': 'metric_formula_accessor_max',
                },
                "root['state']['visualization']['goalAccessor']": {
                    'new_value': 'a1f45243-6e59-79e5-6733-e4c375019e9b',
                    'old_value': 'metric_formula_accessor_goal',
                },
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM metrics-* | STATS avg_disk = AVG(system.filesystem.used.pct)'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'avg_disk',
                        'columnId': 'metric_formula_accessor',
                        'label': 'avg_disk',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'avg_disk'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][3]": {
                    'new_value': {
                        'fieldName': '0.9',
                        'columnId': 'a1f45243-6e59-79e5-6733-e4c375019e9b',
                    },
                    'old_value': {'columnId': 'metric_formula_accessor_goal', 'fieldName': '0.9'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][3]": {
                    'new_value': {
                        'fieldName': '0.9',
                        'columnId': 'a1f45243-6e59-79e5-6733-e4c375019e9b',
                    },
                    'old_value': {'columnId': 'metric_formula_accessor_goal', 'fieldName': '0.9'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'avg_disk',
                        'columnId': 'metric_formula_accessor',
                        'label': 'avg_disk',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'avg_disk'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {'fieldName': '0', 'columnId': 'd346c9c0-f807-92dc-4a87-dd7cfe500505'},
                    'old_value': {'columnId': 'metric_formula_accessor_max', 'fieldName': '1'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {'fieldName': '0', 'columnId': 'd346c9c0-f807-92dc-4a87-dd7cfe500505'},
                    'old_value': {'columnId': 'metric_formula_accessor_max', 'fieldName': '1'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][2]": {
                    'new_value': {'fieldName': '1', 'columnId': '937e1915-1fe1-eff3-2bca-2e6f3dfdd536'},
                    'old_value': {'columnId': 'metric_formula_accessor_min', 'fieldName': '0'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][2]": {
                    'new_value': {'fieldName': '1', 'columnId': '937e1915-1fe1-eff3-2bca-2e6f3dfdd536'},
                    'old_value': {'columnId': 'metric_formula_accessor_min', 'fieldName': '0'},
                },
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"metrics-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
        }
    )


@pytest.mark.slow
async def test_gauge_horizontal_bullet_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test gauge with horizontal bullet shape against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Gauge Horizontal Bullet Test
    panels:
      - title: Network Usage Gauge
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: gauge
          query: FROM metrics-* | STATS avg_network = AVG(system.network.in.bytes)
          metric:
            field: avg_network
            id: metric_formula_accessor
          minimum: 0
          maximum: 1000000
          goal: 500000
          appearance:
            shape: horizontalBullet
"""

    typescript_config = """
    {
        chartType: 'gauge',
        title: 'Network Usage Gauge',
        dataset: { esql: 'FROM metrics-* | STATS avg_network = AVG(system.network.in.bytes)' },
        value: 'avg_network',
        queryMinValue: '0',
        queryMaxValue: '1000000',
        queryGoalValue: '500000',
        shape: 'horizontalBullet',
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'gauge-horizontal-bullet-dynamic',
        'LensGaugeConfig',
        {'from': 'now-15m', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['visualization']['showBar']": True,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"metrics-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"metrics-*","timeFieldName":"@timestamp"}\']': {},
            },
            'values_changed': {
                "root['state']['visualization']['minAccessor']": {
                    'new_value': 'd346c9c0-f807-92dc-4a87-dd7cfe500505',
                    'old_value': 'metric_formula_accessor_min',
                },
                "root['state']['visualization']['maxAccessor']": {
                    'new_value': '1314f79c-0a54-d26b-4de9-dd97fbc02855',
                    'old_value': 'metric_formula_accessor_max',
                },
                "root['state']['visualization']['goalAccessor']": {
                    'new_value': 'b3a35fc3-0d40-fc3d-ff6e-c731fd8a883a',
                    'old_value': 'metric_formula_accessor_goal',
                },
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM metrics-* | STATS avg_network = AVG(system.network.in.bytes)'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'avg_network',
                        'columnId': 'metric_formula_accessor',
                        'label': 'avg_network',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'avg_network'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][3]": {
                    'new_value': {
                        'fieldName': '500000',
                        'columnId': 'b3a35fc3-0d40-fc3d-ff6e-c731fd8a883a',
                    },
                    'old_value': {'columnId': 'metric_formula_accessor_goal', 'fieldName': '500000'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][3]": {
                    'new_value': {
                        'fieldName': '500000',
                        'columnId': 'b3a35fc3-0d40-fc3d-ff6e-c731fd8a883a',
                    },
                    'old_value': {'columnId': 'metric_formula_accessor_goal', 'fieldName': '500000'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'avg_network',
                        'columnId': 'metric_formula_accessor',
                        'label': 'avg_network',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'avg_network'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {'fieldName': '0', 'columnId': 'd346c9c0-f807-92dc-4a87-dd7cfe500505'},
                    'old_value': {'columnId': 'metric_formula_accessor_max', 'fieldName': '1000000'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {'fieldName': '0', 'columnId': 'd346c9c0-f807-92dc-4a87-dd7cfe500505'},
                    'old_value': {'columnId': 'metric_formula_accessor_max', 'fieldName': '1000000'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][2]": {
                    'new_value': {
                        'fieldName': '1000000',
                        'columnId': '1314f79c-0a54-d26b-4de9-dd97fbc02855',
                    },
                    'old_value': {'columnId': 'metric_formula_accessor_min', 'fieldName': '0'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][2]": {
                    'new_value': {
                        'fieldName': '1000000',
                        'columnId': '1314f79c-0a54-d26b-4de9-dd97fbc02855',
                    },
                    'old_value': {'columnId': 'metric_formula_accessor_min', 'fieldName': '0'},
                },
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"metrics-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
        }
    )


@pytest.mark.slow
async def test_gauge_vertical_bullet_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test gauge with vertical bullet shape against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Gauge Vertical Bullet Test
    panels:
      - title: API Latency Gauge
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: gauge
          query: FROM logs-* | STATS avg_latency = AVG(response_time)
          metric:
            field: avg_latency
            id: metric_formula_accessor
          minimum: 0
          maximum: 5000
          goal: 1000
          appearance:
            shape: verticalBullet
"""

    typescript_config = """
    {
        chartType: 'gauge',
        title: 'API Latency Gauge',
        dataset: { esql: 'FROM logs-* | STATS avg_latency = AVG(response_time)' },
        value: 'avg_latency',
        queryMinValue: '0',
        queryMaxValue: '5000',
        queryGoalValue: '1000',
        shape: 'verticalBullet',
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'gauge-vertical-bullet-dynamic',
        'LensGaugeConfig',
        {'from': 'now-15m', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['visualization']['showBar']": True,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
            },
            'values_changed': {
                "root['state']['visualization']['minAccessor']": {
                    'new_value': 'd346c9c0-f807-92dc-4a87-dd7cfe500505',
                    'old_value': 'metric_formula_accessor_min',
                },
                "root['state']['visualization']['maxAccessor']": {
                    'new_value': '98a247b3-b82f-a4cf-8aa2-affd386021e4',
                    'old_value': 'metric_formula_accessor_max',
                },
                "root['state']['visualization']['goalAccessor']": {
                    'new_value': 'cfd0e1ff-4f45-f725-0540-649f0d089c8a',
                    'old_value': 'metric_formula_accessor_goal',
                },
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS avg_latency = AVG(response_time)'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'avg_latency',
                        'columnId': 'metric_formula_accessor',
                        'label': 'avg_latency',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'avg_latency'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][3]": {
                    'new_value': {
                        'fieldName': '1000',
                        'columnId': 'cfd0e1ff-4f45-f725-0540-649f0d089c8a',
                    },
                    'old_value': {'columnId': 'metric_formula_accessor_goal', 'fieldName': '1000'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][3]": {
                    'new_value': {
                        'fieldName': '1000',
                        'columnId': 'cfd0e1ff-4f45-f725-0540-649f0d089c8a',
                    },
                    'old_value': {'columnId': 'metric_formula_accessor_goal', 'fieldName': '1000'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'avg_latency',
                        'columnId': 'metric_formula_accessor',
                        'label': 'avg_latency',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'avg_latency'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {'fieldName': '0', 'columnId': 'd346c9c0-f807-92dc-4a87-dd7cfe500505'},
                    'old_value': {'columnId': 'metric_formula_accessor_max', 'fieldName': '5000'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {'fieldName': '0', 'columnId': 'd346c9c0-f807-92dc-4a87-dd7cfe500505'},
                    'old_value': {'columnId': 'metric_formula_accessor_max', 'fieldName': '5000'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][2]": {
                    'new_value': {
                        'fieldName': '5000',
                        'columnId': '98a247b3-b82f-a4cf-8aa2-affd386021e4',
                    },
                    'old_value': {'columnId': 'metric_formula_accessor_min', 'fieldName': '0'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][2]": {
                    'new_value': {
                        'fieldName': '5000',
                        'columnId': '98a247b3-b82f-a4cf-8aa2-affd386021e4',
                    },
                    'old_value': {'columnId': 'metric_formula_accessor_min', 'fieldName': '0'},
                },
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
        }
    )


@pytest.mark.slow
async def test_heatmap_with_legend_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test heatmap with legend configuration against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Heatmap Legend Test
    panels:
      - title: Request Response Heatmap
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: heatmap
          query: FROM logs-* | STATS count = COUNT() BY request.method, response.keyword
          x_axis:
            field: request.method
            id: x_metric_formula_accessor
          y_axis:
            field: response.keyword
            id: y_metric_formula_accessor
          value:
            field: count
            id: metric_formula_accessor
"""

    typescript_config = """
    {
        chartType: 'heatmap',
        title: 'Request Response Heatmap',
        dataset: { esql: 'FROM logs-* | STATS count = COUNT() BY request.method, response.keyword' },
        xAxis: 'request.method',
        breakdown: 'response.keyword',
        value: 'count',
        legend: { show: true },
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'heatmap-legend-dynamic',
        'LensHeatmapConfig',
        {'from': 'now-7d', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
            },
            'values_changed': {
                "root['state']['visualization']['legend']['position']": {'new_value': 'right', 'old_value': 'left'},
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY request.method, response.keyword'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'request.method',
                        'columnId': 'x_metric_formula_accessor',
                        'label': 'request.method',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'y_metric_formula_accessor',
                        'fieldName': 'response.keyword',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'request.method',
                        'columnId': 'x_metric_formula_accessor',
                        'label': 'request.method',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'y_metric_formula_accessor',
                        'fieldName': 'response.keyword',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'fieldName': 'response.keyword',
                        'columnId': 'y_metric_formula_accessor',
                        'label': 'response.keyword',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'x_metric_formula_accessor',
                        'fieldName': 'request.method',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'fieldName': 'response.keyword',
                        'columnId': 'y_metric_formula_accessor',
                        'label': 'response.keyword',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'x_metric_formula_accessor',
                        'fieldName': 'request.method',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][2]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][2]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                },
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
        }
    )


@pytest.mark.slow
async def test_tagcloud_max_font_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test tagcloud with custom font settings against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Tagcloud Font Test
    panels:
      - title: Top User Agents
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: tagcloud
          query: FROM logs-* | STATS count = COUNT() BY user_agent.name | SORT count DESC | LIMIT 50
          dimension:
            field: user_agent.name
            id: metric_formula_accessor_breakdown
          metric:
            field: count
            id: metric_formula_accessor
"""

    typescript_config = """
    {
        chartType: 'tagcloud',
        title: 'Top User Agents',
        dataset: { esql: 'FROM logs-* | STATS count = COUNT() BY user_agent.name | SORT count DESC | LIMIT 50' },
        value: 'count',
        breakdown: 'user_agent.name',
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'tagcloud-font-dynamic',
        'LensTagCloudConfig',
        {'from': 'now-24h', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
            },
            'values_changed': {
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY user_agent.name | SORT count DESC | LIMIT 50'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'user_agent.name',
                        'columnId': 'metric_formula_accessor_breakdown',
                        'label': 'user_agent.name',
                        'customLabel': False,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown',
                        'fieldName': 'user_agent.name',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown',
                        'fieldName': 'user_agent.name',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'user_agent.name',
                        'columnId': 'metric_formula_accessor_breakdown',
                        'label': 'user_agent.name',
                        'customLabel': False,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                },
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
        }
    )


@pytest.mark.slow
async def test_datatable_multiple_dims_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test datatable with multiple dimensions against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Datatable Multiple Dims Test
    panels:
      - title: User Activity Table
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: datatable
          query: FROM logs-* | STATS count = COUNT(), avg_bytes = AVG(bytes) BY user.name, request.method | SORT count DESC | LIMIT 20
          dimensions:
            - field: user.name
              id: metric_formula_accessor_breakdown_0
            - field: request.method
              id: metric_formula_accessor_breakdown_1
          metrics:
            - field: count
              id: metric_formula_accessor
            - field: avg_bytes
              id: metric_formula_accessor_1
"""

    typescript_config = """
    {
        chartType: 'table',
        title: 'User Activity Table',
        dataset: { esql: 'FROM logs-* | STATS count = COUNT(), avg_bytes = AVG(bytes) BY user.name, request.method | SORT count DESC | LIMIT 20' },
        breakdown: ['user.name', 'request.method'],
        value: ['count', 'avg_bytes'],
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'datatable-multi-dims-dynamic',
        'LensTableConfig',
        {'from': 'now-24h', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
            },
            'values_changed': {
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'user.name',
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'label': 'user.name',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'fieldName': 'user.name',
                    },
                },
                "root['state']['query']": {
                    'new_value': {
                        'esql': 'FROM logs-* | STATS count = COUNT(), avg_bytes = AVG(bytes) BY user.name, request.method | SORT count DESC | LIMIT 20'
                    },
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'user.name',
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'label': 'user.name',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'fieldName': 'user.name',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'fieldName': 'request.method',
                        'columnId': 'metric_formula_accessor_breakdown_1',
                        'label': 'request.method',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown_1',
                        'fieldName': 'request.method',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'fieldName': 'request.method',
                        'columnId': 'metric_formula_accessor_breakdown_1',
                        'label': 'request.method',
                        'customLabel': False,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown_1',
                        'fieldName': 'request.method',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][2]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor',
                        'fieldName': ['count', 'avg_bytes'],
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][2]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor',
                        'fieldName': ['count', 'avg_bytes'],
                    },
                },
                "root['state']['visualization']['columns'][1]": {
                    'new_value': {
                        'columnId': 'metric_formula_accessor_breakdown_1',
                        'isTransposed': False,
                        'isMetric': False,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor_breakdown_0'},
                },
                "root['state']['visualization']['columns'][2]": {
                    'new_value': {
                        'columnId': 'metric_formula_accessor',
                        'isTransposed': False,
                        'isMetric': True,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor_breakdown_1'},
                },
                "root['state']['visualization']['columns'][0]": {
                    'new_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'isTransposed': False,
                        'isMetric': False,
                    },
                    'old_value': {'columnId': 'metric_formula_accessor'},
                },
            },
            'iterable_item_added': {
                "root['state']['visualization']['columns'][3]": {
                    'columnId': 'metric_formula_accessor_1',
                    'isTransposed': False,
                    'isMetric': True,
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][3]": {
                    'fieldName': 'avg_bytes',
                    'columnId': 'metric_formula_accessor_1',
                    'label': 'avg_bytes',
                    'customLabel': False,
                    'meta': {'type': 'number', 'esType': 'long'},
                    'inMetricDimension': True,
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][3]": {
                    'fieldName': 'avg_bytes',
                    'columnId': 'metric_formula_accessor_1',
                    'label': 'avg_bytes',
                    'customLabel': False,
                    'meta': {'type': 'number', 'esType': 'long'},
                    'inMetricDimension': True,
                },
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
        }
    )


@pytest.mark.slow
async def test_metric_secondary_esql_dynamic(
    shared_fixture_container: tuple[Any, Path],
) -> None:
    """Test metric with secondary metric against dynamically generated fixture."""
    container, output_dir = shared_fixture_container
    yaml_content = """
dashboards:
  - name: Metric Secondary Test
    panels:
      - title: Events with Max
        grid: {x: 0, y: 0, w: 24, h: 15}
        esql:
          id: layer_0
          type: metric
          query: FROM logs-* | STATS count = COUNT(), max_bytes = MAX(bytes)
          primary:
            field: count
            id: metric_formula_accessor
          secondary:
            field: max_bytes
            id: metric_formula_accessor_secondary
"""

    typescript_config = """
    {
        chartType: 'metric',
        title: 'Events with Max',
        dataset: { esql: 'FROM logs-* | STATS count = COUNT(), max_bytes = MAX(bytes)' },
        value: 'count',
        secondaryMetric: 'max_bytes',
    }
    """

    fixture = await generate_fixture(
        container,
        output_dir,
        typescript_config,
        'metric-secondary-dynamic',
        'LensMetricConfig',
        {'from': 'now-24h', 'to': 'now', 'type': 'relative'},
    )

    diff = compute_diff(yaml_content, fixture)

    assert diff == snapshot(
        {
            'dictionary_item_added': {
                "root['state']['visualization']['secondaryMetricAccessor']": 'metric_formula_accessor_secondary',
                "root['state']['datasourceStates']['formBased']": {'layers': {}},
                "root['state']['datasourceStates']['indexpattern']": {'layers': {}},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
            },
            'values_changed': {
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT(), max_bytes = MAX(bytes)'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'fieldName': 'count',
                        'columnId': 'metric_formula_accessor',
                        'label': 'count',
                        'customLabel': False,
                        'meta': {'type': 'number', 'esType': 'long'},
                        'inMetricDimension': True,
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                },
            },
            'iterable_item_added': {
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'fieldName': 'max_bytes',
                    'columnId': 'metric_formula_accessor_secondary',
                    'label': 'max_bytes',
                    'customLabel': False,
                    'meta': {'type': 'number', 'esType': 'long'},
                    'inMetricDimension': True,
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'fieldName': 'max_bytes',
                    'columnId': 'metric_formula_accessor_secondary',
                    'label': 'max_bytes',
                    'customLabel': False,
                    'meta': {'type': 'number', 'esType': 'long'},
                    'inMetricDimension': True,
                },
            },
            'iterable_item_removed': {
                "root['state']['internalReferences'][0]": {
                    'type': 'index-pattern',
                    'id': '{"index":"logs-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                }
            },
        }
    )
