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
#
# Note: We use layer_0 IDs to match what Kibana's LensConfigBuilder generates.
# =============================================================================


@pytest.mark.slow
async def test_metric_basic_esql_dynamic(
    require_docker: None,  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
) -> None:
    """Test basic metric compilation against dynamically generated fixture."""
    # Use layer_0 to match what LensConfigBuilder generates
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
          layer_id: layer_0
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

    fixture = await generate_fixture(
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
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]['customLabel']": False,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]['inMetricDimension']": True,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]['label']": 'count',
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]['meta']['esType']": 'long',
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]['customLabel']": False,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]['inMetricDimension']": True,
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]['label']": 'count',
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]['meta']['esType']": 'long',
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
            },
            'dictionary_item_removed': {
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
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
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT()'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
            },
        }
    )


@pytest.mark.slow
async def test_pie_chart_esql_dynamic(
    require_docker: None,  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
) -> None:
    """Test pie chart compilation against dynamically generated fixture."""
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
          layer_id: layer_0
"""

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

    fixture = await generate_fixture(
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
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
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
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
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
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'columnId': 'metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'count',
                        'inMetricDimension': True,
                        'label': 'count',
                        'meta': {'esType': 'long', 'type': 'number'},
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'fieldName': 'log.level',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'customLabel': False,
                        'fieldName': 'log.level',
                        'label': 'log.level',
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'columnId': 'metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'count',
                        'inMetricDimension': True,
                        'label': 'count',
                        'meta': {'esType': 'long', 'type': 'number'},
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'fieldName': 'log.level',
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'columnId': 'metric_formula_accessor_breakdown_0',
                        'customLabel': False,
                        'fieldName': 'log.level',
                        'label': 'log.level',
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'count'},
                },
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 10'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['visualization']['layers'][0]['legendDisplay']": {
                    'new_value': 'default',
                    'old_value': 'show',
                },
            },
        }
    )


@pytest.mark.slow
async def test_xy_chart_esql_dynamic(
    require_docker: None,  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
) -> None:
    """Test XY line chart compilation against dynamically generated fixture."""
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
          layer_id: layer_0
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
        legend: { show: true, position: 'right' },
    }
    """

    fixture = await generate_fixture(
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
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['timeField']": '@timestamp',
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
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"logs-*","timeFieldName":"@timestamp"}\']': {},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"logs-*","timeFieldName":"@timestamp"}',
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
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'customLabel': False,
                        'fieldName': 'count',
                        'inMetricDimension': True,
                        'label': 'count',
                        'meta': {'esType': 'long', 'type': 'number'},
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor0', 'fieldName': '@timestamp'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'columnId': 'x_metric_formula_accessor0',
                        'customLabel': False,
                        'fieldName': '@timestamp',
                        'label': '@timestamp',
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'customLabel': False,
                        'fieldName': 'count',
                        'inMetricDimension': True,
                        'label': 'count',
                        'meta': {'esType': 'long', 'type': 'number'},
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor0', 'fieldName': '@timestamp'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'columnId': 'x_metric_formula_accessor0',
                        'customLabel': False,
                        'fieldName': '@timestamp',
                        'label': '@timestamp',
                    },
                    'old_value': {
                        'columnId': 'metric_formula_accessor0_0',
                        'fieldName': 'count',
                        'meta': {'type': 'number'},
                    },
                },
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM logs-* | STATS count = COUNT() BY @timestamp'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
            },
        }
    )


@pytest.mark.slow
async def test_gauge_esql_dynamic(
    require_docker: None,  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
) -> None:
    """Test gauge compilation against dynamically generated fixture."""
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
          layer_id: layer_0
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
                "root['references'][0]": {
                    'id': '{"index":"metrics-*","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                    'type': 'index-pattern',
                },
            },
            'values_changed': {
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'columnId': 'metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'avg_cpu',
                        'inMetricDimension': True,
                        'label': 'avg_cpu',
                        'meta': {'esType': 'long', 'type': 'number'},
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'avg_cpu'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {'columnId': 'layer_0_1', 'fieldName': '0'},
                    'old_value': {'columnId': 'metric_formula_accessor_max', 'fieldName': '1'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][2]": {
                    'new_value': {'columnId': 'layer_0_2', 'fieldName': '1'},
                    'old_value': {'columnId': 'metric_formula_accessor_min', 'fieldName': '0'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][3]": {
                    'new_value': {'columnId': 'layer_0_3', 'fieldName': '0.8'},
                    'old_value': {'columnId': 'metric_formula_accessor_goal', 'fieldName': '0.8'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'columnId': 'metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'avg_cpu',
                        'inMetricDimension': True,
                        'label': 'avg_cpu',
                        'meta': {'esType': 'long', 'type': 'number'},
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'avg_cpu'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {'columnId': 'layer_0_1', 'fieldName': '0'},
                    'old_value': {'columnId': 'metric_formula_accessor_max', 'fieldName': '1'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][2]": {
                    'new_value': {'columnId': 'layer_0_2', 'fieldName': '1'},
                    'old_value': {'columnId': 'metric_formula_accessor_min', 'fieldName': '0'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][3]": {
                    'new_value': {'columnId': 'layer_0_3', 'fieldName': '0.8'},
                    'old_value': {'columnId': 'metric_formula_accessor_goal', 'fieldName': '0.8'},
                },
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM metrics-* | STATS avg_cpu = AVG(system.cpu.total.pct)'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
                "root['state']['visualization']['goalAccessor']": {
                    'new_value': 'layer_0_3',
                    'old_value': 'metric_formula_accessor_goal',
                },
                "root['state']['visualization']['maxAccessor']": {
                    'new_value': 'layer_0_2',
                    'old_value': 'metric_formula_accessor_max',
                },
                "root['state']['visualization']['minAccessor']": {
                    'new_value': 'layer_0_1',
                    'old_value': 'metric_formula_accessor_min',
                },
            },
        }
    )


@pytest.mark.slow
async def test_heatmap_esql_dynamic(
    require_docker: None,  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
) -> None:
    """Test heatmap compilation against dynamically generated fixture."""
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
          layer_id: layer_0
"""

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

    fixture = await generate_fixture(
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
                'root[\'state\'][\'adHocDataViews\'][\'{"index":"kibana_sample_data_logs","timeFieldName":"@timestamp"}\']': {},
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['index']": '{"index":"kibana_sample_data_logs","timeFieldName":"@timestamp"}',
            },
            'iterable_item_removed': {
                "root['references'][0]": {
                    'id': '{"index":"kibana_sample_data_logs","timeFieldName":"@timestamp"}',
                    'name': 'indexpattern-datasource-layer-layer_0',
                    'type': 'index-pattern',
                },
            },
            'values_changed': {
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][0]": {
                    'new_value': {
                        'columnId': 'x_metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'geo.src',
                        'label': 'geo.src',
                    },
                    'old_value': {'columnId': 'y_metric_formula_accessor', 'fieldName': 'geo.dest'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][1]": {
                    'new_value': {
                        'columnId': 'y_metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'geo.dest',
                        'label': 'geo.dest',
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor', 'fieldName': 'geo.src'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['allColumns'][2]": {
                    'new_value': {
                        'columnId': 'metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'bytes',
                        'inMetricDimension': True,
                        'label': 'bytes',
                        'meta': {'esType': 'long', 'type': 'number'},
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'bytes'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][0]": {
                    'new_value': {
                        'columnId': 'x_metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'geo.src',
                        'label': 'geo.src',
                    },
                    'old_value': {'columnId': 'y_metric_formula_accessor', 'fieldName': 'geo.dest'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][1]": {
                    'new_value': {
                        'columnId': 'y_metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'geo.dest',
                        'label': 'geo.dest',
                    },
                    'old_value': {'columnId': 'x_metric_formula_accessor', 'fieldName': 'geo.src'},
                },
                "root['state']['datasourceStates']['textBased']['layers']['layer_0']['columns'][2]": {
                    'new_value': {
                        'columnId': 'metric_formula_accessor',
                        'customLabel': False,
                        'fieldName': 'bytes',
                        'inMetricDimension': True,
                        'label': 'bytes',
                        'meta': {'esType': 'long', 'type': 'number'},
                    },
                    'old_value': {'columnId': 'metric_formula_accessor', 'fieldName': 'bytes'},
                },
                "root['state']['query']": {
                    'new_value': {'esql': 'FROM kibana_sample_data_logs | STATS bytes = SUM(bytes) BY geo.dest, geo.src'},
                    'old_value': {'language': 'kuery', 'query': ''},
                },
            },
        }
    )
