"""Test compiled output against Kibana JSON fixtures.

This module contains individual test functions that compare compiled visualization output
against known-good Kibana JSON fixtures from the kb-yaml-to-lens-fixtures repository.

Fixture Repository:
    https://github.com/strawgate/kb-yaml-to-lens-fixtures
    - output/v8.19.9/ - Kibana 8.19.9 ES|QL visualizations

Test Pattern:
    Each test function:
    1. Defines a YAML-equivalent config dict matching the fixture's visualization
    2. Compiles the config using the compiler
    3. Uses inline snapshots with dirty-equals to compare against the fixture

    Differences are captured in snapshots and should decrease over time as the compiler
    improves to match Kibana's output more closely.

Note:
    Parametrized tests cannot be used with inline-snapshot, so each fixture
    comparison is an individual test function.
"""

from typing import Any

from dirty_equals import IsUUID
from inline_snapshot import snapshot

from dashboard_compiler.panels.charts.config import ESQLPiePanelConfig
from dashboard_compiler.panels.charts.metric.compile import compile_esql_metric_chart
from dashboard_compiler.panels.charts.metric.config import ESQLMetricChart
from dashboard_compiler.panels.charts.pie.compile import compile_esql_pie_chart
from dashboard_compiler.panels.charts.xy.compile import compile_esql_xy_chart
from dashboard_compiler.panels.charts.xy.config import ESQLAreaChart, ESQLBarChart
from tests.fixtures import extract_visualization_state, load_fixture_by_name

# =============================================================================
# Metric Chart Fixtures (v8.19.9)
# =============================================================================


def test_metric_basic_esql_matches_fixture() -> None:
    """Test basic ESQL metric chart matches Kibana fixture.

    Fixture: output/v8.19.9/metric-basic-esql.json
    - Simple COUNT() metric with no breakdown or secondary metric
    """
    # Load the Kibana fixture
    fixture = load_fixture_by_name('metric-basic-esql', version='v8.19.9')
    fixture_viz = extract_visualization_state(fixture)

    # Compile equivalent YAML config
    # The fixture uses: FROM logs-* | STATS count = COUNT()
    config: dict[str, Any] = {
        'type': 'metric',
        'primary': {
            'field': 'count',
            'id': 'metric_formula_accessor',  # Match fixture's columnId
        },
    }

    esql_chart = ESQLMetricChart.model_validate(config)
    _layer_id, _columns, compiled_viz = compile_esql_metric_chart(esql_chart)

    # Compare visualization states
    compiled_dict = compiled_viz.model_dump()

    # Snapshot the compiled output for tracking
    assert compiled_dict == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': 'metric_formula_accessor',
            'showBar': False,
        }
    )

    # Snapshot the fixture for reference
    assert fixture_viz == snapshot(
        {
            'layerId': 'layer_0',
            'layerType': 'data',
            'metricAccessor': 'metric_formula_accessor',
            'showBar': False,
        }
    )


def test_metric_with_breakdown_esql_matches_fixture() -> None:
    """Test ESQL metric chart with breakdown matches Kibana fixture.

    Fixture: output/v8.19.9/metric-with-breakdown-esql.json
    - COUNT() metric with breakdown by agent.name
    """
    # Load the Kibana fixture
    fixture = load_fixture_by_name('metric-with-breakdown-esql', version='v8.19.9')
    fixture_viz = extract_visualization_state(fixture)

    # Compile equivalent YAML config
    # Use IDs that match the fixture: metric_formula_accessor_breakdown (no _0 suffix)
    config: dict[str, Any] = {
        'type': 'metric',
        'primary': {
            'field': 'count',
            'id': 'metric_formula_accessor',
        },
        'breakdown': {
            'field': 'agent.name',
            'id': 'metric_formula_accessor_breakdown',
        },
    }

    esql_chart = ESQLMetricChart.model_validate(config)
    _layer_id, _columns, compiled_viz = compile_esql_metric_chart(esql_chart)

    # Compare visualization states
    compiled_dict = compiled_viz.model_dump()

    # Snapshot the compiled output
    assert compiled_dict == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': 'metric_formula_accessor',
            'showBar': False,
            'breakdownByAccessor': 'metric_formula_accessor_breakdown',
        }
    )

    # Snapshot the fixture for reference
    assert fixture_viz == snapshot(
        {
            'layerId': 'layer_0',
            'layerType': 'data',
            'metricAccessor': 'metric_formula_accessor',
            'showBar': False,
            'breakdownByAccessor': 'metric_formula_accessor_breakdown',
        }
    )


def test_metric_with_secondary_esql_matches_fixture() -> None:
    """Test ESQL metric chart with secondary metric matches Kibana fixture.

    Fixture: output/v8.19.9/metric-with-secondary-esql.json
    - Primary (avg_time) and secondary (max_time) metrics
    """
    # Load the Kibana fixture
    fixture = load_fixture_by_name('metric-with-secondary-esql', version='v8.19.9')
    fixture_viz = extract_visualization_state(fixture)

    # Compile equivalent YAML config
    # Fixture uses: metric_formula_accessor_secondary (not secondary_metric_formula_accessor)
    config: dict[str, Any] = {
        'type': 'metric',
        'primary': {
            'field': 'avg_time',
            'id': 'metric_formula_accessor',
        },
        'secondary': {
            'field': 'max_time',
            'id': 'metric_formula_accessor_secondary',
        },
    }

    esql_chart = ESQLMetricChart.model_validate(config)
    _layer_id, _columns, compiled_viz = compile_esql_metric_chart(esql_chart)

    # Compare visualization states
    compiled_dict = compiled_viz.model_dump()

    # Snapshot the compiled output
    assert compiled_dict == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': 'metric_formula_accessor',
            'showBar': False,
            'secondaryMetricAccessor': 'metric_formula_accessor_secondary',
        }
    )

    # Snapshot the fixture for reference
    assert fixture_viz == snapshot(
        {
            'layerId': 'layer_0',
            'layerType': 'data',
            'metricAccessor': 'metric_formula_accessor',
            'showBar': False,
            'secondaryMetricAccessor': 'metric_formula_accessor_secondary',
        }
    )


def test_metric_with_max_value_esql_matches_fixture() -> None:
    """Test ESQL metric chart with max value (progress bar) matches Kibana fixture.

    Fixture: output/v8.19.9/metric-with-max-value-esql.json
    - Metric with max value for progress bar display (storage used/total)

    NOTE: The ESQL metric compiler does not yet support the 'maximum' field.
    This test documents the gap - the compiled output is missing maxAccessor.
    """
    # Load the Kibana fixture
    fixture = load_fixture_by_name('metric-with-max-value-esql', version='v8.19.9')
    fixture_viz = extract_visualization_state(fixture)

    # Compile equivalent YAML config
    # Fixture uses: metric_formula_accessor_max, and the field is 'maximum' not 'max'
    config: dict[str, Any] = {
        'type': 'metric',
        'primary': {
            'field': 'used',
            'id': 'metric_formula_accessor',
        },
        'maximum': {
            'field': 'total',
            'id': 'metric_formula_accessor_max',
        },
    }

    esql_chart = ESQLMetricChart.model_validate(config)
    _layer_id, _columns, compiled_viz = compile_esql_metric_chart(esql_chart)

    # Compare visualization states
    compiled_dict = compiled_viz.model_dump()

    # Snapshot the compiled output
    # GAP: Compiler does not yet handle 'maximum' field - maxAccessor is missing
    # GAP: Compiler sets showBar=False, should be True when maxAccessor is set
    assert compiled_dict == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'metricAccessor': 'metric_formula_accessor',
            'showBar': False,
        }
    )

    # Snapshot the fixture for reference
    # Note: showBar is True when maxAccessor is set in Kibana UI
    assert fixture_viz == snapshot(
        {
            'layerId': 'layer_0',
            'layerType': 'data',
            'metricAccessor': 'metric_formula_accessor',
            'showBar': True,
            'maxAccessor': 'metric_formula_accessor_max',
        }
    )


# =============================================================================
# Pie Chart Fixtures (v8.19.9)
# =============================================================================


def test_pie_chart_esql_matches_fixture() -> None:
    """Test basic ESQL pie chart matches Kibana fixture.

    Fixture: output/v8.19.9/pie-chart-esql.json
    - Pie chart with COUNT() by a dimension
    """
    # Load the Kibana fixture
    fixture = load_fixture_by_name('pie-chart-esql', version='v8.19.9')
    fixture_viz = extract_visualization_state(fixture)

    # Compile equivalent YAML config
    config: dict[str, Any] = {
        'type': 'pie',
        'query': 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 10',
        'metrics': [
            {'field': 'count', 'id': 'metric_formula_accessor'},
        ],
        'dimensions': [
            {'field': 'log.level', 'id': 'metric_formula_accessor_breakdown_0'},
        ],
    }

    esql_chart = ESQLPiePanelConfig.model_validate(config)
    _layer_id, _columns, compiled_viz = compile_esql_pie_chart(esql_chart)

    # Get first layer for comparison
    compiled_layer = compiled_viz.layers[0].model_dump() if compiled_viz.layers else {}
    fixture_layer = fixture_viz.get('layers', [{}])[0] if fixture_viz.get('layers') else {}

    # Snapshot the compiled output
    assert compiled_layer == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
            'primaryGroups': ['metric_formula_accessor_breakdown_0'],
            'metrics': ['metric_formula_accessor'],
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'nestedLegend': False,
        }
    )

    # Snapshot the fixture layer for reference
    assert fixture_layer == snapshot(
        {
            'layerId': 'layer_0',
            'layerType': 'data',
            'metrics': ['metric_formula_accessor'],
            'allowMultipleMetrics': False,
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'show',
            'legendPosition': 'right',
            'primaryGroups': ['metric_formula_accessor_breakdown_0'],
        }
    )


def test_pie_chart_donut_esql_matches_fixture() -> None:
    """Test ESQL donut chart matches Kibana fixture.

    Fixture: output/v8.19.9/pie-chart-donut-esql.json
    - Donut chart variant
    """
    # Load the Kibana fixture
    fixture = load_fixture_by_name('pie-chart-donut-esql', version='v8.19.9')
    fixture_viz = extract_visualization_state(fixture)

    # Compile equivalent YAML config
    config: dict[str, Any] = {
        'type': 'pie',
        'query': 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 10',
        'metrics': [
            {'field': 'count', 'id': 'metric_formula_accessor'},
        ],
        'dimensions': [
            {'field': 'log.level', 'id': 'metric_formula_accessor_breakdown_0'},
        ],
        'appearance': {'donut': 'medium'},
    }

    esql_chart = ESQLPiePanelConfig.model_validate(config)
    _layer_id, _columns, compiled_viz = compile_esql_pie_chart(esql_chart)

    # Get first layer for comparison
    compiled_layer = compiled_viz.layers[0].model_dump() if compiled_viz.layers else {}
    fixture_layer = fixture_viz.get('layers', [{}])[0] if fixture_viz.get('layers') else {}

    # Snapshot the compiled output (donut)
    assert compiled_layer == snapshot(
        {
            'layerId': IsUUID,
            'layerType': 'data',
            'colorMapping': {
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
            },
            'primaryGroups': ['metric_formula_accessor_breakdown_0'],
            'metrics': ['metric_formula_accessor'],
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'default',
            'nestedLegend': False,
        }
    )

    # Snapshot the fixture for reference
    assert fixture_layer == snapshot(
        {
            'layerId': 'layer_0',
            'layerType': 'data',
            'metrics': ['metric_formula_accessor'],
            'allowMultipleMetrics': False,
            'numberDisplay': 'percent',
            'categoryDisplay': 'default',
            'legendDisplay': 'show',
            'legendPosition': 'right',
            'primaryGroups': ['metric_formula_accessor_breakdown_0'],
        }
    )


# =============================================================================
# XY Chart Fixtures (v8.19.9)
# =============================================================================


def test_xy_chart_bar_esql_matches_fixture() -> None:
    """Test ESQL bar chart matches Kibana fixture.

    Fixture: output/v8.19.9/xy-chart-bar-esql.json
    - Bar chart with COUNT() over time
    """
    # Load the Kibana fixture
    fixture = load_fixture_by_name('xy-chart-bar-esql', version='v8.19.9')
    fixture_viz = extract_visualization_state(fixture)

    # Compile equivalent YAML config
    # ESQLBarChart uses dimension/metrics pattern (not layers)
    config: dict[str, Any] = {
        'type': 'bar',
        'dimension': {'field': '@timestamp', 'id': 'x_metric_formula_accessor0'},
        'metrics': [{'field': 'count', 'id': 'metric_formula_accessor0_0'}],
    }

    esql_chart = ESQLBarChart.model_validate(config)
    _layer_id, _columns, compiled_viz = compile_esql_xy_chart(esql_chart)

    # Get first layer for comparison
    compiled_layers = [layer.model_dump() for layer in compiled_viz.layers] if compiled_viz.layers else []
    fixture_layers = fixture_viz.get('layers', [])

    # Snapshot the compiled output
    # Note: Compiler outputs additional fields (colorMapping, position, showGridlines) not in fixture
    # Note: Compiler defaults to bar_stacked, fixture has bar (non-stacked)
    assert compiled_layers == snapshot(
        [
            {
                'layerId': IsUUID,
                'layerType': 'data',
                'xAccessor': 'x_metric_formula_accessor0',
                'accessors': ['metric_formula_accessor0_0'],
                'seriesType': 'bar_stacked',
                'position': 'top',
                'showGridlines': False,
                'colorMapping': {
                    'assignments': [],
                    'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                    'paletteId': 'eui_amsterdam_color_blind',
                    'colorMode': {'type': 'categorical'},
                },
            }
        ]
    )

    # Snapshot the fixture layers for reference
    assert fixture_layers == snapshot(
        [
            {
                'layerId': 'layer_0',
                'layerType': 'data',
                'xAccessor': 'x_metric_formula_accessor0',
                'accessors': ['metric_formula_accessor0_0'],
                'seriesType': 'bar',
            }
        ]
    )


def test_xy_chart_area_esql_matches_fixture() -> None:
    """Test ESQL area chart matches Kibana fixture.

    Fixture: output/v8.19.9/xy-chart-area-esql.json
    - Area chart variant
    """
    # Load the Kibana fixture
    fixture = load_fixture_by_name('xy-chart-area-esql', version='v8.19.9')
    fixture_viz = extract_visualization_state(fixture)

    # Compile equivalent YAML config
    # Note: Area chart defaults to mode='stacked', so we set mode='unstacked' to match fixture
    config: dict[str, Any] = {
        'type': 'area',
        'mode': 'unstacked',
        'dimension': {'field': '@timestamp', 'id': 'x_metric_formula_accessor0'},
        'metrics': [{'field': 'count', 'id': 'metric_formula_accessor0_0'}],
    }

    esql_chart = ESQLAreaChart.model_validate(config)
    _layer_id, _columns, compiled_viz = compile_esql_xy_chart(esql_chart)

    # Get first layer for comparison
    compiled_layers = [layer.model_dump() for layer in compiled_viz.layers] if compiled_viz.layers else []
    fixture_layers = fixture_viz.get('layers', [])

    # Snapshot the compiled output
    # Note: Compiler uses 'area_unstacked' while Kibana fixture uses 'area' (both mean unstacked)
    assert compiled_layers == snapshot(
        [
            {
                'layerId': IsUUID,
                'layerType': 'data',
                'xAccessor': 'x_metric_formula_accessor0',
                'accessors': ['metric_formula_accessor0_0'],
                'seriesType': 'area_unstacked',
                'position': 'top',
                'showGridlines': False,
                'colorMapping': {
                    'assignments': [],
                    'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                    'paletteId': 'eui_amsterdam_color_blind',
                    'colorMode': {'type': 'categorical'},
                },
            }
        ]
    )

    # Snapshot the fixture layers for reference
    # Note: Kibana uses 'area' while our compiler uses 'area_unstacked' for the same behavior
    assert fixture_layers == snapshot(
        [
            {
                'layerId': 'layer_0',
                'layerType': 'data',
                'xAccessor': 'x_metric_formula_accessor0',
                'accessors': ['metric_formula_accessor0_0'],
                'seriesType': 'area',
            }
        ]
    )


def test_xy_chart_bar_stacked_esql_matches_fixture() -> None:
    """Test ESQL stacked bar chart matches Kibana fixture.

    Fixture: output/v8.19.9/xy-chart-bar-stacked-esql.json
    - Stacked bar chart with breakdown
    """
    # Load the Kibana fixture
    fixture = load_fixture_by_name('xy-chart-bar-stacked-esql', version='v8.19.9')
    fixture_viz = extract_visualization_state(fixture)

    # Compile equivalent YAML config
    config: dict[str, Any] = {
        'type': 'bar',
        'mode': 'stacked',
        'dimension': {'field': 'timestamp_bucket', 'id': 'x_metric_formula_accessor0'},
        'metrics': [{'field': 'count', 'id': 'metric_formula_accessor0_0'}],
        'breakdown': {'field': 'log.level', 'id': 'metric_formula_accessor0_breakdown'},
    }

    esql_chart = ESQLBarChart.model_validate(config)
    _layer_id, _columns, compiled_viz = compile_esql_xy_chart(esql_chart)

    # Get first layer for comparison
    compiled_layers = [layer.model_dump() for layer in compiled_viz.layers] if compiled_viz.layers else []
    fixture_layers = fixture_viz.get('layers', [])

    # Snapshot the compiled output
    assert compiled_layers == snapshot(
        [
            {
                'layerId': IsUUID,
                'layerType': 'data',
                'xAccessor': 'x_metric_formula_accessor0',
                'accessors': ['metric_formula_accessor0_0'],
                'splitAccessor': 'metric_formula_accessor0_breakdown',
                'seriesType': 'bar_stacked',
                'position': 'top',
                'showGridlines': False,
                'colorMapping': {
                    'assignments': [],
                    'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
                    'paletteId': 'eui_amsterdam_color_blind',
                    'colorMode': {'type': 'categorical'},
                },
            }
        ]
    )

    # Snapshot the fixture layers for reference
    # Note: Fixture uses y_metric_formula_accessor0 for splitAccessor, we use metric_formula_accessor0_breakdown
    assert fixture_layers == snapshot(
        [
            {
                'layerId': 'layer_0',
                'layerType': 'data',
                'xAccessor': 'x_metric_formula_accessor0',
                'splitAccessor': 'y_metric_formula_accessor0',
                'accessors': ['metric_formula_accessor0_0'],
                'seriesType': 'bar_stacked',
            }
        ]
    )
