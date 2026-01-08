"""End-to-end tests for ES|QL XY charts - YAML to dashboard JSON compilation."""

from pathlib import Path

from dirty_equals import IsUUID
from inline_snapshot import snapshot

from dashboard_compiler.dashboard_compiler import load, render
from tests.conftest import de_json_kbn_dashboard


def test_esql_line_chart_e2e(tmp_path: Path) -> None:
    """Test ES|QL line chart end-to-end compilation from YAML.

    This test verifies the full compilation pipeline from YAML to Kibana dashboard JSON
    for an ES|QL line chart, including the exact configuration from issue #489.
    """
    yaml_content = """---
dashboards:
  - name: '[Metrics Aerospike] Overview Yaml'
    description: A dashboard for Aerospike Metrics
    controls:
      - type: options
        label: Aerospike Namespace
        data_view: metrics-*
        field: aerospike.namespace
    panels:
      - title: ES|QL Line Chart
        grid: {x: 0, y: 0, w: 48, h: 16}
        esql:
          type: line
          query: "FROM logs-* | STATS count() BY @timestamp"
          dimension:
            field: "@timestamp"
          metrics:
            - field: count()
"""

    # Write YAML to temporary file
    yaml_file = tmp_path / 'esql_line_chart.yaml'
    _ = yaml_file.write_text(yaml_content)

    # Load and compile the dashboard
    dashboards = load(str(yaml_file))
    assert len(dashboards) > 0, 'Should load at least one dashboard'

    # Render to Kibana JSON
    kbn_dashboard = render(dashboards[0])
    dashboard = de_json_kbn_dashboard(kbn_dashboard.model_dump(by_alias=True, exclude_none=True))

    # Verify dashboard basic structure
    assert dashboard['attributes']['title'] == '[Metrics Aerospike] Overview Yaml'
    assert dashboard['attributes']['description'] == 'A dashboard for Aerospike Metrics'

    # Get the panel
    panels = dashboard['attributes']['panelsJSON']
    assert len(panels) == 1
    panel = panels[0]

    # Verify panel type is lens
    assert panel['type'] == 'lens'

    # Verify panel title (in embeddableConfig.attributes)
    assert panel['embeddableConfig']['attributes']['title'] == 'ES|QL Line Chart'

    # Verify the visualization state
    vis_state = panel['embeddableConfig']['attributes']['state']['visualization']
    assert vis_state['layers'][0] == snapshot(
        {
            'layerId': IsUUID,
            'accessors': [IsUUID],
            'layerType': 'data',
            'seriesType': 'line',
            'xAccessor': IsUUID,
            'position': 'top',
            'showGridlines': False,
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )

    # Verify the query
    query_state = panel['embeddableConfig']['attributes']['state']['query']
    assert query_state['esql'] == 'FROM logs-* | STATS count() BY @timestamp'


def test_esql_bar_chart_e2e(tmp_path: Path) -> None:
    """Test ES|QL bar chart end-to-end compilation from YAML with stacked mode and breakdown."""
    yaml_content = """---
dashboards:
  - name: 'ES|QL Bar Chart Test'
    panels:
      - title: Stacked Bar Chart
        grid: {x: 0, y: 0, w: 24, h: 12}
        esql:
          type: bar
          mode: stacked
          query: "FROM metrics-* | STATS count() BY @timestamp, aerospike.namespace.name"
          dimension:
            field: "@timestamp"
          metrics:
            - field: count()
          breakdown:
            field: aerospike.namespace.name
"""

    # Write YAML to temporary file
    yaml_file = tmp_path / 'esql_bar_chart.yaml'
    _ = yaml_file.write_text(yaml_content)

    # Load and compile the dashboard
    dashboards = load(str(yaml_file))
    assert len(dashboards) > 0

    # Render to Kibana JSON
    kbn_dashboard = render(dashboards[0])
    dashboard = de_json_kbn_dashboard(kbn_dashboard.model_dump(by_alias=True, exclude_none=True))

    panels = dashboard['attributes']['panelsJSON']
    assert len(panels) == 1
    panel = panels[0]

    # Verify panel type is lens
    assert panel['type'] == 'lens'

    # Verify panel title (in embeddableConfig.attributes)
    assert panel['embeddableConfig']['attributes']['title'] == 'Stacked Bar Chart'

    # Verify the visualization state for bar chart
    vis_state = panel['embeddableConfig']['attributes']['state']['visualization']
    layer = vis_state['layers'][0]

    # Verify it's a stacked bar chart with breakdown
    assert layer['seriesType'] == 'bar_stacked'
    assert 'splitAccessor' in layer
    assert layer['layerType'] == 'data'

    # Snapshot the layer structure
    assert layer == snapshot(
        {
            'layerId': IsUUID,
            'accessors': [IsUUID],
            'layerType': 'data',
            'seriesType': 'bar_stacked',
            'xAccessor': IsUUID,
            'position': 'top',
            'showGridlines': False,
            'splitAccessor': IsUUID,
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )

    # Verify the query
    query_state = panel['embeddableConfig']['attributes']['state']['query']
    assert query_state['esql'] == 'FROM metrics-* | STATS count() BY @timestamp, aerospike.namespace.name'


def test_esql_area_chart_e2e(tmp_path: Path) -> None:
    """Test ES|QL area chart end-to-end compilation from YAML with metrics and breakdown."""
    yaml_content = """---
dashboards:
  - name: 'ES|QL Area Chart Test'
    panels:
      - title: Area Chart with Breakdown
        grid: {x: 0, y: 0, w: 24, h: 12}
        esql:
          type: area
          query: "FROM metrics-* | STATS count() BY @timestamp, service.name"
          dimension:
            field: "@timestamp"
          metrics:
            - field: count()
          breakdown:
            field: service.name
"""

    # Write YAML to temporary file
    yaml_file = tmp_path / 'esql_area_chart.yaml'
    _ = yaml_file.write_text(yaml_content)

    # Load and compile the dashboard
    dashboards = load(str(yaml_file))
    assert len(dashboards) > 0

    # Render to Kibana JSON
    kbn_dashboard = render(dashboards[0])
    dashboard = de_json_kbn_dashboard(kbn_dashboard.model_dump(by_alias=True, exclude_none=True))

    panels = dashboard['attributes']['panelsJSON']
    assert len(panels) == 1
    panel = panels[0]

    # Verify panel type is lens
    assert panel['type'] == 'lens'

    # Verify panel title (in embeddableConfig.attributes)
    assert panel['embeddableConfig']['attributes']['title'] == 'Area Chart with Breakdown'

    # Verify the visualization state for area chart
    vis_state = panel['embeddableConfig']['attributes']['state']['visualization']
    layer = vis_state['layers'][0]

    # Verify it's an area chart with breakdown
    assert layer['seriesType'] == 'area'
    assert 'splitAccessor' in layer
    assert layer['layerType'] == 'data'

    # Snapshot the layer structure
    assert layer == snapshot(
        {
            'layerId': IsUUID,
            'accessors': [IsUUID],
            'layerType': 'data',
            'seriesType': 'area',
            'xAccessor': IsUUID,
            'position': 'top',
            'showGridlines': False,
            'splitAccessor': IsUUID,
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )

    # Verify the query
    query_state = panel['embeddableConfig']['attributes']['state']['query']
    assert query_state['esql'] == 'FROM metrics-* | STATS count() BY @timestamp, service.name'


def test_esql_line_chart_two_metrics_e2e(tmp_path: Path) -> None:
    """Test ES|QL line chart with two metrics - issue #710.

    This test verifies that ES|QL line charts can compile with multiple metrics,
    which was previously limited to only the first metric causing compilation failures.
    """
    yaml_content = """---
dashboards:
  - name: 'Multi-Metric Test'
    panels:
      - title: ES|QL Line Chart with Two Metrics
        grid: {x: 0, y: 0, w: 48, h: 16}
        esql:
          type: line
          query: "FROM logs-* | STATS count(), avg(response_time) BY @timestamp"
          dimension:
            field: "@timestamp"
          metrics:
            - field: count()
              label: "Request Count"
            - field: avg(response_time)
              label: "Avg Response Time"
"""

    # Write YAML to temporary file
    yaml_file = tmp_path / 'esql_two_metrics.yaml'
    _ = yaml_file.write_text(yaml_content)

    # Load and compile the dashboard
    dashboards = load(str(yaml_file))
    assert len(dashboards) > 0

    # Render to Kibana JSON
    kbn_dashboard = render(dashboards[0])
    dashboard = de_json_kbn_dashboard(kbn_dashboard.model_dump(by_alias=True, exclude_none=True))

    # Get the panel
    panels = dashboard['attributes']['panelsJSON']
    assert len(panels) == 1
    panel = panels[0]

    # Verify panel type is lens
    assert panel['type'] == 'lens'

    # Verify two metrics in accessors
    vis_state = panel['embeddableConfig']['attributes']['state']['visualization']
    layer = vis_state['layers'][0]
    assert len(layer['accessors']) == 2, 'Should have two metric accessors'

    # Verify the layer structure with two metrics
    assert layer == snapshot(
        {
            'layerId': IsUUID,
            'accessors': [IsUUID, IsUUID],
            'layerType': 'data',
            'seriesType': 'line',
            'xAccessor': IsUUID,
            'position': 'top',
            'showGridlines': False,
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
        }
    )

    # Verify the query
    query_state = panel['embeddableConfig']['attributes']['state']['query']
    assert query_state['esql'] == 'FROM logs-* | STATS count(), avg(response_time) BY @timestamp'
